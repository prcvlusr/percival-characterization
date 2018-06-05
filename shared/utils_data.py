"""Utilities for data handling.
"""
import numpy as np


def decode_dataset_8bit(arr_in, bit_mask, bit_shift):
    """Masks out bits and shifts.

    For every entry in the input array is the undelying binary representation
    of the integegers the bit-wise AND is computed with the bit mask.
    Bit wise AND means:
    e.g. number 13 in binary representation: 00001101
         number 17 in binary representation: 00010001
         The bit-wise AND of these two is:   00000001, or 1
    Then the result if shifted and converted to uint8.

    Args:
        arr_in: Array to decode.
        bit_mask: Bit mask to apply on the arra.
        bit_shift: How much the bits should be shifted.

    Return:
        Array where for each entry in the input array the bit mask is applied,
        the result is shifted and converted to uint8.

    """

    arr_out = np.bitwise_and(arr_in, bit_mask)
    arr_out = np.right_shift(arr_out, bit_shift)
    arr_out = arr_out.astype(np.uint8)

    return arr_out


def convert_bitlist_to_int(bitlist):
    """Converts a list of bits into int.
    Args:
        bitlist (list): A list of bites to convert.

    Return:
        The converted int.
    """
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out


def convert_bytelist_to_int(bytelist, byteorder='big'):
    """Converts a list of bytes into int.
    Args:
        bitlist (list): A list of bytes to convert.

    Return:
        The converted int.
    """
    value = int.from_bytes(bytes(bytelist), byteorder=byteorder)

    return value


def convert_intarray_to_bitarray(in_array, n_bits):
    """Convert numpyarray of uint => array of n_bits bits

    Args:
        in_array: array to convert
        n_bits: number of bits to convert to

    Return:
        Array where the entries where converted.
    """
    in_shape = in_array.shape
    in_array_flat = in_array.flatten()
    out = np.zeros((len(in_array_flat), n_bits))

    for i in range(n_bits):
        out[:, i] = (in_array_flat >> i) & 1

    out = out.reshape(in_shape + (n_bits,))

    return out


def convert_bitarray_to_intarray(bitarray):
    """Convert (numpyarray of [... , ... , n_bits] => array of [... , ... ](int)

    Args:
        bitarray: Bitarray to convert
    """

    shape = bitarray.shape
    n_bits = shape[-1]

    power_matr = np.ones(shape).astype(int)
    power_matr *= (2**np.arange(n_bits)).astype(int)

    out = np.sum(bitarray * power_matr, axis=len(shape)-1).astype(int)

    return out


def swap_bits(bitarray):
    """Swaps bits: 0=>1 , 1=>0

    Args:
        bitarray: array or bit which should be swapped.

    Return:
        Array with swapped entries or swapped bit.
    """
    return 1 - bitarray


def convert_slice_to_tuple(item):
    """Converts an index to something usable in documentation.
    Args:
        item (slice or int): The slice to convert.
    Return:
        The slice is converted into a tuple or None if it does not have any values.
        If item was an int nothing is done.
    """

    if item == slice(None):
        new_item = None
    elif type(item) == slice:
        if item.step == None:
            new_item = (item.start, item.stop)
        else:
            new_item = (item.start, item.stop, item.step)
    else:
        new_item = item

    return new_item


def split_alessandro(raw_dset):
    """Extracts the coarse, fine and gain bits.

    Readout bit number
    15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
    C0  C1  C2  C3  C4  F0  F1  F2  F3  F4  F5  F6  F7  B0  B1  -
    ADC bit numbers

    C: ADC coarse
    F: ADC fine
    B: Gain bit

    Args:
        raw_dset: Array containing 16 bit entries.

    Return:
        Each a coarse, fine and gain bit array.

    """

    # 0xF800 -> 1111100000000000
    coarse_adc = decode_dataset_8bit(arr_in=raw_dset,
                                     bit_mask=0xF800,
                                     bit_shift=1+2+8)

    # 0x07F8 -> 0000011111111000
    fine_adc = decode_dataset_8bit(arr_in=raw_dset,
                                   bit_mask=0x07F8,
                                   bit_shift=1+2)

    # 0x0006 -> 0000000000000110
    gain_bits = decode_dataset_8bit(arr_in=raw_dset,
                                    bit_mask=0x0006,
                                    bit_shift=1)

    return coarse_adc, fine_adc, gain_bits


def split_ulrik(raw_dset):
    """Extracts the coarse, fine and gain bits.

    Readout bit number
    15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
    -   C0  C1  C2  C3  C4  F0  F1  F2  F3  F4  F5  F6  F7  B0  B1
    ADC bit numbers

    C: ADC coarse
    F: ADC fine
    B: Gain bit

    Args:
        raw_dset: Array containing 16 bit entries.

    Return:
        Each a coarse, fine and gain bit array.

    """

    # 0x7C00 -> 0111110000000000
    coarse_adc = decode_dataset_8bit(arr_in=raw_dset,
                                     bit_mask=0x7C00,
                                     bit_shift=2+8)

    # 0x03FC -> 0000001111111100
    fine_adc = decode_dataset_8bit(arr_in=raw_dset,
                                   bit_mask=0x03FC,
                                   bit_shift=2)

    # 0x0003 -> 0000000000000011
    gain_bits = decode_dataset_8bit(arr_in=raw_dset,
                                    bit_mask=0x0003,
                                    bit_shift=0)

    return coarse_adc, fine_adc, gain_bits


def split(raw_dset):
    """Extracts the coarse, fine and gain bits.

    Readout bit number
    0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
    -   B0  B1  F0  F1  F2  F3  F4  F5  F6  F7  C0  C1  C2  C3  C4
    ADC bit numbers

    C: ADC coarse (5 bit)
    F: ADC fine (8 bit)
    B: Gain bit (2 bit)

    Args:
        raw_dset: Array containing 16 bit entries.

    Return:
        Each a coarse, fine and gain bit array.

    """

    # 0x1F   -> 0000000000011111
    coarse_adc = decode_dataset_8bit(arr_in=raw_dset,
                                     bit_mask=0x1F,
                                     bit_shift=0)

    # 0x1FE0 -> 0001111111100000
    fine_adc = decode_dataset_8bit(arr_in=raw_dset,
                                   bit_mask=0x1FE0,
                                   bit_shift=5)

    # 0x6000 -> 0110000000000000
    gain_bits = decode_dataset_8bit(arr_in=raw_dset,
                                    bit_mask=0x6000,
                                    bit_shift=5+8)

    return coarse_adc, fine_adc, gain_bits


def get_adc_col_array(n_adc=7, n_xcols=4, n_ncols=8):
    """Get the ADC column array.
    """
    cols = np.arange(n_xcols * n_ncols)
    cols = cols.reshape((n_xcols, n_ncols))
    cols = cols.transpose()
    cols = np.fliplr(cols)  # in the end it is cols[ix,in]

    # this gives the (i_adc, i_col) indices of a pixel in a Rowblk, given
    # its sequence in the streamout
    adc_cols = []
    for i_n in range(n_ncols):
        for i_adc in range(n_adc)[::-1]:
            for i_x in range(n_xcols):
                adc_cols += [(i_adc, cols[i_n, i_x])]

    # to use this:
    # for ipix in range(32*7):
    #     (ord_adc, ord_col) = adc_cols[ipix]
    adc_cols = np.array(adc_cols)

    return adc_cols


def get_col_grp():
    """Get column groups
    """
    i_g = np.array(0)
    i_h0 = np.arange(21+1, 0+1-1, -1)
    i_h1 = np.arange(22+21+1, 22+0+1-1, -1)

    col_grp = np.append(i_g, i_h0)
    col_grp = np.append(col_grp, i_h1)

    return col_grp


def reorder_pixels_gncrsfn(in_data, n_adc, n_col_in_row_blk):
    """ P2M pixel reorder for a image.

    (n_grp, n_pads, n_adc * n_col_in_row_blk, 3), disordered
    => (n_grp, n_pads, n_adc, n_col_in_row_blk, 3), ordered

    """

    (n_grp, n_pads, _, n_gncrsfn) = in_data.shape
    adc_cols = get_adc_col_array()
    col_grp = get_col_grp()

    output_shape = (n_grp, n_pads, n_adc, n_col_in_row_blk, n_gncrsfn)
    out_data = np.zeros(output_shape).astype('uint8')
    pix_sorted = np.zeros(output_shape).astype('uint8')

    # pixel reorder inside each block
    for i in range(n_adc * n_col_in_row_blk):
        (ord_adc, ord_col) = adc_cols[i]
        pix_sorted[:, :, ord_adc, ord_col, :] = in_data[:, :, i, :]

    # ColGrp order from chipscope to P2M
    for i in range(n_pads):
        out_data[:, i, :, :, :] = pix_sorted[:, col_grp[i], :, :, :]

    return out_data


def convert_gncrsfn_to_dlsraw(in_data,
                              in_err,
                              out_err,
                              indices=(0, 1, 0, 1, 2)):
    """ Converts gain, coarse and fine data sets.

    (Nimg, Smpl/Rst, NRow, NCol, Gn/Crs/Fn), int16(err=in_err)
    => DLSraw: Smpl&Rst(Nimg,NRow,NCol), uint16(err=out_err)
               [X,GG,FFFFFFFF,CCCCC]

    Args:
        in_data (array): Data to convert.
                         Shape: (n_img, smpl/rst, n_row, n_col, gn/crs/fn)
        in_err (int): Value to detect errors in the input data.
        out_err: (int): The value to which the data with errors should be set
                        to in the output data.
        idices (tuple, optional): Location of sample/reset and
                                  coarse/gfine/gain in the input array.
                                  (i_smpl, i_rst, i_gn, i_crs, i_fn)

    Return:
        Two numpy arrays (sample and reset) where the coarse fine and gain
        are converted into one int.
    """

    (i_smpl, i_rst, i_gn, i_crs, i_fn) = indices

    data = np.clip(in_data, 0, (2**8)-1)
    data = data.astype('uint16')

    # convert to DLSraw format
    sample = ((2**13) * data[:, i_smpl, :, :, i_gn]
              + (2**5) * data[:, i_smpl, :, :, i_fn]
              + data[:, i_smpl, :, :, i_crs])

    reset = ((2**13) * data[:, i_rst, :, :, i_gn]
             + ((2**5) * data[:, i_rst, :, :, i_fn])
             + data[:, i_rst, :, :, i_crs])

    # track errors in DLSraw mode with the ERRDLSraw (max of uint16) value
    # (usually this in not reached because pixel= 15 bit)
    err_mask = in_data[:, i_smpl, :, :, i_gn] == in_err
    sample[err_mask] = out_err

    err_mask = in_data[:, i_rst, :, :, i_gn] == in_err
    reset[err_mask] = out_err

    return sample, reset
