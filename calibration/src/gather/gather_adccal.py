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

        self._fixed_n_frames_per_run = 20
        self._n_rows_per_group = self._n_rows // self._n_adc

        self._paths = {
            "data": "data",
            "reset": "reset"
        }

        self.initiate()

    def initiate(self):
        self.read_register()

        self._n_runs = len(self._register)
        self._n_frames_per_run = (np.ones(self._n_runs, np.int16)
                                  * self._fixed_n_frames_per_run)
        self._n_frames = np.sum(self._n_frames_per_run)

        self._raw_tmp_shape = (self._n_frames,
                               self._n_rows,
                               self._n_cols)
        self._raw_shape = (-1,
                           self._n_rows_per_group,
                           self._n_adc_groups,
                           self._n_cols)

        self._metadata = {
            "n_frames_per_run": self._n_frames_per_run,
            "n_frames": self._n_frames,
            "n_runs": self._n_runs,
            "n_adc_groups": self. _n_adc_groups
        }

        self._data_to_write = {
            "data": {
                "path": "data",
                "data": np.zeros(self._raw_tmp_shape),
                "type": np.uint16
            },
            "reset": {
                "path": "reset",
                "data": np.zeros(self._raw_tmp_shape),
                "type": np.uint16
            },
            "vin": {
                "path": "vin",
                "data": np.zeros(self._n_frames),
                "type": np.uint16
            }
        }

    def read_register(self):
        print("meta_fname", self._meta_fname)

        with open(self._meta_fname, "r") as f:
            file_content = f.read().splitlines()

        # data looks like this: <V_in>  <file_prefix>
        file_content = [s.split("\t") for s in file_content]
        for s in file_content:
            s[0]=float(s[0])

        self._register = sorted(file_content)

    def _load_data(self):
        # for convenience
        data = self._data_to_write["data"]["data"]
        reset = self._data_to_write["reset"]["data"]
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
                in_data = f[self._paths["data"]][idx]
                in_reset = f[self._paths["reset"]][idx]

            # determine where this data block should go in the result
            # matrix
            start = i * self._n_frames_per_run[i]
            stop = (i + 1) * self._n_frames_per_run[i]
            t_idx = slice(start, stop)
            print("Getting frames {} to {} of {}"
                  .format(start, stop, data.shape[0]))

            data[t_idx, Ellipsis] = in_data
            reset[t_idx, Ellipsis] = in_reset

            vin[i] = v

        # split the data into ADC groups
        print(data.shape)
        data.shape = self._raw_shape
        reset.shape = self._raw_shape
        print(data.shape)
