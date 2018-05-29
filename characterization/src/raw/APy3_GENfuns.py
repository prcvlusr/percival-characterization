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
#%% numeric formats
def convert_uint_2_bits_Ar(in_intAr,Nbits):
    ''' convert (numpyarray of uint => array of Nbits bits) for many bits in parallel '''
    inSize_T= in_intAr.shape
    in_intAr_flat=in_intAr.flatten()
    out_NbitAr= numpy.zeros((len(in_intAr_flat),Nbits))
    for iBits in range(Nbits):
        out_NbitAr[:,iBits]= (in_intAr_flat>>iBits)&1
    out_NbitAr= out_NbitAr.reshape(inSize_T+(Nbits,))
    return out_NbitAr        
#
def convert_bits_2_int_Ar(in_bitAr):
    ''' convert (numpyarray of [... , ... , Nbits] => array of [... , ... ](int) for many values in parallel'''
    inSize_T= in_bitAr.shape 
    Nbits= inSize_T[-1]
    outSize_T= inSize_T[0:-1]
    out_intAr=numpy.zeros(outSize_T)
    power2Matrix=( 2**numpy.arange(Nbits) ).astype(int) 
    aux_powerMatr= power2Matrix* numpy.ones(inSize_T).astype(int) 
    totalVector_xDAr= numpy.sum(in_bitAr*aux_powerMatr, axis=len(inSize_T)-1); 
    out_intAr=totalVector_xDAr.astype(int)
    return out_intAr  
#
def convert_britishBits_Ar(BritishBitArray):
    " 0=>1 , 1=>0 "
    HumanReadableBitArray=1-BritishBitArray
    return HumanReadableBitArray
#
def convert_int_2_2xuint8(int2convert):
    ''' 259 => (1,3) '''
    out_uint8_MSB= int2convert//256
    out_uint8_LSB= int2convert%256
    return (out_uint8_MSB, out_uint8_LSB)
#
def convert_2xuint8_2_int(MSByte,LSByte):
    ''' 259 <= (1,3) '''
    out_int= (256*MSByte)+LSByte
    return (out_int)
#
def convert_int_2_4xuint8(int2convert):
    ''' 259 => (0,0,1,3) '''
    aux_int2convert=int2convert
    out_MSB= int2convert//(2**24)
    if aux_int2convert>=(2**24): aux_int2convert=aux_int2convert-(2**24)
    out_mid2SByte= int2convert//(2**16)
    if aux_int2convert>=(2**16): aux_int2convert=aux_int2convert-(2**16)
    out_mid1SByte= int2convert//(2**8)
    if aux_int2convert>=(2**8): aux_int2convert=aux_int2convert-(2**8)
    out_LSB= aux_int2convert
    return(out_MSB, out_mid2SByte, out_mid1SByte, out_LSB)
#
def convert_4xuint8_2_int(MSByte,mid2SByte,mid1SByte,LSByte):
    ''' 259 <= (0,0,1,3) '''
    out_int= ((2**24)*MSByte)+ ((2**16)*mid2SByte)+ ((2**8)*mid1SByte)+ LSByte
    return (out_int)
#
def convert_hex_byteSwap_Ar(data2convert_Ar):
    ''' interpret the ints in an array as 16 bits. byte-swap them: (byte0,byte1) => (byte1,byte0) '''
    aux_bitted= convert_uint_2_bits_Ar(data2convert_Ar,16).astype('uint8')
    aux_byteinverted= numpy.zeros_like(aux_bitted).astype('uint8')
    #
    aux_byteinverted[...,0:8]= aux_bitted[...,8:16]
    aux_byteinverted[...,8:16]= aux_bitted[...,0:8]
    data_ByteSwapped_Ar=convert_bits_2_int_Ar(aux_byteinverted)
    return (data_ByteSwapped_Ar)
#
#
#
#%% print
def dot():
    '''print a dot '''
    sys.stdout.write(".")
    sys.stdout.flush() # print it now
#
def printcol(string,colour):
    ''' write in colour (red/green/orange/blue/purple) '''
    white  = '\033[0m'  # white (normal)
    if (colour=='black'): outColor  = '\033[30m' # black
    elif (colour=='red'): outColor= '\033[31m' # red
    elif (colour=='green'): outColor  = '\033[32m' # green
    elif (colour=='orange'): outColor  = '\033[33m' # orange
    elif (colour=='blue'): outColor  = '\033[34m' # blue
    elif (colour=='purple'): outColor  = '\033[35m' # purple
    else: outColor  = '\033[30m'
    print(outColor+string+white)
    sys.stdout.flush()
#
#%% yes, no
def isitYes(string):
    ''' recognize a yes '''
    YESarray=['y','Y','yes','YES','Yes','si','SI','Si','ja','JA','Ja','true','TRUE','True']  
    isitYes= False
    if string in YESarray:
        isitYes=True
    return(isitYes)
#
def isitNo(string):
    ''' recognize a no '''
    NOarray=['n','N','no','NO','No','over my dead body','forget about it','nope','nein','NEIN','Nein','false','FALSE','False']  
    isitNO= False
    if string in NOarray:
        isitNO=True
    return(isitNO)
#
#%% matlab-like function
def clean():
    ''' close all figures '''   
    matplotlib.pyplot.close('all')
#    
#def find_2D(Xin,Yin,conditionList):
#    ''' 
#    emulate matlab 'find' (as much as possible in the python nonsense)
#    returns arrays X[i],Y[i] only if conditions[i]==True
#    note that conditions is a list of booleans (created with a statement like "Xin>a_number")
#    '''
#    Xout=[]; Yout=[]
#    for i in range(len(Xin)):
#        if (conditionList[i]==True):
#            Xout+= [Xin[i]]
#            Yout+= [Yin[i]]
#    Xout= numpy.array(Xout)
#    Yout= numpy.array(Yout)
#    return (Xout, Yout)
#
def matlabLike_range(matlabstring):
    '''
    use the sensible matlab syntax to make incremental array, instead of the python nonsense
    'xx:yy'    means:    [xx,xx+1,xx+2,...,yy-1,yy] (numpy array)
    equivalent to numpy.arange(xx,yy+1)
    '''  
    from_str= matlabstring.partition(':')[0]
    to_str= matlabstring.partition(':')[-1]
    #
    out_python_range=numpy.array([]) # default
    if (from_str.isdigit())&(to_str.isdigit()):
        if (int(from_str)<=int(to_str)):
            from_int= int(from_str);  to_int= int(to_str); 
            out_python_range= numpy.arange(from_int, to_int+1)
        else: 
            print("UNABLE TO RECOGNIZE MATLAB-LIKE RANGE, WILL USE NONE []")            
    else:
        print("UNABLE TO RECOGNIZE MATLAB-LIKE RANGE, WILL USE NONE []") # yes, also this is needed
    return(out_python_range)
#
#%% sorting list in natural form
''' natural sorting of a list of strings with numbers ['a0','a1','a2',...,'a10','a11',...] '''
def atoi(text):
    return int(text) if text.isdigit() else text
#
def natural_keys(text):
    ''' thisIsaList.sort(key=natural_keys)'''
    return [atoi(c) for c in re.split('(\d+)', text)]
def sort_nicely(myList):
    ''' natural sorting of a list of strings with numbers ['a0','a1','a2',...,'a10','a11',...] '''
    myList.sort(key=natural_keys)
#
#
#
#%% indexing functions
#
# indices in the form (row, col) => pointTuple[Trow]= pointTuple[0]= row
#Trow=0
#Tcol=1
#
def indices_rectangle(Rows2look,Cols2look):
    ''' list of tuples covering the rectangle [Rows2look,Cols2look]'''
    indices=[]
    #
    for iRow in Rows2look:
        for iCol in Cols2look:
            indices += [(iRow,iCol)]
    return indices
#
#def my_indices_cuboid(Imgs2look,Rows2look,Cols2look):
#    indices=[]
#    #
#    for iImg in Imgs2look:    
#        for iRow in Rows2look:
#            for iCol in Cols2look:
#                indices += [(iImg,iRow,iCol)]
#    return indices
# 
#def my_indices_circle(centerT, radius, inROITArray): 
#    indices=[]
#    radius= radius+0.0
#    #
#    for thispointT in inROITArray:
#        thisDistance = (centerT[Trow] - thispointT[Trow])**2 +0.0
#        thisDistance += (centerT[Tcol] - thispointT[Tcol])**2 +0.0
#        thisDistance= numpy.sqrt(thisDistance)
#        if (thisDistance <= radius):
#           indices += [thispointT] 
#    return indices  
#   
#%% file functions
#
def read_csv(filenamepath):
    ''' read numerical data from csv '''
    my_data= numpy.genfromtxt(filenamepath, delimiter= ',')
    return my_data
# 
def write_csv(filenamepath, data):
    ''' write numerical data from csv '''
    numpy.savetxt(filenamepath, data, fmt='%f', delimiter=",")
#
def read_tst(filenamepath):
    ''' read text from tab-separated-texts file '''
    #my_data= numpy.genfromtxt(filenamepath, delimiter= '\t', dtype='string')
    my_data= numpy.genfromtxt(filenamepath, delimiter= '\t', dtype=str)
    return my_data
#
def write_tst(filenamepath, data):
    ''' write text in tab-separated-texts file '''
    numpy.savetxt(filenamepath, data, delimiter= '\t', fmt='%s')
#
def read_bin_uint8(filenamepath):
    ''' read data from binary file '''
    thisfile= open(filenamepath, 'r')
    fileContent=numpy.fromfile(thisfile, dtype=numpy.uint8); 
    thisfile.close()
    return fileContent
#
#def read_binary(filenamepath):
#    ''' read data from binary file '''
#    thisfile= open(filenamepath, 'rb')
#    fileContent=thisfile.read()
#    thisfile.close()
#    return fileContent
#
def read_1xh5(filenamepath, path_2read):
    ''' read h5 file: data in path_2read '''
    my5hfile= h5py.File(filenamepath, 'r')
    myh5dataset=my5hfile[path_2read]
    my_data_2D= numpy.array(myh5dataset)
    my5hfile.close()
    return my_data_2D
#
def write_1xh5(filenamepath, data2write, path_2write):
    ''' write h5 file: data in path_2write '''
    my5hfile= h5py.File(filenamepath, 'w')
    my5hfile.create_dataset(path_2write, data=data2write) 
    my5hfile.close()
#
def read_2xh5(filenamepath, path1_2read, path2_2read):
    ''' read 2xXD h5 file (paths_2read: '/data/','/reset/' ) '''
    my5hfile= h5py.File(filenamepath, 'r')
    myh5dataset=my5hfile[path1_2read]
    my_data1_2D= numpy.array(myh5dataset)
    myh5dataset=my5hfile[path2_2read]
    my_data2_2D= numpy.array(myh5dataset)
    my5hfile.close()
    return (my_data1_2D,my_data2_2D) 
#
def write_2xh5(filenamepath, data1_2write, path1_2write, data2_2write, path2_2write):
    ''' write 2xXD h5 file (paths_2write: '/data/','/reset/' ) '''
    my5hfile= h5py.File(filenamepath, 'w')
    my5hfile.create_dataset(path1_2write, data=data1_2write) #
    my5hfile.create_dataset(path2_2write, data=data2_2write) #
    my5hfile.close()
#
def list_files(folderpath, expectedPrefix, expectedSuffix):
    ''' look for files in directory having the expected prefix and suffix ('*' to have any) '''
    anyfix='*'
    allFileNameList=os.listdir(folderpath)
    dataFileNameList=[]
    for thisFile in allFileNameList:
        if (expectedPrefix==anyfix)&(expectedSuffix==anyfix):
            dataFileNameList.append(thisFile)
        elif (expectedPrefix==anyfix)&(expectedSuffix!=anyfix)&(thisFile.endswith(expectedSuffix)):
            dataFileNameList.append(thisFile)
        elif (expectedPrefix!=anyfix)&(expectedSuffix==anyfix)&(thisFile.startswith(expectedPrefix)):
            dataFileNameList.append(thisFile)
        elif (expectedPrefix!=anyfix)&(expectedSuffix!=anyfix)& \
                (thisFile.endswith(expectedSuffix))&(thisFile.startswith(expectedPrefix)):
            dataFileNameList.append(thisFile)
    sort_nicely(dataFileNameList) # natural sorting
    return dataFileNameList
#    
#
#
#%% GUI
def my_GUIwin_bring2front(win):
    ''' bring the GUI window to the foreground '''
    win.lift()
    win.attributes('-topmost', True)
    win.attributes('-topmost', False)
#    
def my_GUIwin_text(arguments):
    '''
    create a GUI window
    arguments should  be label0, default_val0, label1, default_val1,  ...
    label and default_val are strings
    '''
    #    
    win=tkinter.Tk()
    my_GUIwin_bring2front(win)    
    #
    Nargs= len(arguments)//2
    VariableList=[]
    #
    for iitem in range(Nargs):
        ilabel= 2*iitem
        idefault= 1+2*iitem
        #
        thisLabel=tkinter.Label(win, text=arguments[ilabel])
        thisLabel.grid(row=iitem, column=0)
        #
        thisVariable=tkinter.StringVar()
        thisVariable.set(arguments[idefault])
        thisField= tkinter.Entry(win, textvariable=thisVariable, width=100)
        VariableList += [thisVariable]                
        thisField.grid(row=iitem, column=1)
    #
    execButton= tkinter.Button(win, text="execute")
    execButton.grid(row=Nargs, column=1)
    #
    ValuesList= []
    #
    def my_GUIexec():
        ''' GUI exec button: saves variable values and close window '''
        for iitem in range(Nargs):
            ValuesList.append( VariableList[iitem].get() )
        win.destroy()
    #
    execButton.configure(command= my_GUIexec)
    #
    win.mainloop()
    return(ValuesList)
#
#
#
#%% plots
def color_y_axis(ax, color):
    '''Color your axes '''
    for t in ax.get_yticklabels():
        t.set_color(color)
    return None
#
def plot_1D(arrayX, arrayY, label_x,label_y,label_title):
    ''' 1D scatter plot ''' 
    fig = matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(arrayX, arrayY, 'o', fillstyle='none')
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title(label_title)    
    matplotlib.pyplot.show(block=False)
    return (fig)
#
def plot_multi1D(arrayX, arrayY_2D, infoSets_List, label_x,label_y,label_title, showLineFlag):
    """ plot1D multiple datasets (arrayX[:], arrayY_2D[i,:]) , identified by infoSets_List[i] """
    fig = matplotlib.pyplot.figure()
    (Nsets,Npoints)= arrayY_2D.shape
    for iSet, thisSet in enumerate(infoSets_List):
        if showLineFlag: matplotlib.pyplot.plot(arrayX, arrayY_2D[iSet,:],'o-', fillstyle='none')
        else: matplotlib.pyplot.plot(arrayX, arrayY_2D[iSet,:],'o', fillstyle='none')
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title(label_title)   
    matplotlib.pyplot.legend(infoSets_List, loc='upper right')
    matplotlib.pyplot.show(block=False) 
    return fig
#
def plot_1D_2scales(dataX, dataY0, dataY1, labelX, labelY0, labelY1, labelTitle):
    ''' scatter plot dataY0/1 on left/right axes'''
    colY0='blue'
    colY1='red'
    #
    fig, ax1 = matplotlib.pyplot.subplots()
    ax2 = ax1.twinx()
    ax1.plot(dataX, dataY0, 'o', color=colY0, fillstyle='none')
    ax1.set_xlabel(labelX)
    ax1.set_ylabel(labelY0,color=colY0)
    ax2.plot(dataX, dataY1, 'x', color=colY1)
    ax2.set_ylabel(labelY1, color=colY1)
    matplotlib.pyplot.title(labelTitle)
    color_y_axis(ax1, colY0)
    color_y_axis(ax2, colY1)
    matplotlib.pyplot.show(block=False)
    return (fig, ax1, ax2)
#
def plot_2D(array2D, label_x,label_y,label_title, invertx_flag, ErrBelow):
    ''' 2D image , mark as error (white) the values << ErrBelow''' 
    cmap = matplotlib.pyplot.cm.jet
    cmap.set_under(color='white')    
    fig = matplotlib.pyplot.figure()
    matplotlib.pyplot.imshow(array2D, interpolation='none', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title(label_title)    
    matplotlib.pyplot.colorbar()
    if (invertx_flag==True): matplotlib.pyplot.gca().invert_xaxis();  
    matplotlib.pyplot.show(block=False)
    return (fig) 
#
def plot_2D_stretched(array2D, label_x,label_y,label_title, invertx_flag, ErrBelow):
    ''' 2D image (stretched), mark as error (white) the values << ErrBelow''' 
    cmap = matplotlib.pyplot.cm.jet
    cmap.set_under(color='white')    
    fig = matplotlib.pyplot.figure()
    matplotlib.pyplot.imshow(array2D, interpolation='none', aspect='auto', cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title(label_title)    
    matplotlib.pyplot.colorbar()
    if (invertx_flag==True): matplotlib.pyplot.gca().invert_xaxis();  
    matplotlib.pyplot.show(block=False)
    return (fig)    
#       
#def my_surf(X,Y,Z,label_x,label_y,label_title):
#    '''X,Y,Z (each 1D) => surf plot'''
#    fig = matplotlib.pyplot.figure()
#    ax = fig.add_subplot(111, projection='3d')
#    Axes3D.plot_trisurf(ax,X,Y,Z)
#    matplotlib.pyplot.xlabel(label_x)
#    matplotlib.pyplot.ylabel(label_y)
#    matplotlib.pyplot.title(label_title)
#    matplotlib.pyplot.show()
#    return (fig,ax)
#
#def my_scatter3D(X,Y,Z,label_x,label_y,label_title):
#    '''X,Y,Z (each 1D) => 3D scatter plot'''
#    fig = matplotlib.pyplot.figure()
#    ax = fig.add_subplot(111, projection='3d')
#    Axes3D.scatter(ax, X,Y,Z, zdir='z', s=len(X), c='b', depthshade=True)
#    matplotlib.pyplot.xlabel(label_x)
#    matplotlib.pyplot.ylabel(label_y)
#    matplotlib.pyplot.title(label_title)
#    matplotlib.pyplot.show()
#    return (fig,ax)
#
def plot_histo2D(X,Y, nbinsX,nbinsY, label_x,label_y,label_title,ErrBelow):
    ''' 2D histogram plot, set to white anything < ErrBelow (e.g. 0.1)'''
    cmap = matplotlib.pyplot.cm.jet
    cmap.set_under(color='white')    
    fig = matplotlib.pyplot.figure()
    matplotlib.pyplot.hist2d(X,Y, bins=[nbinsX,nbinsY], cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title(label_title)    
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.show(block=False)
    return (fig)    
#
#
