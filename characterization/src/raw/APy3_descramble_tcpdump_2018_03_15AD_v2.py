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
iGn=0; iCrs=1; iFn=2; NGnCrsFn=3
iSmpl=0; iRst=1; NSmplRst=2 
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
        #dflt_mainFolder= "/home/prcvlusr/PercAuxiliaryTools/PercPython/data/testFramework/2018.05.25/try1/"
        #dflt_fileName_prefix= "VRST=10k_AD_10frames"
        dflt_mainFolder= "/home/prcvlusr/PercAuxiliaryTools/PercPython/data/testFramework/2018.05.25/try2/"
        dflt_fileName_prefix= "2018.05.23_AD_02"
        dflt_fileName_suffix0= "_lnk0.dmp"
        dflt_fileName_suffix1= "_lnk1.dmp"
        dflt_fileName_suffix2= "_lnk2.dmp"
        dflt_filenamepath_in0= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffix0
        dflt_filenamepath_in1= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffix1
        dflt_filenamepath_in2= "not_a_real_file"
        #
        dflt_saveFileFlag='N'
        dflt_fileName_suffixout= "_dscrmbld_DLSraw.h5"
        dflt_filenamepath_out= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffixout
        #
        dflt_debugFlag='Y';
        dflt_debugImg2show_mtlb='0:0'
        dflt_deepDebug_Rows_mtlb= '140:146' 
        dflt_deepDebug_Cols_mtlb= '100:100'
        dflt_deepDebug_SmplRst= 'Y'
        #
        dflt_saveMultiFileFlag='Y'
        dflt_saveMulti_metaFile= dflt_mainFolder+dflt_fileName_prefix+"_meta.dat"
        #dflt_saveMulti_ImgxFile= "2"
        dflt_saveMulti_ImgxFile= "1"
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
        GUIwin_arguments+= ['save 1 descrambled file? [Y/N]'] 
        GUIwin_arguments+= [dflt_saveFileFlag] 
        GUIwin_arguments+= ['if save 1 file: where? [file path & name]'] 
        GUIwin_arguments+= [dflt_filenamepath_out] 
        #
        GUIwin_arguments+= ['save to multiple descrambled files (scan)? [Y/N]'] 
        GUIwin_arguments+= [dflt_saveMultiFileFlag]  
        GUIwin_arguments+= ['if save multiple files: using filename from metafile [file path & name]'] 
        GUIwin_arguments+= [dflt_saveMulti_metaFile]    
        GUIwin_arguments+= ['if save multiple files: assuming each step of the scan has x Images:'] 
        GUIwin_arguments+= [dflt_saveMulti_ImgxFile]     
        #
        GUIwin_arguments+= ['debug (show images)? [Y/N]'] 
        GUIwin_arguments+= [dflt_debugFlag] 
        GUIwin_arguments+= ['if debug: show which images? [from:to]'] 
        GUIwin_arguments+= [dflt_debugImg2show_mtlb] 
        GUIwin_arguments+= ['if debug & save multiple: show evolution of Rows [from:to]'] 
        GUIwin_arguments+= [dflt_deepDebug_Rows_mtlb] 
        GUIwin_arguments+= ['if debug & save multiple: show evolution of Cols [from:to]'] 
        GUIwin_arguments+= [dflt_deepDebug_Cols_mtlb] 
        GUIwin_arguments+= ['if debug & save multiple: show Smpl/Rst [Y=Smpl / N=Rst]'] 
        GUIwin_arguments+= [dflt_deepDebug_SmplRst] 
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
        saveMultiFileFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        saveMulti_metaFile= dataFromUser[iparam]; iparam+=1 
        saveMulti_ImgxFile= int(dataFromUser[iparam]); iparam+=1 
        #
        debugFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        debugImg2show_mtlb= dataFromUser[iparam]; iparam+=1; 
        debugImg2show=APy3_GENfuns.matlabLike_range(debugImg2show_mtlb)   
        #
        deepDebug_Rows_mtlb= dataFromUser[iparam]; iparam+=1;  
        deepDebug_Rows= APy3_GENfuns.matlabLike_range(deepDebug_Rows_mtlb)
        deepDebug_Cols_mtlb= dataFromUser[iparam]; iparam+=1;
        deepDebug_Cols= APy3_GENfuns.matlabLike_range(deepDebug_Cols_mtlb)
        deepDebug_SmplRst_str= dataFromUser[iparam]; iparam+=1;
        if APy3_GENfuns.isitYes(deepDebug_SmplRst_str): deepDebug_SmplRst= iSmpl
        else: deepDebug_SmplRst= iRst
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

            if saveMultiFileFlag: 
                APy3_GENfuns.printcol('will save to multiple descrambled files, using filenames provided in metafile: '+saveMulti_metaFile+ ' and assuming '+str(saveMulti_ImgxFile)+' Img per step','green')

            if debugFlag: APy3_GENfuns.printcol('debug: will show images: '+str(debugImg2show),'green')
            if debugFlag & saveMultiFileFlag: APy3_GENfuns.printcol('debug: will evolution of pixels ('+deepDebug_Rows_mtlb+','+deepDebug_Cols_mtlb+')','green')
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
        # - - -
        #
        # convert Gn/Crs/Fn => DLSraw: 16bit (errorbit+15bits)
        if verboseFlag: APy3_GENfuns.printcol('converting to DLSraw format ( uint16: [X, Gn,Gn, Fn,Fn,Fn,Fn,Fn,Fn,Fn,Fn, Crs,Crs,Crs,Crs,Crs] )','green')
        (dscrmbld_Smpl_DLSraw,dscrmbld_Rst_DLSraw)=APy3_P2Mfuns.convert_GnCrsFn_2_DLSraw(multiImg_SmplRstGnCrsFn, ERRint16, ERRDLSraw)
        if cleanMemFlag: del multiImg_SmplRstGnCrsFn
        # - - -
        #
        # save descrambled data to 1 file
        if saveFileFlag: 
            if verboseFlag: APy3_GENfuns.printcol("saving data to 1 file",'blue')
            APy3_GENfuns.write_2xh5(filenamepath_out, dscrmbld_Smpl_DLSraw,'/data/', dscrmbld_Rst_DLSraw,'/reset/')
            APy3_GENfuns.printcol('data saved to: '+filenamepath_out,'green')
        # - - -
        # show saved data
        #if debugFlag & saveFileFlag:
        #    (reread_Smpl,reread_Rst)= APy3_GENfuns.read_2xh5(filenamepath_out, '/data/', '/reset/')
        #    reread_GnCrsFn= APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(reread_Smpl,reread_Rst, ERRDLSraw, ERRint16)
        #    if cleanMemFlag: del reread_Smpl; del reread_Rst
        #    for iImg_h5, thisImg_dump in enumerate(debugImg2show_tcpdump):
        #        aux_title= "Img "+str(iImg_h5)+" from file"
        #        aux_ERRBlw=-0.1
        #        APy3_P2Mfuns.percDebug_plot_6x2D(reread_GnCrsFn[iImg_h5,iSmpl,:,:,iGn],reread_GnCrsFn[iImg_h5,iSmpl,:,:,iCrs],reread_GnCrsFn[iImg_h5,iSmpl,:,:,iFn],\
        #                                reread_GnCrsFn[iImg_h5,iRst,:,:,iGn],reread_GnCrsFn[iImg_h5,iRst,:,:,iCrs],reread_GnCrsFn[iImg_h5,iRst,:,:,iFn],\
        #                                aux_title,aux_ERRBlw)
        # - - -
        # save descrambled data to multiple files
        if saveMultiFileFlag:
            if verboseFlag: APy3_GENfuns.printcol("saving data to multiple file",'blue')
            if os.path.isfile(saveMulti_metaFile)==False: 
                APy3_GENfuns.printcol('unable to find '+saveMulti_metaFile,'red')
                return
            saveMultiOutdir= os.path.dirname(saveMulti_metaFile)
            scanList= APy3_GENfuns.read_tst(saveMulti_metaFile)
            scanList_shape= scanList.shape
            if len(scanList_shape)!=2:
                APy3_GENfuns.printcol('metafile should tahe 2 columns, tab-spaced','red')
                return 
            fileNamelist= scanList[:,1]
            Nsteps= len(fileNamelist)
            (auxNImg,auxNRow,auxNCol)=dscrmbld_Smpl_DLSraw.shape
            if auxNImg!=(Nsteps*saveMulti_ImgxFile):
                APy3_GENfuns.printcol('NImg =/= Nsteps * NImg/Step','red')
                APy3_GENfuns.printcol(str(auxNImg)+' =/= '+str(Nsteps)+' * '+str(saveMulti_ImgxFile),'red')
                return
            #
            Smpl_DLSraw_xStep= dscrmbld_Smpl_DLSraw.reshape(Nsteps,saveMulti_ImgxFile,auxNRow,auxNCol) #(Nsteps,NImgPerStep,NRow,NCol)
            Rst_DLSraw_xStep=  dscrmbld_Rst_DLSraw.reshape( Nsteps,saveMulti_ImgxFile,auxNRow,auxNCol)
            for iStep,thisFilePrefix in enumerate(fileNamelist):
                thisFilePath_out= saveMultiOutdir+thisFilePrefix+'_DLSraw.h5'
                APy3_GENfuns.write_2xh5(thisFilePath_out, Smpl_DLSraw_xStep[iStep,:,:,:],'/data/', Rst_DLSraw_xStep[iStep,:,:,:],'/reset/')
                APy3_GENfuns.printcol(str(saveMulti_ImgxFile)+" Images saved to "+thisFilePath_out,'green')
            if cleanMemFlag: del Smpl_DLSraw_xStep; del Rst_DLSraw_xStep
        # - - -
        #
        # show multiple-file-saved data
        if debugFlag & saveMultiFileFlag:
            scanList= APy3_GENfuns.read_tst(saveMulti_metaFile)
            fileNamelist= scanList[:,1]
            scanPoints= scanList[:,0].astype(float)
            Nsteps= len(fileNamelist)
            MultiDataReread= numpy.zeros((Nsteps,saveMulti_ImgxFile,NSmplRst,auxNRow,auxNCol,NGnCrsFn)).astype('uint16')
            for iStep,thisFilePrefix in enumerate(fileNamelist):
                thisFilePath_in= saveMultiOutdir+thisFilePrefix+'_DLSraw.h5'
                (reread_Smpl,reread_Rst)= APy3_GENfuns.read_2xh5(thisFilePath_in, '/data/', '/reset/')
                MultiDataReread[iStep,:,:,:,:,:]= APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(reread_Smpl,reread_Rst, ERRDLSraw, ERRint16)
            #
            # show 1st pixel, per Img
            XtoPlot= scanPoints
            thisRow=deepDebug_Rows[0]
            thisCol=deepDebug_Cols[0]
            kindOfScanLabel= 'VRST [V]'
            aux_title= 'pixel '+str((thisRow,thisCol))+' vs Img number'
            if deepDebug_SmplRst==iSmpl: aux_title+=' (Smpl)'
            else:                        aux_title+=' (Rst)'
            aux_infoSets_List= []
            for iImg in range(saveMulti_ImgxFile):
                aux_infoSets_List+=['Img='+str(iImg)] 
            YtoPlot2D= MultiDataReread[:,:,deepDebug_SmplRst,thisRow,thisCol,iCrs].transpose((1,0))
            APy3_GENfuns.plot_multi1D(XtoPlot, YtoPlot2D, aux_infoSets_List, kindOfScanLabel,'Crs',aux_title,True)
            YtoPlot2D= MultiDataReread[:,:,deepDebug_SmplRst,thisRow,thisCol,iFn].transpose((1,0))
            APy3_GENfuns.plot_multi1D(XtoPlot, YtoPlot2D, aux_infoSets_List, kindOfScanLabel,'Fn',aux_title,True)
            #
            # show several pixels, all Img
            XtoPlot= numpy.repeat(scanPoints[:, numpy.newaxis], saveMulti_ImgxFile, axis=1).flatten()
            #YtoPlot2D5= MultiDataReread[:,:,deepDebug_SmplRst,deepDebug_Rows,deepDebug_Cols,:] #(Steps,ImgPerStep,Rows2Show,Cols2Show,GnCrsFn)
            YtoPlot2D5= MultiDataReread[:,:,deepDebug_SmplRst,deepDebug_Rows[0]:deepDebug_Rows[-1]+1,deepDebug_Cols[0]:deepDebug_Cols[-1]+1,:] #(Steps,ImgPerStep,Rows2Show,Cols2Show,GnCrsFn)
            YtoPlot2D5= YtoPlot2D5.reshape((Nsteps*saveMulti_ImgxFile,len(deepDebug_Rows),len(deepDebug_Cols),NGnCrsFn))
            YtoPlot2D5= YtoPlot2D5.reshape((Nsteps*saveMulti_ImgxFile,len(deepDebug_Rows)*len(deepDebug_Cols),NGnCrsFn))
            YtoPlot2D5= YtoPlot2D5.transpose((1,0,2)) # (pixels2show,Nsteps*saveMulti_ImgxFile,NGnCrsFn)
            aux_infoSets_List= []
            for thisRow in deepDebug_Rows:
                for thisCol in deepDebug_Cols:
                    aux_infoSets_List+=['pixel '+str((thisRow,thisCol))]
            aux_title= 'pixels ('+deepDebug_Rows_mtlb+','+deepDebug_Cols_mtlb+'), using all images' 
            if deepDebug_SmplRst==iSmpl: aux_title+=' (Smpl)'
            else:                        aux_title+=' (Rst)'
            APy3_GENfuns.plot_multi1D(XtoPlot, YtoPlot2D5[:,:,iCrs], aux_infoSets_List, kindOfScanLabel,'Crs',aux_title,False)     
            APy3_GENfuns.plot_multi1D(XtoPlot, YtoPlot2D5[:,:,iFn], aux_infoSets_List, kindOfScanLabel,'Fn',aux_title,False)                 
            #
            # show 1stpixel, 2dhisto
            thisRow=deepDebug_Rows[0]
            thisCol=deepDebug_Cols[0]
            kindOfScanLabel= 'VRST [V]'
            aux_title= 'pixel '+str((thisRow,thisCol))
            if deepDebug_SmplRst==iSmpl: aux_title+=' (Smpl)'
            else:                        aux_title+=' (Rst)'
            APy3_GENfuns.plot_histo2D(XtoPlot,YtoPlot2D5[0,:,iCrs], len(XtoPlot),31, kindOfScanLabel,'Crs',aux_title,0.1)
            APy3_GENfuns.plot_histo2D(XtoPlot,YtoPlot2D5[0,:,iFn], len(XtoPlot),31, kindOfScanLabel,'Fn',aux_title,0.1)
        # - - -
        #
        #%% that's all folks
        print("------------------------") 
        print("done")
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script ended at {0}".format(aux_timeId) ,'blue')
        for iaux in range(3): print("------------------------")
        input('Press enter to end')
        

