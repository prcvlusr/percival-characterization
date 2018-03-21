import h5py
import sys
import numpy as np
import time
import os
from datetime import date

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
SRC_PATH = os.path.join(BASE_PATH, "src")
PROCESS_PATH = os.path.join(SRC_PATH, "process")

if PROCESS_PATH not in sys.path:
    sys.path.insert(0, PROCESS_PATH)

from process_base import ProcessBase


class ProcessAdccalBase(ProcessBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._paths = {
            "s_coarse": "sample/coarse",
            "s_fine": "sample/fine",
            "s_gain": "sample/gain",
            "r_coarse": "reset/coarse",
            "r_fine": "reset/fine",
            "r_gain": "reset/gain",
            "vin": "vin",
            "n_frames_per_run": "collection/n_frames_per_run"
        }

        self._n_adcs = None
        self._n_total_frames = None

        self._set_dimensions()

    def _set_dimensions(self):

        with h5py.File(self._in_fname, "r") as f:
            s_coarse = f[self._paths["s_coarse"]][()]
            n_frames_per_vin = f[self._paths["n_frames_per_run"]][()]

        self._n_adcs = s_coarse.shape[0]
        self._n_cols = s_coarse.shape[1]
        self._n_groups = s_coarse.shape[2]
        self._n_frames = s_coarse.shape[3]

        self._n_total_frames = self._n_groups * self._n_frames

        self._n_frames_per_vin = n_frames_per_vin

    def _load_data(self, in_fname):

        data = {}
        with h5py.File(self._in_fname, "r") as f:
            for key in self._paths:
                data[key] = f[self._paths[key]][()]

        return data

    def _fill_up_vin(self, vin):
        # create as many entries for each vin as there were original frames
        x = [np.full(self._n_frames_per_vin[i] * self._n_groups, v)
             for i, v in enumerate(vin)]

        x = np.hstack(x)

        return x

    def _merge_groups_with_frames(self, data):
        # data has the dimension (n_adcs, n_cols, n_groups, n_frames)
        # should be transformed into (n_adcs, n_cols, n_groups * n_frames)

        data.shape = (self._n_adcs,
                      self._n_cols,
                      self._n_total_frames)
