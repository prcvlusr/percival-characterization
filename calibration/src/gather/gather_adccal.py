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

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from gather_base import GatherBase

class Gather(GatherBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._metadata = None
        self._register = None

        self._n_adc_groups = 7
        self._n_rows_total = 1484
        self._n_cols_total = 1440

        # TODO determine a proper size
        self._n_rows = 42
        self._n_cols = 40

        self._fixed_n_frames_per_run = 20
        self._n_rows_per_group = self._n_rows // self._n_adc_groups

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

    def read_register(self):
        print("meta_fname", self._meta_fname)

        with open(self._meta_fname, "r") as f:
            file_content = f.read().splitlines()

        # data looks like this: <V_in>  <file_prefix>
        file_content = [s.split("\t") for s in file_content]
        for s in file_content:
            s[0]=float(s[0])

        self._register = sorted(file_content)

    def run(self):
        self.read_data()

    def read_data(self):

        raw_tmp = np.zeros(self._raw_tmp_shape)
        vin_values = np.zeros(self._n_runs)

        for i, (vin, prefix) in enumerate(self._register[:10]):
            in_fname = self._in_fname.format(run=prefix)

            load_idx_rows = slice(0, self._n_rows)
            load_idx_cols = slice(0, self._n_cols)
            idx = (Ellipsis, load_idx_rows, load_idx_cols)

            print("in_fname", in_fname)
            with h5py.File(in_fname, "r") as f:
                data = f[self._paths["data"]][idx]

            start = i * self._n_frames_per_run[i]
            stop = (i + 1) * self._n_frames_per_run[i]
            t_idx = slice(start, stop)
            print("t_idx", t_idx)
            raw_tmp[t_idx, Ellipsis] = data

            vin_values[i] = vin

        print(raw_tmp.shape)
        raw_tmp.shape = self._raw_shape
        print(raw_tmp.shape)

        self._data = raw_tmp
        self._vin = vin_values

        self._write_data()

    def _write_data(self):

        with h5py.File(self._out_fname, "w", libver='latest') as f:
            f.create_dataset("data", data=self._data, dtype=np.int16)
            f.create_dataset("vin", data=self._vin, dtype=np.uint16)

            # save metadata from original files
            for key, value in iter(self._metadata.items()):
                gname = "metadata"

                name = "{}/{}".format(gname, key)
                try:
                    f.create_dataset(name, data=value)
                except:
                    print("Error in", name, value.dtype)
                    raise


            f.flush()
