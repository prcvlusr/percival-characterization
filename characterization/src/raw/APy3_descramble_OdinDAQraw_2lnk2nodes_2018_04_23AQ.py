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
        ''' 2xh5 files saved with Odin-DAQ (raw mode, scrambled) using 2018.04.23_AQ Firmware (2links,2nodes) through switch => descramble => save as an h5 file in agreed format'''
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script beginning at {0}".format(aux_timeId) ,'blue')
        APy3_GENfuns.printcol("this scripts takes 2 scrambled h5 files (from Odin-DAQ), combines and descrambles data. If needed shows/save descrambled data" ,'orange')
        #
        NADC=APy3_P2Mfuns.NADC #7
        NGrp=APy3_P2Mfuns.NGrp #212
        NSmplRst= APy3_P2Mfuns.NSmplRst #2 
        NRow= APy3_P2Mfuns.NRow # 212
        #NCol= APy3_P2Mfuns.NCol
        NPad= APy3_P2Mfuns.NPad # 45
        NDataPads= APy3_P2Mfuns.NPad-1 #44
        NColInBlock= APy3_P2Mfuns.NColInBlock #32
        # - - -
        #
        # default values
        dflt_mainFolder= "/home/marras/PERCIVAL/PercFramework/data/h5_scrmbl_view/h5in/"
        dflt_fileName_prefix= "test003"
        #
        dflt_fileName_suffix0= "_fl0.h5"
        dflt_fileName_suffix1= "_fl1.h5"
        dflt_filenamepath_in0= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffix0
        dflt_filenamepath_in1= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffix1
        #
        dflt_saveFileFlag='Y'
        dflt_fileName_suffixout= "_dscrmbld_DLSraw.h5"
        dflt_filenamepath_out= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_suffixout
        #
        dflt_debugFlag='N';
        dflt_debugImg2show_mtlb='3:4'
        #
        dflt_cleanMemFlag='Y'
        dflt_verboseFlag='Y' 
        # - - -  
        #
        # GUI window
        GUIwin_arguments= []
        GUIwin_arguments+= ['path & name of node0-h5 file to descramble'] 
        GUIwin_arguments+= [dflt_filenamepath_in0] 
        GUIwin_arguments+= ['path & name of node1-h5 file to descramble'] 
        GUIwin_arguments+= [dflt_filenamepath_in1] 
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
            APy3_GENfuns.printcol('will load h5 files:','green')
            APy3_GENfuns.printcol('node-0 file: '+filenamepath_in0,'green')
            APy3_GENfuns.printcol('node-1 file: '+filenamepath_in1,'green')
            #
            if saveFileFlag: APy3_GENfuns.printcol('will save descrambled file: '+filenamepath_out,'green')
            if debugFlag: APy3_GENfuns.printcol('debug: will show images: '+str(debugImg2show),'green')
            #
            if cleanMemFlag: APy3_GENfuns.printcol('will clean memory when possible','green')
            APy3_GENfuns.printcol("verbose",'green')
        # - - -
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
                aux_title= "Img "+str(aux_thisimg)+" from file"
                aux_ERRBlw=-0.1
                APy3_P2Mfuns.percDebug_plot_6x2D(reread_GnCrsFn[aux_thisimg,iSmpl,:,:,iGn],reread_GnCrsFn[aux_thisimg,iSmpl,:,:,iCrs],reread_GnCrsFn[aux_thisimg,iSmpl,:,:,iFn],\
                                        reread_GnCrsFn[aux_thisimg,iRst,:,:,iGn],reread_GnCrsFn[aux_thisimg,iRst,:,:,iCrs],reread_GnCrsFn[aux_thisimg,iRst,:,:,iFn],\
                                        aux_title,aux_ERRBlw)
        # - - -
        #
        #%% that's all folks
        print("------------------------") 
        print("done")
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script ended at {0}".format(aux_timeId) ,'blue')
        input('Press enter to end')
        for iaux in range(3): print("------------------------")        

