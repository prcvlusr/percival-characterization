import glob
import h5py
import numpy as np
import os

import utils


class LoadRaw():
    def __init__(self, input_fname, output_dir, frame=None, row=None, col=None):

        self._input_fname = input_fname
        self._output_dir = os.path.normpath(output_dir)
        self._frame = frame or slice(None)
        self._row = row or slice(None)
        self._col = col or slice(None)

        self._data_type = "raw"

        self._paths = {
            "sample": "data",
            "reset": "reset",
        }

        self._n_frames_per_vin = None

        self._n_frames = None
        self._n_groups = None
        self._n_total_frames = None

    def load_data(self):
        idx = (self._frame, self._row, self._col)

        data = {}
        with h5py.File(self._input_fname, "r") as f:
            #sample
            path = self._paths["sample"]
            coarse, fine, gain = utils.split(f[path][idx])
            data["s_coarse"] = coarse
            data["s_fine"] = fine
            data["s_gain"] = gain

            # reset
            path = self._paths["reset"]
            coarse, fine, gain = utils.split(f[path][idx])
            data["r_coarse"] = coarse
            data["r_fine"] = fine
            data["r_gain"] = gain

        return data

    def get_vin(self):
        pass
