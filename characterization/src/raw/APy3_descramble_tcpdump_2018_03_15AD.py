import copy
import matplotlib
# Generate 2D images having a window appear
# matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
from plot_base import PlotBase  # noqa E402
import webbrowser # to show images
#
#
#
#%% useful imports & flags
from APy3_auxINIT import *
#
ERRint16=-256
ERRBlw= -0.1
ERRDLSraw= 65535
iGn=0; iCrs=1; iFn=2 
iSmpl=0; iRst=1 
#
#
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
        ''' 1/2/3x tcpdump files using 2018.03.15_AD Firmware (2links,2nodes) no switch => descramble => save as an h5 file in agreed format'''
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script beginning at {0}".format(aux_timeId) ,'blue')
        #
        # general constants
        NADC=APy3_P2Mfuns.NADC #7
        NGrp=APy3_P2Mfuns.NGrp #212
        NSmplRst= APy3_P2Mfuns.NSmplRst #2 
        NRow= APy3_P2Mfuns.NRow # 212
        #NCol= APy3_P2Mfuns.NCol
        NPad= APy3_P2Mfuns.NPad # 45
        NDataPads= APy3_P2Mfuns.NPad-1 #44
        NColInBlock= APy3_P2Mfuns.NColInBlock #32
        NRowInBlock= NADC # 7
        NPixsInBlock= NColInBlock*NRowInBlock #224
        NbitsInPix=15
        NGnCrsFn=3
        #
        # tcpdump-related constants
        excessBytesinfront=24 # excess Bytes added at the beginning of tcpdump file
        goodData_Size=4928
        fullpack_Size=5040
        headerSize=fullpack_Size-goodData_Size # 112
        imgCounterByte0=88-excessBytesinfront # also+1
        packCounterByte0=90-excessBytesinfront # also+1
        portByte0=53
        #
        NpacksInRowgrp=4
        NpacksInImg= NpacksInRowgrp*NGrp*NSmplRst #1696
        aux_maxPackN= 1695
        # - - -
        #
        # default values
        dflt_mainFolder= "/home/prcvlusr/PercAuxiliaryTools/PercPython/data/test4G/2018.05.11/"
        dflt_fileName_prefix= "2018.05.11_025serie_4G_VRST2.7V_VrefDB2.5V_OD1.5_200ms"
        dflt_fileName_suffix0= "_lnk0.dmp"
        dflt_fileName_suffix1= "_lnk1.dmp"
        dflt_fileName_suffix2= "_lnk2.dmp"
        dflt_filenamepath_in0= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffix0
        dflt_filenamepath_in1= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffix1
        #dflt_filenamepath_in2= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffix2
        dflt_filenamepath_in2= "not_a_real_file"
        #
        dflt_saveFileFlag='Y'
        dflt_fileName_suffixout= "_dscrmbld_DLSraw.h5"
        dflt_filenamepath_out= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffixout
        #
        dflt_debugFlag='N';
        dflt_debugImg2show_mtlb='0:4'
        #
        dflt_cleanMemFlag='Y'
        dflt_verboseFlag='Y' 
        # - - -  
        #
        # GUI window
        GUIwin_arguments= []
        GUIwin_arguments+= ['path & name of lnk0-tcpdump-file to descramble'] 
        GUIwin_arguments+= [dflt_filenamepath_in0] 
        GUIwin_arguments+= ['path & name of lnk1-tcpdump-file to descramble (if any)'] 
        GUIwin_arguments+= [dflt_filenamepath_in1] 
        GUIwin_arguments+= ['path & name of lnk2-tcpdump-file to descramble (if any)'] 
        GUIwin_arguments+= [dflt_filenamepath_in2] 
        #
        GUIwin_arguments+= ['save descrambled file? [Y/N]'] 
        GUIwin_arguments+= [dflt_saveFileFlag] 
        GUIwin_arguments+= ['if save descrambled: where? [file path & name]'] 
        GUIwin_arguments+= [dflt_filenamepath_out] 
        #
        GUIwin_arguments+= ['debug? [Y/N]'] 
        GUIwin_arguments+= [dflt_debugFlag] 
        GUIwin_arguments+= ['if debug: show which images? [from:to]'] 
        GUIwin_arguments+= [dflt_debugImg2show_mtlb] 
        #
        GUIwin_arguments+= ['clean memory when possible? [Y/N]'] 
        GUIwin_arguments+= [dflt_cleanMemFlag] 
        GUIwin_arguments+= ['verbose? [Y/N]'] 
        GUIwin_arguments+= [dflt_verboseFlag] 
        #
        GUIwin_arguments=tuple(GUIwin_arguments)
        dataFromUser= APy3_GENfuns.my_GUIwin_text(GUIwin_arguments)
        iparam=0
        filenamepath_in0= dataFromUser[iparam]; iparam+=1   
        filenamepath_in1= dataFromUser[iparam]; iparam+=1   
        filenamepath_in2= dataFromUser[iparam]; iparam+=1   
        filesNamePath_T=(filenamepath_in0, filenamepath_in1,filenamepath_in2)
        #    
        saveFileFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        filenamepath_out= dataFromUser[iparam]; iparam+=1  
        #
        debugFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        debugImg2show_mtlb= dataFromUser[iparam]; iparam+=1; 
        debugImg2show=APy3_GENfuns.matlabLike_range(debugImg2show_mtlb)        
        #
        cleanMemFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        verboseFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        #
        if verboseFlag: 
            APy3_GENfuns.printcol('will load tcpdump files:','green')
            for thisFileNamePath in filesNamePath_T: 
                if os.path.isfile(thisFileNamePath): APy3_GENfuns.printcol(thisFileNamePath,'green')
                else: APy3_GENfuns.printcol(thisFileNamePath+' does not exist','purple')            
            #
            if saveFileFlag: APy3_GENfuns.printcol('will save descrambled file: '+filenamepath_out,'green')
            if debugFlag: APy3_GENfuns.printcol('debug: will show images: '+str(debugImg2show),'green')
            #
            if cleanMemFlag: APy3_GENfuns.printcol('will clean memory when possible','green')
            APy3_GENfuns.printcol("verbose",'green')
        # - - -
        #
        # read files
        if verboseFlag: APy3_GENfuns.printcol("reading files",'blue')
        if os.path.isfile(filesNamePath_T[0]): 
            fileContent0_uint8= APy3_GENfuns.read_bin_uint8(filesNamePath_T[0])
            fileContent0_uint8= fileContent0_uint8[excessBytesinfront:]
        else: fileContent0_uint8=numpy.array([]).astype('uint8')
        if os.path.isfile(filesNamePath_T[1]): 
            fileContent1_uint8= APy3_GENfuns.read_bin_uint8(filesNamePath_T[1])
            fileContent1_uint8= fileContent1_uint8[excessBytesinfront:]
        else: fileContent1_uint8=numpy.array([]).astype('uint8')
        if os.path.isfile(filesNamePath_T[2]): 
            fileContent2_uint8= APy3_GENfuns.read_bin_uint8(filesNamePath_T[2])
            fileContent2_uint8= fileContent2_uint8[excessBytesinfront:]
        else: fileContent2_uint8=numpy.array([]).astype('uint8')
        if ((os.path.isfile(filesNamePath_T[0])==False)):
            APy3_GENfuns.printcol('main (lnk0) file does not exist','red')
            return()
        #
        Npackets_file= numpy.zeros((3)).astype(int)
        fileSize= len(fileContent0_uint8); Npackets_file[0]= fileSize//fullpack_Size
        fileSize= len(fileContent1_uint8); Npackets_file[1]= fileSize//fullpack_Size
        fileSize= len(fileContent2_uint8); Npackets_file[2]= fileSize//fullpack_Size
        fileContentAll_int=[fileContent0_uint8,fileContent1_uint8,fileContent2_uint8]
        if cleanMemFlag: del fileContent0_uint8; del fileContent1_uint8; del fileContent2_uint8; 
        #
        if verboseFlag: APy3_GENfuns.printcol("data read from files ("+str(Npackets_file[0])+"+"+str(Npackets_file[1])+"+"+str(Npackets_file[2])+" packets)", 'green')
        # - - -
        # 
        # look for 1st/last image, scan for obvious packet error
        if verboseFlag: APy3_GENfuns.printcol("scanning files for obvious packet errors",'blue')
        aux1stImg= (2**32)-1
        auxlastImg= 0
        for iFile,thisFile in enumerate(filesNamePath_T):
            if os.path.isfile(thisFile):
                for ipack in range(Npackets_file[iFile]):
                    aux_start= ipack*fullpack_Size; aux_endp1= ( (ipack+1)*fullpack_Size )
                    data_thisPack= fileContentAll_int[iFile][aux_start:aux_endp1]
                    thisImg=APy3_GENfuns.convert_4xuint8_2_int(data_thisPack[imgCounterByte0-2],data_thisPack[imgCounterByte0-1],data_thisPack[imgCounterByte0],data_thisPack[imgCounterByte0+1])
                    if thisImg<=aux1stImg: aux1stImg= thisImg
                    if thisImg>=auxlastImg: auxlastImg= thisImg
                    #
                    thispackN=APy3_GENfuns.convert_2xuint8_2_int(data_thisPack[packCounterByte0],data_thisPack[packCounterByte0+1])
                    if thispackN>aux_maxPackN:
                        APy3_GENfuns.printcol('inconsistent packet in '+filesNamePath_T[iFile],'red')
                        APy3_GENfuns.printcol('(packet '+str(ipack)+'-th in the file is identified as packN='+str(thispackN)+' > '+str(aux_maxPackN)+')','red')
                        return()
        #
        auxImgs_tcpdump= numpy.arange(aux1stImg,auxlastImg+1)
        NImg= len(auxImgs_tcpdump)
        if (len(debugImg2show)> NImg): debugImg2show= numpy.array([0])  # if needed, reduce Img2show to the 1st image 
        debugImg2show_tcpdump= debugImg2show+aux1stImg        # start from 1st image in the file

        #
        APy3_GENfuns.printcol('the lowest-numbered Img of the sequence is: tcpdump-Image '+str(aux1stImg),'green')
        APy3_GENfuns.printcol('the highest-numbered Img of the sequence is: tcpdump-Image '+str(auxlastImg),'green')
        APy3_GENfuns.printcol('the range of Imgs to show are modified as: tcpdump-Image '+str(debugImg2show_tcpdump),'green')
        #
        if cleanMemFlag: del data_thisPack
        # - - -
        # 
        # resort data from images
        if verboseFlag: APy3_GENfuns.printcol("resorting packages",'blue')
        multiImgPackCheck= numpy.zeros((NImg,2*NGrp*NpacksInRowgrp)).astype(bool)
        multiImageStrm_Data_xPack=  numpy.zeros((NImg,2*NGrp*NpacksInRowgrp,goodData_Size)).astype('uint8')
        multiImageStrm_Header_xPack=  numpy.zeros((NImg,2*NGrp*NpacksInRowgrp,headerSize)).astype('uint8')
        #
        for iImg_h5, thisImg_dump in enumerate(auxImgs_tcpdump):
            if verboseFlag: APy3_GENfuns.dot()
            for iFile,thisFile in enumerate(filesNamePath_T):
                for ipack in range(len(fileContentAll_int[iFile])//fullpack_Size):
                    aux_start= ipack*fullpack_Size; aux_endp1= ( (ipack+1)*fullpack_Size )

                    data_thisPack=  fileContentAll_int[iFile][aux_start:aux_endp1]
                    if ( (data_thisPack[imgCounterByte0-2],data_thisPack[imgCounterByte0-1],data_thisPack[imgCounterByte0],data_thisPack[imgCounterByte0+1])==APy3_GENfuns.convert_int_2_4xuint8(thisImg_dump) ):
                        thisPackID= APy3_GENfuns.convert_2xuint8_2_int( data_thisPack[packCounterByte0],data_thisPack[packCounterByte0+1] )
                        multiImageStrm_Data_xPack[iImg_h5,thisPackID,:] = data_thisPack[headerSize:]
                        multiImageStrm_Header_xPack[iImg_h5,thisPackID,:]= data_thisPack[:headerSize]
                        multiImgPackCheck[iImg_h5,thisPackID] =True
        if verboseFlag: APy3_GENfuns.printcol(" ",'blue')
        if cleanMemFlag: del fileContentAll_int
        #
        # missing package detail
        for iImg, thisImg in enumerate(auxImgs_tcpdump):
            if verboseFlag:
                if numpy.sum(numpy.logical_not(multiImgPackCheck[iImg,:]))<1: APy3_GENfuns.printcol("all packets for image "+str(thisImg)+" are there",'green')
                else: APy3_GENfuns.printcol(str( numpy.sum(numpy.logical_not(multiImgPackCheck[iImg,:])))+" packets missing from image "+ str(thisImg),'purple')
                if debugFlag:
                    for ipack in range(NpacksInImg):
                        if ((multiImgPackCheck[iImg,ipack]==False)): APy3_GENfuns.printcol("packet "+str(ipack)+ "-th is missing from image "+str(thisImg),'purple' )

        # when a packet is missing, set to 0 its 4-uple of packets (i.e. the RowGrp), to avoid confusion
        multiImgRowGrpCheck= numpy.logical_and(multiImgPackCheck[:,0::4],multiImgPackCheck[:,1::4])
        multiImgRowGrpCheck= numpy.logical_and(multiImgRowGrpCheck,multiImgPackCheck[:,2::4])
        multiImgRowGrpCheck= numpy.logical_and(multiImgRowGrpCheck,multiImgPackCheck[:,3::4]) #(NImg,NrowGrpInImgStrm)
        # - - -
        # 
        # descrambling proper
        if verboseFlag: APy3_GENfuns.printcol("descrambling images",'blue')
        multiImg_aggr_withRef= numpy.ones((NImg,NSmplRst*NGrp,NPad,NPixsInBlock,NGnCrsFn)).astype('uint8')
        for iImg_h5, thisImg_dump in enumerate(auxImgs_tcpdump):  
            if verboseFlag: APy3_GENfuns.dot()
            # combine values to 16bits,
            auxil_thisImg= multiImageStrm_Data_xPack[iImg_h5,:,:].reshape((NSmplRst*NGrp,NpacksInRowgrp*goodData_Size))
            auxil_thisImg= auxil_thisImg.reshape((NSmplRst*NGrp,NpacksInRowgrp*goodData_Size//(NDataPads*32//8),NDataPads,32//8) )
            auxil_thisImg= numpy.transpose(auxil_thisImg, (0,2,1,3)) # NSmplRst*NGrp,NDataPads,NpacksInRowgrp*goodData_Size/(NDataPads*32/8),32/8)
            auxil_thisImg= auxil_thisImg.reshape((NSmplRst*NGrp,NDataPads,NpacksInRowgrp*goodData_Size//NDataPads))  
            #
            #auxil_thisImg_8bitted= APy3_GENfuns.convert_uint_2_bits_Ar(auxil_thisImg,8).astype('uint8')
            auxil_thisImg_8bitted= APy3_GENfuns.convert_uint_2_bits_Ar(auxil_thisImg,8)[:,:,:,::-1].astype('uint8')


            auxil_thisImg_8bitted= auxil_thisImg_8bitted.reshape((NSmplRst*NGrp,NDataPads,NpacksInRowgrp*goodData_Size//NDataPads,8))
            if cleanMemFlag: del auxil_thisImg
            auxil_thisImg_16bitted= numpy.zeros((NSmplRst*NGrp,NDataPads,NpacksInRowgrp*goodData_Size//(NDataPads*2),16)).astype('uint8')
            auxil_thisImg_16bitted[:,:,:,0:8]= auxil_thisImg_8bitted[:,:,0::2,:]
            auxil_thisImg_16bitted[:,:,:,8:16]= auxil_thisImg_8bitted[:,:,1::2,:]
            if cleanMemFlag: del auxil_thisImg_8bitted
            #  remove head 0, concatenate and reorder
            auxil_thisImg_15bitted= auxil_thisImg_16bitted[:,:,:,1:] # we can remove this because the grps//missing packets are already identified by multiImgRowGrpCheck
            if cleanMemFlag: del auxil_thisImg_16bitted
            #
            auxil_thisImg_asFromChip= auxil_thisImg_15bitted.reshape((NSmplRst*NGrp,NDataPads,NpacksInRowgrp*goodData_Size*15//(NDataPads*2)))
            auxil_thisImg_asFromChip= auxil_thisImg_asFromChip.reshape((NSmplRst*NGrp,NDataPads,NbitsInPix,NPixsInBlock))    
            if cleanMemFlag: del auxil_thisImg_15bitted
            # BBT: 0=>1, 1=>0
            auxil_thisImg_asFromChip= numpy.transpose(auxil_thisImg_asFromChip,(0,1,3,2)) # (NSmplRst*NGrp,NDataPads,NPixsInRowBlk,NbitsInPix)
            auxil_thisImg_asFromChip= APy3_GENfuns.convert_britishBits_Ar(auxil_thisImg_asFromChip) # 0=>1, 1=>0
            #  
            auxil_thisImg_aggr= numpy.zeros((NSmplRst*NGrp,NDataPads,NPixsInBlock,NGnCrsFn)).astype('uint8')  
            # binary aggregate Gn bit(0,1) 
            aux_bits2descr=2; aux_frombit=0; aux_tobit_puls1=1+1
            power2Matrix=(2**numpy.arange(aux_bits2descr) )[::-1].astype(int) 
            aux_powerMatr= power2Matrix* numpy.ones((NSmplRst*NGrp,NDataPads,NPixsInBlock, len(power2Matrix)) ).astype(int) ; #print aux_powerMatr.shape, aux_powerMatr[0,:]
            totalVector_xDAr= numpy.sum(auxil_thisImg_asFromChip[:,:, :, aux_frombit:aux_tobit_puls1]*aux_powerMatr, axis=3); #print totalVector_xDAr, #print totalVector_xDAr.shape ;# (NImg,NPad,40)
            auxil_thisImg_aggr[:,:,:,iGn]=totalVector_xDAr.astype('uint8')
            #
            # binary aggregate Crs bit(10,11,12,13,14) 
            aux_bits2descr=5; aux_frombit=10; aux_tobit_puls1=14+1
            power2Matrix=(2**numpy.arange(aux_bits2descr) )[::-1].astype(int) 
            aux_powerMatr= power2Matrix* numpy.ones((NSmplRst*NGrp,NDataPads,NPixsInBlock, len(power2Matrix)) ).astype(int) ; #print aux_powerMatr.shape, aux_powerMatr[0,:]
            totalVector_xDAr= numpy.sum(auxil_thisImg_asFromChip[:,:, :, aux_frombit:aux_tobit_puls1]*aux_powerMatr, axis=3); #print totalVector_xDAr, #print totalVector_xDAr.shape ;# (NImg,NPad,40)
            auxil_thisImg_aggr[:,:,:,iCrs]=totalVector_xDAr  
            #
            # binary aggregate Fn bit(2,3,4,5,6,7,8,9) 
            aux_bits2descr=8; aux_frombit=2; aux_tobit_puls1=9+1
            power2Matrix=(2**numpy.arange(aux_bits2descr) )[::-1].astype(int) 
            aux_powerMatr= power2Matrix* numpy.ones((NSmplRst*NGrp,NDataPads,NPixsInBlock, len(power2Matrix)) ).astype(int) ; #print aux_powerMatr.shape, aux_powerMatr[0,:]
            totalVector_xDAr= numpy.sum(auxil_thisImg_asFromChip[:,:, :, aux_frombit:aux_tobit_puls1]*aux_powerMatr, axis=3); #print totalVector_xDAr, #print totalVector_xDAr.shape ;# (NImg,NPad,40)
            auxil_thisImg_aggr[:,:,:,iFn]=totalVector_xDAr
            #
            if cleanMemFlag: del auxil_thisImg_asFromChip; del power2Matrix; del aux_powerMatr; del totalVector_xDAr

            #
            # add RefCols
            auxil_thisImg_aggr_withRef= numpy.zeros((NSmplRst*NGrp,NPad,NPixsInBlock,NGnCrsFn)).astype('uint8')
            auxil_thisImg_aggr_withRef[:,1:,:,:]=auxil_thisImg_aggr[:,:,:,:]
            if cleanMemFlag: del auxil_thisImg_aggr
            multiImg_aggr_withRef[iImg_h5,:,:,:,:]= auxil_thisImg_aggr_withRef[:,:,:,:]
        if cleanMemFlag: del auxil_thisImg_aggr_withRef
        if verboseFlag: APy3_GENfuns.printcol(" ",'blue')
        # - - -
        # 
        #
        #reorder pixels and pads 
        if verboseFlag: APy3_GENfuns.printcol("reordering pixels",'blue')
        multiImg_GrpDscrmbld= numpy.zeros((NImg,NSmplRst*NGrp,NPad,NRowInBlock,NColInBlock,NGnCrsFn)).astype('uint8')
        for iImg_h5, thisImg_dump in enumerate(auxImgs_tcpdump):    
            multiImg_GrpDscrmbld[iImg_h5,:,:,:,:,:]= APy3_P2Mfuns.reorder_pixels_GnCrsFn(multiImg_aggr_withRef[iImg_h5,:,:,:,:],NADC,NColInBlock)
        #
        # add error tracking
        multiImg_GrpDscrmbld= multiImg_GrpDscrmbld.astype('int16') # -256 => 255
        for iImg_h5, thisImg_dump in enumerate(auxImgs_tcpdump):  
            for iGrp in range(NSmplRst*NGrp):
                if (multiImgRowGrpCheck[iImg_h5,iGrp]==False): multiImg_GrpDscrmbld[iImg_h5,iGrp,:,:,:,:]=ERRint16
        #%% error tracking for refCol
        multiImg_GrpDscrmbld[:,:,0,:,:,:]=ERRint16   
        #
        # reorder by Smpl,Rst
        multiImg_SmplRst= numpy.zeros((NImg,NSmplRst,NGrp,NPad,NRowInBlock,NColInBlock,NGnCrsFn)).astype('int16')
        multiImg_SmplRst[:,iSmpl,1:,:,:,:,:]= multiImg_GrpDscrmbld[:,1:(212*2)-1:2,:,:,:,:]
        multiImg_SmplRst[:,iRst,:(-1),:,:,:,:]= multiImg_GrpDscrmbld[:,2:212*2:2,:,:,:,:]
        multiImg_SmplRst[:,iSmpl,0,:,:,:,:]=  multiImg_GrpDscrmbld[:,0,:,:,:,:]
        multiImg_SmplRst[:,iRst,-1,:,:,:,:]=  multiImg_GrpDscrmbld[:,-1,:,:,:,:]
        #
        multiImg_SmplRst= numpy.transpose(multiImg_SmplRst,(0,1,2,4,3,5,6)).astype('int16') #(NImg,Smpl/Rst,NGrp,NRowInBlock,NPad,NColInBlock,Gn/Crs/Fn)
        multiImg_SmplRstGnCrsFn=multiImg_SmplRst.reshape((NImg,NSmplRst,NGrp*NADC,NPad*NColInBlock,NGnCrsFn))
        if cleanMemFlag: del multiImg_SmplRst
        # - - -
        # show descrambled data
        if debugFlag: 
            aux_ERRBlw=-0.1
            for iImg_h5, thisImg_dump in enumerate(debugImg2show_tcpdump):
                aux_title= "tcpdump Img "+str(thisImg_dump)+" descrambled as h5 Img "+str(iImg_h5)
                APy3_P2Mfuns.percDebug_plot_6x2D(multiImg_SmplRstGnCrsFn[iImg_h5,iSmpl,:,:,iGn],multiImg_SmplRstGnCrsFn[iImg_h5,iSmpl,:,:,iCrs],multiImg_SmplRstGnCrsFn[iImg_h5,iSmpl,:,:,iFn],\
                                        multiImg_SmplRstGnCrsFn[iImg_h5,iRst,:,:,iGn],multiImg_SmplRstGnCrsFn[iImg_h5,iRst,:,:,iCrs],multiImg_SmplRstGnCrsFn[iImg_h5,iRst,:,:,iFn],\
                                        aux_title,aux_ERRBlw)
            #
            #auxThisImg=4
            #auxThisRow=612 #584 #882 #494
            #auxThisCol=730 # 1003 #862 #1086
            #print("{0},{1},{2}={3},{4}".format(auxThisImg,auxThisRow,auxThisCol,\
            #                        multiImg_SmplRstGnCrsFn[auxThisImg,iSmpl,auxThisRow,auxThisCol,iGn],\
            #                        multiImg_SmplRstGnCrsFn[auxThisImg,iSmpl,auxThisRow,auxThisCol,iCrs]) )
            #
        # - - -
        #
        # convert Gn/Crs/Fn => DLSraw: 16bit (errorbit+15bits)
        if verboseFlag: APy3_GENfuns.printcol('converting to DLSraw format ( uint16: [X, Gn,Gn, Fn,Fn,Fn,Fn,Fn,Fn,Fn,Fn, Crs,Crs,Crs,Crs,Crs] )','green')
        (dscrmbld_Smpl_DLSraw,dscrmbld_Rst_DLSraw)=APy3_P2Mfuns.convert_GnCrsFn_2_DLSraw(multiImg_SmplRstGnCrsFn, ERRint16, ERRDLSraw)
        if cleanMemFlag: del multiImg_SmplRstGnCrsFn
        # - - -
        #
        # save descrambled data
        if saveFileFlag: 
            APy3_GENfuns.write_2xh5(filenamepath_out, dscrmbld_Smpl_DLSraw,'/data/', dscrmbld_Rst_DLSraw,'/reset/')
            APy3_GENfuns.printcol('data saved to: '+filenamepath_out,'green')
            if cleanMemFlag: del dscrmbld_Smpl_DLSraw; del dscrmbld_Rst_DLSraw
        # - - -
        #
        # show saved data
        if debugFlag & saveFileFlag:
            (reread_Smpl,reread_Rst)= APy3_GENfuns.read_2xh5(filenamepath_out, '/data/', '/reset/')
            reread_GnCrsFn= APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(reread_Smpl,reread_Rst, ERRDLSraw, ERRint16)
            if cleanMemFlag: del reread_Smpl; del reread_Rst
            for iImg_h5, thisImg_dump in enumerate(debugImg2show_tcpdump):
                aux_title= "Img "+str(iImg_h5)+" from file"
                aux_ERRBlw=-0.1
                APy3_P2Mfuns.percDebug_plot_6x2D(reread_GnCrsFn[iImg_h5,iSmpl,:,:,iGn],reread_GnCrsFn[iImg_h5,iSmpl,:,:,iCrs],reread_GnCrsFn[iImg_h5,iSmpl,:,:,iFn],\
                                        reread_GnCrsFn[iImg_h5,iRst,:,:,iGn],reread_GnCrsFn[iImg_h5,iRst,:,:,iCrs],reread_GnCrsFn[iImg_h5,iRst,:,:,iFn],\
                                        aux_title,aux_ERRBlw)


        '''# show freshly descrambled images
        if debugFlag:
            ERRBlw=-0.1 
            for iImg_h5, thisImg_dump in enumerate(debugImg2show_tcpdump):  
                APy3_P2Mfuns.percDebug_plot_6x2D(multiImg_SmplRstGnCrsFn[iImg_h5,iSmpl,:,:,iGn],\
                                            multiImg_SmplRstGnCrsFn[iImg_h5,iSmpl,:,:,iCrs],\
                                            multiImg_SmplRstGnCrsFn[iImg_h5,iSmpl,:,:,iFn], \
                                            multiImg_SmplRstGnCrsFn[iImg_h5,iRst,:,:,iGn],\
                                            multiImg_SmplRstGnCrsFn[iImg_h5,iRst,:,:,iCrs],\
                                            multiImg_SmplRstGnCrsFn[iImg_h5,iRst,:,:,iFn], \
                                            'tcpdump Img '+str(thisImg_dump)+', saved as Img '+str(iImg_h5),
                                            ERRBlw)


        '''#
        '''


        '''


        #
        # Smpl/Rst
        # reorder
        # GnCrsFn => DLSraw
        # save file
        # open file, DLSraw => GnCrsFn, show
        #
        '''
        #
        # load h5 files
        if verboseFlag: APy3_GENfuns.printcol('reading files','blue')
        aux_path1_2read='/data/';  aux_path2_2read='/reset/'
        if (os.path.isfile(filenamepath_in0)==False): APy3_GENfuns.printcol('unable to find node-0 file: '+filenamepath_in0,'red'); return()
        (data_fl0_Smpl,data_fl0_Rst)= APy3_GENfuns.read_2xh5(filenamepath_in0, aux_path1_2read, aux_path2_2read)
        if (os.path.isfile(filenamepath_in1)==False): APy3_GENfuns.printcol('unable to find node-1 file: '+filenamepath_in1,'red'); return()
        (data_fl1_Smpl,data_fl1_Rst)= APy3_GENfuns.read_2xh5(filenamepath_in1, aux_path1_2read, aux_path2_2read)
        #
        (NImg_fl0,auxNRow,auxNCol)= data_fl0_Smpl.shape
        (NImg_fl1,auxNRow,auxNCol)= data_fl1_Smpl.shape
        auxNImg= NImg_fl0+NImg_fl1
        if verboseFlag: 
            APy3_GENfuns.printcol(str(NImg_fl0)+' Img-equivalent found in '+filenamepath_in0,'green')
            APy3_GENfuns.printcol(str(NImg_fl1)+' Img-equivalent found in '+filenamepath_in1,'green')
        if debugImg2show[-1] >= auxNImg: 
            debugImg2show=numpy.array([0])
            APy3_GENfuns.printcol('Img range selected to be shown does not match with total images available. Will show Img '+str(debugImg2show),'orange');
        #
        # combine in one array: Img0-from-fl0, then Img0-from-fl1, then Img1-from-fl0, then Img1-from-fl1, ...
        scrmbl_Smpl= numpy.zeros((auxNImg,auxNRow,auxNCol)).astype('uint16')
        scrmbl_Rst= numpy.zeros_like(scrmbl_Smpl).astype('uint16')
        for iImg in range(auxNImg):
            if( (iImg%2==0)&((iImg//2)<NImg_fl0) ):
                scrmbl_Smpl[iImg,:,:]= data_fl0_Smpl[iImg//2,:,:]
                scrmbl_Rst[iImg,:,:]= data_fl0_Rst[iImg//2,:,:]
            if( (iImg%2==1)&((iImg//2)<NImg_fl1) ):
                scrmbl_Smpl[iImg,:,:]= data_fl1_Smpl[iImg//2,:,:]
                scrmbl_Rst[iImg,:,:]= data_fl1_Rst[iImg//2,:,:]
        if cleanMemFlag: del data_fl0_Smpl; del data_fl1_Smpl; del data_fl0_Rst; del data_fl1_Rst
        # - - -
        #
        # solving DAQ-scrambling: byte swap in hex (byte0,byte1) => (byte1,byte0)
        if verboseFlag: APy3_GENfuns.printcol("solving DAQ-scrambling: byte-swapping (it might take a while)",'blue')
        dataSmpl_ByteSwap= APy3_GENfuns.convert_hex_byteSwap_Ar(scrmbl_Smpl)
        dataRst_ByteSwap= APy3_GENfuns.convert_hex_byteSwap_Ar(scrmbl_Rst)
        if cleanMemFlag: del scrmbl_Smpl; del scrmbl_Rst
        #
        # solving DAQ-scrambling: "pixel" reordering
        if verboseFlag: APy3_GENfuns.printcol("solving DAQ-scrambling: reordering subframes",'blue')
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
        dataSmpl_asMezz= convert_OdinDAQ_2_Mezzanine(dataSmpl_ByteSwap)
        dataRst_asMezz= convert_OdinDAQ_2_Mezzanine(dataRst_ByteSwap)
        if cleanMemFlag: del dataSmpl_ByteSwap; del dataRst_ByteSwap
        # - - -
        #
        # solving mezzanine-scrambling
        if verboseFlag: APy3_GENfuns.printcol("solving mezzanine&chip-scrambling: preparation",'blue')
        dataSmpl_2_srcmbl= dataSmpl_asMezz
        dataRst_2_srcmbl= dataRst_asMezz
        data_2_srcmbl_norefCol= numpy.ones((auxNImg,NSmplRst,auxNRow,auxNCol)).astype('uint16')* ((2**16)-1)
        data_2_srcmbl_norefCol[:,iSmpl,:,:]= dataSmpl_2_srcmbl
        data_2_srcmbl_norefCol[:,iRst,:,:]= dataRst_2_srcmbl
        data_2_srcmbl_norefCol=data_2_srcmbl_norefCol.reshape((auxNImg,NSmplRst,NGrp,NADC,auxNCol))
        #
        # track missing packets: False== RowGrp OK; True== packet(s) missing makes rowgroup moot (1111 1111 1111 1111 instead of 0xxx xxxx xxxx xxxx) 
        MissingRowGrpTracker= numpy.ones((auxNImg,NSmplRst,NGrp)).astype(bool) 
        MissingRowGrpTracker= data_2_srcmbl_norefCol[:,:,:,0,0]==ERRDLSraw   
        # - - -
        #
        # descramble proper
        if verboseFlag: APy3_GENfuns.printcol("solving mezzanine&chip-scrambling: pixel descrambling",'blue')
        multiImg_aggr_withRef= numpy.zeros((auxNImg,NSmplRst,NGrp,NPad,NADC*NColInBlock,3)).astype('uint8')
        for iImg in range(auxNImg):
            if verboseFlag: APy3_GENfuns.dot()
            auxil_thisImg= data_2_srcmbl_norefCol[iImg,:,:,:,:].reshape((NSmplRst,NGrp,NADC*auxNCol)) #(NSmplRst,NRowGrpInShot,NADC*auxNCol)
            auxil_thisImg= auxil_thisImg.reshape((NSmplRst,NGrp,NADC*auxNCol//(NDataPads*2),NDataPads,2)) #32bit=2"pix" from 1st pad, 2"pix" from 2nd pad, ...
            auxil_thisImg= numpy.transpose(auxil_thisImg, (0,1,3,2,4)) # NSmplRst,NGrp,NDataPads,NADC*auxNCol//(NDataPads*2),2"pix")
            auxil_thisImg= auxil_thisImg.reshape((NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads)) 
            #
            #%% bit, remove head 0, concatenate and reorder
            auxil_thisImg_16bitted= APy3_GENfuns.convert_uint_2_bits_Ar(auxil_thisImg,16)[:,:,:,:,::-1].astype('uint8') #NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads,15bits
            auxil_thisImg_bitted= auxil_thisImg_16bitted[:,:,:,:,1:] #NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads,15bits
            auxil_thisImg_bitted= auxil_thisImg_bitted.reshape((NSmplRst,NGrp,NDataPads,NADC*auxNCol*15//NDataPads))
            auxil_thisImg_bitted= auxil_thisImg_bitted.reshape((NSmplRst,NGrp,NDataPads,15,NADC*NColInBlock)) 
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
        if verboseFlag: APy3_GENfuns.printcol("",'blue')
        if cleanMemFlag: del auxil_thisImg_aggr_withRef    
        # - - -
        #
        # reorder pixels and pads 
        if verboseFlag: APy3_GENfuns.printcol("solving chip-scrambling: pixel reordering",'blue')
        multiImg_GrpDscrmbld= numpy.zeros((auxNImg,NSmplRst,NGrp,NPad,NADC,NColInBlock,3)).astype('uint8')
        for iImg in range(auxNImg):
            for iSmplRst in range(NSmplRst):    
                multiImg_GrpDscrmbld[iImg,iSmplRst,:,:,:,:,:]= APy3_P2Mfuns.reorder_pixels_GnCrsFn(multiImg_aggr_withRef[iImg,iSmplRst,:,:,:,:],NADC,NColInBlock)
        # - - -
        #
        # add error tracking
        if verboseFlag: APy3_GENfuns.printcol("lost packet tracking",'blue')
        multiImg_GrpDscrmbld= multiImg_GrpDscrmbld.astype('int16') # -256 upto 255
        for iImg in range(auxNImg):
            for iGrp in range(NGrp):
                for iSmplRst in range(NSmplRst):
                    if (MissingRowGrpTracker[iImg,iSmplRst,iGrp]): multiImg_GrpDscrmbld[iImg,iSmplRst,iGrp,:,:,:,:]=ERRint16
        multiImg_GrpDscrmbld[:,:,:,0,:,:,:]=ERRint16 # also err tracking for ref col
        # - - -
        #
        # reshaping as an Img array
        dscrmbld_GnCrsFn= numpy.zeros((auxNImg,NSmplRst,NGrp,NPad,NADC,NColInBlock,3)).astype('int16')
        dscrmbld_GnCrsFn[:,:,:,:,:,:,:]= multiImg_GrpDscrmbld[:,:,:,:,:,:,:]
        dscrmbld_GnCrsFn= numpy.transpose(dscrmbld_GnCrsFn,(0,1,2,4,3,5,6)).astype('int16') #(NImg,Smpl/Rst,NGrp,NADC,NPad,NColInBlk,Gn/Crs/Fn)
        dscrmbld_GnCrsFn=dscrmbld_GnCrsFn.reshape((auxNImg,NSmplRst,NGrp*NADC,NPad*NColInBlock,3))
        # - - -
        #
        # show descrambled data
        if debugFlag: 
            aux_ERRBlw=-0.1
            for aux_thisimg in debugImg2show:
                aux_title= "Img "+str(aux_thisimg)+" descrambled"
                APy3_P2Mfuns.percDebug_plot_6x2D(dscrmbld_GnCrsFn[aux_thisimg,iSmpl,:,:,iGn],dscrmbld_GnCrsFn[aux_thisimg,iSmpl,:,:,iCrs],dscrmbld_GnCrsFn[aux_thisimg,iSmpl,:,:,iFn],\
                                        dscrmbld_GnCrsFn[aux_thisimg,iRst,:,:,iGn],dscrmbld_GnCrsFn[aux_thisimg,iRst,:,:,iCrs],dscrmbld_GnCrsFn[aux_thisimg,iRst,:,:,iFn],\
                                        aux_title,aux_ERRBlw)
        # - - -
        #
        # convert Gn/Crs/Fn => DLSraw: 16bit (errorbit+15bits)
        if verboseFlag: APy3_GENfuns.printcol('converting to DLSraw format ( uint16: [X, Gn,Gn, Fn,Fn,Fn,Fn,Fn,Fn,Fn,Fn, Crs,Crs,Crs,Crs,Crs] )','green')
        (dscrmbld_Smpl_DLSraw,dscrmbld_Rst_DLSraw)=APy3_P2Mfuns.convert_GnCrsFn_2_DLSraw(dscrmbld_GnCrsFn, ERRint16, ERRDLSraw)
        if cleanMemFlag: del dscrmbld_GnCrsFn
        # - - -
        #
        # save descrambled data
        if saveFileFlag: 
            APy3_GENfuns.write_2xh5(filenamepath_out, dscrmbld_Smpl_DLSraw,'/data/', dscrmbld_Rst_DLSraw,'/reset/')
            APy3_GENfuns.printcol('data saved to: '+filenamepath_out,'green')
            if cleanMemFlag: del dscrmbld_Smpl_DLSraw; del dscrmbld_Rst_DLSraw
        # - - -
        #
        # show saved data
        if debugFlag & saveFileFlag:
            (reread_Smpl,reread_Rst)= APy3_GENfuns.read_2xh5(filenamepath_out, '/data/', '/reset/')
            reread_GnCrsFn= APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(reread_Smpl,reread_Rst, ERRDLSraw, ERRint16)
            if cleanMemFlag: del reread_Smpl; del reread_Rst
            for aux_thisimg in debugImg2show:
                aux_title= "Img "+str(aux_thisimg)+" read from file"
                aux_ERRBlw=-0.1
                APy3_P2Mfuns.percDebug_plot_6x2D(reread_GnCrsFn[aux_thisimg,iSmpl,:,:,iGn],reread_GnCrsFn[aux_thisimg,iSmpl,:,:,iCrs],reread_GnCrsFn[aux_thisimg,iSmpl,:,:,iFn],\
                                        reread_GnCrsFn[aux_thisimg,iRst,:,:,iGn],reread_GnCrsFn[aux_thisimg,iRst,:,:,iCrs],reread_GnCrsFn[aux_thisimg,iRst,:,:,iFn],\
                                        aux_title,aux_ERRBlw)
        # - - -
        '''

        #
        #%% that's all folks
        print("------------------------") 
        print("done")
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script ended at {0}".format(aux_timeId) ,'blue')
        for iaux in range(3): print("------------------------")
        input('Press enter to end')
        

