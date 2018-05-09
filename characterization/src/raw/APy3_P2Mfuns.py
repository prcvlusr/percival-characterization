# -*- coding: utf-8 -*-
"""
general functions and fitting
(a half-decent language would have those functions already). Python is worth what it costs.
"""
#%% imports
#
import sys # command line argument, print w/o newline, version
import numpy
from scipy import stats # linear regression
from scipy.optimize import curve_fit # non-linear fit
import math
import scipy
import matplotlib
import os # list files in a folder
import re # to sort naturally
import h5py # deal with HDF5
import tkinter
#
from mpl_toolkits.mplot3d import Axes3D
#
#
#
#%% constant
VERYBIGNUMBER= 1e18
#
NSmplRst=2
NGrp=212
NPad=45
NADC=7
NColInBlock=32
NRowInBlock=NADC #7
NCol=NColInBlock*NPad # 32*45=1440, including RefCol
NRow= NADC*NGrp # 212*7=1484
#
iGn=0; iCrs=1; iFn=2 
iSmpl=0; iRst=1 
#   
#
#
# percival-specific data reordering functions
#
# from P2M manual
N_xcolArray=4
N_ncolArray=8
NADC=7
colArray= numpy.arange(N_xcolArray*N_ncolArray).reshape((N_xcolArray,N_ncolArray)).transpose()
colArray= numpy.fliplr(colArray) # in the end it is colArray[ix,in]
#
# this gives the (iADC,iCol) indices of a pixel in a Rowblk, given its sequence in the streamout 
ADCcolArray_1DA=[]
for i_n in range(N_ncolArray):   
    for i_ADC in range(NADC)[::-1]:
        for i_x in range(N_xcolArray):
            ADCcolArray_1DA += [(i_ADC,colArray[i_n,i_x])]
ADCcolArray_1DA=numpy.array(ADCcolArray_1DA) #to use this:  for ipix in range(32*7): (ord_ADC,ord_col)=ADCcolArray_1DA[ipix]
#
iG=0
iH0= numpy.arange(21+1,0+1-1,-1)
iH1= numpy.arange(22+21+1,22+0+1-1,-1)
iP2M_ColGrp=numpy.append(numpy.array(iG),iH0)
iP2M_ColGrp=numpy.append(iP2M_ColGrp,iH1)
#
def reorder_pixels_GnCrsFn(disord_4DAr,NADC,NColInRowBlk):
    ''' P2M pixel reorder for a image: (NGrp,NDataPads,NADC*NColInRowBlk,3),disordered =>  (NGrp,NDataPads,NADC,NColInRowBlk,3),ordered '''
    (aux_NGrp,aux_NPads,aux_pixInBlk, auxNGnCrsFn)= disord_4DAr.shape    
    ord_5DAr= numpy.zeros((aux_NGrp,aux_NPads,NADC,NColInRowBlk,auxNGnCrsFn)).astype('uint8')
    aux_pixOrd_padDisord_5DAr= numpy.zeros((aux_NGrp,aux_NPads,NADC,NColInRowBlk,auxNGnCrsFn)).astype('uint8')   
    # pixel reorder inside each block
    for ipix in range(NADC*NColInRowBlk):
        (ord_ADC,ord_Col)=ADCcolArray_1DA[ipix]
        aux_pixOrd_padDisord_5DAr[:,:,ord_ADC,ord_Col,:]= disord_4DAr[:,:,ipix,:]    
    # ColGrp order from chipscope to P2M
    for iColGrp in range(aux_NPads):
        ord_5DAr[:,iColGrp,:,:,:]= aux_pixOrd_padDisord_5DAr[:,iP2M_ColGrp[iColGrp],:,:,:]    
    return ord_5DAr    
#
# percival-specific data conversion functions
#
def convert_GnCrsFn_2_DLSraw(in_GnCrsFn_int16, inErr, outERR):
    ''' (Nimg,Smpl/Rst,NRow,NCol,Gn/Crs/Fn),int16(err=inErr) => DLSraw: Smpl&Rst(Nimg,NRow,NCol),uint16(err=outErr):[X,GG,FFFFFFFF,CCCCC]'''
    multiImg_SmplRstGnGrsFn_u16=numpy.clip(in_GnCrsFn_int16,0,(2**8)-1)
    multiImg_SmplRstGnGrsFn_u16= multiImg_SmplRstGnGrsFn_u16.astype('uint16')
    # convert to DLSraw format
    (NImg,aux_NSmplRst,aux_NRow,aux_NCol,aux_NGnCrsFn)= in_GnCrsFn_int16.shape
    out_multiImg_Smpl_DLSraw= numpy.zeros((NImg, NGrp*NRowInBlock,NPad*NColInBlock)).astype('uint16')
    out_multiImg_Rst_DLSraw= numpy.zeros((NImg, NGrp*NRowInBlock,NPad*NColInBlock)).astype('uint16')  
    out_multiImg_Smpl_DLSraw[:,:,:]= ((2**13)*multiImg_SmplRstGnGrsFn_u16[:,iSmpl,:,:,iGn].astype('uint16'))+ \
                                ((2**5)*multiImg_SmplRstGnGrsFn_u16[:,iSmpl,:,:,iFn].astype('uint16'))+\
                                multiImg_SmplRstGnGrsFn_u16[:,iSmpl,:,:,iCrs].astype('uint16') 
    out_multiImg_Rst_DLSraw[:,:,:]= ((2**13)*multiImg_SmplRstGnGrsFn_u16[:,iRst,:,:,iGn].astype('uint16'))+ \
                                ((2**5)*multiImg_SmplRstGnGrsFn_u16[:,iRst,:,:,iFn].astype('uint16'))+\
                                multiImg_SmplRstGnGrsFn_u16[:,iRst,:,:,iCrs].astype('uint16')               
    #%% track errors in DLSraw mode with the ERRDLSraw (max of uint16) value (usually this in not reached because pixel= 15 bit)
    errMask= in_GnCrsFn_int16[:,iSmpl,:,:,iGn]==inErr
    out_multiImg_Smpl_DLSraw[errMask]= outERR
    errMask= in_GnCrsFn_int16[:,iRst,:,:,iGn]==inErr
    out_multiImg_Rst_DLSraw[errMask]= outERR
    #
    return (out_multiImg_Smpl_DLSraw,out_multiImg_Rst_DLSraw)  
#       
def convert_DLSraw_2_GnCrsFn(in_Smpl_DLSraw, in_Rst_DLSraw, inErr, outERR):
    ''' (Nimg,Smpl/Rst,NRow,NCol,Gn/Crs/Fn),int16(err=inErr) <= DLSraw: Smpl&Rst(Nimg,NRow,NCol),uint16(err=outErr):[X,GG,FFFFFFFF,CCCCC]'''
    in_Smpl_uint16=numpy.clip(in_Smpl_DLSraw,0,(2**15)-1).astype('uint16')
    in_Rst_uint16=numpy.clip(in_Rst_DLSraw,0,(2**15)-1).astype('uint16')
    #
    (aux_NImg,aux_NRow,aux_NCol)=in_Smpl_DLSraw.shape
    auxSmpl_multiImg_GnCrsFn= numpy.zeros((aux_NImg,aux_NRow,aux_NCol,3)).astype('uint8')
    auxRst_multiImg_GnCrsFn= numpy.zeros((aux_NImg,aux_NRow,aux_NCol,3)).astype('uint8')
    out_multiImg_GnCrsFn= numpy.zeros((aux_NImg,2,aux_NRow,aux_NCol,3)).astype('int16')
    #
    imgGn= numpy.zeros((aux_NRow, aux_NCol)).astype('uint8')
    imgCrs=numpy.zeros_like(imgGn).astype('uint8')
    imgFn=numpy.zeros_like(imgGn).astype('uint8')
    for iImg in range(aux_NImg):
        imgGn= in_Smpl_uint16[iImg,:,:]//(2**13)
        imgFn= (in_Smpl_uint16[iImg,:,:]-(imgGn.astype('uint16')*(2**13)))//(2**5)
        imgCrs= in_Smpl_uint16[iImg,:,:] -(imgGn.astype('uint16')*(2**13)) -(imgFn.astype('uint16')*(2**5))
        auxSmpl_multiImg_GnCrsFn[iImg,:,:,iGn]=imgGn
        auxSmpl_multiImg_GnCrsFn[iImg,:,:,iCrs]=imgCrs
        auxSmpl_multiImg_GnCrsFn[iImg,:,:,iFn]=imgFn
        #
        imgGn= in_Rst_uint16[iImg,:,:]//(2**13)
        imgFn= (in_Rst_uint16[iImg,:,:]-(imgGn.astype('uint16')*(2**13)))//(2**5)
        imgCrs= in_Rst_uint16[iImg,:,:] -(imgGn.astype('uint16')*(2**13)) -(imgFn.astype('uint16')*(2**5))
        auxRst_multiImg_GnCrsFn[iImg,:,:,iGn]=imgGn
        auxRst_multiImg_GnCrsFn[iImg,:,:,iCrs]=imgCrs
        auxRst_multiImg_GnCrsFn[iImg,:,:,iFn]=imgFn           
    #
    #%% track errors in GnCrsFn mode with the ERRint16 (-256) value (usually this in tot reached because all>0)
    auxSmpl_multiImg_GnCrsFn=auxSmpl_multiImg_GnCrsFn.astype('uint16')
    auxRst_multiImg_GnCrsFn=auxRst_multiImg_GnCrsFn.astype('uint16')
    errMask= in_Smpl_DLSraw[:,:,:]==inErr
    auxSmpl_multiImg_GnCrsFn[errMask,:]= outERR        
    errMask= in_Rst_DLSraw[:,:,:]==inErr
    auxRst_multiImg_GnCrsFn[errMask,:]= outERR 
    #             
    out_multiImg_GnCrsFn[:,iSmpl,:,:,:]= auxSmpl_multiImg_GnCrsFn[:,:,:,:]
    out_multiImg_GnCrsFn[:,iRst,:,:,:]= auxRst_multiImg_GnCrsFn[:,:,:,:]
    #    
    return(out_multiImg_GnCrsFn)
#
#
#
#%% percival-specific debug-plot dunctions

def percDebug_plot_6x2D(GnSmpl,CrsSmpl,FnSmpl, GnRst,CrsRst,FnRst, label_title,ErrBelow):
    """ 2D plot of Smpl/Rst, Gn/Crs/Fn, give mark as error (white) the values << ErrBelow """ 
    cmap = matplotlib.pyplot.cm.jet
    cmap.set_under(color='white') 
    #fig = matplotlib.pyplot.figure(figsize=(18,12))
    fig = matplotlib.pyplot.figure()
    fig.canvas.set_window_title(label_title) 
    label_x="col"; label_y="row"
    #
    matplotlib.pyplot.subplot(2,3,1)
    matplotlib.pyplot.imshow(GnSmpl, interpolation='none', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Sample Gain')
    matplotlib.pyplot.clim(0,3)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();
    #
    matplotlib.pyplot.subplot(2,3,2)
    matplotlib.pyplot.imshow(CrsSmpl, interpolation='none', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Sample Coarse')
    matplotlib.pyplot.clim(0,31)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();
    #
    matplotlib.pyplot.subplot(2,3,3)
    matplotlib.pyplot.imshow(FnSmpl, interpolation='none', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Sample Fine')
    matplotlib.pyplot.clim(0,255)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();
    #
    matplotlib.pyplot.subplot(2,3,4)
    matplotlib.pyplot.imshow(GnRst, interpolation='none', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Reset Gain (not relevant)')
    matplotlib.pyplot.clim(0,3)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();
    #
    matplotlib.pyplot.subplot(2,3,5)
    matplotlib.pyplot.imshow(CrsRst, interpolation='none', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Reset Coarse')
    matplotlib.pyplot.clim(0,31)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();
    #
    matplotlib.pyplot.subplot(2,3,6)
    matplotlib.pyplot.imshow(FnRst, interpolation='none', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Reset Fine')
    matplotlib.pyplot.clim(0,255)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();
    matplotlib.pyplot.show(block=False)
    return fig
#
def percDebug_plot_2x2D(ShtSmpl,ShtRst, label_title, ErrAbove):  
    ''' plot Smpl & Rst img, white if above ErrAbove (e.g. 33000)''' 
    cmap = matplotlib.pyplot.cm.jet
    cmap.set_over(color='white') 
    fig = matplotlib.pyplot.figure()
    fig.canvas.set_window_title(label_title)
    label_x="col"; label_y="row"
    #
    matplotlib.pyplot.subplot(1,2,1); 
    matplotlib.pyplot.imshow(ShtSmpl, interpolation='none', cmap=cmap, vmax=ErrAbove)
    matplotlib.pyplot.title('Sample')
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y) 
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();   
    #
    matplotlib.pyplot.subplot(1,2,2); 
    matplotlib.pyplot.imshow(ShtRst, interpolation='none', cmap=cmap, vmax=ErrAbove)
    matplotlib.pyplot.title('Reset')
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();  
    #
    matplotlib.pyplot.show(block=False)
    return fig
#
