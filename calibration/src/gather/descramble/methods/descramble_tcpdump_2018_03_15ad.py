"""
Descrample tcpdump output from the mezzanine to a data format
readable in gather.
"""
import os  # to list files in a directory
import time  # to have time
import numpy as np
from colorama import init, Fore

import __init__
import utils

from descramble_base import DescrambleBase


class Descramble(DescrambleBase):
    """ Descample tcpdump data
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # the gather method sets the following parameters
        #   input_fnames
        #   output_fname

        # in the method section of the config file the following parameters
        # have to be defined:
        #   n_adc
        #   n_grp
        #   n_pad
        #   n_col_in_blk
        #   save_file
        #   clean_memory
        #   verbose

        # useful constants
        # negative value usable to track Gn/Crs/Fn from missing pack
        self._err_int16 = -256
#        self._err_blw = -0.1
        # forbidden uint16, usable to track "pixel" from missing pack
        self._err_dlsraw = 65535
        self._i_smp = 0
        self._i_rst = 1
        self._i_gn = 0
        self._i_crs = 1
        self._i_fn = 2

        # general constants for a P2M system
        self._n_smpl_rst = 2
        self._n_data_pads = self._n_pad - 1  # 44
        self._n_row_in_blk = self._n_adc  # 7
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

        # 1 RowGrp (7x32x44pixel) in in 4 UDPacket
        self._n_packs_in_rowgrp = 4
        # 1Img (Smpl+Rst)= 1696 UDPacket
        self.n_packs_in_img = (self._n_packs_in_rowgrp
                               * self._n_grp
                               * self._n_smpl_rst)
        # thus packet count is never > 1695
        self._max_n_pack = 1695

        self._result_data = None

    def run(self):
        """
        descrambles tcpdump-binary files, save to h5 in DLSraw standard format

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
            - whether it is part of a Smpl/Rst
            - which Img (frame) the packet belongs to
            - its own packet number (0:1696), which determines the RowGrp the
            packet's data goes into
        3a) the packets are sent from 2 mezzanine links (some on one link, some
            on the other), and are saved a 2 binary files by tcpdump
            24Bytes are added at the start of each file

        Args:
            filenamepath_in0/1/2: name of tcpdump scrambled binary files
                Might exist or not
            output_fname: name of h5 descrambled file to generate
            save_file/debugFlag/clean_memory/verbose: no need to explain

        Returns:
            creates a h5 file (if save_file) in DLSraw standard format
                no explicit return()
        """

        init(autoreset=True)

        start_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        print(Fore.BLUE + "Script beginning at {}".format(start_time))
        self._report_arguments()

        file_content = self._reading_file_content()

        n_packets = [len(content) // self._fullpack_size
                     for content in file_content]

        if self._verbose:
            print(Fore.GREEN +
                  ("data read from files ({} packets)"
                   .format("+".join([str(n) for n in n_packets]))))

        # search for 1st & last image: this is needed to resort the data from
        # the file in a proper array of (n_img, n_pack)
        # also scan for fatal packet error: if a packet has a number > 1695
        # then the data is corrupted
        if self._verbose:
            print(Fore.BLUE + "scanning files for obvious packet errors")

        first_img, last_img = self._scanning_files(n_packets, file_content)

        # if needed, reduce Img2show to the 1st image
        # (the 1st img in the sequence might have a Img_counter number >0)
        imgs_tcpdump = np.arange(first_img, last_img + 1)
        n_img = len(imgs_tcpdump)

        msg = (("The lowest-numbered Img of the sequence is: "
                "tcpdump-Image {}\n"
                "The highest-numbered Img of the sequence is: "
                "tcpdump-Image {}").format(first_img, last_img))
        print(Fore.GREEN + msg)

        # solving the 2c-part of scrambling
        # resort data from files (assign pack to its Img,Smpl/Rst)
        if self._verbose:
            print(Fore.BLUE + "resorting packages")

        data, _, pack_check = self._resorting_data(n_img,
                                                   imgs_tcpdump,
                                                   file_content)

        if self._verbose:
            print(Fore.BLUE + " ")

        if self._clean_memory:
            del file_content

        # missing package detail: (pack,Img) not flagged as good, are missing
        for i, img in enumerate(imgs_tcpdump):
            if self._verbose:
                missing_packages = np.sum(np.logical_not(pack_check[i, :]))

                if missing_packages < 1:
                    print(Fore.GREEN +
                          "All packets for image {} are there".format(img))
                else:
                    print(Fore.MAGENTA +
                          ("{} packets missing from image {}"
                           .format(missing_packages, img)))

        # at this point the dsata from the 2 files is ordered in a array of
        # dinesion (n_img, n_pack)

        # 1 rowgrp = 4 packets
        # when a packet is missing, the whole rowgrp is compromised
        # if so, flag the 4-tuple of packets (i.e. the rowgrp), as bad
        rowgrp_check = (pack_check[:, 0::4]
                        & pack_check[:, 1::4]
                        & pack_check[:, 2::4]
                        & pack_check[:, 3::4])
        # - - -

        if self._verbose:
            print(Fore.BLUE + "descrambling images")

        descrambled_data = self._descrambling_images(n_img,
                                                     imgs_tcpdump,
                                                     data)

        if self._verbose:
            print(Fore.BLUE + " ")

        # solving the 1b-part of scrambling:
        # reorder pixels and pads
        if self._verbose:
            print(Fore.BLUE + "reordering pixels")

        self._result_data = self._reordering_pixels(n_img,
                                                    imgs_tcpdump,
                                                    descrambled_data,
                                                    rowgrp_check)

        # save data to single file
        if self._save_file:
            self._save_data()

        # save data to multiple file
        if self._multiple_save_files:
            if self._verbose:
                print(Fore.BLUE + "saving to multiple files")

            if os.path.isfile(self._multiple_metadata_file) is False:
                msg = "metafile file does not exist"
                print(Fore.RED + msg)
                raise Exception(msg)

            meta_data = np.genfromtxt(self._multiple_metadata_file,
                                      delimiter='\t',
                                      dtype=str)
            fileprefix_list = meta_data[:, 1]

            aux_n_of_files = len(fileprefix_list)

            if (aux_n_of_files * self._multiple_imgperfile) != n_img:
                msg = ("{} != {} x {} ".format(n_img,
                                               aux_n_of_files,
                                               self._multiple_imgperfile))
                print(Fore.RED + msg)

                msg = ("n of images != metafile enties x Img/file ")
                print(Fore.RED + msg)
                raise Exception(msg)
            # ...

            (sample, reset) = utils.convert_gncrsfn_to_dlsraw(self._result_data,
                                                              self._err_int16,
                                                              self._err_dlsraw)
            (aux_nimg, aux_nrow, aux_ncol) = sample.shape
            shape_datamultfiles = (aux_n_of_files,
                                   self._multiple_imgperfile,
                                   aux_nrow,
                                   aux_ncol)
            sample = sample.reshape(shape_datamultfiles).astype('uint16')
            reset = reset.reshape(shape_datamultfiles).astype('uint16')

            for i, prefix in enumerate(fileprefix_list):
            
                filepath = os.path.dirname(self._output_fname)+'/'+prefix + ".h5"

                with h5py.File(filepath, "w", libver='latest') as my5hfile:
                    my5hfile.create_dataset('/data/', data=sample[i, :, :, :])
                    my5hfile.create_dataset('/reset/', data=reset[i, :, :, :])

                if self._verbose:
                    print(Fore.GREEN + "{0} Img saved to file {1}".format(
                        self._multiple_imgperfile, filepath))


        # that's all folks
        print("------------------------")
        print("done")
        stop_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        print(Fore.BLUE + "script ended at {}".format(stop_time))
        print("------------------------\n" * 3)

    def _report_arguments(self):
        """ report arguments from conf file """
        if self._verbose:
            print(Fore.GREEN + "Will try to load tcpdump files:")
            for fname in self._input_fnames:
                print(Fore.GREEN + fname)

            if self._save_file:
                print(Fore.GREEN +
                      ("Will save single descrambled file: {}"
                       .format(self._output_fname)))

            if self._multiple_save_files:
                print(Fore.GREEN + "will save to multiple files, using "
                      "file names in {0}".format(self._multiple_metadata_file))
                print(Fore.GREEN + "assuming each file has "
                      "{0} images".format(self._multiple_imgperfile))

            if self._clean_memory:
                print(Fore.GREEN + "Will clean memory when possible")

            print(Fore.GREEN + "verbose")
            print(Fore.GREEN + "--  --  --")

    def _reading_file_content(self):
        file_missing = [not os.path.isfile(fname)
                        for fname in self._input_fnames]

        # checks is least one of the input files exists
        if self._verbose:
            print(Fore.GREEN + "loaded tcpdump files:")

            for i, fname in enumerate(self._input_fnames):
                if file_missing[i]:
                    print(Fore.MAGENTA + fname + " does not exist")
                else:
                    print(Fore.GREEN + fname)

        # at least one of the input files must exist
        if all(file_missing):
            msg = "None of the input files exists"
            print(Fore.RED + msg)
            raise Exception(msg)

            if self._save_file:
                print(Fore.GREEN +
                      ("Will save descrambled file: {}"
                       .format(self._output_fname)))

            if self._clean_memory:
                print(Fore.GREEN + "Will clean memory when possible")

            print(Fore.GREEN + "verbose")
        # - - -

        # checks that at least one of the input files exists
        if all(file_missing):
            msg = "Non of the input files exists"
            print(Fore.RED + msg)
            raise Exception(msg)

        # solving the 3a-part of scrambling
        # read the tcpdump binary files, cut excess_bytesinfront
        if self._verbose:
            print(Fore.BLUE + "reading files")

        file_content = []
        for i, fname in enumerate(self._input_fnames):
            if file_missing[i]:
                content = np.array([]).astype('uint8')

            else:
                # read uint8 data from binary file
                with open(fname) as bin_file:
                    content = np.fromfile(bin_file, dtype=np.uint8)

                # cut off the excess bytes at the beginning
                content = content[self._excess_bytesinfront:]

            file_content.append(content)

        return file_content

    def _scanning_files(self, n_packets, file_content):
        """Scanning the files for errors and determining first and last image.
        """

        first_img = (2**32) - 1
        last_img = 0
        for i, n_pack in enumerate(n_packets):
            # n_pack is 0 for all non existing files
            for ipack in range(n_pack):
                start = ipack * self._fullpack_size
                end = (ipack + 1) * self._fullpack_size
                file_data = file_content[i][start:end]

                # the frame (Img) number in this pack header (4-Bytes)
                bytelist = file_data[self._img_counter-2:self._img_counter+2]
                img = utils.convert_bytelist_to_int(bytelist=bytelist)

                if img <= first_img:
                    first_img = img
                if img >= last_img:
                    last_img = img

                # the packet number in this pack header (2-Bytes)
                bitlist = file_data[self._pack_counter:self._pack_counter+2]
                pack_nmbr = utils.convert_bitlist_to_int(bitlist=bitlist)

                if pack_nmbr > self._max_n_pack:  # fatal error in the data
                    msg = ("Inconsistent packet in {}\n"
                           "(packet {}-th in the file is identified as "
                           "pack_nmbr={} > {})").format(self._input_fnames[i],
                                                        ipack,
                                                        pack_nmbr,
                                                        self._max_n_pack)
                    print(Fore.RED + msg)
                    raise Exception(msg)

        return first_img, last_img

    def _resorting_data(self, n_img, imgs_tcpdump, file_content):
        """
        """

        shape_img_pack = (n_img, 2 * self._n_grp * self._n_packs_in_rowgrp)
        shape_data = shape_img_pack + (self._gooddata_size,)
        shape_header = shape_img_pack + (self._header_size,)

        pack_check = np.zeros(shape_img_pack).astype(bool)
        data = np.zeros(shape_data).astype('uint8')
        header = np.zeros(shape_header).astype('uint8')

        for i, img_dump in enumerate(imgs_tcpdump):
            if self._verbose:
                print(".", end="", flush=True)

            for ifile, _ in enumerate(self._input_fnames):
                n_packs = len(file_content[ifile]) // self._fullpack_size

                for ipack in range(n_packs):
                    start = ipack * self._fullpack_size
                    end = (ipack + 1) * self._fullpack_size

                    file_data = file_content[ifile][start:end]

                    # if this pack (header) has a Img (frame) number
                    bytel = file_data[self._img_counter-2:self._img_counter+2]
                    conv_bytel = utils.convert_bytelist_to_int(bytelist=bytel)

                    if conv_bytel == img_dump:
                        idx = slice(self._pack_counter, self._pack_counter+2)
                        bytel = file_data[idx]
                        pack_id = utils.convert_bytelist_to_int(bytelist=bytel)

                        # then save it in the appropriate position
                        data[i, pack_id, :] = file_data[self._header_size:]
                        header[i, pack_id, :] = file_data[:self._header_size]
                        # and flag that (pack,Img) as good
                        pack_check[i, pack_id] = True

        return data, header, pack_check

    def _descrambling_images(self, n_img, imgs_tcpdump, data):

        n_smpl_rst_x_n_grp = self._n_smpl_rst * self._n_grp
        data_size = self._n_packs_in_rowgrp * self._gooddata_size

        shape_aggr_with_ref = (n_img,
                               n_smpl_rst_x_n_grp,
                               self._n_pad,
                               self._n_pixs_in_blk,
                               self._n_gn_crs_fn)
        descrambled_data = np.ones(shape_aggr_with_ref).astype('uint8')

        for i, _ in enumerate(imgs_tcpdump):
            if self._verbose:
                print(".", end="", flush=True)

            # 4UDP=> 1RowGrp
            img = data[i, ...].reshape((n_smpl_rst_x_n_grp, data_size))

            # solving the 2b-part of the scrambing (mezzanine interleaving
            # 32bit-sequences from each pad)
            img_shape_pad = (n_smpl_rst_x_n_grp,
                             data_size // (self._n_data_pads * 32//8),
                             self._n_data_pads,
                             32//8)
            img = img.reshape(img_shape_pad)
            img = img.transpose((0, 2, 1, 3))
            # dimensions of img at this point:
            # (self._n_smpl_rst * self._n_grp,
            #  self._n_data_pads,
            #  self._n_packs_in_rowgrp * self._gooddata_size
            #       // (self._n_data_pads * 32//8),
            #  32//8)

            new_shape2 = (n_smpl_rst_x_n_grp,
                          self._n_data_pads,
                          data_size // self._n_data_pads)
            img = img.reshape(new_shape2)

            # array of uint8 => array of [x,x,x,x, x,x,x,x] bits
            bitarray = utils.convert_intarray_to_bitarray(img, 8)
            img_8bitted = bitarray[Ellipsis, ::-1].astype('uint8')

            shape_8bit = (n_smpl_rst_x_n_grp,
                          self._n_data_pads,
                          data_size // self._n_data_pads,
                          8)
            img_8bitted = img_8bitted.reshape(shape_8bit)

            if self._clean_memory:
                del img

            shape_16bit = (n_smpl_rst_x_n_grp,
                           self._n_data_pads,
                           data_size // (self._n_data_pads * 2),
                           16)
            # combine 2x8bit to 16bit
            img_16bitted = np.zeros(shape_16bit).astype('uint8')
            img_16bitted[Ellipsis, 0:8] = img_8bitted[:, :, 0::2, :]
            img_16bitted[Ellipsis, 8:16] = img_8bitted[:, :, 1::2, :]

            if self._clean_memory:
                del img_8bitted

            # solving the 2a-part of scrambling:
            # remove head 0, concatenate and reorder
            # we can remove head 0 because the grps//missing packets are
            # already identified by rowgrp_check
            img_15bitted = img_16bitted[Ellipsis, 1:]

            if self._clean_memory:
                del img_16bitted

            shape_15bit = (n_smpl_rst_x_n_grp,
                           self._n_data_pads,
                           data_size * 15 // (self._n_data_pads * 2))
            img_as_from_chip = img_15bitted.reshape(shape_15bit)

            shape_as_from_chip = (n_smpl_rst_x_n_grp,
                                  self._n_data_pads,
                                  self._n_bits_in_pix,
                                  self._n_pixs_in_blk)
            img_as_from_chip = img_as_from_chip.reshape(shape_as_from_chip)

            if self._clean_memory:
                del img_15bitted

            # solving the 1d-part if scrambling
            # British Bit translation: 0->1, 1->0
            img_as_from_chip = np.transpose(img_as_from_chip, (0, 1, 3, 2))
            # img_as_from_chip dimension are now
            # (self._n_smpl_rst * self._n_grp,
            #  self._n_data_pads,
            #  n_pixs_in_rowblk,
            #  self._n_bits_in_pix)

            # 0=>1, 1=>0
            img_as_from_chip = utils.swap_bits(bitarray=img_as_from_chip)

            shape_img_aggr = (n_smpl_rst_x_n_grp,
                              self._n_data_pads,
                              self._n_pixs_in_blk,
                              self._n_gn_crs_fn)
            img_aggr = np.zeros(shape_img_aggr).astype('uint8')

            # solving the 1c-part if scrambling:
            # binary aggregate to gain/coarse/fine
            bitarray = img_as_from_chip[Ellipsis, ::-1]
            img_int = utils.convert_bitarray_to_intarray(bitarray)

            (coarse, fine, gain) = utils.split(img_int)
            img_aggr[Ellipsis, self._i_crs] = coarse
            img_aggr[Ellipsis, self._i_fn] = fine
            img_aggr[Ellipsis, self._i_gn] = gain

            if self._clean_memory:
                del img_as_from_chip

            shape_ref = (n_smpl_rst_x_n_grp,
                         self._n_pad,
                         self._n_pixs_in_blk,
                         self._n_gn_crs_fn)
            # add RefCols (that had been ignored by mezzanine in 2a-scramblig)
            img_aggr_withref = np.zeros(shape_ref).astype('uint8')
            img_aggr_withref[:, 1:, :, :] = img_aggr

            if self._clean_memory:
                del img_aggr

            descrambled_data[i, Ellipsis] = img_aggr_withref

        return descrambled_data

    def _reordering_pixels(self, n_img, imgs_tcpdump, data, rowgrp_check):

        shape_descrambled = (n_img,
                             self._n_smpl_rst * self._n_grp,
                             self._n_pad,
                             self._n_row_in_blk,
                             self._n_col_in_blk,
                             self._n_gn_crs_fn)
        img = np.zeros(shape_descrambled).astype('uint8')

        for i, _ in enumerate(imgs_tcpdump):
            img[i, Ellipsis] = utils.reorder_pixels_gncrsfn(data[i, Ellipsis],
                                                            self._n_adc,
                                                            self._n_col_in_blk)

        # add error tracking for data coming from missing packets
        img = img.astype('int16')  # -256upto255
        for i, _ in enumerate(imgs_tcpdump):
            for igrp in range(self._n_smpl_rst * self._n_grp):
                if rowgrp_check[i, igrp] is False:
                    img[i, igrp, Ellipsis] = self._err_int16

        # error tracking for refCol
        img[:, :, 0, :, :, :] = self._err_int16

        # solving the 1a-part of scrambling:
        # reorder by Smpl,Rst
        shape_smplrst = (n_img,
                         self._n_smpl_rst,
                         self._n_grp,
                         self._n_pad,
                         self._n_row_in_blk,
                         self._n_col_in_blk,
                         self._n_gn_crs_fn)
        img_smplrst = np.zeros(shape_smplrst).astype('int16')

        img_smplrst[:, self._i_smp, 1:, ...] = img[:, 1:(212*2)-1:2, ...]
        img_smplrst[:, self._i_rst, :(-1), ...] = img[:, 2:212*2:2, ...]
        img_smplrst[:, self._i_smp, 0, ...] = img[:, 0, ...]
        img_smplrst[:, self._i_rst, -1, ...] = img[:, -1, ...]

        transpose_order = (0, 1, 2, 4, 3, 5, 6)
        img_smplrst = np.transpose(img_smplrst, transpose_order)
        # new order:
        # (n_img,
        #  Smpl/Rst,
        #  self._n_grp,
        #  self._n_row_in_blk,
        #  self._n_pad,
        #  self._n_col_in_blk,
        #  Gn/Crs/Fn)

        shape_smplrst_split = (n_img,
                               self._n_smpl_rst,
                               self._n_grp * self._n_adc,
                               self._n_pad * self._n_col_in_blk,
                               self._n_gn_crs_fn)
        img_smplrst_split = img_smplrst.reshape(shape_smplrst_split)

        return img_smplrst_split

    def _save_data(self):
        """Save descrambled data to h5 file in the standard format.
        """
        # convert Gn/Crs/Fn => DLSraw: 16bit (errorbit + 15bits)
        if self._verbose:
            msg = ("converting to DLSraw format (uint16-> "
                   "[X, Gn,Gn, Fn,Fn,Fn,Fn,Fn,Fn,Fn,Fn, Crs,Crs,Crs,Crs,Crs])")
            print(Fore.GREEN + msg)

        (sample, reset) = utils.convert_gncrsfn_to_dlsraw(self._result_data,
                                                          self._err_int16,
                                                          self._err_dlsraw)

        self._data_to_write["sample"]["data"] = sample
        self._data_to_write["reset"]["data"] = reset

        self._write_data()
        print(Fore.GREEN + "Data saved to: {}".format(self._output_fname))
