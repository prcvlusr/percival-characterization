"""
Descramble 2xh5 files from OdinDAQ (raw), from the raw
(bit-scrambled, pixel-disordered, missing RefCol,
OdinDAQ-further-scrambled) format to a data format
readable in gather.
mezzanine Firmware >= 2018.06.18_AY (same subnet)
"""
import sys
import os  # to list files in a directory
import time  # to have time
import h5py
import numpy as np
from colorama import init, Fore

import matplotlib
import matplotlib.pyplot

import __init__  # noqa F401
import utils

from descramble_base import DescrambleBase
matplotlib.use('TkAgg')

# from P2M manual : pixel scrambling
N_xcolArray = 4
N_ncolArray = 8
colArray = np.arange(N_xcolArray * N_ncolArray).reshape(
    (N_xcolArray, N_ncolArray)).transpose()
colArray = np.fliplr(colArray)  # in the end it is colArray[ix,in]
#
# this gives the (iADC,iCol) indices of a pixel in a Rowblk,
# given its sequence in the streamout
ADCcolArray_1DA = []
for i_n in range(N_ncolArray):
    for i_ADC in range(7)[::-1]:
        for i_x in range(N_xcolArray):
            ADCcolArray_1DA += [(i_ADC, colArray[i_n, i_x])]
ADCcolArray_1DA = np.array(ADCcolArray_1DA)
# to use this: for ipix in range(32*7): (ord_ADC,ord_col)=ADCcolArray_1DA[ipix]

# from P2M manual : pad order
iG = 0
iH0 = np.arange(21+1, 0+1-1, -1)
iH1 = np.arange(22+21+1, 22+0+1-1, -1)
iP2M_ColGrp = np.append(np.array(iG), iH0)
iP2M_ColGrp = np.append(iP2M_ColGrp, iH1)


# NOO functions
def dot():
    '''print a dot '''
    sys.stdout.write(".")
    sys.stdout.flush()  # print it now


def read_2xh5(filenamepath, path1_2read, path2_2read):
    ''' read 2xXD h5 file (paths_2read: '/data/','/reset/' ) '''
    with h5py.File(filenamepath, "r", libver='latest') as my5hfile:
        my_data1_2D = np.array(my5hfile[path1_2read])
        my_data2_2D = np.array(my5hfile[path2_2read])
        my5hfile.close()
    return (my_data1_2D, my_data2_2D)


def write_2xh5(filenamepath,
               data1_2write, path1_2write,
               data2_2write, path2_2write):
    ''' write 2xXD h5 file (paths_2write: '/data/','/reset/' ) '''
    with h5py.File(filenamepath, "w", libver='latest') as my5hfile:
        my5hfile.create_dataset(path1_2write, data=data1_2write)
        my5hfile.create_dataset(path2_2write, data=data2_2write)
        my5hfile.close()


def convert_uint_2_bits_Ar(in_intAr, Nbits):
    ''' convert (numpyarray of uint to array of Nbits bits)
    for many bits in parallel '''
    inSize_T = in_intAr.shape
    in_intAr_flat = in_intAr.flatten()
    out_NbitAr = np.zeros((len(in_intAr_flat), Nbits))
    for iBits in range(Nbits):
        out_NbitAr[:, iBits] = (in_intAr_flat >> iBits) & 1
    out_NbitAr = out_NbitAr.reshape(inSize_T+(Nbits,))
    return out_NbitAr


def convert_bits_2_int_Ar(in_bitAr):
    ''' convert (numpyarray of [... , ... , Nbits] to
    array of [... , ... ](int) for many values in parallel'''
    inSize_T = in_bitAr.shape
    Nbits = inSize_T[-1]
    outSize_T = inSize_T[0:-1]
    out_intAr = np.zeros(outSize_T)
    power2Matrix = (2**np.arange(Nbits)).astype(int)
    aux_powerMatr = power2Matrix * np.ones(inSize_T).astype(int)
    totalVector_xDAr = np.sum(in_bitAr*aux_powerMatr, axis=len(inSize_T)-1)
    out_intAr = totalVector_xDAr.astype(int)
    return out_intAr


def convert_hex_byteSwap_Ar(data2convert_Ar):
    ''' interpret the ints in an array as 16 bits.
    byte-swap them: (byte0,byte1) => (byte1,byte0) '''
    aux_bitted = convert_uint_2_bits_Ar(data2convert_Ar, 16).astype('uint8')
    aux_byteinverted = np.zeros_like(aux_bitted).astype('uint8')
    #
    aux_byteinverted[..., 0:8] = aux_bitted[..., 8:16]
    aux_byteinverted[..., 8:16] = aux_bitted[..., 0:8]
    data_ByteSwapped_Ar = convert_bits_2_int_Ar(aux_byteinverted)
    return (data_ByteSwapped_Ar)


def convert_britishBits_Ar(BritishBitArray):
    " 0=>1 , 1=>0 "
    HumanReadableBitArray = 1 - BritishBitArray
    return HumanReadableBitArray


def reorder_pixels_GnCrsFn(disord_4DAr, NADC, NColInRowBlk):
    ''' P2M pixel reorder for a image:
    (NGrp,NDataPads,NADC*NColInRowBlk,3),disordered =>
    (NGrp,NDataPads,NADC,NColInRowBlk,3),ordered '''
    (aux_NGrp, aux_NPads, aux_pixInBlk, auxNGnCrsFn) = disord_4DAr.shape
    ord_5DAr = np.zeros((aux_NGrp, aux_NPads, NADC, NColInRowBlk,
                         auxNGnCrsFn)).astype('uint8')
    aux_pixOrd_padDisord_5DAr = np.zeros((aux_NGrp, aux_NPads, NADC,
                                          NColInRowBlk,
                                          auxNGnCrsFn)).astype('uint8')
    # pixel reorder inside each block
    for ipix in range(NADC * NColInRowBlk):
        (ord_ADC, ord_Col) = ADCcolArray_1DA[ipix]
        aux_pixOrd_padDisord_5DAr[
            :, :, ord_ADC, ord_Col,
            :] = disord_4DAr[:, :, ipix, :]
    # ColGrp order from chipscope to P2M
    for iColGrp in range(aux_NPads):
        ord_5DAr[
            :, iColGrp, :, :,
            :] = aux_pixOrd_padDisord_5DAr[:, iP2M_ColGrp[iColGrp],
                                           :, :, :]
    return ord_5DAr


def percDebug_plot_6x2D(GnSmpl, CrsSmpl,
                        FnSmpl, GnRst,
                        CrsRst, FnRst,
                        label_title, ErrBelow):
    """ 2D plot of Smpl/Rst, Gn/Crs/Fn, white values << ErrBelow """
    cmap = matplotlib.pyplot.cm.jet
    cmap.set_under(color='white')
    # fig = matplotlib.pyplot.figure(figsize=(18,12))
    fig = matplotlib.pyplot.figure()
    fig.canvas.set_window_title(label_title)
    label_x = "col"
    label_y = "row"
    #
    matplotlib.pyplot.subplot(2, 3, 1)
    matplotlib.pyplot.imshow(GnSmpl, interpolation='none',
                             cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Sample Gain')
    matplotlib.pyplot.clim(0, 3)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis()
    #
    matplotlib.pyplot.subplot(2, 3, 2)
    matplotlib.pyplot.imshow(CrsSmpl, interpolation='none',
                             cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Sample Coarse')
    matplotlib.pyplot.clim(0, 31)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis()
    #
    matplotlib.pyplot.subplot(2, 3, 3)
    matplotlib.pyplot.imshow(FnSmpl, interpolation='none',
                             cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Sample Fine')
    matplotlib.pyplot.clim(0, 255)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis()
    #
    matplotlib.pyplot.subplot(2, 3, 4)
    matplotlib.pyplot.imshow(GnRst, interpolation='none',
                             cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Reset Gain (not relevant)')
    matplotlib.pyplot.clim(0, 3)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis()
    #
    matplotlib.pyplot.subplot(2, 3, 5)
    matplotlib.pyplot.imshow(CrsRst, interpolation='none',
                             cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Reset Coarse')
    matplotlib.pyplot.clim(0, 31)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis()
    #
    matplotlib.pyplot.subplot(2, 3, 6)
    matplotlib.pyplot.imshow(FnRst, interpolation='none',
                             cmap=cmap, vmin=ErrBelow)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.title('Reset Fine')
    matplotlib.pyplot.clim(0, 255)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis()
    # matplotlib.pyplot.show(block=False)
    matplotlib.pyplot.show()
    return fig


# OO methods
class Descramble(DescrambleBase):
    """ Descample tcpdump data
    """

    def __init__(self, **kwargs):  # noqa F401

        super().__init__(**kwargs)

        # in the method and the method section of the config file the following
        # parameters have to be defined:
        #   input_fnames
        #   save_file
        #   output_fname
        #   clean_memory
        #   verbose
        #   debug

        # useful constants
        # negative value usable to track Gn/Crs/Fn from missing pack
        self._err_int16 = -256
        # self._err_blw = -0.1
        # forbidden uint16, usable to track "pixel" from missing pack
        self._err_dlsraw = 65535
        self._i_smp = 0
        self._i_rst = 1
        self._i_gn = 0
        self._i_crs = 1
        self._i_fn = 2

        # general constants for a P2M system
        self._n_smpl_rst = 2  # 0=Rst, 1=Smpl
        self._n_subframe = 2  # 0 or 1
        self._n_pad = 45
        self._n_data_pads = self._n_pad - 1  # 44
        self._n_adc = 7
        self._n_row_in_blk = self._n_adc  # 7
        self._n_grp = 212
        self._n_col_in_blk = 32
        self._n_pixs_in_blk = (self._n_col_in_blk * self._n_row_in_blk)  # 224
        self._n_bits_in_pix = 15
        self._n_gn_crs_fn = 3

        # tcpdump-related constants
        # excess Bytes at the beginning of tcpdump file
        self._excess_bytesinfront = 24
        # UDPacket content in Byte (excluding header)
        self._gooddata_size = 4928
        # UDPacket content in Byte (including header)
        self._fullpack_size = 5040
        self._header_size = self._fullpack_size - self._gooddata_size  # 112
        self._img_counter = 88 - self._excess_bytesinfront  # also+1
        self._pack_counter = 90 - self._excess_bytesinfront  # also+1
        #
        self._datatype_counter = self._img_counter - 4
        self._subframe_counter = self._img_counter - 3

        # 1 RowGrp (7x32x44pixel) in in 4 UDPacket
        self._n_packs_in_rowgrp = 4
        # 1Img (Smpl+Rst)= 1696 UDPacket, id by (datatype,subframe,n_pack)
        self.n_packs_in_img = (self._n_packs_in_rowgrp *
                               self._n_grp * self._n_smpl_rst)
        # thus packet count is never > 423
        self._max_n_pack = 423

        self._result_data = None

    def run(self):
        """
        descrambles h5-odinDAQ(raw) files, save to h5 in standard format

        Here is how data are scrambled:

        1a) the chips send data out interleaving RowGroups
            (7row x (32 Col x 45 pads) ) from Sample/Reset, as:
            Smpl, Smpl,   Smpl, Rst, Smpl, Rst, ... , Smpl, Rst,   Rst, Rst
        1b) the position of pixels (pix0/1/2 in the next point) is mapped to
            the (7row x 32 Col) block according to the adc_cols lost
        1c) inside a (7row x 32 Col) block, the data are streamed out as:
            bit0-of-pix0, bit0-of-pix1, bit0-of-pix2, ... , bit0-of-pix1, ...
        1d) all the data coming from the sensor are bit-inverted: 0->1; 1->0
        2a) the mezzanine takes the data coming from each (7 x 32) block,
            and add a "0" it in front of every 15 bits:
            xxx xxxx xxxx xxxx  yyy ... => 0xxx xxxx xxxx xxxx 0yyy ...
        2b) the mezzanine takes the data coming from a 44x (7 x 32) blocks
            (this corresponds to a complete RowCrp, ignoring RefCol )
            and interleaves 32 bits at a time:
            32b-from-pad1, 32b-from-pad2, ... , 32b-from-pad44,
            next-32b-from-pad1, next-32b-from-pad2, ...
        2c) the mezzanine packs the bits in Bytes, and the Bytes in UDPackets
            4 UDPackets contain all the bits of a 44x (7 x 32) Rowgrp.
            A complete image (Smpl+Rst) = 1696 UDPackets
            each UDPack has 4928Byte of information, and 112Byte of header.
            each UDPack is univocally identified by the header:
            - which Img (frame) the packet belongs to
            - datatype: whether it is part of a Smpl/Rst (respect. 1 or 0)
            - subframenumber (0 or 1)
            - packetnumber (0:423), which determines the RowGrp the
            packet's data goes into
            there are 1696 packets in an image; a packet is identified by the
            triplet (datatype,subframenumber,packetnumber)
        3a) the packets are sent from 2 mezzanine links (some on one link, some
            on the other), and are saved to 2 h5 files by odinDAQ
        4a) OdinDAQ byte-swaps every 16-bit sequence (A8 B8 becomes B8 A8)
        5a) OdinDAQ rearranges the 4 quarters of each rowblock
        6a) OdinDAQ seems to invert Smpl and Rst

        Args:
            filenamepath_in0/1: name of scrambled h5 files
            output_fname: name of h5 descrambled file to generate
            save_file/debugFlag/clean_memory/verbose: no need to explain

        Returns:
            creates a h5 file (if save_file) in DLSraw standard format
                no explicit return()
        """
        iSmpl = self._i_smp
        iRst = self._i_rst
        iGn = self._i_gn
        iCrs = self._i_crs
        iFn = self._i_fn

        NSmplRst = self._n_smpl_rst
        NADC = self._n_adc
        NColInBlock = self._n_col_in_blk
        NRowInBlock = self._n_row_in_blk
        NGrp = self._n_grp
        NPad = self._n_pad
        NDataPads = NPad - 1

        ERRDLSraw = self._err_dlsraw
        ERRint16 = self._err_int16

        init(autoreset=True)  # every colorama starts from standard

        start_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        print(Fore.BLUE + "Script beginning at {}".format(start_time))
        # print(self.__dict__.keys())
        self._report_arguments()
        # - - -
        #
        # read h5 files
        print(Fore.BLUE + "reading files")
        if (os.path.isfile(self._input_fnames[0])):
            (data_fl0_Smpl, data_fl0_Rst) = read_2xh5(self._input_fnames[0],
                                                      '/data/', '/reset/')
        else:
            msg = "unable to find {}".format(self._input_fnames[0])
            print(Fore.RED + msg)
            return()

        if (os.path.isfile(self._input_fnames[1])):
            (data_fl1_Smpl, data_fl1_Rst) = read_2xh5(self._input_fnames[1],
                                                      '/data/', '/reset/')
        else:
            msg = "unable to find {}".format(self._input_fnames[1])
            print(Fore.RED + msg)
            return()

        (NImg_fl0, auxNRow, auxNCol) = data_fl0_Smpl.shape
        (NImg_fl1, auxNRow, auxNCol) = data_fl1_Smpl.shape
        auxNImg = NImg_fl0 + NImg_fl0
        print(Fore.GREEN + "{0}+{1} Img read from files".format(NImg_fl0,
                                                                NImg_fl0))
        # - - -
        #
        # combine in one array: Img0-from-fl0, Img0-from-fl1, Img1-from-fl0...
        scrmbl_Smpl = np.zeros((auxNImg, auxNRow, auxNCol)).astype('uint16')
        scrmbl_Rst = np.zeros_like(scrmbl_Smpl).astype('uint16')
        for iImg in range(auxNImg):
            if((iImg % 2 == 0) & ((iImg // 2) < NImg_fl0)):
                scrmbl_Smpl[iImg, :, :] = data_fl0_Smpl[iImg // 2, :, :]
                scrmbl_Rst[iImg, :, :] = data_fl0_Rst[iImg // 2, :, :]
            if((iImg % 2 == 1) & ((iImg // 2) < NImg_fl1)):
                scrmbl_Smpl[iImg, :, :] = data_fl1_Smpl[iImg // 2, :, :]
                scrmbl_Rst[iImg, :, :] = data_fl1_Rst[iImg // 2, :, :]
        if self._clean_memory:
            del data_fl0_Smpl
            del data_fl0_Rst
            del data_fl1_Smpl
            del data_fl1_Rst
        # - - -
        #
        # solving 4a DAQ-scrambling: byte swap in hex (By0,By1) => (By1,By0)
        msg = "solving DAQ-scrambling: byte-swapping (it might take a while)"
        print(Fore.BLUE + msg)

        dataSmpl_ByteSwap = np.zeros_like(scrmbl_Smpl).astype('uint16')
        dataRst_ByteSwap = np.zeros_like(scrmbl_Smpl).astype('uint16')
        for iImg in range(auxNImg):
            dataSmpl_ByteSwap[iImg, :, :] = convert_hex_byteSwap_Ar(
                scrmbl_Smpl[iImg, :, :])
            dataRst_ByteSwap[iImg, :, :] = convert_hex_byteSwap_Ar(
                scrmbl_Rst[iImg, :, :])
            dot()
        print(" ")
        if self._clean_memory:
            del scrmbl_Smpl
            del scrmbl_Rst
        # - - -
        #
        # solving DAQ-scrambling: "pixel" reordering
        msg = "solving DAQ-scrambling: reordering subframes"
        print(Fore.BLUE + msg)

        def convert_OdinDAQ_2_Mezzanine(shotIn):
            (auxNImg, auxNRow, auxNCol) = shotIn.shape
            aux_reord = shotIn.reshape((auxNImg, NGrp, NADC, auxNCol))
            aux_reord = aux_reord.reshape(
                (auxNImg, NGrp, NADC, 2, auxNCol // 2))
            aux_reord = np.transpose(
                aux_reord, (0, 1, 3, 2, 4))
            # auxNImg,NGrp, 2left/right,NADC,auxNCol//2
            aux_reord = aux_reord.reshape(
                (auxNImg, NGrp, 2, NADC * auxNCol // 2))
            # auxNImg,NGrp,2left/right,NADC*auxNCol//2
            aux_reord = aux_reord.reshape(
                (auxNImg, NGrp, 2, 2, NADC * auxNCol // 4))
            # auxNImg,NGrp,2left/right,2up/down,NADC*auxNCol//4
            aux_reordered = np.ones((
                auxNImg, NGrp, 4,
                NADC * auxNCol // 4)).astype('uint16') * ERRDLSraw
            aux_reordered[:, :, 0, :] = aux_reord[:, :, 0, 0, :]
            aux_reordered[:, :, 1, :] = aux_reord[:, :, 1, 0, :]
            aux_reordered[:, :, 2, :] = aux_reord[:, :, 0, 1, :]
            aux_reordered[:, :, 3, :] = aux_reord[:, :, 1, 1, :]
            aux_reordered = aux_reordered.reshape(
                (auxNImg, NGrp, NADC * auxNCol))
            aux_reordered = aux_reordered.reshape(
                (auxNImg, NGrp, NADC, auxNCol))
            aux_reordered = aux_reordered.reshape(
                (auxNImg, NGrp * NADC, auxNCol))
            return aux_reordered
        #
        dataSmpl_asMezz = convert_OdinDAQ_2_Mezzanine(dataSmpl_ByteSwap)
        dataRst_asMezz = convert_OdinDAQ_2_Mezzanine(dataRst_ByteSwap)
        if self._clean_memory:
            del dataSmpl_ByteSwap
            del dataRst_ByteSwap
        # - - -
        #
        # solving mezzanine-scrambling
        msg = "solving mezzanine&chip-scrambling: preparation"
        print(Fore.BLUE + msg)

        dataSmpl_2_srcmbl = dataSmpl_asMezz
        dataRst_2_srcmbl = dataRst_asMezz
        data_2_srcmbl_norefCol = np.ones(
            (auxNImg, NSmplRst,
             auxNRow, auxNCol)).astype('uint16') * ((2**16) - 1)
        data_2_srcmbl_norefCol[:, iSmpl, :, :] = dataSmpl_2_srcmbl
        data_2_srcmbl_norefCol[:, iRst, :, :] = dataRst_2_srcmbl
        data_2_srcmbl_norefCol = data_2_srcmbl_norefCol.reshape(
            (auxNImg, NSmplRst, NGrp, NADC, auxNCol))
        #
        # track missing packets: False==RowGrp OK;
        # True== packet(s) missing makes rowgroup moot
        # (1111 1111 1111 1111 instead of 0xxx xxxx xxxx xxxx)
        MissingRowGrpTracker = np.ones((auxNImg, NSmplRst, NGrp)).astype(bool)
        MissingRowGrpTracker = data_2_srcmbl_norefCol[
            :, :, :, 0, 0] == ERRDLSraw
        # - - -
        #
        # descramble proper
        msg = "solving mezzanine&chip-scrambling: pixel descrambling"
        print(Fore.BLUE + msg)
        multiImg_aggr_withRef = np.zeros(
           (auxNImg, NSmplRst, NGrp, NPad,
            NADC * NColInBlock, 3)).astype('uint8')

        for iImg in range(auxNImg):
            dot()
            auxil_thisImg = data_2_srcmbl_norefCol[
                iImg, :, :, :, :].reshape((NSmplRst, NGrp, NADC*auxNCol))
            # (NSmplRst,NRowGrpInShot,NADC*auxNCol)

            auxil_thisImg = auxil_thisImg.reshape(
                (NSmplRst, NGrp,
                 NADC * auxNCol // (NDataPads * 2), NDataPads, 2))
            # 32bit=2"pix" from 1st pad, 2"pix" from 2nd pad, ...

            auxil_thisImg = np.transpose(auxil_thisImg, (0, 1, 3, 2, 4))
            # NSmplRst,NGrp,NDataPads,NADC*auxNCol//(NDataPads*2),2"pix")

            auxil_thisImg = auxil_thisImg.reshape((NSmplRst, NGrp, NDataPads,
                                                   NADC*auxNCol//NDataPads))
            #
            # bit, remove head 0, concatenate and reorder
            auxil_thisImg_16bitted = convert_uint_2_bits_Ar(
                auxil_thisImg, 16)[:, :, :, :, ::-1].astype('uint8')
            # NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads,15bits

            auxil_thisImg_bitted = auxil_thisImg_16bitted[:, :, :, :, 1:]
            # NSmplRst,NGrp,NDataPads,NADC*auxNCol//NDataPads,15bits

            auxil_thisImg_bitted = auxil_thisImg_bitted.reshape(
                (NSmplRst, NGrp, NDataPads, NADC * auxNCol * 15 // NDataPads))
            auxil_thisImg_bitted = auxil_thisImg_bitted.reshape(
                (NSmplRst, NGrp, NDataPads, 15, NADC * NColInBlock))

            # BBT: 0=>1, 1=>0
            auxil_thisImg_bitted = np.transpose(auxil_thisImg_bitted,
                                                (0, 1, 2, 4, 3))
            # (NSmplRst,NGrp,NDataPads,NPixsInRowBlk,15)
            auxil_thisImg_bitted = convert_britishBits_Ar(auxil_thisImg_bitted)
            #
            auxil_thisImg_aggr = np.zeros(
                (NSmplRst, NGrp, NDataPads,
                 NADC * NColInBlock, 3)).astype('uint8')
            #
            # binary aggregate Gn bit(0,1)
            aux_bits2descr = 2
            aux_frombit = 0
            aux_tobit_puls1 = 1 + 1
            power2Matrix = (2 ** np.arange(aux_bits2descr))[::-1].astype(int)
            aux_powerMatr = power2Matrix * np.ones(
                (NSmplRst, NGrp, NDataPads, NADC * NColInBlock,
                 len(power2Matrix))).astype(int)
            totalVector_xDAr = np.sum(auxil_thisImg_bitted[
                :, :, :, :,
                aux_frombit:aux_tobit_puls1] * aux_powerMatr, axis=4)
            auxil_thisImg_aggr[
                :, :, :, :, iGn] = totalVector_xDAr.astype('uint8')
            #
            # binary aggregate Crs bit(10,11,12,13,14)
            aux_bits2descr = 5
            aux_frombit = 10
            aux_tobit_puls1 = 14 + 1
            power2Matrix = (2**np.arange(aux_bits2descr))[::-1].astype(int)
            aux_powerMatr = power2Matrix * np.ones(
                (NSmplRst, NGrp, NDataPads, NADC*NColInBlock,
                 len(power2Matrix))).astype(int)
            totalVector_xDAr = np.sum(auxil_thisImg_bitted[
                :, :, :, :,
                aux_frombit:aux_tobit_puls1] * aux_powerMatr, axis=4)
            auxil_thisImg_aggr[:, :, :, :, iCrs] = totalVector_xDAr
            #
            # binary aggregate Fn bit(2,3,4,5,6,7,8,9)
            aux_bits2descr = 8
            aux_frombit = 2
            aux_tobit_puls1 = 9 + 1
            power2Matrix = (2**np.arange(aux_bits2descr))[::-1].astype(int)
            aux_powerMatr = power2Matrix * np.ones(
                (NSmplRst, NGrp, NDataPads, NADC*NColInBlock,
                 len(power2Matrix))).astype(int)
            totalVector_xDAr = np.sum(auxil_thisImg_bitted[
                :, :, :, :,
                aux_frombit:aux_tobit_puls1] * aux_powerMatr, axis=4)
            auxil_thisImg_aggr[:, :, :, :, iFn] = totalVector_xDAr
            #
            if self._clean_memory:
                del auxil_thisImg_bitted
                del power2Matrix
                del aux_powerMatr
                del totalVector_xDAr
            #
            # including reference column
            auxil_thisImg_aggr_withRef = np.ones(
                (NSmplRst, NGrp, NPad, NADC*NColInBlock,
                 3)).astype('uint8') * ((2 ** 8) - 1)
            auxil_thisImg_aggr_withRef[
                :, :, 1:, :,
                :] = auxil_thisImg_aggr[:, :, :, :, :]
            if self._clean_memory:
                del auxil_thisImg_aggr
            #
            multiImg_aggr_withRef[
                iImg, :, :, :, :,
                :] = auxil_thisImg_aggr_withRef[:, :, :, :, :]
        print(" ")
        if self._clean_memory:
            del auxil_thisImg_aggr_withRef
        # - - -
        #
        # reorder pixels and pads
        msg = "solving chip-scrambling: pixel reordering"
        print(Fore.BLUE + msg)

        multiImg_GrpDscrmbld = np.zeros(
            (auxNImg, NSmplRst, NGrp, NPad,
             NADC, NColInBlock, 3)).astype('uint8')
        for iImg in range(auxNImg):
            for iSmplRst in range(NSmplRst):
                multiImg_GrpDscrmbld[
                    iImg, iSmplRst, :, :, :, :,
                    :] = reorder_pixels_GnCrsFn(multiImg_aggr_withRef[
                        iImg, iSmplRst, :, :, :, :], NADC, NColInBlock)
        # - - -
        #
        # add error tracking
        msg = "lost packet tracking"
        print(Fore.BLUE + msg)

        multiImg_GrpDscrmbld = multiImg_GrpDscrmbld.astype('int16')
        # -256 upto 255

        for iImg in range(auxNImg):
            for iGrp in range(NGrp):
                for iSmplRst in range(NSmplRst):
                    if (MissingRowGrpTracker[iImg, iSmplRst, iGrp]):
                        multiImg_GrpDscrmbld[
                            iImg, iSmplRst, iGrp, :, :, :,
                            :] = ERRint16
        multiImg_GrpDscrmbld[:, :, :, 0, :, :, :] = ERRint16
        # also err tracking for ref col
        # - - -
        #
        # reshaping as an Img array
        dscrmbld_GnCrsFn = np.zeros(
            (auxNImg, NSmplRst, NGrp,
             NPad, NADC, NColInBlock, 3)).astype('int16')
        dscrmbld_GnCrsFn[:, :, :, :, :, :, :] = multiImg_GrpDscrmbld[
            :, :, :, :, :, :, :]
        dscrmbld_GnCrsFn = np.transpose(dscrmbld_GnCrsFn,
                                        (0, 1, 2, 4, 3, 5, 6)).astype('int16')
        # (NImg,Smpl/Rst,NGrp,NADC,NPad,NColInBlk,Gn/Crs/Fn)

        dscrmbld_GnCrsFn = dscrmbld_GnCrsFn.reshape(
            (auxNImg, NSmplRst, NGrp * NADC, NPad * NColInBlock, 3))
        # - - -
        #
        # convert Gn/Crs/Fn => DLSraw: 16bit (errorbit+15bits)
        msg = "converting to DLSraw format"
        print(Fore.BLUE + msg)

        def convert_DLSraw_2_GnCrsFn(in_Smpl_DLSraw, in_Rst_DLSraw,
                                     inErr, outERR):
            ''' (Nimg,Smpl/Rst,NRow,NCol,Gn/Crs/Fn),int16(err=inErr) <=
            DLSraw: Smpl&Rst(Nimg,NRow,NCol),uint16(err=outErr):[X,2G,8F,5C]'''
            in_Smpl_uint16 = np.clip(
                in_Smpl_DLSraw, 0, (2**15) - 1).astype('uint16')
            in_Rst_uint16 = np.clip(
                in_Rst_DLSraw, 0, (2**15) - 1).astype('uint16')

            (aux_NImg, aux_NRow, aux_NCol) = in_Smpl_DLSraw.shape
            auxSmpl_multiImg_GnCrsFn = np.zeros(
                (aux_NImg, aux_NRow, aux_NCol, 3)).astype('uint8')
            auxRst_multiImg_GnCrsFn = np.zeros(
                (aux_NImg, aux_NRow, aux_NCol, 3)).astype('uint8')
            out_multiImg_GnCrsFn = np.zeros(
                (aux_NImg, 2, aux_NRow, aux_NCol, 3)).astype('int16')
            imgGn = np.zeros((aux_NRow, aux_NCol)).astype('uint8')
            imgCrs = np.zeros_like(imgGn).astype('uint8')
            imgFn = np.zeros_like(imgGn).astype('uint8')
            for iImg in range(aux_NImg):
                imgGn = in_Smpl_uint16[iImg, :, :] // (2**13)
                imgFn = (in_Smpl_uint16[iImg, :, :] - (
                    imgGn.astype('uint16') * (2**13))) // (2**5)
                imgCrs = in_Smpl_uint16[iImg, :, :] - (
                    imgGn.astype('uint16') * (2**13)) - (
                        imgFn.astype('uint16') * (2**5))
                auxSmpl_multiImg_GnCrsFn[iImg, :, :, iGn] = imgGn
                auxSmpl_multiImg_GnCrsFn[iImg, :, :, iCrs] = imgCrs
                auxSmpl_multiImg_GnCrsFn[iImg, :, :, iFn] = imgFn

                imgGn = in_Rst_uint16[iImg, :, :] // (2**13)
                imgFn = (in_Rst_uint16[iImg, :, :] - (
                    imgGn.astype('uint16') * (2**13))) // (2**5)
                imgCrs = in_Rst_uint16[iImg, :, :] - (
                    imgGn.astype('uint16') * (2**13)) - (
                        imgFn.astype('uint16') * (2**5))
                auxRst_multiImg_GnCrsFn[iImg, :, :, iGn] = imgGn
                auxRst_multiImg_GnCrsFn[iImg, :, :, iCrs] = imgCrs
                auxRst_multiImg_GnCrsFn[iImg, :, :, iFn] = imgFn

            # track errors with ERRint16 (-256)
            auxSmpl_multiImg_GnCrsFn = auxSmpl_multiImg_GnCrsFn.astype(
                'uint16')
            auxRst_multiImg_GnCrsFn = auxRst_multiImg_GnCrsFn.astype('uint16')
            errMask = in_Smpl_DLSraw[:, :, :] == inErr
            auxSmpl_multiImg_GnCrsFn[errMask, :] = outERR
            errMask = in_Rst_DLSraw[:, :, :] == inErr
            auxRst_multiImg_GnCrsFn[errMask, :] = outERR

            out_multiImg_GnCrsFn[:, iSmpl, :,
                                 :, :] = auxSmpl_multiImg_GnCrsFn[:, :, :, :]
            out_multiImg_GnCrsFn[:, iRst,
                                 :, :, :] = auxRst_multiImg_GnCrsFn[:, :, :, :]

            return(out_multiImg_GnCrsFn)

        def convert_GnCrsFn_2_DLSraw(in_GnCrsFn_int16, inErr, outERR):
            ''' (Nimg,Smpl/Rst,NRow,NCol,Gn/Crs/Fn),int16(err=inErr) =>
            DLSraw: Smpl&Rst(Nimg,NRow,NCol),uint16(err=outErr):[X,2G,8F,5C]'''
            multiImg_SmplRstGnGrsFn_u16 = np.clip(
                in_GnCrsFn_int16, 0, (2**8) - 1)
            multiImg_SmplRstGnGrsFn_u16 = multiImg_SmplRstGnGrsFn_u16.astype(
                'uint16')
            # convert to DLSraw format
            (NImg, aux_NSmplRst, aux_NRow,
             aux_NCol, aux_NGnCrsFn) = in_GnCrsFn_int16.shape
            out_multiImg_Smpl_DLSraw = np.zeros(
                (NImg, NGrp * NRowInBlock,
                 NPad * NColInBlock)).astype('uint16')
            out_multiImg_Rst_DLSraw = np.zeros(
                (NImg, NGrp * NRowInBlock,
                 NPad * NColInBlock)).astype('uint16')
            out_multiImg_Smpl_DLSraw[
                :, :, :] = ((2**13)*multiImg_SmplRstGnGrsFn_u16[
                    :, iSmpl, :, :, iGn].astype('uint16')) + (
                        (2**5) * multiImg_SmplRstGnGrsFn_u16[
                            :, iSmpl, :, :,
                            iFn].astype(
                                'uint16')) + multiImg_SmplRstGnGrsFn_u16[
                                    :, iSmpl, :, :, iCrs].astype('uint16')
            out_multiImg_Rst_DLSraw[
                :, :, :] = ((2**13) * multiImg_SmplRstGnGrsFn_u16[
                    :, iRst, :, :, iGn].astype('uint16')) + (
                        (2**5) * multiImg_SmplRstGnGrsFn_u16[
                            :, iRst, :, :,
                            iFn].astype(
                                'uint16')) + multiImg_SmplRstGnGrsFn_u16[
                                    :, iRst, :, :, iCrs].astype('uint16')

            # track errors in DLSraw mode with the ERRDLSraw (max of uint16)
            errMask = in_GnCrsFn_int16[:, iSmpl, :, :, iGn] == inErr
            out_multiImg_Smpl_DLSraw[errMask] = outERR
            errMask = in_GnCrsFn_int16[:, iRst, :, :, iGn] == inErr
            out_multiImg_Rst_DLSraw[errMask] = outERR
            #
            return (out_multiImg_Smpl_DLSraw, out_multiImg_Rst_DLSraw)

        (dscrmbld_Smpl_DLSraw, dscrmbld_Rst_DLSraw) = convert_GnCrsFn_2_DLSraw(
            dscrmbld_GnCrsFn, ERRint16, ERRDLSraw)

        if self._swap_sample_reset:
            msg = "swapping Smpl and Rst data"
            print(Fore.BLUE + msg)
            (dscrmbld_Rst_DLSraw, dscrmbld_Smpl_DLSraw) = convert_GnCrsFn_2_DLSraw(
                dscrmbld_GnCrsFn, ERRint16, ERRDLSraw)       

        if self._clean_memory:
            del dscrmbld_GnCrsFn
        # - - -
        #
        # show descrambled data
        if self._debug:
            (auxNImg, auxNRow, auxNCol) = dscrmbld_Smpl_DLSraw.shape
            reread_GnCrsFn = convert_DLSraw_2_GnCrsFn(
                dscrmbld_Smpl_DLSraw, dscrmbld_Rst_DLSraw, ERRDLSraw, ERRint16)
            for aux_thisimg in range(auxNImg):
                aux_title = "Img " + str(aux_thisimg)
                aux_ERRBlw = -0.1
                percDebug_plot_6x2D(
                    reread_GnCrsFn[aux_thisimg, iSmpl, :, :, iGn],
                    reread_GnCrsFn[aux_thisimg, iSmpl, :, :, iCrs],
                    reread_GnCrsFn[aux_thisimg, iSmpl, :, :, iFn],
                    reread_GnCrsFn[aux_thisimg, iRst, :, :, iGn],
                    reread_GnCrsFn[aux_thisimg, iRst, :, :, iCrs],
                    reread_GnCrsFn[aux_thisimg, iRst, :, :, iFn],
                    aux_title, aux_ERRBlw)
            # ingnoreme = input("press enter to continue")
        # - - -
        #
        # save descrambled data
        if self._save_file:
            filenamepath_out = self._output_fname
            write_2xh5(filenamepath_out, dscrmbld_Smpl_DLSraw, '/data/',
                       dscrmbld_Rst_DLSraw, '/reset/')
            msg = 'data saved to: '+filenamepath_out
            print(Fore.GREEN + msg)

            if self._clean_memory:
                del dscrmbld_Smpl_DLSraw
                del dscrmbld_Rst_DLSraw

        # show saved data
        if self._save_file & self._debug:
            (reread_Smpl, reread_Rst) = read_2xh5(
                filenamepath_out, '/data/', '/reset/')
            (auxNImg, auxNRow, auxNCol) = reread_Smpl.shape
            reread_GnCrsFn = convert_DLSraw_2_GnCrsFn(
                reread_Smpl, reread_Rst, ERRDLSraw, ERRint16)
            if self._clean_memory:
                del reread_Smpl
                del reread_Rst
            for aux_thisimg in range(auxNImg):
                aux_title = "re-read Img " + str(aux_thisimg)
                aux_ERRBlw = -0.1
                percDebug_plot_6x2D(
                    reread_GnCrsFn[aux_thisimg, iSmpl, :, :, iGn],
                    reread_GnCrsFn[aux_thisimg, iSmpl, :, :, iCrs],
                    reread_GnCrsFn[aux_thisimg, iSmpl, :, :, iFn],
                    reread_GnCrsFn[aux_thisimg, iRst, :, :, iGn],
                    reread_GnCrsFn[aux_thisimg, iRst, :, :, iCrs],
                    reread_GnCrsFn[aux_thisimg, iRst, :, :, iFn],
                    aux_title, aux_ERRBlw)
            # ingnoreme = input("press enter to continue")
        # - - -
        #
        # that's all folks
        print("------------------------")
        print("done")
        stop_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        print(Fore.BLUE + "script ended at {}".format(stop_time))
        print("------------------------\n" * 3)

    def _report_arguments(self):
        """ report arguments form conf file """

        if self._verbose:
            print(Fore.GREEN + "Will try to load scrmbld files:")
            for fname in self._input_fnames:
                print(Fore.GREEN + fname)

            if self._swap_sample_reset:
                print(Fore.GREEN +
                      ("Will swap Sample and Reset images"))

            if self._save_file:
                print(Fore.GREEN +
                      ("Will save single descrambled file: {}"
                       .format(self._output_fname)))

            if self._debug:
                print(Fore.GREEN + "debug: will show images")

            if self._clean_memory:
                print(Fore.GREEN + "Will clean memory when possible")

            print(Fore.GREEN + "verbose")
            print(Fore.GREEN + "--  --  --")

