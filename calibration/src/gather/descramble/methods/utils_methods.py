import os  # to list files in a directory
import sys  # print special functions
import time  # to have time
import h5py
import numpy as np
import matplotlib.pyplot as plt
import itertools
from scipy import stats  # linear regression

from utils import split as aggregate_crsfngn  # aggregate bits to crs,fn,gn

# useful global constants
n_adc = 7
n_row_in_blk = n_adc
n_col_in_blk = 32
n_grp = 212
n_pad = 45
n_data_pads = n_pad - 1  # 44

n_col_p2m = n_col_in_blk * n_pad
n_row_p2m = n_adc * n_grp

n_smplrst = 2
n_gncrsfn = 3
ismpl = 0
irst = 1
ign = 0
icrs = 1
ifn = 2

err_dlsraw = (2**16)-1
err_gncrsfn = -256

# from P2M manual : pixel scrambling
n_xcol_array = 4
n_ncol_array = 8
col_array = np.arange(n_xcol_array * n_ncol_array).reshape(
    (n_xcol_array, n_ncol_array)).transpose()
col_array = np.fliplr(col_array)  # in the end it is col_array[ix,in]
# this gives the (iADC,iCol) indices of a pixel in a Rowblk,
# given its sequence in the streamout
adc_col_array_1d = []
for i_n in range(n_ncol_array):
    for i_adc in range(7)[::-1]:
        for i_x in range(n_xcol_array):
            adc_col_array_1d += [(i_adc, col_array[i_n, i_x])]
adc_col_array_1d = np.array(adc_col_array_1d)
# to use this: for ipix in range(32*7):
#                  (ord_adc,ord_adc)=adc_col_array_1d[ipix]

# from P2M manual : pad order
i_g = 0
i_h0 = np.arange(21+1, 0+1-1, -1)
i_h1 = np.arange(22+21+1, 22+0+1-1, -1)
ip2m_colgrp = np.append(np.array(i_g), i_h0)
ip2m_colgrp = np.append(ip2m_colgrp, i_h1)


# NOO functions: print
def dot():
    '''print a dot '''
    sys.stdout.write(".")
    sys.stdout.flush()  # print it now


def printcol(string2print, colour):
    ''' write in colour (red/green/orange/blue/purple) '''
    white = '\033[0m'  # white (normal)
    if (colour == 'black'):
        outcolor = '\033[30m'  # black
    elif (colour == 'red'):
        outcolor = '\033[31m'  # red
    elif (colour == 'green'):
        outcolor = '\033[32m'  # green
    elif (colour == 'orange'):
        outcolor = '\033[33m'  # orange
    elif (colour == 'blue'):
        outcolor = '\033[34m'  # blue
    elif (colour == 'purple'):
        outcolor = '\033[35m'  # purple
    else:
        outcolor = '\033[30m'
    print(outcolor + string2print + white)
    sys.stdout.flush()  # print it now


# NOO functions: natural sorting
def atoi(text):
    ''' needed for natural sorting '''
    return int(text) if text.isdigit() else text


def natural_keys(text):
    ''' needed for natural sorting '''
    return [atoi(c) for c in re.split('(\d+)', text)]


def sort_nicely(my_list):
    '''
    natural sorting of a list of strings with numbers
    ['a0','a1','a2',...,'a10','a11',...]
    '''
    my_list.sort(key=natural_keys)


# NOO functions: general utilities
def list_files(folderpath, expected_prefix, expected_suffix):
    '''
    look for files in directory having the expected prefix and suffix
    ('*' to have any)
    '''
    anyfix = '*'
    allfiles_list = os.listdir(folderpath)
    out_file_list = []
    for thisfile in allfiles_list:
        if ((expected_prefix == anyfix) & (expected_suffix == anyfix)):
            out_file_list.append(thisfile)
        elif ((expected_prefix == anyfix) &
              (expected_suffix != anyfix) &
              (thisfile.endswith(expected_suffix))):
            out_file_list.append(thisfile)
        elif ((expected_prefix != anyfix) &
              (expected_suffix == anyfix) &
              (thisfile.startswith(expected_prefix))):
            out_file_list.append(thisfile)
        elif ((expected_prefix != anyfix) &
              (expected_suffix != anyfix) &
              (thisfile.endswith(expected_suffix)) &
              (thisfile.startswith(expected_prefix))):
            out_file_list.append(thisfile)
    sort_nicely(out_file_list)  # natural sorting
    return out_file_list


def find_mostcommon_uint(array2search, minval, maxval):
    '''
    which value appears most often, shile being >=minval and <= maxval
    all values need to be int>=0
    '''
    reducedindices = np.where(np.logical_and(array2search >= minval,
                                             array2search <= maxval))
    reducedarray = array2search[reducedindices]
    aux_counts = np.bincount(reducedarray)
    if len(aux_counts) > 0:
        mostcommon_val = np.argmax(aux_counts)
        err_flag = False
    else:
        mostcommon_val = -1
        err_flag = True

    return (mostcommon_val, err_flag)


# NOO functions: conversions
def convert_uint_2_bits_ar(in_int_ar, n_bits):
    ''' convert (numpyarray of uint to array of n_bits bits)
    for many bits in parallel '''
    insize_t = in_int_ar.shape
    in_int_ar_flat = in_int_ar.flatten()
    out_n_bit_ar = np.zeros((len(in_int_ar_flat), n_bits))
    for i_bits in range(n_bits):
        out_n_bit_ar[:, i_bits] = (in_int_ar_flat >> i_bits) & 1
    out_n_bit_ar = out_n_bit_ar.reshape(insize_t+(n_bits,))
    return out_n_bit_ar


def convert_bits_2_int_ar(in_bit_arr):
    ''' convert (numpyarray of [... , ... , n_bits] to
    array of [... , ... ](int) for many values in parallel'''
    insize_t = in_bit_arr.shape
    n_bits = insize_t[-1]
    out_size_t = insize_t[0:-1]
    out_int_ar = np.zeros(out_size_t)
    power2matrix = (2**np.arange(n_bits)).astype(int)
    aux_power_matr = power2matrix * np.ones(insize_t).astype(int)
    totalvector_xd_ar = np.sum(in_bit_arr*aux_power_matr, axis=len(insize_t)-1)
    out_int_ar = totalvector_xd_ar.astype(int)
    return out_int_ar


def convert_hex_byteswap_ar(data2convert_ar):
    ''' interpret the ints in an array as 16 bits.
    byte-swap them: (byte0,byte1) => (byte1,byte0) '''
    aux_bitted = convert_uint_2_bits_ar(data2convert_ar, 16).astype('uint8')
    aux_byteinverted = np.zeros_like(aux_bitted).astype('uint8')
    #
    aux_byteinverted[..., 0:8] = aux_bitted[..., 8:16]
    aux_byteinverted[..., 8:16] = aux_bitted[..., 0:8]
    data_byteswapped_ar = convert_bits_2_int_ar(aux_byteinverted)
    return (data_byteswapped_ar)


def convert_britishbits_ar(britishbit_array):
    " 0=>1 , 1=>0 "
    humanreadable_bitarray = 1 - britishbit_array
    return humanreadable_bitarray


# NOO functions: files
def read_tst(filenamepath):
    ''' read tab-separated-text file'''
    out_data = np.genfromtxt(filenamepath, delimiter='\t', dtype=str)
    return out_data


def write_tst(filenamepath, data):
    '''  write text in tab-separated-texts file '''
    np.savetxt(filenamepath, data, delimiter='\t', fmt='%s')


def read_csv(filenamepath):
    ''' read numerical data from csv '''
    my_data = np.genfromtxt(filenamepath, delimiter=',')
    return my_data


def write_csv(filenamepath, data):
    ''' write numerical data from csv '''
    np.savetxt(filenamepath, data, fmt='%f', delimiter=",")


def read_binary(filenamepath):
    ''' read data from binary file '''
    thisfile = open(filenamepath, 'rb')
    fileContent = thisfile.read()
    thisfile.close()
    return fileContent


def read_2xh5(filenamepath, path1_2read, path2_2read):
    ''' read 2xXD h5 file (paths_2read: '/data/','/reset/' ) '''
    with h5py.File(filenamepath, "r", libver='latest') as my5hfile:
        my_data1 = np.array(my5hfile[path1_2read])
        my_data2 = np.array(my5hfile[path2_2read])
        my5hfile.close()
    return (my_data1, my_data2)


def read_1xh5(filenamepath, path_2read):
    ''' read h5 file: data in path_2read '''
    my5hfile = h5py.File(filenamepath, 'r')
    myh5dataset = my5hfile[path_2read]
    my_data_out = np.array(myh5dataset)
    my5hfile.close()
    return my_data_out


def write_1xh5(filenamepath, data2write, path_2write):
    ''' write h5 file: data in path_2write '''
    my5hfile = h5py.File(filenamepath, 'w')
    my5hfile.create_dataset(path_2write, data=data2write)
    my5hfile.close()


def write_2xh5(filenamepath,
               data1_2write, path1_2write,
               data2_2write, path2_2write):
    ''' write 2xXD h5 file (paths_2write: '/data/','/reset/' ) '''
    with h5py.File(filenamepath, "w", libver='latest') as my5hfile:
        my5hfile.create_dataset(path1_2write, data=data1_2write)
        my5hfile.create_dataset(path2_2write, data=data2_2write)
        my5hfile.close()


# NOO functions: plots
def plot_multi1d_withmask(array_x, array_y_2d, mask_2d, info_list,
                          label_x, label_y, label_title, showline_flag):
    """ plot1D multiple datasets (array_x[:], array_y_2d[:,i]) ,
        identified by info_list[i] (use only values are True in
        mask2D[:,i])"""
    fig = plt.figure()
    marker = itertools.cycle(('o', '*', '+', '.', '^', 'v', '>', '<'))
    for i_set, this_set in enumerate(info_list):
        reduced_x = array_x[mask_2d[:, i_set]]
        reduced_y = array_y_2d[:, i_set][mask_2d[:, i_set]]
        if showline_flag:
            plt.plot(reduced_x, reduced_y, linestyle='-',
                     marker=marker.__next__(), fillstyle='none')
        else:
            plt.plot(reduced_x, reduced_y, linestyle='',
                     marker=marker.__next__(), fillstyle='none')
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title(label_title)
    plt.legend(info_list, loc='upper right')
    plt.show(block=False)
    return fig


def plot_multi1d(array_x, array_y_2d, info_list,
                 label_x, label_y, label_title, showline_flag):
    """ plot1D multiple datasets (arrayX[:], arrayY_2D[:,i]) ,
        identified by infoSets_List[i] """
    fakemask_2d = np.ones_like(array_y_2d).astype(bool)
    fig = plot_multi1d_withmask(array_x, array_y_2d, fakemask_2d, info_list,
                                label_x, label_y, label_title, showline_flag)
    return fig


def plot_multihist_withmask(array_y_2d, mask_2d, histobins, info_list,
                            label_x, label_y, label_title):
    """ plot multiple histograms (array_y_2d[:,i]) ,
        identified by info_list[i] (use only values are True in
        mask2D[:,i])"""
    fig = plt.figure()
    for i_set, this_set in enumerate(info_list):
        reduced_y = array_y_2d[:, i_set][mask_2d[:, i_set]]
        plt.hist(reduced_y, histobins, alpha=0.5,
                 label=info_list[i_set])
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title(label_title)
    plt.legend(info_list, loc='upper right')
    plt.show(block=False)
    return fig


def plot_2d(array_2d, label_x, label_y, label_title,
            invertx_flag, rst_fn):
    ''' 2D image , mark as error (white) the values << rst_fn'''
    cmap = plt.cm.jet
    cmap.set_under(color='white')
    fig = plt.figure()
    plt.imshow(array_2d, interpolation='none', cmap=cmap, vmin=rst_fn)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title(label_title)
    plt.colorbar()
    if invertx_flag:
        plt.gca().invert_xaxis()
    plt.show(block=False)
    return (fig)


# P2M specific functions
def reorder_pixels_gncrsfn(disord_4d_ar, n_adc, n_col_in_rowblk):
    ''' P2M pixel reorder for a image:
    (NGrp,NDataPads,n_adc*n_col_in_rowblk,3),disordered =>
    (NGrp,NDataPads,n_adc,n_col_in_rowblk,3),ordered '''
    (aux_n_grp, aux_n_pads, aux_pix_in_blk, aux_n_gncrsfn) = disord_4d_ar.shape
    ord_5d_ar = np.zeros((aux_n_grp, aux_n_pads, n_adc, n_col_in_rowblk,
                         aux_n_gncrsfn)).astype('uint8')
    aux_pixord_paddisord_5d_ar = np.zeros((aux_n_grp, aux_n_pads, n_adc,
                                          n_col_in_rowblk,
                                          aux_n_gncrsfn)).astype('uint8')
    # pixel reorder inside each block
    for ipix in range(n_adc * n_col_in_rowblk):
        (ord_adc, ord_col) = adc_col_array_1d[ipix]
        aux_pixord_paddisord_5d_ar[
            :, :, ord_adc, ord_col,
            :] = disord_4d_ar[:, :, ipix, :]
    # ColGrp order from chipscope to P2M
    for i_colgrp in range(aux_n_pads):
        ord_5d_ar[
            :, i_colgrp, :, :,
            :] = aux_pixord_paddisord_5d_ar[:, ip2m_colgrp[i_colgrp],
                                            :, :, :]
    return ord_5d_ar


def convert_dlsraw_2_gncrsfn(smpl_dlsraw, rst_dlsraw, verbose_flag):
    ''' 2x(Img,Row,Col) of uint16 => (Img,Smpl/Rst,Row,Col,Gn/Crs/Fn)'''
    (aux_n_img, aux_n_col, aux_n_row) = smpl_dlsraw.shape
    out_gncrsfn = np.zeros((aux_n_img, n_smplrst,
                            aux_n_col, aux_n_row, n_gncrsfn)).astype('int16')
    for i_img in range(aux_n_img):
        if verbose_flag:
            dot()
        (auxcrs, auxfn, auxgn) = aggregate_crsfngn(smpl_dlsraw[i_img, :, :])
        out_gncrsfn[i_img, ismpl, :, :, ign] = auxgn
        out_gncrsfn[i_img, ismpl, :, :, icrs] = auxcrs
        out_gncrsfn[i_img, ismpl, :, :, ifn] = auxfn

        errorMap = smpl_dlsraw[i_img, :, :] == err_dlsraw
        out_gncrsfn[i_img, ismpl, errorMap, :] = err_gncrsfn

        (auxcrs, auxfn, auxgn) = aggregate_crsfngn(rst_dlsraw[i_img, :, :])
        out_gncrsfn[i_img, irst, :, :, ign] = auxgn
        out_gncrsfn[i_img, irst, :, :, icrs] = auxcrs
        out_gncrsfn[i_img, irst, :, :, ifn] = auxfn

        errorMap = rst_dlsraw[i_img, :, :] == err_dlsraw
        out_gncrsfn[i_img, irst, errorMap, :] = err_gncrsfn
    if verbose_flag:
        print(" ")
        sys.stdout.flush()

    return out_gncrsfn


def convert_gncrsfn_2_dlsraw(in_gncrsfn_int16, verbose_flag):
    ''' (Nimg,Smpl/Rst,NRow,NCol,Gn/Crs/Fn),int16(err=err_gncrsfn) =>
    DLSraw: Smpl&Rst(Nimg,NRow,NCol),uint16(err=err_dlsraw):[X,2G,8F,5C]'''
    multiimg_smplrstgncrsfn_u16 = np.clip(
        in_gncrsfn_int16, 0, (2**8) - 1)
    multiimg_smplrstgncrsfn_u16 = multiimg_smplrstgncrsfn_u16.astype('uint16')
    # convert to DLSraw format
    if verbose_flag:
        dot()

    (n_img, aux_n_smplrst, aux_n_row,
     aux_n_col, aux_n_gncrsfn) = in_gncrsfn_int16.shape
    out_multiimg_smpl_dlsraw = np.zeros(
        (n_img, n_grp * n_row_in_blk,
         n_pad * n_col_in_blk)).astype('uint16')
    out_multiimg_rst_dlsraw = np.zeros(
        (n_img, n_grp * n_row_in_blk,
         n_pad * n_col_in_blk)).astype('uint16')

    if verbose_flag:
        dot()

    out_multiimg_smpl_dlsraw[
        :, :, :] = ((2**13)*multiimg_smplrstgncrsfn_u16[
            :, ismpl, :, :, ign].astype('uint16')) + (
                (2**5) * multiimg_smplrstgncrsfn_u16[
                    :, ismpl, :, :,
                    ifn].astype(
                        'uint16')) + multiimg_smplrstgncrsfn_u16[
                            :, ismpl, :, :, icrs].astype('uint16')

    if verbose_flag:
        dot()

    out_multiimg_rst_dlsraw[
        :, :, :] = ((2**13) * multiimg_smplrstgncrsfn_u16[
            :, irst, :, :, ign].astype('uint16')) + (
                (2**5) * multiimg_smplrstgncrsfn_u16[
                    :, irst, :, :,
                    ifn].astype(
                        'uint16')) + multiimg_smplrstgncrsfn_u16[
                            :, irst, :, :, icrs].astype('uint16')

    # track errors in DLSraw mode with the err_dlsraw (max of uint16)
    err_mask = in_gncrsfn_int16[:, ismpl, :, :, ign] == err_gncrsfn
    out_multiimg_smpl_dlsraw[err_mask] = err_dlsraw
    err_mask = in_gncrsfn_int16[:, irst, :, :, ign] == err_gncrsfn
    out_multiimg_rst_dlsraw[err_mask] = err_dlsraw

    if verbose_flag:
        print(" ")
        sys.stdout.flush()

    #
    return (out_multiimg_smpl_dlsraw, out_multiimg_rst_dlsraw)


def perc_plot_6x2d(smpl_gn, smpl_crs, smpl_fn,
                   rst_gn, rst_crs, rst_fn,
                   label_title, err_below):
    """ 2D plot of Smpl/Rst, Gn/Crs/Fn, white values << err_below """
    cmap = plt.cm.jet
    cmap.set_under(color='white')
    # fig = plt.figure(figsize=(18,12))
    fig = plt.figure()
    fig.canvas.set_window_title(label_title)
    label_x = "col"
    label_y = "row"
    #
    plt.subplot(2, 3, 1)
    plt.imshow(smpl_gn, interpolation='none', cmap=cmap, vmin=err_below)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title('Sample Gain')
    plt.clim(0, 3)
    plt.colorbar()
    plt.gca().invert_xaxis()
    #
    plt.subplot(2, 3, 2)
    plt.imshow(smpl_crs, interpolation='none', cmap=cmap, vmin=err_below)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title('Sample Coarse')
    plt.clim(0, 31)
    plt.colorbar()
    plt.gca().invert_xaxis()
    #
    plt.subplot(2, 3, 3)
    plt.imshow(smpl_fn, interpolation='none', cmap=cmap, vmin=err_below)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title('Sample Fine')
    plt.clim(0, 255)
    plt.colorbar()
    plt.gca().invert_xaxis()
    #
    plt.subplot(2, 3, 4)
    plt.imshow(rst_gn, interpolation='none', cmap=cmap, vmin=err_below)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title('Reset Gain (not relevant)')
    plt.clim(0, 3)
    plt.colorbar()
    plt.gca().invert_xaxis()
    #
    plt.subplot(2, 3, 5)
    plt.imshow(rst_crs, interpolation='none', cmap=cmap, vmin=err_below)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title('Reset Coarse')
    plt.clim(0, 31)
    plt.colorbar()
    plt.gca().invert_xaxis()
    #
    plt.subplot(2, 3, 6)
    plt.imshow(rst_fn, interpolation='none', cmap=cmap, vmin=err_below)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title('Reset Fine')
    plt.clim(0, 255)
    plt.colorbar()
    plt.gca().invert_xaxis()
    # plt.show(block=False)
    plt.show()
    return fig

