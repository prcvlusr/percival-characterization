import h5py
import numpy as np

import __init__  # noqa F401
from process_base import ProcessBase


class ProcessAdccalBase(ProcessBase):
    def __init__(self, **kwargs):  # noqa F811
        super().__init__(**kwargs)

        self._paths = {
            "s_coarse": "sample/coarse",
            "s_fine": "sample/fine",
            "s_gain": "sample/gain",
            "r_coarse": "reset/coarse",
            "r_fine": "reset/fine",
            "r_gain": "reset/gain",
            "vin": "vin"
        }

        self._n_adcs = None
        self._n_rows = None

        self._set_dimensions()

    def _set_dimensions(self):

        with h5py.File(self._in_fname, "r") as f:
            s_coarse = f[self._paths["s_coarse"]][()]

        self._n_adcs = s_coarse.shape[0]
        self._n_rows = s_coarse.shape[1]

    def _load_data(self, in_fname):

        data = {}
        with h5py.File(self._in_fname, "r") as f:
            for key in self._paths:
                data[key] = f[self._paths[key]][()]

        return data

