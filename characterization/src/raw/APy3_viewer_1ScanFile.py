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
iTRow=0; iTCol=1
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
        ''' 1h5 file containing all the images of a scan (DLSraw) + 1 metafile with the Vx value for each image => show crs & fn evolution'''
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script beginning at {0}".format(aux_timeId) ,'blue')
        APy3_GENfuns.printcol("this scripts1h5 file containing all the images of a scan (DLSraw) + 1 metafile with the Vx value for each image => show crs & fn evolution" ,'orange')
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
        dflt_mainFolder= "/home/prcvlusr/Desktop/LinkToPercAuxiliaryTools/PercPython/data/testADC/testADC07_VRST/ADCClk_25MHz/20180503/00_prelimTest_toVerifyFunctionality/"
        dflt_fileName_prefix= "prelim_Iain2018.05.03_VRSTfromVin_1100,34000,100_1Img"
        dflt_fileName_data_suffix= "_DLSraw.h5"
        dflt_filenamepath_data= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_data_suffix
        dflt_fileName_info_suffix= "_DLSraw.VRST"
        dflt_filenamepath_info= dflt_mainFolder+dflt_fileName_prefix+dflt_fileName_info_suffix
        #
        dflt_Row2show_mtlb='140:146'
        dflt_Col2show_mtlb='100:101'
        dflt_showSmplRst='Y'
        dflt_showLineFlag='Y'
        #
        dflt_kindOfScanLabel= 'VRST [V]'        
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
        GUIwin_arguments+= ['path & name of h5 file'] 
        GUIwin_arguments+= [dflt_filenamepath_data] 
        GUIwin_arguments+= ['path & name of info'] 
        GUIwin_arguments+= [dflt_filenamepath_info] 
        #
        GUIwin_arguments+= ['show evolution of which pixel? [fromRow:toRow]'] 
        GUIwin_arguments+= [dflt_Row2show_mtlb] 
        GUIwin_arguments+= ['show evolution of which pixel? [fromCol:toCol]'] 
        GUIwin_arguments+= [dflt_Col2show_mtlb]
        GUIwin_arguments+= ['show Sample? [Y=Sample/N=Reset]'] 
        GUIwin_arguments+= [dflt_showSmplRst]
        GUIwin_arguments+= ['show Lines? [Y/N]'] 
        GUIwin_arguments+= [dflt_showLineFlag]
        GUIwin_arguments+= ['which kind of scan is it?'] 
        GUIwin_arguments+= [dflt_kindOfScanLabel]        
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
        filenamepath_data= dataFromUser[iparam]; iparam+=1   
        filenamepath_info= dataFromUser[iparam]; iparam+=1  
        Row2show_str=dataFromUser[iparam]; iparam+=1; Row2show= APy3_GENfuns.matlabLike_range(Row2show_str)
        Col2show_str=dataFromUser[iparam]; iparam+=1; Col2show= APy3_GENfuns.matlabLike_range(Col2show_str)
        showSmpl_Flag= APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        showLineFlag= APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        kindOfScanLabel= dataFromUser[iparam]; iparam+=1 
        #
        debugFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        debugImg2show=APy3_GENfuns.matlabLike_range(dataFromUser[iparam]); iparam+=1;  
        #
        cleanMemFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        verboseFlag=APy3_GENfuns.isitYes(dataFromUser[iparam]); iparam+=1
        #
        if verboseFlag: 
            APy3_GENfuns.printcol('will load files:','green')
            APy3_GENfuns.printcol('data: '+filenamepath_data,'green')
            APy3_GENfuns.printcol('info: '+filenamepath_info,'green')
            APy3_GENfuns.printcol(kindOfScanLabel+'-scan','green')
            APy3_GENfuns.printcol('will show evolution of pixels in: ','green')
            APy3_GENfuns.printcol('Rows: '+str(Row2show),'green')
            APy3_GENfuns.printcol('Cols: '+str(Col2show),'green')
            if showSmpl_Flag: APy3_GENfuns.printcol('will show Sample data ','green')
            else: APy3_GENfuns.printcol('will show Reset data ','green')
            if debugFlag: APy3_GENfuns.printcol('debug: will show images: '+str(debugImg2show),'green')
            if cleanMemFlag: APy3_GENfuns.printcol('will clean memory when possible','green')
            APy3_GENfuns.printcol("verbose",'green')
        # - - -
        #
        # load files
        if verboseFlag: APy3_GENfuns.printcol('reading files','blue')
        aux_path1_2read='/data/';  aux_path2_2read='/reset/'
        if (os.path.isfile(filenamepath_data)==False): APy3_GENfuns.printcol('unable to find data file: '+filenamepath_data,'red'); return()
        (dataDLSraw_Smpl,dataDLSraw_Rst)= APy3_GENfuns.read_2xh5(filenamepath_data, aux_path1_2read, aux_path2_2read)
        if (os.path.isfile(filenamepath_info)==False): APy3_GENfuns.printcol('unable to find info file: '+filenamepath_info,'red'); return()
        infoScan= APy3_GENfuns.read_tst(filenamepath_info)
        # - - -
        #
        # convert files
        data_GnCrsFn=APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(dataDLSraw_Smpl,dataDLSraw_Rst, ERRDLSraw, ERRint16)
        (auxNImg, auxNSmplRst, auxNRow, auxNCol, auxNGnCrsFn)= data_GnCrsFn.shape
        if verboseFlag: APy3_GENfuns.printcol(str(auxNImg)+' Img found in the data file','blue')
        if infoScan.ndim==1: scanParameter= infoScan.astype(float) # 1-column file
        else: scanParameter= infoScan[:,0].astype(float) # multi-column file
        #
        if (len(scanParameter)!=auxNImg): APy3_GENfuns.printcol(str(len(scanParameter))+' points found in the info file','red'); return() 
        if debugFlag & (debugImg2show[-1]>=auxNImg):
            debugImg2show=numpy.array([0])
            APy3_GENfuns.printcol('debug: images to be shown changed to: '+str(debugImg2show),'purple')
        if cleanMemFlag: del dataDLSraw_Smpl; del dataDLSraw_Rst; del infoScan
        # - - -
        #
        # show evolution of crs, fn
        sets_TList= APy3_GENfuns.indices_rectangle(Row2show,Col2show)
        auxNSets= len(sets_TList)
        aux_crsSets2show_2D= numpy.zeros((auxNSets,auxNImg)).astype('int16')
        aux_fnSets2show_2D= numpy.zeros((auxNSets,auxNImg)).astype('int16')
        aux_infoSets_List=[]
        if showSmpl_Flag: iSmplRst=iSmpl; aux_title= 'Sample ,'
        else: iSmplRst=iRst; aux_title= 'Reset ,'
        aux_title= aux_title+'pixels in Rows '+Row2show_str+ ', Cols '+Col2show_str
        #
        for iSet,thisT in enumerate(sets_TList):
            thisRow= thisT[iTRow]
            thisCol= thisT[iTCol]
            aux_crsSets2show_2D[iSet,:]= data_GnCrsFn[:,iSmplRst,thisRow,thisCol,iCrs]
            aux_fnSets2show_2D[iSet,:]= data_GnCrsFn[:,iSmplRst,thisRow,thisCol,iFn]
            aux_infoSets_List+=[str(thisT)]
        #
        APy3_GENfuns.plot_multi1D(scanParameter, aux_crsSets2show_2D, aux_infoSets_List, kindOfScanLabel,'crs',aux_title,showLineFlag)
        APy3_GENfuns.plot_multi1D(scanParameter, aux_fnSets2show_2D, aux_infoSets_List, kindOfScanLabel,'fn',aux_title,showLineFlag)
        # - - -
        #
        # debug
        if debugFlag: 
            aux_ERRBlw=-0.1
            for aux_thisimg in debugImg2show:
                aux_title= "Img "+str(aux_thisimg)
                APy3_P2Mfuns.percDebug_plot_6x2D(data_GnCrsFn[aux_thisimg,iSmpl,:,:,iGn],data_GnCrsFn[aux_thisimg,iSmpl,:,:,iCrs],data_GnCrsFn[aux_thisimg,iSmpl,:,:,iFn],\
                                        data_GnCrsFn[aux_thisimg,iRst,:,:,iGn],data_GnCrsFn[aux_thisimg,iRst,:,:,iCrs],data_GnCrsFn[aux_thisimg,iRst,:,:,iFn],\
                                        aux_title,aux_ERRBlw)
        #
        #%% that's all folks
        print("------------------------") 
        print("done")
        aux_timeId=time.strftime("%Y_%m_%d__%H:%M:%S")
        APy3_GENfuns.printcol("script ended at {0}".format(aux_timeId) ,'blue')
        input('Press enter to end')
        for iaux in range(3): print("------------------------")        

