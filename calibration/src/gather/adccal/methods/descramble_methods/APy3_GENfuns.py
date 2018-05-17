# -*- coding: utf-8 -*-
"""
general functions and fitting
"""
#%% imports
#
import numpy
import os # list files in a folder
import re # to sort naturally

#%% constant
VERYBIGNUMBER= 1e18


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


def convert_britishBits_Ar(BritishBitArray):
    " 0=>1 , 1=>0 "
    HumanReadableBitArray=1-BritishBitArray
    return HumanReadableBitArray


def convert_int_2_2xuint8(int2convert):
    ''' 259 => (1,3) '''
    out_uint8_MSB= int2convert//256
    out_uint8_LSB= int2convert%256
    return (out_uint8_MSB, out_uint8_LSB)


def convert_2xuint8_2_int(MSByte,LSByte):
    ''' 259 <= (1,3) '''
    out_int= (256*MSByte)+LSByte
    return (out_int)


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


def convert_4xuint8_2_int(MSByte, mid2SByte, mid1SByte, LSByte):
    ''' 259 <= (0,0,1,3) '''
    out_int= ((2**24)*MSByte)+ ((2**16)*mid2SByte)+ ((2**8)*mid1SByte)+ LSByte
    return (out_int)


def convert_hex_byteSwap_Ar(data2convert_Ar):
    ''' interpret the ints in an array as 16 bits. byte-swap them: (byte0,byte1) => (byte1,byte0) '''
    aux_bitted= convert_uint_2_bits_Ar(data2convert_Ar,16).astype('uint8')
    aux_byteinverted= numpy.zeros_like(aux_bitted).astype('uint8')
    #
    aux_byteinverted[...,0:8]= aux_bitted[...,8:16]
    aux_byteinverted[...,8:16]= aux_bitted[...,0:8]
    data_ByteSwapped_Ar=convert_bits_2_int_Ar(aux_byteinverted)
    return (data_ByteSwapped_Ar)

#%% matlab-like function
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


#%% sorting list in natural form
''' natural sorting of a list of strings with numbers ['a0','a1','a2',...,'a10','a11',...] '''
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    ''' thisIsaList.sort(key=natural_keys)'''
    return [atoi(c) for c in re.split('(\d+)', text)]


def sort_nicely(myList):
    ''' natural sorting of a list of strings with numbers ['a0','a1','a2',...,'a10','a11',...] '''
    myList.sort(key=natural_keys)


#%% indexing functions

# indices in the form (row, col) => pointTuple[Trow]= pointTuple[0]= row
#Trow=0
#Tcol=1

def indices_rectangle(Rows2look,Cols2look):
    ''' list of tuples covering the rectangle [Rows2look,Cols2look]'''
    indices=[]
    #
    for iRow in Rows2look:
        for iCol in Cols2look:
            indices += [(iRow,iCol)]
    return indices

#%% file functions

def read_csv(filenamepath):
    ''' read numerical data from csv '''
    my_data= numpy.genfromtxt(filenamepath, delimiter= ',')
    return my_data


def write_csv(filenamepath, data):
    ''' write numerical data from csv '''
    numpy.savetxt(filenamepath, data, fmt='%f', delimiter=",")


def read_tst(filenamepath):
    ''' read text from tab-separated-texts file '''
    my_data= numpy.genfromtxt(filenamepath, delimiter= '\t', dtype=str)
    return my_data


def write_tst(filenamepath, data):
    ''' write text in tab-separated-texts file '''
    numpy.savetxt(filenamepath, data, delimiter= '\t', fmt='%s')


def read_bin_uint8(filenamepath):
    ''' read uint8 data from binary file '''
    with open(filenamepath) as f:
        fileContent = numpy.fromfile(f, dtype = numpy.uint8)
    return fileContent

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
