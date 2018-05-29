import copy
import matplotlib
# Generate 2D images having a window appear
# matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

from plot_base import PlotBase  # noqa E402

import webbrowser # to show images

#%% my imports & flags
from APy3_auxINIT import *
#import numpy
#import time # to have time
#import os # to recognize if files exist
#import APy3_GENfuns
#import APy3_P2Mfuns
#
ERRint16=-256
ERRBlw= -0.1
ERRDLSraw= 65535
iGn=0; iCrs=1; iFn=2 
iSmpl=0; iRst=1 
#

class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["col"] = None
        new_kwargs["row"] = None
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def _check_dimension(self, data):
        if data.shape[0] != 1:
            raise("Plot method one image can only show one image at the time.")

    def _generate_single_plot(self, data, plot_title, label, out_fname):       
        ''' 2D plot set <-0.1 as white'''
        fig= APy3_GENfuns.plot_2D(data,"cols","rows",plot_title,True,-0.1)
        fig.savefig(out_fname, dpi=(600))
        webbrowser.open(out_fname+'.png')

    def plot_combined(self):
        ''' debugging of DLS-DAQ output (starting from 16-bit files)'''
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script beginning at {0}".format(aux_timeId) ,'blue')
        #
        NADC=APy3_P2Mfuns.NADC #7
        NGrp=APy3_P2Mfuns.NGrp #212
        #
        #%% default values
        dflt_filenamepath_h5= self._input_fname
        dflt_showThisImg= self._frame
        dflt_filenamepath_tcpdumpCcompare="/home/marras/PERCIVAL/PercFramework/data/h5_scrmbl_view/h5in/"+"compare_p2018.04.13crdAQ_h14_lnk0.dmp"
        #dflt_filenamepath_tcpdumpCcompare="/home/marras/PERCIVAL/PercFramework/data/h5_scrmbl_view/h5in/"+"NotARealFile"
        dflt_debugFlag='N'; # dflt_debug=True 
        dflt_cleanMemFlag='Y'
        dflt_verboseFlag='Y'
        #
        #%% GUI window
        GUIwin_arguments= []
        GUIwin_arguments+= ['path & name of h5 file to read'] 
        GUIwin_arguments+= [dflt_filenamepath_h5] 
        GUIwin_arguments+= ['image to process'] 
        GUIwin_arguments+= [dflt_showThisImg] 
        GUIwin_arguments+= ['path & name of tcpdump (comparison) file to read'] 
        GUIwin_arguments+= [dflt_filenamepath_tcpdumpCcompare] 
        GUIwin_arguments+= ['debug? [Y/N]'] 
        GUIwin_arguments+= [dflt_debugFlag] 
        GUIwin_arguments+= ['clean memory when possible? [Y/N]'] 
        GUIwin_arguments+= [dflt_cleanMemFlag] 
        GUIwin_arguments+= ['verbose? [Y/N]'] 
        GUIwin_arguments+= [dflt_verboseFlag] 
        #
        GUIwin_arguments=tuple(GUIwin_arguments)
        dataFromUser= APy3_GENfuns.my_GUIwin_text(GUIwin_arguments)
        iparam=0
        filenamepath_h5=dataFromUser[iparam]; iparam+=1
        showThisImg=int(dataFromUser[iparam]); iparam+=1
        filenamepath_tcpdumpCcompare=dataFromUser[iparam]; iparam+=1
        debugFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        cleanMemFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        verboseFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        #
        if verboseFlag: 
            APy3_GENfuns.printcol('usable variables for self are: {0}'.format(self.__dict__.keys()),'purple')
            APy3_GENfuns.printcol('will load h5 file: {0}'.format(filenamepath_h5),'purple')
            APy3_GENfuns.printcol('will work on image: {0}'.format(showThisImg),'purple')
            APy3_GENfuns.printcol('will load tcpdump comparison file: {0}'.format(filenamepath_tcpdumpCcompare),'purple')
        #
        # load h5 file
        if verboseFlag: APy3_GENfuns.printcol("loading files",'blue')
        path1_2read='/data/';  path2_2read='/reset/'
        if (os.path.isfile(filenamepath_h5)==False): APy3_GENfuns.printcol('unable to find {0}'.format(filenamepath_h5),'red')
        elif verboseFlag&debugFlag: APy3_GENfuns.printcol('will take data from {0}'.format(filenamepath_h5),'blue')
        (dataSmpl_orig,dataRst_orig)= APy3_GENfuns.read_2xh5(filenamepath_h5, path1_2read, path2_2read)
        (auxNImg,auxNRow,auxNCol)= dataSmpl_orig.shape
        if verboseFlag&debugFlag: APy3_GENfuns.printcol('{0} Img-equivalent data found in the file'.format(auxNImg),'blue')
        #
        # show data as it comes out of the DAQ
        if debugFlag:
            ErrAbove= 66000
            label_title= "data (as it comes out of the DAQ), Img "+str(showThisImg)
            if verboseFlag: APy3_GENfuns.printcol('will plot data from Img {0}'.format(showThisImg),'blue')
            fig1= APy3_P2Mfuns.percDebug_plot_2x2D(dataSmpl_orig[showThisImg,:,:],dataRst_orig[showThisImg,:,:], label_title,ErrAbove)
            APy3_GENfuns.printcol(label_title,'green')
        #input('Press enter to continue')
        #
        #%% byte swap in hex (byte0,byte1) => (byte1,byte0)
        if verboseFlag: APy3_GENfuns.printcol("byte-swapping data",'blue')
        dataSmpl_ByteSwap= APy3_GENfuns.convert_hex_byteSwap_Ar(dataSmpl_orig)
        dataRst_ByteSwap= APy3_GENfuns.convert_hex_byteSwap_Ar(dataRst_orig)
        if debugFlag:
            ErrAbove= 33000
            label_title= "data (Byte-swapped), Img "+str(showThisImg)
            fig2= APy3_P2Mfuns.percDebug_plot_2x2D(dataSmpl_ByteSwap[showThisImg,:,:],dataRst_ByteSwap[showThisImg,:,:], label_title,ErrAbove)
            APy3_GENfuns.printcol(label_title,'green')
        #input('Press enter to continue')
        #
        # example of a rowgroup
        if debugFlag:
            ErrBelow=-1
            label_title= "single RowGroup (Byte-swapped), Img "+str(showThisImg)
            fig3= APy3_GENfuns.plot_2D_stretched(dataSmpl_ByteSwap[showThisImg,0:7,:], "cols","rows",label_title, True, ErrBelow)
            APy3_GENfuns.printcol(label_title,'green')
        #input('Press enter to continue')
        #
        #%% comparison to tcpdump data
        if debugFlag:
            label_title= "comparison to expected data"
            auxStart=525; aux_Row=5
            dataRead= dataSmpl_ByteSwap[showThisImg,aux_Row,auxStart:(auxStart+100)]
            #
            tcpdump_fileOffset=24
            tcpdump_packheader_sizeByte= 112
            tcpdump_packData_sizeByte= 4928
            if verboseFlag&debugFlag: APy3_GENfuns.printcol("tcpdump comparison data from "+filenamepath_tcpdumpCcompare ,'blue')
            if (os.path.isfile(filenamepath_tcpdumpCcompare)==False): APy3_GENfuns.printcol('unable to find {0}'.format(filenamepath_tcpdumpCcompare),'red')
            compare_tcpdumpData_int= APy3_GENfuns.read_bin_uint8(filenamepath_tcpdumpCcompare)
            compare_tcpdumpData_int=compare_tcpdumpData_int[tcpdump_fileOffset:]
            auxStart= tcpdump_packheader_sizeByte+tcpdump_packData_sizeByte+tcpdump_packheader_sizeByte
            auxEnd= auxStart+tcpdump_packData_sizeByte
            compare_tcpdump3rdpack= compare_tcpdumpData_int[auxStart:auxEnd]
            compare_tcpdump3rdpack_uint16= APy3_GENfuns.convert_2xuint8_2_int(compare_tcpdump3rdpack[0::2],compare_tcpdump3rdpack[1::2]).astype('uint16') # 2xuint8 => uint16
            expectData=compare_tcpdump3rdpack_uint16[1581:1681]
            fig4= APy3_GENfuns.plot_1D_2scales(numpy.arange(auxStart,auxStart+100), dataRead, expectData, "data position", "read data (Byte-swapped)", "expected data (Byte-shifted)", label_title)
            APy3_GENfuns.printcol(label_title,'green')
        #
        # solving the additional scrambling introduced by Odin-DAQ
        def convert_OdinDAQ_2_Mezzanine(shotIn):
            (auxNImg,auxNRow,auxNCol)= shotIn.shape
            aux_reord= shotIn.reshape((auxNImg,NGrp,NADC,auxNCol)) #
            aux_reord= aux_reord.reshape((auxNImg,NGrp,NADC,2,auxNCol//2)) #
            aux_reord=numpy.transpose(aux_reord,(0,1,3,2,4)) #auxNImg,NGrp, 2left/right,NADC,auxNCol//2
            aux_reord= aux_reord.reshape((auxNImg,NGrp,2,NADC*auxNCol//2)) #auxNImg,NGrp,2left/right,NADC*auxNCol//2
            aux_reord= aux_reord.reshape((auxNImg,NGrp,2,2,NADC*auxNCol//4)) #auxNImg,NGrp,2left/right,2up/down,NADC*auxNCol//4
            aux_reordered= numpy.ones((auxNImg,NGrp,4,NADC*auxNCol//4)).astype('uint16')*ERRDLSraw
            aux_reordered[:,:,0,:]= aux_reord[:,:,0,0,:]
            aux_reordered[:,:,1,:]= aux_reord[:,:,1,0,:]
            aux_reordered[:,:,2,:]= aux_reord[:,:,0,1,:]
            aux_reordered[:,:,3,:]= aux_reord[:,:,1,1,:]
            aux_reordered= aux_reordered.reshape((auxNImg,NGrp,NADC*auxNCol))
            aux_reordered= aux_reordered.reshape((auxNImg,NGrp,NADC,auxNCol))
            aux_reordered= aux_reordered.reshape((auxNImg,NGrp*NADC,auxNCol))
            return aux_reordered
        #
        if verboseFlag: APy3_GENfuns.printcol("solving the additional scrambling introduced by Odin-DAQ",'blue')
        dataSmpl_asMezz= convert_OdinDAQ_2_Mezzanine(dataSmpl_ByteSwap)
        dataRst_asMezz= convert_OdinDAQ_2_Mezzanine(dataRst_ByteSwap)
        if debugFlag:
            label_title= "revert to Mezzanine-order (Sample, single RowGroup)"
            fig5= APy3_GENfuns.plot_2D_stretched(dataSmpl_asMezz[showThisImg,0:7,:], "cols","rows",label_title, True, ErrBelow)
            label_title= "revert to Mezzanine-order (Reset, single RowGroup)"
            fig6= APy3_GENfuns.plot_2D_stretched(dataRst_asMezz[showThisImg,0:7,:], "cols","rows",label_title, True, ErrBelow)
        #
        # now descramble it as if it was coming form the mezzanine ....
        #
        NSmplRst= APy3_P2Mfuns.NSmplRst
        NRow= APy3_P2Mfuns.NRow
        #NCol= APy3_P2Mfuns.NCol
        NADC= APy3_P2Mfuns.NADC
        NGrp= APy3_P2Mfuns.NGrp
        NPad= APy3_P2Mfuns.NPad # 45
        NDataPads= APy3_P2Mfuns.NPad-1 #44
        #NRowInBlock= APy3_P2Mfuns.NRowInBlock #7
        NColInBlock= APy3_P2Mfuns.NColInBlock #32
        RefColInInputData_Flag=False
        # 
        # prepare
        dataSmpl_2_srcmbl= dataSmpl_asMezz
        dataRst_2_srcmbl= dataRst_asMezz
        (auxNImg,auxNRow,auxNCol)= dataSmpl_2_srcmbl.shape
        if verboseFlag: APy3_GENfuns.printcol(str(auxNImg)+" Img found on H5 file",'green')
        #
        ########################### data from the 2 files to be interleaved here
        data_2_srcmbl_norefCol= numpy.ones((auxNImg,NSmplRst,auxNRow,auxNCol)).astype('uint16')* ((2**16)-1)
        data_2_srcmbl_norefCol[:,iSmpl,:,:]= dataSmpl_2_srcmbl
        data_2_srcmbl_norefCol[:,iRst,:,:]= dataRst_2_srcmbl
        data_2_srcmbl_norefCol=data_2_srcmbl_norefCol.reshape((auxNImg,NSmplRst,NGrp,NADC,auxNCol))
        #APy3_GENfuns.plot_2D_stretched(data_2_srcmbl_norefCol[showThisImg,iSmpl,0,:,:], "cols","rows","xxx", True, ErrBelow)
        #
        ########################### ref cols to be dealt with here here
        #
        # track missing packets: False== RowGrp OK; True== packet(s) missing makes rowgroup moot (1111 1111 1111 1111 instead of 0xxx xxxx xxxx xxxx) 
        MissingRowGrpTracker= numpy.ones((auxNImg,NSmplRst,NGrp)).astype(bool) 
        MissingRowGrpTracker= data_2_srcmbl_norefCol[:,:,:,0,0]==ERRDLSraw         
        #
        # descramble proper
        if verboseFlag: APy3_GENfuns.printcol("descrambling",'blue')
        multiImg_aggr_withRef= numpy.zeros((auxNImg,NSmplRst,NGrp,NPad,NADC*NColInBlock,3)).astype('uint8')
        for iImg in range(auxNImg):
            if verboseFlag: APy3_GENfuns.dot()
            auxil_thisImg= data_2_srcmbl_norefCol[iImg,:,:,:,:].reshape((NSmplRst,NGrp,NADC*auxNCol)) #(NSmplRst,NRowGrpInShot,NADC*auxNCol)
            auxil_thisImg= auxil_thisImg.reshape((NSmplRst,NGrp,NADC*auxNCol//(NDataPads*2),NDataPads,2)) #32bit=2"pix" from 1st pad, 2"pix" from 2nd pad, ...
            auxil_thisImg= numpy.transpose(auxil_thisImg, (0,1,3,2,4)) # NSmplRst,NGrp,NDataPads,NADC*auxNCol//(NDataPads*2),2"pix")
            auxil_thisImg= auxil_thisImg.reshape((NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads)) 
            #if iImg==showThisImg: APy3_GENfuns.plot_2D_stretched(auxil_thisImg[iSmpl,0,:,:], "pads","rows","xxx", True, ErrBelow)
            #
            #%% bit, remove head 0, concatenate and reorder
            auxil_thisImg_16bitted= APy3_GENfuns.convert_uint_2_bits_Ar(auxil_thisImg,16)[:,:,:,:,::-1].astype('uint8') #NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads,15bits
            auxil_thisImg_bitted= auxil_thisImg_16bitted[:,:,:,:,1:] #NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads,15bits
            #if iImg==showThisImg: print(str(auxil_thisImg_bitted[0,0,0,0,:]))
            auxil_thisImg_bitted= auxil_thisImg_bitted.reshape((NSmplRst,NGrp,NDataPads,NADC*auxNCol*15//NDataPads))
            auxil_thisImg_bitted= auxil_thisImg_bitted.reshape((NSmplRst,NGrp,NDataPads,15,NADC*NColInBlock)) 
            #
            #%% BBT: 0=>1, 1=>0
            auxil_thisImg_bitted= numpy.transpose(auxil_thisImg_bitted,(0,1,2,4,3)) # (NSmplRst,NGrp,NDataPads,NPixsInRowBlk,15)    
            auxil_thisImg_bitted= APy3_GENfuns.convert_britishBits_Ar(auxil_thisImg_bitted) # 0=>1, 1=>0
            #    
            auxil_thisImg_aggr= numpy.zeros((NSmplRst,NGrp,NDataPads,NADC*NColInBlock,3)).astype('uint8') 
            #
            #%% binary aggregate Gn bit(0,1) 
            aux_bits2descr=2; aux_frombit=0; aux_tobit_puls1=1+1
            power2Matrix=(2**numpy.arange(aux_bits2descr) )[::-1].astype(int) 
            aux_powerMatr= power2Matrix* numpy.ones((NSmplRst,NGrp,NDataPads,NADC*NColInBlock, len(power2Matrix)) ).astype(int) ; 
            totalVector_xDAr= numpy.sum(auxil_thisImg_bitted[:,:,:, :, aux_frombit:aux_tobit_puls1]*aux_powerMatr, axis=4); 
            auxil_thisImg_aggr[:,:,:,:,iGn]=totalVector_xDAr.astype('uint8')
            #
            #%% binary aggregate Crs bit(10,11,12,13,14) 
            aux_bits2descr=5; aux_frombit=10; aux_tobit_puls1=14+1
            power2Matrix=(2**numpy.arange(aux_bits2descr) )[::-1].astype(int) 
            aux_powerMatr= power2Matrix* numpy.ones((NSmplRst,NGrp,NDataPads,NADC*NColInBlock, len(power2Matrix)) ).astype(int) ; 
            totalVector_xDAr= numpy.sum(auxil_thisImg_bitted[:,:,:, :, aux_frombit:aux_tobit_puls1]*aux_powerMatr, axis=4); 
            auxil_thisImg_aggr[:,:,:,:,iCrs]=totalVector_xDAr  
            #
            #%% binary aggregate Fn bit(2,3,4,5,6,7,8,9) 
            aux_bits2descr=8; aux_frombit=2; aux_tobit_puls1=9+1
            power2Matrix=(2**numpy.arange(aux_bits2descr) )[::-1].astype(int) 
            aux_powerMatr= power2Matrix* numpy.ones((NSmplRst,NGrp,NDataPads,NADC*NColInBlock, len(power2Matrix)) ).astype(int) ; 
            totalVector_xDAr= numpy.sum(auxil_thisImg_bitted[:,:,:, :, aux_frombit:aux_tobit_puls1]*aux_powerMatr, axis=4); 
            auxil_thisImg_aggr[:,:,:,:,iFn]=totalVector_xDAr
            #
            if cleanMemFlag: del auxil_thisImg_bitted; del power2Matrix; del aux_powerMatr; del totalVector_xDAr
            #
            #%% including reference column
            auxil_thisImg_aggr_withRef= numpy.ones((NSmplRst,NGrp,NPad,NADC*NColInBlock,3)).astype('uint8')*((2**8)-1)
            auxil_thisImg_aggr_withRef[:,:,1:,:,:]=auxil_thisImg_aggr[:,:,:,:,:]
            if cleanMemFlag: del auxil_thisImg_aggr
            #
            multiImg_aggr_withRef[iImg,:,:,:,:,:]= auxil_thisImg_aggr_withRef[:,:,:,:,:]
        if cleanMemFlag: del auxil_thisImg_aggr_withRef    
        #
        # reorder pixels and pads 
        multiImg_GrpDscrmbld= numpy.zeros((auxNImg,NSmplRst,NGrp,NPad,NADC,NColInBlock,3)).astype('uint8')
        for iImg in range(auxNImg):
            for iSmplRst in range(NSmplRst):    
                multiImg_GrpDscrmbld[iImg,iSmplRst,:,:,:,:,:]= APy3_P2Mfuns.reorder_pixels_GnCrsFn(multiImg_aggr_withRef[iImg,iSmplRst,:,:,:,:],NADC,NColInBlock)
        #
        # add error tracking
        if verboseFlag: APy3_GENfuns.printcol("\n"+"lost packet tracking",'blue')
        multiImg_GrpDscrmbld= multiImg_GrpDscrmbld.astype('int16') # -256 upto 255
        for iImg in range(auxNImg):
            for iGrp in range(NGrp):
                for iSmplRst in range(NSmplRst):
                    if (MissingRowGrpTracker[iImg,iSmplRst,iGrp]): multiImg_GrpDscrmbld[iImg,iSmplRst,iGrp,:,:,:,:]=ERRint16
        multiImg_GrpDscrmbld[:,:,:,0,:,:,:]=ERRint16 # also err tracking for ref col
        #
        # reorder as an img array
        dscrmbld_GnCrsFn= numpy.zeros((auxNImg,NSmplRst,NGrp,NPad,NADC,NColInBlock,3)).astype('int16')
        dscrmbld_GnCrsFn[:,:,:,:,:,:,:]= multiImg_GrpDscrmbld[:,:,:,:,:,:,:]
        dscrmbld_GnCrsFn= numpy.transpose(dscrmbld_GnCrsFn,(0,1,2,4,3,5,6)).astype('int16') #(NImg,Smpl/Rst,NGrp,NADC,NPad,NColInBlk,Gn/Crs/Fn)
        dscrmbld_GnCrsFn=dscrmbld_GnCrsFn.reshape((auxNImg,NSmplRst,NGrp*NADC,NPad*NColInBlock,3))
        #
        # show
        aux_ERRBlw=-0.1
        #aux_thisimg=showThisImg
        for aux_thisimg in range(auxNImg):
            aux_title= "Img "+str(aux_thisimg)+" descrambled"
            APy3_P2Mfuns.percDebug_plot_6x2D(dscrmbld_GnCrsFn[aux_thisimg,iSmpl,:,:,iGn],dscrmbld_GnCrsFn[aux_thisimg,iSmpl,:,:,iCrs],dscrmbld_GnCrsFn[aux_thisimg,iSmpl,:,:,iFn],\
                                        dscrmbld_GnCrsFn[aux_thisimg,iRst,:,:,iGn],dscrmbld_GnCrsFn[aux_thisimg,iRst,:,:,iCrs],dscrmbld_GnCrsFn[aux_thisimg,iRst,:,:,iFn],\
                                        aux_title,aux_ERRBlw)
        #
        # GnCrsFn => DLSraw
        # save as DLSraw
        # GnCrsFn <= DLSraw
        # show again
        #
        #
        #
        #
        #%% that's all folks
        print("------------------------") 
        print("done")
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script ended at {0}".format(aux_timeId) ,'blue')
        input('Press enter to end')
        for iaux in range(3): print("------------------------")        

