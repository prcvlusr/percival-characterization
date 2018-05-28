"""Base class for all ADC calibration gather methods.
"""
import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

CALIBRATION_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(CURRENT_DIR)
    )
)
BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")
GATHER_DIR = os.path.join(CALIBRATION_DIR, "src", "gather")

if GATHER_DIR not in sys.path:
    sys.path.insert(0, GATHER_DIR)

from gather_base import GatherBase


class GatherAdcBase(GatherBase):
    """Base class for all ADC calibration methods.
    """
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

        self._raw_tmp_shape = None
        self._data_to_write = {}

    def _set_data_to_write(self):
        """Define which data should be written into file.
        """

        self._metadata = {
            "n_frames_per_run": self._n_frames_per_run,
            "n_frames": self._n_frames,
            "n_runs": self._n_runs,
            "n_adc": self. _n_adc,
            "colums_used": [self._part * self._n_cols,
                            (self._part + 1) * self._n_cols]
        }

        self._raw_tmp_shape = (self._n_frames,
                               self._n_rows,
                               self._n_cols)

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
                "data": np.zeros(self._n_runs, dtype=np.float),
                "type": np.float
            }
        }
