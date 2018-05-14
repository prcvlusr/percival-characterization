from colorama import init, Fore
import numpy as np
import os # to list files in a folder
import sys # to play command line argument, print w/o newline, version
import time # to have time

import APy3_GENfuns # general functions
import APy3_P2Mfuns # P2M-specific functions

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(CURRENT_DIR)
                        )
                    )
                )
           )
SHARED_DIR = os.path.join(BASE_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils


# - - -
#
#%% useful constants
ERRint16 =-256 # negative value usable to track Gn/Crs/Fn from missing pack
ERRBlw = -0.1
ERRDLSraw = 65535 # forbidden uint16, usable to track "pixel" from missing pack
i_gain = 0
i_coarse = 1
i_fine = 2
i_sample = 0
i_reset = 1
# - - -


class Descramble():
    def __init__(self, **kwargs):  # noqa F401

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        print(vars(self))

    def run(self):
        '''
        descrambles tcpdump-binary files, save to h5 in DLSraw standard format

        Here is how data are scrambled:

        1a) the chips send data out interleaving RowGroups
            (7row x (32 Col x 45 pads) ) from Sample/Reset, as:
            Smpl, Smpl,   Smpl, Rst, Smpl, Rst, ... , Smpl, Rst,   Rst, Rst
        1b) the position of pixels (pix0/1/2 in the next point) is mapped to
            the (7row x 32 Col) block according to:
            (ADC,Col)= APy3_P2Mfuns.ADCcolArray_1DA[pix_i]
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

        (note that the args cannot be taken from conf file for the moment.
        we need conf file revision (method-specific args) to pass from conf file.
        args are for the moment defined in the GUI pop-up)

        Args:
            filenamepath_in0/1/2: name of tcpdump scrambled binary files
                Might exist or not
            output_fname: name of h5 descrambled file to generate
            save_file/debugFlag/clean_memory/verbose: no need to explain

        Returns:
            creates a h5 file (if save_file) in DLSraw standard format
                no explicit return()
        '''
        init(autoreset=True)

        start_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        print(Fore.BLUE + "script beginning at {}".format(start_time))

        # general constants for a P2M system
        self._n_adc = self._method_properties["n_adc"] # 7
        self._n_grp = self._method_properties["n_grp"] # 212
        self._n_smpl_rst = APy3_P2Mfuns.NSmplRst # 2
        self._n_pad = self._method_properties["n_pad"] # 45
        self._n_data_pads = self._n_pad - 1 # 44
        self._n_col_in_block = self._method_properties["n_col_in_block"] #32
        self._n_row_in_block = self._n_adc # 7
        self._n_pixs_in_block = self._n_col_in_block * self._n_row_in_block #224
        self._n_bits_in_pix = 15
        self._n_gn_crs_fn = 3

        # tcpdump-related constants
        excess_bytesinfront = 24 # excess Bytes at the beginning of tcpdump file
        gooddata_size = 4928 # UDPacket content in Byte (excluding header)
        fullpack_size = 5040 # UDPacket content in Byte (including header)
        header_size = fullpack_size - gooddata_size # 112
        img_counter = 88 - excess_bytesinfront # also+1
        pack_counter = 90 - excess_bytesinfront # also+1

        n_packs_in_rowgrp = 4 # 1 RowGrp (7x32x44pixel) in in 4 UDPacket
        n_packs_in_img = n_packs_in_rowgrp * self._n_grp * self._n_smpl_rst #1Img (Smpl+Rst)= 1696 UDPacket
        max_n_pack = 1695 # thus packet count is never > 1695
        # - - -

        input_fnames = self._method_properties["input"]
        save_file = self._method_properties["save_file"]
        output_fname = os.path.join(self._method_properties["output"],
                                    "p2018.03.15crdAD_h10_dscrmbld_{}.h5".format(self._run))

        clean_memory = self._method_properties["clean_memory"]
        verbose = self._method_properties["verbose"]

        # report the user-provided args
        if verbose:
            print(Fore.GREEN + 'will load tcpdump files:')

            for fname in input_fnames:
                if os.path.isfile(fname):
                    print(Fore.GREEN + fname)
                else:
                    print(Fore.MAGENTA + ' does not exist')

            if save_file:
                print(Fore.GREEN
                      + 'will save descrambled file: {}'.format(output_fname))

            if clean_memory:
                print(Fore.GREEN + 'will clean memory when possible')

            print(Fore.GREEN + "verbose")
        # - - -

        # solving the 3a-part of scrambling
        # read the tcpdump binary files, cut excess_bytesinfront
        if verbose:
            print(Fore.BLUE + "reading files")

        # checks that at least one of the input files exists
        file_missing = [not os.path.isfile(fname) for fname in input_fnames]
        if all(file_missing):
            msg = "Non of the input files exists"
            print(Fore.RED + msg)
            raise Exception(msg)

        file_content = []
        for fname in input_fnames:
            if os.path.isfile(fname):
                # read uint8 data from binary file
                with open(fname) as f:
                    content = np.fromfile(f, dtype = np.uint8)
                # cut off the excess bytes at the beginning
                content = content[excess_bytesinfront:]
            else:
                content = np.array([]).astype('uint8')

            file_content.append(content)

        n_packets = [len(content) // fullpack_size for content in file_content]

        if verbose:
            print(Fore.GREEN
                  + "data read from files ({}+{} packets)"
                    .format(n_packets[0], n_packets[1]))
        # - - -

        # search for 1st & last image: this is needed to resort the data from
        # the file in a proper array of (n_img, n_pack)
        # also scan for fatal packet error: if a packet has a number > 1695
        # then the data is corrupted
        if verbose:
            print(Fore.BLUE + "scanning files for obvious packet errors")

        first_img = (2**32) - 1
        last_img = 0
        for i, fname in enumerate(input_fnames):
            if os.path.isfile(fname):
                for ipack in range(n_packets[i]):
                    start = ipack * fullpack_size
                    end = (ipack + 1) * fullpack_size
                    file_data = file_content[i][start:end]

                    # the frame (Img) number in this pack header (4-Bytes)
                    bytelist = file_data[img_counter-2:img_counter+2]
                    img = utils.convert_bytelist_to_int(bytelist=bytelist)

                    if img <= first_img:
                        first_img = img
                    if img >= last_img:
                        last_img = img

                    # the packet number in this pack header (2-Bytes)
                    bitlist = file_data[pack_counter:pack_counter+2]
                    pack_nmbr = utils.convert_bitlist_to_int(bitlist=bitlist)

                    if pack_nmbr > max_n_pack: # fatal error in the data
                        msg = ("Inconsistent packet in {}\n"
                               "(packet {}-th in the file is identified as "
                               "pack_nmbr={} > {})").format(input_fnames[i],
                                                            ipack,
                                                            pack_nmbr,
                                                            max_n_pack)
                        print(Fore.RED + msg)
                        raise Exception(msg)

        # if needed, reduce Img2show to the 1st image
        # (the 1st img in the sequence might have a Img_counter number >0)
        imgs_tcpdump = np.arange(first_img, last_img + 1)
        n_img = len(imgs_tcpdump)

        msg = (("The lowest-numbered Img of the sequence is: tcpdump-Image {}\n"
                "The highest-numbered Img of the sequence is: tcpdump-Image {}")
                .format(first_img, last_img))
        print(Fore.GREEN + msg)

        if clean_memory:
            del file_data
        # - - -

        # solving the 2c-part of scrambling
        # resort data from files (assign pack to its Img,Smpl/Rst)
        if verbose:
            print(Fore.BLUE + "resorting packages")

        shape_img_pack = (n_img, 2 * self._n_grp * n_packs_in_rowgrp)

        pack_check = np.zeros(shape_img_pack).astype(bool)
        data = np.zeros(shape_img_pack + (gooddata_size,)).astype('uint8')
        header = np.zeros(shape_img_pack + (header_size,)).astype('uint8')

        for iimg, img_dump in enumerate(imgs_tcpdump):
            if verbose:
                APy3_GENfuns.dot()

            for ifile, _ in enumerate(input_fnames):
                n_packs = len(file_content[ifile]) // fullpack_size
                for ipack in range(n_packs):
                    start = ipack * fullpack_size
                    end = (ipack + 1) * fullpack_size

                    file_data = file_content[ifile][start:end]

                    # if this pack (header) has a Img (frame) number
                    bytel = file_data[img_counter-2:img_counter+2]
                    conv_bytel = utils.convert_bytelist_to_int(bytelist=bytel)

                    if conv_bytel == img_dump:
                        bytel = file_data[pack_counter:pack_counter+2]
                        pack_id = utils.convert_bytelist_to_int(bytelist=bytel)

                        # then save it in the appropriate position
                        data[iimg, pack_id, :] = file_data[header_size:]
                        header[iimg, pack_id, :] = file_data[:header_size]
                        # and flag that (pack,Img) as good
                        pack_check[iimg, pack_id] = True

        if verbose:
            print(Fore.BLUE + " ")

        if clean_memory:
            del file_content

        # missing package detail: (pack,Img) not flagged as good, are missing
        for i, img in enumerate(imgs_tcpdump):
            if verbose:
                missing_packages = np.sum(np.logical_not(pack_check[i, :]))

                if missing_packages < 1:
                    print(Fore.GREEN
                          + "All packets for image {} are there".format(img))
                else:
                    print(Fore.MAGENTA
                          + "{} packets missing from image {}"
                            .format(missing_packages, img))

        # at this point the dsata from the 2 files is ordered in a array of
        # dinesion (n_img, n_pack)
        #
        # 1 rowgrp = 4 packets
        # when a packet is missing, the whole rowgrp is compromised
        # if so, flag the 4-tuple of packets (i.e. the rowgrp), as bad
        rowgrp_check = (pack_check[:,0::4]
                        & pack_check[:,1::4]
                        & pack_check[:,2::4]
                        & pack_check[:,3::4])
        # - - -
        #
        if verbose:
            print(Fore.BLUE + "descrambling images")

        shape_aggr_with_ref = (n_img,
                               self._n_smpl_rst * self._n_grp,
                               self._n_pad,
                               self._n_pixs_in_block,
                               self._n_gn_crs_fn)
        multiImg_aggr_withRef = np.ones(shape_aggr_with_ref).astype('uint8')

        for i, _ in enumerate(imgs_tcpdump):
            if verbose:
                APy3_GENfuns.dot()

            # 4UDP=> 1RowGrp
            new_shape = (self._n_smpl_rst * self._n_grp,
                         n_packs_in_rowgrp * gooddata_size)
            img = data[i, :, :].reshape(new_shape)

            # solving the 2b-part of the scrambing (mezzanine interleaving
            # 32bit-sequences from each pad)
            new_shape_pad = (self._n_smpl_rst * self._n_grp,
                             n_packs_in_rowgrp * gooddata_size // (self._n_data_pads * 32//8),
                             self._n_data_pads,
                             32//8)
            img = img.reshape(new_shape_pad)
            img = img.transpose((0, 2, 1, 3))
            # dimensions of img at this point:
            # (self._n_smpl_rst * self._n_grp,
            #  self._n_data_pads,
            #  n_packs_in_rowgrp * gooddata_size // (self._n_data_pads * 32//8),
            #  32//8)

            new_shape2 = (self._n_smpl_rst * self._n_grp,
                          self._n_data_pads,
                          n_packs_in_rowgrp * gooddata_size // self._n_data_pads)
            img = img.reshape(new_shape2)

            # array of uint8 => array of [x,x,x,x, x,x,x,x] bits
            bitarray = utils.convert_intarray_to_bitarray(img, 8)
            img_8bitted = bitarray[:, :, :, ::-1].astype('uint8')

            shape_8bit = (self._n_smpl_rst * self._n_grp,
                          self._n_data_pads,
                          n_packs_in_rowgrp * gooddata_size // self._n_data_pads,
                          8)
            img_8bitted = img_8bitted.reshape(shape_8bit)

            if clean_memory:
                del img

            shape_16bit = (self._n_smpl_rst * self._n_grp,
                           self._n_data_pads,
                           n_packs_in_rowgrp * gooddata_size // (self._n_data_pads * 2),
                           16)
            # combine 2x8bit to 16bit
            img_16bitted= np.zeros(shape_16bit).astype('uint8')
            img_16bitted[:,:,:,0:8] = img_8bitted[:,:,0::2,:]
            img_16bitted[:,:,:,8:16] = img_8bitted[:,:,1::2,:]

            if clean_memory:
                del img_8bitted

            # solving the 2a-part of scrambling:
            # remove head 0, concatenate and reorder
            # we can remove head 0 because the grps//missing packets are already
            # identified by rowgrp_check
            img_15bitted = img_16bitted[:,:,:,1:]

            if clean_memory:
                del img_16bitted

            shape_15bit = (self._n_smpl_rst * self._n_grp,
                           self._n_data_pads,
                           n_packs_in_rowgrp * gooddata_size * 15 // (self._n_data_pads * 2))
            img_as_from_chip = img_15bitted.reshape(shape_15bit)

            shape_as_from_chip = (self._n_smpl_rst * self._n_grp,
                                  self._n_data_pads,
                                  self._n_bits_in_pix,
                                  self._n_pixs_in_block)
            img_as_from_chip = img_as_from_chip.reshape(shape_as_from_chip)

            if clean_memory:
                del img_15bitted

            # solving the 1d-part if scrambling
            # British Bit translation: 0->1, 1->0
            img_as_from_chip = np.transpose(img_as_from_chip, (0,1,3,2))
            # img_as_from_chip dimension are now
            # (self._n_smpl_rst * self._n_grp,
            #  self._n_data_pads,
            #  n_pixs_in_rowblk,
            #  self._n_bits_in_pix)

            # 0=>1, 1=>0
            img_as_from_chip = utils.swap_bits(bitarray=img_as_from_chip)

            shape_img_aggr = (self._n_smpl_rst * self._n_grp,
                              self._n_data_pads,
                              self._n_pixs_in_block,
                              self._n_gn_crs_fn)
            img_aggr= np.zeros(shape_img_aggr).astype('uint8')

            # solving the 1c-part if scrambling:
            # binary aggregate to gain/coarse/fine
            bitarray = img_as_from_chip[Ellipsis,::-1]
            img_int = utils.convert_bitarray_to_intarray(bitarray)

            (coarse, fine, gain) = utils.split(img_int)
            img_aggr[Ellipsis, i_coarse] = coarse
            img_aggr[Ellipsis, i_fine] = fine
            img_aggr[Ellipsis, i_gain] = gain

            if clean_memory:
                del img_as_from_chip

            shape_ref = (self._n_smpl_rst * self._n_grp,
                         self._n_pad,
                         self._n_pixs_in_block,
                         self._n_gn_crs_fn)
            # add RefCols (that had been ignored by mezzanine in 2a-scramblig)
            img_aggr_withref = np.zeros(shape_ref).astype('uint8')
            img_aggr_withref[:, 1:, :, :] = img_aggr

            if clean_memory:
                del img_aggr

            multiImg_aggr_withRef[i, Ellipsis] = img_aggr_withref

        if clean_memory:
            del img_aggr_withref

        if verbose:
            print(Fore.BLUE + " ")
        # - - -


        # solving the 1b-part if scrambling:
        # reorder pixels and pads
        if verbose:
            print(Fore.BLUE + "reordering pixels")

        shape_descrambled = (n_img,
                             self._n_smpl_rst * self._n_grp,
                             self._n_pad,
                             self._n_row_in_block,
                             self._n_col_in_block,
                             self._n_gn_crs_fn)
        img_grp_descrambled= np.zeros(shape_descrambled).astype('uint8')

        for i, _ in enumerate(imgs_tcpdump):
            img_grp_descrambled[i,Ellipsis] = APy3_P2Mfuns.reorder_pixels_GnCrsFn(
                    multiImg_aggr_withRef[i, Ellipsis],
                    self._n_adc,
                    self._n_col_in_block)

        # add error tracking for data coming from missing packets
        img_grp_descrambled = img_grp_descrambled.astype('int16') # -256upto255
        for i, _ in enumerate(imgs_tcpdump):
            for igrp in range(self._n_smpl_rst * self._n_grp):
                if (rowgrp_check[i, igrp] == False):
                    img_grp_descrambled[i, igrp, Ellipsis] = ERRint16

        # error tracking for refCol
        img_grp_descrambled[:,:,0,:,:,:] = ERRint16

        # solving the 1a-part if scrambling:
        # reorder by Smpl,Rst
        shape_smplrst= (n_img,
                        self._n_smpl_rst,
                        self._n_grp,
                        self._n_pad,
                        self._n_row_in_block,
                        self._n_col_in_block,
                        self._n_gn_crs_fn)
        img_smplrst = np.zeros(shape_smplrst).astype('int16')

        img_smplrst[:, i_sample, 1:, Ellipsis] = img_grp_descrambled[:, 1:(212*2)-1:2, Ellipsis]
        img_smplrst[:, i_reset, :(-1), Ellipsis] = img_grp_descrambled[:, 2:212*2:2, Ellipsis]
        img_smplrst[:, i_sample, 0, Ellipsis] = img_grp_descrambled[:, 0, Ellipsis]
        img_smplrst[:, i_reset, -1, Ellipsis] = img_grp_descrambled[:, -1, Ellipsis]

        img_smplrst = np.transpose(img_smplrst,(0,1,2,4,3,5,6)).astype('int16')
        # new order:
        # (n_img,
        #  Smpl/Rst,
        #  self._n_grp,
        #  self._n_row_in_block,
        #  self._n_pad,
        #  self._n_col_in_block,
        #  Gn/Crs/Fn)

        shape_smplrst_split = (n_img,
                               self._n_smpl_rst,
                               self._n_grp * self._n_adc,
                               self._n_pad * self._n_col_in_block,
                               self._n_gn_crs_fn)
        img_smplrst_split = img_smplrst.reshape(shape_smplrst_split)

        if clean_memory:
            del img_smplrst
        # - - -

        # convert Gn/Crs/Fn => DLSraw: 16bit (errorbit + 15bits)
        if verbose:
            msg = ("converting to DLSraw format (uint16-> "
                   "[X, Gn,Gn, Fn,Fn,Fn,Fn,Fn,Fn,Fn,Fn, Crs,Crs,Crs,Crs,Crs])")
            print(Fore.GREEN + msg)

        (dscrmbld_smpl_dlsraw,
         dscrmbld_rst_dlsraw) = APy3_P2Mfuns.convert_GnCrsFn_2_DLSraw(
                                img_smplrst_split,
                                ERRint16,
                                ERRDLSraw)

        if clean_memory:
            del img_smplrst_split
        # - - -

        # save descrambled data to h5 file in the standard format
        if save_file:
            APy3_GENfuns.write_2xh5(output_fname,
                                    dscrmbld_smpl_dlsraw, '/data/',
                                    dscrmbld_rst_dlsraw, '/reset/')
            print(Fore.GREEN + 'data saved to: '+ output_fname)

            if clean_memory:
                del dscrmbld_smpl_dlsraw
                del dscrmbld_rst_dlsraw
        # - - -

        # show saved data if debug-requested
        if save_file:
            (reread_smpl,
             reread_rst)= APy3_GENfuns.read_2xh5(output_fname,
                                                 '/data/', '/reset/')

            # DLSraw->Gn/Crs/Fn
            (n_img, n_row, n_col) = reread_smpl.shape
            shape_smplrst2 = (n_img,
                              self._n_smpl_rst,
                              n_row,
                              n_col)
            reread_smplrst = np.zeros(shape_smplrst2).astype('uint16')
            reread_gn_crs_fn = np.zeros(shape_smplrst2
                                        + (self._n_gn_crs_fn,)).astype('int16')
            reread_smplrst[:, i_sample, :, :] = reread_smpl
            reread_smplrst[:, i_reset, :, :] = reread_rst

            (coarse, fine, gain) = utils.split(reread_smplrst)
            reread_gn_crs_fn[Ellipsis, i_gain] = gain
            reread_gn_crs_fn[Ellipsis, i_coarse] = coarse
            reread_gn_crs_fn[Ellipsis, i_fine] = fine

            # tracking missing-packet pixels by setting Gn/Crs/Fn to -256
            errormap = reread_smplrst == ERRDLSraw
            reread_gn_crs_fn[errormap,:] = ERRint16

            if clean_memory:
                del reread_smpl
                del reread_rst
        # - - -

        # that's all folks
        print("------------------------")
        print("done")
        stop_time = time.strftime("%Y_%m_%d__%H:%M:%S")
        print(Fore.BLUE + "script ended at {}".format(stop_time))
        print("------------------------\n" * 3)
