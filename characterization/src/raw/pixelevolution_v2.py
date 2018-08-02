import copy
import matplotlib
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

import os  # to list files in a directory
import sys  # print special functions
import time  # to have time
import h5py
import numpy as np
from utils import split as aggregate_crsfngn
import itertools
from plot_base import PlotBase  # noqa E402
from scipy import stats  # linear regression

from utils_raw import *  # NOO useful functions/constants


# OO methods
class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["frame"] = None
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def plot_sample(self):
        """ show evolution of mutliple pixels (Smpl) """
        self._prepare_to_multiplot()

        if self._show_evol:
            label_x = self._type_of_scan
            if self._verbose:
                label_y = "Crs"
                label_title = "Smpl,Crs evolution (includ. lost packs)"
                plot_multi1d(self._data2show_x_1d,
                             self._data2show_y_2d5[:, ismpl, :, icrs],
                             self._info_list,
                             label_x, label_y, label_title,
                             self._plot_lines)

                label_y = "Fn"
                label_title = "Smpl,Fn evolution (includ. lost packs)"
                plot_multi1d(self._data2show_x_1d,
                             self._data2show_y_2d5[:, ismpl, :, ifn],
                             self._info_list,
                             label_x, label_y, label_title,
                             self._plot_lines)

                label_y = "Gn"
                label_title = "Smpl,Gn evolution (includ. lost packs)"
                plot_multi1d(self._data2show_x_1d,
                             self._data2show_y_2d5[:, ismpl, :, ign],
                             self._info_list,
                             label_x, label_y, label_title,
                             self._plot_lines)

                label_y = "Gn"
                label_title = "Smpl,Gn evolution"
                plot_multi1d_withmask(
                    self._data2show_x_1d,
                    self._data2show_y_2d5[:, ismpl, :, ign],
                    self._validmask_3d[:, ismpl, :], self._info_list,
                    label_x, label_y, label_title, self._plot_lines)

                label_y = "Fn"
                label_title = "Smpl,Fn evolution"
                plot_multi1d_withmask(
                    self._data2show_x_1d,
                    self._data2show_y_2d5[:, ismpl, :, ifn],
                    self._validmask_3d[:, ismpl, :], self._info_list,
                    label_x, label_y, label_title, self._plot_lines)

            label_y = "Fn"
            label_title = "Smpl,Fn (prevailing Crs) evolution"
            plot_multi1d_withmask(
                self._data2show_x_1d, self._data2show_y_2d5[:, ismpl, :, ifn],
                self._validmask_fn_3d[:, ismpl, :], self._info_list,
                label_x, label_y, label_title, self._plot_lines)

            label_y = "Crs"
            label_title = "Smpl,Crs evolution"
            plot_multi1d_withmask(
                self._data2show_x_1d, self._data2show_y_2d5[:, ismpl, :, icrs],
                self._validmask_3d[:, ismpl, :], self._info_list,
                label_x, label_y, label_title, self._plot_lines)
        # ---
        if self._show_fitquality_fnhist & self._show_evol:
            aux_histobins = np.arange(256)
            plot_multihist_withmask(self._data2show_y_2d5[:, ismpl, :, ifn],
                                    self._validmask_fn_3d[:, ismpl, :],
                                    aux_histobins, self._info_list,
                                    "fn values", "occurrences", label_title)
        # ---
        if self._show_fitquality_r2:
            r2_crs = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            r2_fn = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            for i_pix, this_pix in enumerate(self._pixel_list):
                thisRow = this_pix[0]
                thisCol = this_pix[1]

                r2_crs[thisRow, thisCol] = self._fitquality_r2[
                    ismpl, icrs, i_pix]
                r2_fn[thisRow, thisCol] = self._fitquality_r2[
                    ismpl, ifn, i_pix]
            #
            # show on a reduced scale to better spot problems
            plot_2d(r2_fn, "row", "col",
                    "Smpl,Fn fit quality (R^2): reduced col scale",
                    True, -0.1)
            plt.clim(self._r2_floor, 1)

            if self._verbose:
                plot_2d(r2_crs, "row", "col",
                        "Smpl,Crs fit quality (R^2): reduced col scale",
                        True, -0.1)
                plt.clim(self._r2_floor, 1)
            #
            # save R2 results to h5
            if self._save_file:
                aux_path = os.path.dirname(
                    self._pixelevolution_metadata_fname) + '/'
                aux_pathInh5 = '/data/data/'
                aux_filenamepath = aux_path + 'fitStats_Smpl,Crs_r2.h5'
                write_1xh5(aux_filenamepath, r2_crs, aux_pathInh5)
                aux_filenamepath = aux_path + 'fitStats_Smpl,Fn_r2.h5'
                write_1xh5(aux_filenamepath, r2_fn, aux_pathInh5)

        # ---
        if self._show_fitquality_chi2:
            chi2_fn = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            for i_pix, this_pix in enumerate(self._pixel_list):
                thisRow = this_pix[0]
                thisCol = this_pix[1]
                chi2_fn[thisRow, thisCol] = self._fitquality_chi2[
                    ismpl, ifn, i_pix]
            plot_2d(chi2_fn, "row", "col",
                    "Smpl,Fn fit quality (Chi^2/NdegrFree)",
                    True, -0.1)
            if self._save_file:
                aux_path = os.path.dirname(
                    self._pixelevolution_metadata_fname) + '/'
                aux_pathInh5 = '/data/data/'
                aux_filenamepath = aux_path + 'fitStats_Smpl,Fn_chi2.h5'
                write_1xh5(aux_filenamepath, chi2_fn, aux_pathInh5)
        # ---
        if self._show_fitquality_fnhist:
            max_fnhist = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            for i_pix, this_pix in enumerate(self._pixel_list):
                thisRow = this_pix[0]
                thisCol = this_pix[1]
                max_fnhist[thisRow, thisCol] = self._fitquality_fnhisto[
                    ismpl, ifn, i_pix]
            plot_2d(max_fnhist, "row", "col",
                    "Smpl: max occurrences of the same Fn value",
                    True, -0.1)
            if self._save_file:
                aux_path = os.path.dirname(
                    self._pixelevolution_metadata_fname) + '/'
                aux_pathInh5 = '/data/data/'
                aux_filenamepath = aux_path + 'fitStats_Smpl,Fn_max_same_Fn.h5'
                write_1xh5(aux_filenamepath, max_fnhist, aux_pathInh5)
        # ---
        input('Press enter to continue/end')

    def plot_reset(self):
        """ show evolution of mutliple pixels (Rst) """
        self._prepare_to_multiplot()

        if self._show_evol:
            label_x = self._type_of_scan
            if self._verbose:
                label_y = "Crs"
                label_title = "Rst,Crs evolution (includ. lost packs)"
                plot_multi1d(self._data2show_x_1d,
                             self._data2show_y_2d5[:, irst, :, icrs],
                             self._info_list,
                             label_x, label_y, label_title,
                             self._plot_lines)

                label_y = "Fn"
                label_title = "Rst,Fn evolution (includ. lost packs)"
                plot_multi1d(self._data2show_x_1d,
                             self._data2show_y_2d5[:, irst, :, ifn],
                             self._info_list,
                             label_x, label_y, label_title,
                             self._plot_lines)

                label_y = "Gn"
                label_title = "Rst,Gn evolution (includ. lost packs)"
                plot_multi1d(self._data2show_x_1d,
                             self._data2show_y_2d5[:, irst, :, ign],
                             self._info_list,
                             label_x, label_y, label_title,
                             self._plot_lines)

                label_y = "Gn"
                label_title = "Rst,Gn evolution"
                plot_multi1d_withmask(
                    self._data2show_x_1d,
                    self._data2show_y_2d5[:, irst, :, ign],
                    self._validmask_3d[:, irst, :], self._info_list,
                    label_x, label_y, label_title, self._plot_lines)

                label_y = "Fn"
                label_title = "Rst,Fn evolution"
                plot_multi1d_withmask(
                    self._data2show_x_1d,
                    self._data2show_y_2d5[:, irst, :, ifn],
                    self._validmask_3d[:, irst, :], self._info_list,
                    label_x, label_y, label_title, self._plot_lines)

            label_y = "Fn"
            label_title = "Rst,Fn (prevailing Crs) evolution"
            plot_multi1d_withmask(
                self._data2show_x_1d, self._data2show_y_2d5[:, irst, :, ifn],
                self._validmask_fn_3d[:, irst, :], self._info_list,
                label_x, label_y, label_title, self._plot_lines)

            label_y = "Crs"
            label_title = "Rst,Crs evolution"
            plot_multi1d_withmask(
                self._data2show_x_1d, self._data2show_y_2d5[:, irst, :, icrs],
                self._validmask_3d[:, irst, :], self._info_list,
                label_x, label_y, label_title, self._plot_lines)
        # ---
        if self._show_fitquality_fnhist & self._show_evol:
            aux_histobins = np.arange(256)
            plot_multihist_withmask(self._data2show_y_2d5[:, irst, :, ifn],
                                    self._validmask_fn_3d[:, irst, :],
                                    aux_histobins, self._info_list,
                                    "fn values", "occurrences", label_title)
        # ---
        if self._show_fitquality_r2:
            r2_crs = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            r2_fn = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            for i_pix, this_pix in enumerate(self._pixel_list):
                thisRow = this_pix[0]
                thisCol = this_pix[1]

                r2_crs[thisRow, thisCol] = self._fitquality_r2[
                    irst, icrs, i_pix]
                r2_fn[thisRow, thisCol] = self._fitquality_r2[
                    irst, ifn, i_pix]
            #
            # show on a reduced scale to better spot problems
            plot_2d(r2_fn, "row", "col",
                    "Rst,Fn fit quality (R^2): reduced col scale",
                    True, -0.1)
            plt.clim(self._r2_floor, 1)

            if self._verbose:
                plot_2d(r2_crs, "row", "col",
                        "Rst,Crs fit quality (R^2): reduced col scale",
                        True, -0.1)
                plt.clim(self._r2_floor, 1)

            #
            # save R2 results to h5
            if self._save_file:
                aux_path = os.path.dirname(
                    self._pixelevolution_metadata_fname) + '/'
                aux_pathInh5 = '/data/data/'
                aux_filenamepath = aux_path + 'fitStats_Rst,Crs_r2.h5'
                write_1xh5(aux_filenamepath, r2_crs, aux_pathInh5)
                aux_filenamepath = aux_path + 'fitStats_Rst,Fn_r2.h5'
                write_1xh5(aux_filenamepath, r2_fn, aux_pathInh5)
            #
        #
        # ---
        if self._show_fitquality_chi2:
            chi2_fn = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            for i_pix, this_pix in enumerate(self._pixel_list):
                thisRow = this_pix[0]
                thisCol = this_pix[1]
                chi2_fn[thisRow, thisCol] = self._fitquality_chi2[
                    irst, ifn, i_pix]
            plot_2d(chi2_fn, "row", "col",
                    "Smpl,Fn fit quality (Chi^2/NdegrFree)",
                    True, -0.1)
            if self._save_file:
                aux_path = os.path.dirname(
                    self._pixelevolution_metadata_fname) + '/'
                aux_pathInh5 = '/data/data/'
                aux_filenamepath = aux_path + 'fitStats_Rst,Fn_chi2.h5'
                write_1xh5(aux_filenamepath, chi2_fn, aux_pathInh5)
        # ---
        if self._show_fitquality_fnhist:
            max_fnhist = np.ones((n_row_p2m, n_col_p2m)) * (-1.0)
            for i_pix, this_pix in enumerate(self._pixel_list):
                thisRow = this_pix[0]
                thisCol = this_pix[1]
                max_fnhist[thisRow, thisCol] = self._fitquality_fnhisto[
                    irst, ifn, i_pix]
            plot_2d(max_fnhist, "row", "col",
                    "Rst: max occurrences of the same Fn value",
                    True, -0.1)
            if self._save_file:
                aux_path = os.path.dirname(
                    self._pixelevolution_metadata_fname) + '/'
                aux_pathInh5 = '/data/data/'
                aux_filenamepath = aux_path + 'fitStats_Rst,Fn_max_same_Fn.h5'
                write_1xh5(aux_filenamepath, max_fnhist, aux_pathInh5)
        # ---
        input('Press enter to continue/end')

    def plot_combined(self):
        pass

    def _prepare_to_multiplot(self):
        """
        prepare data to be plotted from a scan ()

        Args:
            yaml: pixelevolution: pixelevolution_metadata_fname: metadata file
                (standard format) reporting filenames of a scan
                (and relative parameter)
            it is not an explicit arg, but it is assumed that also the files
                listed in the metadata file (standard DLSraw format) are in
                the same directrory

            yaml: raw: col: [x,y] operate on pixels from col x to col y-1
            yaml: raw: row: [x,y] operate on pixels from col x to col y-1
            yaml: pixelevolution: use_Imgs: [x,y] operate on Imgs from col x
                to col y-1

        Returns:
            self._data2show_x_1d: [n_steps * n_img_slice] : x to plot
                (1D array where all the Img in the same file have the
                 same patrameter value)
            self._data2show_y_2d5: [n_steps * n_img_slice, n_smplrst,
                n_row_slice * n_col_slice, n_gncrsfn]: Y to plot
            self._info_list [n_steps * n_img_slice] : legend
            data to be plotted are passed to plot_sample and plot_reset
        """
        #
        start_time_inhuman = time.time()
        start_time = time.strftime("%Y_%m_%d__%H:%M:%S",
                                   time.gmtime(start_time_inhuman))
        printcol("Script beginning at " + str(start_time), 'blue')
        start_time = time.time()
        #
        # print(self.__dict__.keys())
        # print(self._method_properties)
        self._report_arguments()
        #
        # grofsc
        fit_minpoints = self._fit_minpoints
        # ---
        #
        # read metafile
        printcol("reading files", 'blue')
        (vsteps_list, file_list) = self._read_meta()
        n_steps = len(vsteps_list)
        n_img_slice = len(self._use_imgs)
        frm_img = self._use_imgs[0]
        to_img = self._use_imgs[-1] + 1
        frm_row = self._row.start
        to_row = self._row.stop
        n_row_slice = to_row - frm_row
        frm_col = self._col.start
        to_col = self._col.stop
        n_col_slice = to_col - frm_col
        #
        aux_shape = (n_steps, n_img_slice, n_smplrst,
                     n_row_slice, n_col_slice, n_gncrsfn)
        data2show_y_2d5 = np.zeros(aux_shape).astype('int16')
        #
        aux_shape = (n_steps, n_img_slice)
        data2show_x_1d = np.zeros(aux_shape).astype('float')
        #
        for i_file, this_file in enumerate(file_list):
            if os.path.isfile(this_file) is False:
                msg = "{0} file does not exist".format(this_file)
                printcol(msg, 'red')
                raise Exception(msg)
            (data_smpl, data_rst) = read_2xh5(this_file,
                                              '/data/', '/reset/')
            (aux_n_img, aux_n_row, aux_n_col) = data_smpl.shape
            if self._verbose:
                printcol("{0} Images in file:"
                         "{1}".format(aux_n_img, this_file), 'green')
            elif ((i_file + 1) % 10) == 0:
                dot()

            if self._use_imgs[-1] >= aux_n_img:
                msg = "{0} Img on this file".format(aux_n_img)
                printcol(msg, 'red')
                raise Exception(msg)

            data2show_y_2d5[
                i_file, :, :, :, :,
                :] = convert_dlsraw_2_gncrsfn(data_smpl[frm_img:to_img, :, :],
                                              data_rst[frm_img:to_img, :, :],
                                              False)[:, :, frm_row:to_row,
                                                     frm_col:to_col, :]
            data2show_x_1d[i_file, :] = float(vsteps_list[i_file])
        printcol(" ", 'blue')

        printcol("reshaping", 'blue')
        aux_shape = (n_steps * n_img_slice, n_smplrst,
                     n_row_slice * n_col_slice, n_gncrsfn)
        self._data2show_y_2d5 = data2show_y_2d5.reshape(aux_shape)
        self._data2show_x_1d = data2show_x_1d.reshape((n_steps * n_img_slice))

        printcol("preparing legend", 'blue')
        info_list = []
        pixel_List = []
        for i_row in range(frm_row, to_row):
            for i_col in range(frm_col, to_col):
                info_list += ["pix "+str((i_row, i_col))]
                pixel_List += [(i_row, i_col)]
        self._info_list = info_list
        self._pixel_list = pixel_List
        # ---
        #
        # identify lost packs
        aux_mask_3d = np.zeros((n_steps * n_img_slice,
                                n_smplrst,
                                n_row_slice * n_col_slice)).astype(bool)
        aux_maskfn_3d = np.zeros_like(aux_mask_3d).astype(bool)

        for i_pix, this_pix in enumerate(pixel_List):
            for i_smplrst in range(n_smplrst):
                aux_mask_3d[:, i_smplrst, i_pix] = (
                    self._data2show_y_2d5[:, i_smplrst, i_pix, ign] >= 0) & (
                    self._data2show_y_2d5[:, i_smplrst, i_pix, ign] <= 2)
        self._validmask_3d = aux_mask_3d
        # ---
        #
        # printcol("preparing to fit", 'blue')
        aux_shape = (n_smplrst, n_gncrsfn, len(self._pixel_list))
        fit_slope = np.ones(aux_shape) * (-1)
        fit_offset = np.ones(aux_shape) * (-1)
        fitquality_r2 = np.ones(aux_shape) * (-1)
        fitquality_chi2 = np.ones(aux_shape) * (-1)
        fitquality_fnhisto = np.ones(aux_shape) * (-1)

        printcol("judging linear-fit quality", 'blue')
        for i_pix, this_pix in enumerate(self._pixel_list):
            for i_smplrst in range(n_smplrst):
                if i_smplrst == ismpl:
                    smplrst_str = "Smpl"
                else:
                    smplrst_str = "Rst"
                # fit Crs
                reduced_x_crs = self._data2show_x_1d[
                    aux_mask_3d[:, i_smplrst, i_pix]]
                reduced_y_crs = self._data2show_y_2d5[
                    :, i_smplrst, i_pix, icrs][
                        aux_mask_3d[:, i_smplrst, i_pix]]

                if len(reduced_x_crs) < fit_minpoints:
                    aux_msg = "{0},{1},Crs: unable to fit".format(this_pix,
                                                                  smplrst_str)
                    aux_col = "orange"
                else:
                    (aux_slope, aux_offset) = linear_fit(reduced_x_crs,
                                                         reduced_y_crs)
                    aux_r2 = linear_fit_r2(reduced_x_crs, reduced_y_crs)
                    fit_slope[i_smplrst, icrs, i_pix] = aux_slope
                    fit_offset[i_smplrst, icrs, i_pix] = aux_offset
                    fitquality_r2[i_smplrst, icrs, i_pix] = aux_r2

                    aux_msg = ("{0},{4},Crs: slope={1},offset={2},"
                               "R2={3}".format(this_pix, aux_slope, aux_offset,
                                               aux_r2, smplrst_str))
                    aux_col = "green"

                    if self._show_fitquality_chi2:
                        aux_chi2 = linear_fit_chi2(reduced_x_crs,
                                                   reduced_y_crs)
                        fitquality_chi2[i_smplrst, icrs, i_pix] = aux_chi2
                        aux_msg = aux_msg + ",Chi2/degFree=" + str(aux_chi2)

                if self._verbose:
                    printcol(aux_msg, aux_col)

                #
                # fit Fn
                (mostcommon_crs, aux_err_flag) = find_mostcommon_uint(
                    self._data2show_y_2d5[:, i_smplrst, i_pix, icrs],
                    self._fnfit_mincrs, self._fnfit_maxcrs)
                if aux_err_flag:
                    aux_msg = "{0},{1},Fn: unable to Fn-fit".format(
                        this_pix, smplrst_str)
                    if self._verbose:
                        printcol(aux_msg, 'orange')
                else:
                    aux_maskfn_3d[:, i_smplrst, i_pix] = (
                        (self._data2show_y_2d5[:, i_smplrst,
                                               i_pix, ign] >= 0) &
                        (self._data2show_y_2d5[:, i_smplrst,
                                               i_pix, ign] <= 2) &
                        (self._data2show_y_2d5[:,
                                               i_smplrst,
                                               i_pix,
                                               icrs] == mostcommon_crs))
                    reduced_x_fn = self._data2show_x_1d[aux_maskfn_3d[
                        :, i_smplrst, i_pix]]
                    reduced_y_fn = self._data2show_y_2d5[
                        :, i_smplrst, i_pix, ifn][aux_maskfn_3d[:, i_smplrst,
                                                                i_pix]]

                    if len(reduced_x_fn) < fit_minpoints:
                        aux_msg = "{0},{1},Fn: unable to Fn-fit".format(
                            this_pix, smplrst_str)
                        aux_col = "orange"
                    else:
                        (aux_slope, aux_offset) = linear_fit(reduced_x_fn,
                                                             reduced_y_fn)
                        aux_r2 = linear_fit_r2(reduced_x_fn, reduced_y_fn)

                        fit_slope[i_smplrst, ifn, i_pix] = aux_slope
                        fit_offset[i_smplrst, ifn, i_pix] = aux_offset
                        fitquality_r2[i_smplrst, ifn, i_pix] = aux_r2

                        aux_msg = ("{0},{4},Fn (Crs=={5}): slope={2},"
                                   "offset={2},"
                                   "R2={3}".format(this_pix, aux_slope,
                                                   aux_offset,
                                                   aux_r2, smplrst_str,
                                                   mostcommon_crs))
                        aux_col = "green"

                        if self._show_fitquality_chi2:
                            aux_chi2 = linear_fit_chi2(reduced_x_fn,
                                                       reduced_y_fn)
                            fitquality_chi2[i_smplrst, ifn, i_pix] = aux_chi2
                            aux_msg = aux_msg + ",Chi2/degFree=" + str(
                                aux_chi2)

                        if self._show_fitquality_fnhist:
                            aux_binhisto = np.arange(256)
                            (aux_fnhist, ignore) = np.histogram(reduced_y_fn,
                                                                aux_binhisto)
                            fitquality_fnhisto[i_smplrst, ifn, i_pix] = max(
                                aux_fnhist)
                            aux_msg = aux_msg + ",same-Fn occurr=" + str(
                                max(aux_fnhist))

                    if self._verbose:
                        printcol(aux_msg, aux_col)

            if self._verbose is False:
                if ((i_pix+1) % 1000) == 0:
                    dot()
                if ((i_pix+1) % 100000) == 0:
                    printcol(str(this_pix), 'green')
        printcol("- - -", 'green')

        self._validmask_fn_3d = aux_maskfn_3d

        self._fit_slope = fit_slope
        self._fit_offset = fit_offset
        self._fitquality_r2 = fitquality_r2
        self._fitquality_chi2 = fitquality_chi2
        self._fitquality_fnhisto = fitquality_fnhisto

        end_time_inhuman = time.time()
        aux_dur = end_time_inhuman - start_time_inhuman
        end_time = time.strftime("%Y_%m_%d__%H:%M:%S",
                                 time.gmtime(end_time_inhuman))
        printcol("Data elaboration ended at " + str(end_time) +
                 " (" + str(aux_dur) + "s)", 'blue')
        # ---
        # end of _prepare_to_multiplot

    def _report_arguments(self):
        """ report arguments from conf file """
        self._verbose = self._method_properties["verbose"]
        self._clean_memory = self._method_properties["clean_memory"]
        self._metasuffix = self._method_properties["metasuffix"]
        self._type_of_scan = self._method_properties["type_of_scan"]
        self._plot_lines = self._method_properties["plot_lines"]

        aux_use_imgs = self._method_properties["use_Imgs"]
        self._use_imgs = np.arange(aux_use_imgs[0], aux_use_imgs[1])
        self._pixelevolution_metadata_fname = self._method_properties[
            "pixelevolution_metadata_fname"]

        self._show_evol = self._method_properties["showEvolution"]

        self._fit_minpoints = self._method_properties["fit_minpoints"]
        self._fnfit_mincrs = self._method_properties["FnFit_minCrs"]
        self._fnfit_maxcrs = self._method_properties["FnFit_maxCrs"]

        self._r2_floor = self._method_properties["R2_colScaleFloor"]

        self._show_fitquality_r2 = self._method_properties[
             "showFitQuality_R2"]
        self._show_fitquality_chi2 = self._method_properties[
             "showFitQuality_Chi2"]
        self._show_fitquality_fnhist = self._method_properties[
            "showFitQuality_FnHist"]

        self._save_file = self._method_properties["save_file"]

        printcol("Will try to load files listed in:{0}".format(
            self._pixelevolution_metadata_fname), 'green')

        printcol("Will show evolution of pixels ({0}:{1},{2}:{3}) in "
                 "Img {4}".format(self._row.start, self._row.stop,
                                  self._col.start, self._col.stop,
                                  self._use_imgs), 'green')

        printcol("will Fn-fit for {0}<=Crs<={1}".format(
            self._fnfit_mincrs, self._fnfit_maxcrs), 'green')

        if self._save_file:
            printcol("Will save fit quality data", 'green')

        if self._clean_memory:
                printcol("Will clean memory when possible", 'green')

        if self._verbose:
            printcol("verbose", 'green')

        printcol("--  --  --", 'green')

    def _read_meta(self):
        """ read metafile file """
        filename = self._pixelevolution_metadata_fname
        suffix = self._metasuffix
        if os.path.isfile(filename) is False:
            msg = "metafile file does not exist"
            printcol(msg, 'red')
            raise Exception(msg)
        meta_data = np.genfromtxt(filename,
                                  delimiter='\t',
                                  dtype=str)
        fileprefix_list = meta_data[:, 1]
        v_steps_list = meta_data[:, 0]
        #
        filepath = os.path.dirname(filename) + '/'
        aux_fileprefix = fileprefix_list.tolist
        file_list = []
        for i_file, this_prefix in enumerate(fileprefix_list):
            file_list += [filepath + this_prefix + suffix]
        file_list = np.array(file_list)
        #
        return (v_steps_list, file_list)

