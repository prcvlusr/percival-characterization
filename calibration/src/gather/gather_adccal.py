import h5py
import numpy as np
import os
import sys
import time
import glob

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
SRC_DIR = os.path.join(BASE_DIR, "src")

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from gather_base import GatherBase

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import utils


class Gather(GatherBase):
    def __init__(self, n_rows, n_cols, part, **kwargs):
        super().__init__(**kwargs)

        self._metadata = None
        self._register = None

        self._n_adc = 7
        self._n_rows = n_rows
        self._n_cols = n_cols

        self._part = part

        self._n_rows_per_group = self._n_rows // self._n_adc

        self._paths = {
            "sample": "data",
            "reset": "reset"
        }

        self.initiate()

    def initiate(self):
        self._read_register()

        self._n_runs = len(self._register)

        self._set_n_frames_per_run()

        self._n_frames = np.sum(self._n_frames_per_run)

        self._raw_tmp_shape = (self._n_frames,
                               self._n_rows,
                               self._n_cols)
        self._raw_shape = (-1,
                           self._n_rows_per_group,
                           self._n_adc,
                           self._n_cols)

        # (n_frames, n_groups, n_rows, n_cols)
        # is transposed to
        # (n_rows, n_cols, n_groups, n_frames)
        self._transpose_order = (2, 3, 1, 0)

        self._metadata = {
            "n_frames_per_run": self._n_frames_per_run,
            "n_frames": self._n_frames,
            "n_runs": self._n_runs,
            "n_adc": self. _n_adc
        }

        self._data_to_write = {
            "s_coarse": {
                "path": "sample/coarse",
                "data": np.zeros(self._raw_tmp_shape, dtype=np.uint8),
                "type": np.uint8
            },
            "s_fine": {
                "path": "sample/fine",
                "data": np.zeros(self._raw_tmp_shape, dtype=np.uint8),
                "type": np.uint8
            },
            "s_gain": {
                "path": "sample/gain",
                "data": np.zeros(self._raw_tmp_shape, dtype=np.uint8),
                "type": np.uint8
            },
            "r_coarse": {
                "path": "reset/coarse",
                "data": np.zeros(self._raw_tmp_shape, dtype=np.uint8),
                "type": np.uint8
            },
            "r_fine": {
                "path": "reset/fine",
                "data": np.zeros(self._raw_tmp_shape, dtype=np.uint8),
                "type": np.uint8
            },
            "r_gain": {
                "path": "reset/gain",
                "data": np.zeros(self._raw_tmp_shape, dtype=np.uint8),
                "type": np.uint8
            },
            "vin": {
                "path": "vin",
                "data": np.zeros(self._n_runs, dtype=np.float16),
                "type": np.float16
            }
        }

    def _read_register(self):
        print("meta_fname", self._meta_fname)

        with open(self._meta_fname, "r") as f:
            file_content = f.read().splitlines()

        # data looks like this: <V_in>  <file_prefix>
        file_content = [s.split("\t") for s in file_content]
        for s in file_content:
            s[0]=float(s[0])

        self._register = sorted(file_content)

    def _set_n_frames_per_run(self):
        self._n_frames_per_run = []

        for i in self._register:
            in_fname = self._in_fname.format(run=i[1])

            with h5py.File(in_fname, "r") as f:
                n_frames = f[self._paths["sample"]].shape[0]
                self._n_frames_per_run.append(n_frames)

    def _load_data(self):
        # for convenience
        s_coarse = self._data_to_write["s_coarse"]["data"]
        s_fine = self._data_to_write["s_fine"]["data"]
        s_gain = self._data_to_write["s_gain"]["data"]

        r_coarse = self._data_to_write["r_coarse"]["data"]
        r_fine = self._data_to_write["r_fine"]["data"]
        r_gain = self._data_to_write["r_gain"]["data"]

        vin = self._data_to_write["vin"]["data"]

        #  split the raw data in slices to handle the size
        load_idx_rows = slice(0, self._n_rows)
        load_idx_cols = slice(self._part * self._n_cols,
                              (self._part + 1) * self._n_cols)
        idx = (Ellipsis, load_idx_rows, load_idx_cols)

        for i, (v, prefix) in enumerate(self._register):
            in_fname = self._in_fname.format(run=prefix)

            # read in data for this slice
            print("in_fname", in_fname)
            with h5py.File(in_fname, "r") as f:
                in_sample = f[self._paths["sample"]][idx]
                in_reset = f[self._paths["reset"]][idx]

#            print(idx)
#            test = in_sample[0, 0, 36]
            #test = in_sample[0, 0, 100]
#            print(test, bin(test))
#            print(hex(0b0110000000000000))
#            arr_out = np.bitwise_and(test, 0x6000)
#            arr_out = np.right_shift(arr_out, 5+8)
#            arr_out = arr_out.astype(np.uint8)
#            print(arr_out)

#            continue


            # determine where this data block should go in the result
            # matrix
            start = i * self._n_frames_per_run[i]
            stop = (i + 1) * self._n_frames_per_run[i]
            t_idx = slice(start, stop)
            print("Getting frames {} to {} of {}"
                  .format(start, stop, s_coarse.shape[0]))

            # split the 16 bit into coarse, fine and gain
            # and set them on the correct position in the result matrix
            coarse, fine, gain = utils.split(in_sample)
            s_coarse[t_idx, Ellipsis] = coarse
            s_fine[t_idx, Ellipsis] = fine
            s_gain[t_idx, Ellipsis] = gain

            coarse, fine, gain = utils.split(in_reset)
            r_coarse[t_idx, Ellipsis] = coarse
            r_fine[t_idx, Ellipsis] = fine
            r_gain[t_idx, Ellipsis] = gain

            vin[i] = v

        # split the rows into ADC groups
        print(s_coarse.shape)
        s_coarse.shape = self._raw_shape
        s_fine.shape = self._raw_shape
        s_gain.shape = self._raw_shape

        r_coarse.shape = self._raw_shape
        r_fine.shape = self._raw_shape
        r_gain.shape = self._raw_shape
        print(s_coarse.shape)

        # optimize memory layout for further processing
        s_coarse = s_coarse.transpose(self._transpose_order)
        s_fine = s_fine.transpose(self._transpose_order)
        s_gain = s_gain.transpose(self._transpose_order)

        r_coarse = r_coarse.transpose(self._transpose_order)
        r_fine = r_fine.transpose(self._transpose_order)
        r_gain = r_gain.transpose(self._transpose_order)
        print(s_coarse.shape)

        # the transpose is not done on the original arrays but creates a copy
        self._data_to_write["s_coarse"]["data"] = s_coarse
        self._data_to_write["s_fine"]["data"] = s_fine
        self._data_to_write["s_gain"]["data"] = s_gain

        self._data_to_write["r_coarse"]["data"] = r_coarse
        self._data_to_write["r_fine"]["data"] = r_fine
        self._data_to_write["r_gain"]["data"] = r_gain
