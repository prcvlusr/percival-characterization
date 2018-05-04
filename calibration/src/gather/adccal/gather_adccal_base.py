import h5py
import numpy as np
import os
import sys

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

CALIBRATION_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")
GATHER_DIR = os.path.join(CALIBRATION_DIR, "src", "gather")

if GATHER_DIR not in sys.path:
    sys.path.insert(0, GATHER_DIR)

from gather_base import GatherBase  # noqa E402

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils  # noqa E402


class GatherAdcBase(GatherBase):
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

