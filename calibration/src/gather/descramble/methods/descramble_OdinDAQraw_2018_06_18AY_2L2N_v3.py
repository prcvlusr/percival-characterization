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

import matplotlib
import matplotlib.pyplot

import __init__  # noqa F401
import utils

from descramble_base import DescrambleBase
from utils_methods import *

matplotlib.use('TkAgg')


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
        start_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        printcol("Script beginning at {}".format(start_time), 'blue')
        # print(self.__dict__.keys())
        self._report_arguments()
        # - - -
        #
        # read h5 files
        printcol("reading files", 'blue',)
        if (os.path.isfile(self._input_fnames[0])):
            (data_fl0_smpl, data_fl0_rst) = read_2xh5(self._input_fnames[0],
                                                      '/data/', '/reset/')
        else:
            msg = "unable to find {}".format(self._input_fnames[0])
            printcol(msg, 'red')
            return()

        if (os.path.isfile(self._input_fnames[1])):
            (data_fl1_smpl, data_fl1_rst) = read_2xh5(self._input_fnames[1],
                                                      '/data/', '/reset/')
        else:
            msg = "unable to find {}".format(self._input_fnames[1])
            printcol(msg, 'red')
            return()

        (n_img_fl0, aux_nrow, aux_ncol) = data_fl0_smpl.shape
        (n_img_fl1, aux_nrow, aux_ncol) = data_fl1_smpl.shape
        aux_n_img = n_img_fl0 + n_img_fl0
        printcol("{0}+{1} Img read from files".format(n_img_fl0,
                                                      n_img_fl0), 'green')
        # - - -
        #
        # combine in one array: Img0-from-fl0, Img0-from-fl1, Img1-from-fl0...
        scrmbl_smpl = np.zeros(
            (aux_n_img, aux_nrow, aux_ncol)).astype('uint16')
        scrmbl_rst = np.zeros_like(scrmbl_smpl).astype('uint16')
        for i_img in range(aux_n_img):
            if((i_img % 2 == 0) & ((i_img // 2) < n_img_fl0)):
                scrmbl_smpl[i_img, :, :] = data_fl0_smpl[i_img // 2, :, :]
                scrmbl_rst[i_img, :, :] = data_fl0_rst[i_img // 2, :, :]
            if((i_img % 2 == 1) & ((i_img // 2) < n_img_fl1)):
                scrmbl_smpl[i_img, :, :] = data_fl1_smpl[i_img // 2, :, :]
                scrmbl_rst[i_img, :, :] = data_fl1_rst[i_img // 2, :, :]
        if self._clean_memory:
            del data_fl0_smpl
            del data_fl0_rst
            del data_fl1_smpl
            del data_fl1_rst
        # - - -
        #
        # solving 4a DAQ-scrambling: byte swap in hex (By0,By1) => (By1,By0)
        msg = "solving DAQ-scrambling: byte-swapping (it might take a while)"
        printcol(msg, 'blue')

        datasmpl_byteswap = np.zeros_like(scrmbl_smpl).astype('uint16')
        datarst_byteswap = np.zeros_like(scrmbl_smpl).astype('uint16')
        for i_img in range(aux_n_img):
            datasmpl_byteswap[i_img, :, :] = convert_hex_byteswap_ar(
                scrmbl_smpl[i_img, :, :])
            datarst_byteswap[i_img, :, :] = convert_hex_byteswap_ar(
                scrmbl_rst[i_img, :, :])
            dot()
        print(" ")
        if self._clean_memory:
            del scrmbl_smpl
            del scrmbl_rst
        # - - -
        #
        # solving DAQ-scrambling: "pixel" reordering
        msg = "solving DAQ-scrambling: reordering subframes"
        printcol(msg, 'blue')

        def convert_odin_daq_2_mezzanine(shot_in):
            ''' descrambles the OdinDAQ-scrambling '''
            (aux_n_img, aux_nrow, aux_ncol) = shot_in.shape
            aux_reord = shot_in.reshape((aux_n_img, n_grp, n_adc, aux_ncol))
            aux_reord = aux_reord.reshape(
                (aux_n_img, n_grp, n_adc, 2, aux_ncol // 2))
            aux_reord = np.transpose(
                aux_reord, (0, 1, 3, 2, 4))
            # aux_n_img,n_grp, 2left/right,n_adc,aux_ncol//2
            aux_reord = aux_reord.reshape(
                (aux_n_img, n_grp, 2, n_adc * aux_ncol // 2))
            # aux_n_img,n_grp,2left/right,n_adc*aux_ncol//2
            aux_reord = aux_reord.reshape(
                (aux_n_img, n_grp, 2, 2, n_adc * aux_ncol // 4))
            # aux_n_img,n_grp,2left/right,2up/down,n_adc*aux_ncol//4
            aux_reordered = np.ones((
                aux_n_img, n_grp, 4,
                n_adc * aux_ncol // 4)).astype('uint16') * err_dlsraw
            aux_reordered[:, :, 0, :] = aux_reord[:, :, 0, 0, :]
            aux_reordered[:, :, 1, :] = aux_reord[:, :, 1, 0, :]
            aux_reordered[:, :, 2, :] = aux_reord[:, :, 0, 1, :]
            aux_reordered[:, :, 3, :] = aux_reord[:, :, 1, 1, :]
            aux_reordered = aux_reordered.reshape(
                (aux_n_img, n_grp, n_adc * aux_ncol))
            aux_reordered = aux_reordered.reshape(
                (aux_n_img, n_grp, n_adc, aux_ncol))
            aux_reordered = aux_reordered.reshape(
                (aux_n_img, n_grp * n_adc, aux_ncol))
            return aux_reordered
        #
        datasmpl_asmezz = convert_odin_daq_2_mezzanine(datasmpl_byteswap)
        datarst_asmezz = convert_odin_daq_2_mezzanine(datarst_byteswap)
        if self._clean_memory:
            del datasmpl_byteswap
            del datarst_byteswap
        # - - -
        #
        # solving mezzanine-scrambling
        msg = "solving mezzanine&chip-scrambling: preparation"
        printcol(msg, 'blue')

        datasmpl_2_dscrmbl = datasmpl_asmezz
        datarst_2_dscrmbl = datarst_asmezz
        data_2_srcmbl_norefcol = np.ones(
            (aux_n_img, n_smplrst,
             aux_nrow, aux_ncol)).astype('uint16') * ((2**16) - 1)
        data_2_srcmbl_norefcol[:, ismpl, :, :] = datasmpl_2_dscrmbl
        data_2_srcmbl_norefcol[:, irst, :, :] = datarst_2_dscrmbl
        data_2_srcmbl_norefcol = data_2_srcmbl_norefcol.reshape(
            (aux_n_img, n_smplrst, n_grp, n_adc, aux_ncol))
        #
        # track missing packets: False==RowGrp OK;
        # True== packet(s) missing makes rowgroup moot
        # (1111 1111 1111 1111 instead of 0xxx xxxx xxxx xxxx)
        missing_rowgrp_tracker = np.ones(
            (aux_n_img, n_smplrst, n_grp)).astype(bool)
        missing_rowgrp_tracker = data_2_srcmbl_norefcol[
            :, :, :, 0, 0] == err_dlsraw
        # - - -
        #
        # descramble proper
        msg = "solving mezzanine&chip-scrambling: pixel descrambling"
        printcol(msg, 'blue')
        multiimg_aggr_withref = np.zeros(
           (aux_n_img, n_smplrst, n_grp, n_pad,
            n_adc * n_col_in_blk, 3)).astype('uint8')

        for i_img in range(aux_n_img):
            dot()
            auxil_thisimg = data_2_srcmbl_norefcol[
                i_img, :, :, :, :].reshape((n_smplrst, n_grp, n_adc*aux_ncol))
            # (n_smplrst,NRowGrpInShot,n_adc*aux_ncol)

            auxil_thisimg = auxil_thisimg.reshape(
                (n_smplrst, n_grp,
                 n_adc * aux_ncol // (n_data_pads * 2), n_data_pads, 2))
            # 32bit=2"pix" from 1st pad, 2"pix" from 2nd pad, ...

            auxil_thisimg = np.transpose(auxil_thisimg, (0, 1, 3, 2, 4))
            # (n_smplrst,n_grp,n_data_pads,
            # n_adc*aux_ncol//(n_data_pads*2),2"pix")

            auxil_thisimg = auxil_thisimg.reshape(
                (n_smplrst, n_grp, n_data_pads, n_adc*aux_ncol//n_data_pads))
            #
            # bit, remove head 0, concatenate and reorder
            auxil_thisimg_16bitted = convert_uint_2_bits_ar(
                auxil_thisimg, 16)[:, :, :, :, ::-1].astype('uint8')
            # n_smplrst,n_grp,n_data_pads,n_adc*aux_ncol//n_data_pads,15bits

            auxil_thisimg_bitted = auxil_thisimg_16bitted[:, :, :, :, 1:]
            # n_smplrst,n_grp,n_data_pads,n_adc*aux_ncol//n_data_pads,15bits

            auxil_thisimg_bitted = auxil_thisimg_bitted.reshape(
                (n_smplrst, n_grp, n_data_pads,
                 n_adc * aux_ncol * 15 // n_data_pads))
            auxil_thisimg_bitted = auxil_thisimg_bitted.reshape(
                (n_smplrst, n_grp, n_data_pads, 15, n_adc * n_col_in_blk))

            # BBT: 0=>1, 1=>0
            auxil_thisimg_bitted = np.transpose(auxil_thisimg_bitted,
                                                (0, 1, 2, 4, 3))
            # (n_smplrst,n_grp,n_data_pads,NPixsInRowBlk,15)
            auxil_thisimg_bitted = convert_britishbits_ar(auxil_thisimg_bitted)
            #
            auxil_thisimg_aggr = np.zeros(
                (n_smplrst, n_grp, n_data_pads,
                 n_adc * n_col_in_blk, 3)).astype('uint8')
            #
            # binary aggregate Gn bit(0,1)
            aux_bits2descr = 2
            aux_frombit = 0
            aux_tobit_puls1 = 1 + 1
            power2matrix = (2 ** np.arange(aux_bits2descr))[::-1].astype(int)
            aux_power_matr = power2matrix * np.ones(
                (n_smplrst, n_grp, n_data_pads, n_adc * n_col_in_blk,
                 len(power2matrix))).astype(int)
            totalvector_xd_ar = np.sum(auxil_thisimg_bitted[
                :, :, :, :,
                aux_frombit:aux_tobit_puls1] * aux_power_matr, axis=4)
            auxil_thisimg_aggr[
                :, :, :, :, ign] = totalvector_xd_ar.astype('uint8')
            #
            # binary aggregate Crs bit(10,11,12,13,14)
            aux_bits2descr = 5
            aux_frombit = 10
            aux_tobit_puls1 = 14 + 1
            power2matrix = (2**np.arange(aux_bits2descr))[::-1].astype(int)
            aux_power_matr = power2matrix * np.ones(
                (n_smplrst, n_grp, n_data_pads, n_adc*n_col_in_blk,
                 len(power2matrix))).astype(int)
            totalvector_xd_ar = np.sum(auxil_thisimg_bitted[
                :, :, :, :,
                aux_frombit:aux_tobit_puls1] * aux_power_matr, axis=4)
            auxil_thisimg_aggr[:, :, :, :, icrs] = totalvector_xd_ar
            #
            # binary aggregate Fn bit(2,3,4,5,6,7,8,9)
            aux_bits2descr = 8
            aux_frombit = 2
            aux_tobit_puls1 = 9 + 1
            power2matrix = (2**np.arange(aux_bits2descr))[::-1].astype(int)
            aux_power_matr = power2matrix * np.ones(
                (n_smplrst, n_grp, n_data_pads, n_adc*n_col_in_blk,
                 len(power2matrix))).astype(int)
            totalvector_xd_ar = np.sum(auxil_thisimg_bitted[
                :, :, :, :,
                aux_frombit:aux_tobit_puls1] * aux_power_matr, axis=4)
            auxil_thisimg_aggr[:, :, :, :, ifn] = totalvector_xd_ar
            #
            if self._clean_memory:
                del auxil_thisimg_bitted
                del power2matrix
                del aux_power_matr
                del totalvector_xd_ar
            #
            # including reference column
            auxil_thisImg_aggr_withref = np.ones(
                (n_smplrst, n_grp, n_pad, n_adc*n_col_in_blk,
                 3)).astype('uint8') * ((2 ** 8) - 1)
            auxil_thisImg_aggr_withref[
                :, :, 1:, :,
                :] = auxil_thisimg_aggr[:, :, :, :, :]
            if self._clean_memory:
                del auxil_thisimg_aggr
            #
            multiimg_aggr_withref[
                i_img, :, :, :, :,
                :] = auxil_thisImg_aggr_withref[:, :, :, :, :]
        print(" ")
        if self._clean_memory:
            del auxil_thisImg_aggr_withref
        # - - -
        #
        # reorder pixels and pads
        msg = "solving chip-scrambling: pixel reordering"
        printcol(msg, 'blue')

        multiimg_grpdscrmbld = np.zeros(
            (aux_n_img, n_smplrst, n_grp, n_pad,
             n_adc, n_col_in_blk, 3)).astype('uint8')
        for i_img in range(aux_n_img):
            for i_smplrst in range(n_smplrst):
                multiimg_grpdscrmbld[
                    i_img, i_smplrst, :, :, :, :,
                    :] = reorder_pixels_gncrsfn(multiimg_aggr_withref[
                        i_img, i_smplrst, :, :, :, :], n_adc, n_col_in_blk)
        # - - -
        #
        # add error tracking
        msg = "lost packet tracking"
        printcol(msg, 'blue')

        multiimg_grpdscrmbld = multiimg_grpdscrmbld.astype('int16')
        # -256 upto 255

        for i_img in range(aux_n_img):
            for i_grp in range(n_grp):
                for i_smplrst in range(n_smplrst):
                    if (missing_rowgrp_tracker[i_img, i_smplrst, i_grp]):
                        multiimg_grpdscrmbld[
                            i_img, i_smplrst, i_grp, :, :, :,
                            :] = err_gncrsfn
        multiimg_grpdscrmbld[:, :, :, 0, :, :, :] = err_gncrsfn
        # also err tracking for ref col
        # - - -
        #
        # reshaping as an Img array
        dscrmbld_gncrsfn = np.zeros(
            (aux_n_img, n_smplrst, n_grp,
             n_pad, n_adc, n_col_in_blk, 3)).astype('int16')
        dscrmbld_gncrsfn[:, :, :, :, :, :, :] = multiimg_grpdscrmbld[
            :, :, :, :, :, :, :]
        dscrmbld_gncrsfn = np.transpose(dscrmbld_gncrsfn,
                                        (0, 1, 2, 4, 3, 5, 6)).astype('int16')
        # (NImg,Smpl/Rst,n_grp,n_adc,n_pad,NColInBlk,Gn/Crs/Fn)

        dscrmbld_gncrsfn = dscrmbld_gncrsfn.reshape(
            (aux_n_img, n_smplrst, n_grp * n_adc, n_pad * n_col_in_blk, 3))
        # - - -
        #
        # convert Gn/Crs/Fn => DLSraw: 16bit (errorbit+15bits)
        msg = "converting to DLSraw format"
        printcol(msg, 'blue')

        (dscrmbld_smpl_dlsraw,
         dscrmbld_rst_dlsraw) = convert_gncrsfn_2_dlsraw(
            dscrmbld_gncrsfn, False)

        if self._swap_sample_reset:
            msg = "swapping Smpl and Rst data"
            printcol(msg, 'blue')
            (dscrmbld_rst_dlsraw,
             dscrmbld_smpl_dlsraw) = convert_gncrsfn_2_dlsraw(
                dscrmbld_gncrsfn, False)

        if self._clean_memory:
            del dscrmbld_gncrsfn
        # - - -
        #
        # show descrambled data
        if self._debug:
            (aux_n_img, aux_nrow, aux_ncol) = dscrmbld_smpl_dlsraw.shape
            reread_gncrsfn = convert_dlsraw_2_gncrsfn(
                dscrmbld_smpl_dlsraw, dscrmbld_rst_dlsraw, False)
            for aux_thisimg in range(aux_n_img):
                aux_title = "Img " + str(aux_thisimg)
                aux_err_below = -0.1
                perc_plot_6x2d(
                    reread_gncrsfn[aux_thisimg, ismpl, :, :, ign],
                    reread_gncrsfn[aux_thisimg, ismpl, :, :, icrs],
                    reread_gncrsfn[aux_thisimg, ismpl, :, :, ifn],
                    reread_gncrsfn[aux_thisimg, irst, :, :, ign],
                    reread_gncrsfn[aux_thisimg, irst, :, :, icrs],
                    reread_gncrsfn[aux_thisimg, irst, :, :, ifn],
                    aux_title, aux_err_below)
            # ingnoreme = input("press enter to continue")
        # - - -
        #
        # save descrambled data
        if self._save_file:
            filenamepath_out = self._output_fname
            write_2xh5(filenamepath_out, dscrmbld_smpl_dlsraw, '/data/',
                       dscrmbld_rst_dlsraw, '/reset/')
            msg = 'data saved to: '+filenamepath_out
            printcol(msg, 'green')
        # - - -
        #

        # save data to multiple file
        if self._multiple_save_files:
            (n_img, aux_row, aux_col) = dscrmbld_smpl_dlsraw.shape
            if self._verbose:
                printcol("saving to multiple files", 'blue')

            if os.path.isfile(self._multiple_metadata_file) is False:
                msg = "metafile file does not exist"
                printcol(msg, 'red')
                raise Exception(msg)

            meta_data = read_tst(self._multiple_metadata_file)
            fileprefix_list = meta_data[:, 1]

            aux_n_of_files = len(fileprefix_list)
            if (aux_n_of_files*self._multiple_imgperfile) != n_img:
                msg = 'number of images: '+str(n_img)
                printcol(msg, 'red')
                msg = 'number of metafile entries: ' + str(aux_n_of_files)
                printcol(msg, 'red')
                msg = 'number of images per file: ' + str(
                    self._multiple_imgperfile)
                printcol(msg, 'red')
                msg = ("n of images != metafile enties x Img/file ")
                printcol(msg, 'red')
                raise Exception(msg)

            sample = dscrmbld_smpl_dlsraw
            reset = dscrmbld_rst_dlsraw

            (_, aux_nrow, aux_ncol) = sample.shape
            shape_datamultfiles = (aux_n_of_files,
                                   self._multiple_imgperfile,
                                   aux_nrow,
                                   aux_ncol)
            sample = sample.reshape(shape_datamultfiles).astype('uint16')
            reset = reset.reshape(shape_datamultfiles).astype('uint16')

            for i, prefix in enumerate(fileprefix_list):

                filepath = os.path.dirname(
                    self._output_fname) + '/' + prefix + ".h5"

                write_2xh5(filepath, sample[i, :, :, :], '/data/',
                           reset[i, :, :, :], '/reset/')

                if self._verbose:
                    msg = "{0} Img saved to file {1}".format(
                        self._multiple_imgperfile, filepath)
                    printcol(msg, 'green')

            if self._clean_memory:
                del dscrmbld_smpl_dlsraw
                del dscrmbld_rst_dlsraw
        # - - -
        #
        # show saved data

        if self._save_file & self._debug:
            (reread_smpl, reread_rst) = read_2xh5(
                filenamepath_out, '/data/', '/reset/')
            (aux_n_img, aux_nrow, aux_ncol) = reread_smpl.shape
            reread_gncrsfn = convert_dlsraw_2_gncrsfn(
                reread_smpl, reread_rst, False)
            if self._clean_memory:
                del reread_smpl
                del reread_rst
            for aux_thisimg in range(aux_n_img):
                aux_title = "re-read Img " + str(aux_thisimg)
                aux_err_below = -0.1
                perc_plot_6x2d(
                    reread_gncrsfn[aux_thisimg, ismpl, :, :, ign],
                    reread_gncrsfn[aux_thisimg, ismpl, :, :, icrs],
                    reread_gncrsfn[aux_thisimg, ismpl, :, :, ifn],
                    reread_gncrsfn[aux_thisimg, irst, :, :, ign],
                    reread_gncrsfn[aux_thisimg, irst, :, :, icrs],
                    reread_gncrsfn[aux_thisimg, irst, :, :, ifn],
                    aux_title, aux_err_below)
            # ingnoreme = input("press enter to continue")
        # - - -
        #
        # that's all folks
        printcol("------------------------", 'black')
        printcol("done", 'black')
        stop_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        printcol("script ended at {}".format(stop_time), 'blue')
        printcol("------------------------\n" * 3, 'black')

    def _report_arguments(self):
        """ report arguments form conf file """

        if self._verbose:
            printcol("Will try to load scrmbld files:", 'green')
            for fname in self._input_fnames:
                printcol(fname, 'green')

            if self._swap_sample_reset:
                printcol("Will swap Sample and Reset images", 'green')

            if self._save_file:
                printcol("Will save single descrambled file: {}".format(
                    self._output_fname), 'green')

            if self._multiple_save_files:
                printcol("will save to multiple files, using file names in "
                         "{0}".format(self._multiple_metadata_file), 'green')
                printcol("assuming each file has {0} images".format(
                    self._multiple_imgperfile), 'green')

            if self._debug:
                printcol("debug: will show images", 'green')

            if self._clean_memory:
                printcol("Will clean memory when possible", 'green')

            printcol("verbose", 'green')
            printcol("--  --  --", 'green')

