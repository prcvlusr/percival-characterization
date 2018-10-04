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
n_col_p2m = 32 * 45
n_row_p2m = 7 * 106 * 2
n_smplrst = 2
n_gncrsfn = 3
ismpl = 0
irst = 1
ign = 0
icrs = 1
ifn = 2
err_dlsraw = (2**16)-1
err_gncrsfn = -256


# NOO functions: print
def dot():
    '''print a dot '''
    sys.stdout.write(".")
    sys.stdout.flush()  # print it now


def printcol(string2print, colour):
    ''' write in colour (red/green/orange/blue/purple) '''
    white = '\033[0m'  # white (normal)
    if (colour == 'black'):
        outcolor = '\033[30m '  # black
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


# NOO functions: general utility files
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


# NOO functions: files
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


# NOO functions: fits
def linear_fun(x, slope, intercept):
    '''straight line function'''
    return intercept + (slope * x)


def linear_fit(x, y):
    '''fit linear'''
    slopefit, interceptfit, r_val, p_val, std_err = stats.linregress(x, y)
    return (slopefit, interceptfit)


def linear_fit_r2(x, y):
    '''R^2 quality of fit linear'''
    slopefit, interceptfit, r_val, p_val, std_err = stats.linregress(x, y)
    r2 = r_val**2
    return (r2)


def linear_fit_chi2(x, y):
    '''Chi^2/NdegreesOfFreedom quality of fit linear'''
    slopefit, interceptfit, r_val, p_val, std_err = stats.linregress(x, y)
    expected_val = (slopefit * x) + interceptfit
    (chi2, pval) = stats.chisquare(y, f_exp=expected_val)
    n_degr_freedom = float(len(x) - 2)
    return (chi2 / n_degr_freedom)


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
            invertx_flag, err_below):
    ''' 2D image , mark as error (white) the values << err_below'''
    cmap = plt.cm.jet
    cmap.set_under(color='white')
    fig = plt.figure()
    plt.imshow(array_2d, interpolation='none', cmap=cmap, vmin=err_below)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title(label_title)
    plt.colorbar()
    if invertx_flag:
        plt.gca().invert_xaxis()
    plt.show(block=False)
    return (fig)


# P2M specific functions
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

