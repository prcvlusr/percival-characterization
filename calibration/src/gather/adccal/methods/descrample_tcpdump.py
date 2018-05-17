import h5py
import numpy as np
import sys

from __init__ import DESCRAMBLE_DIR
from gather_adccal_base import GatherAdcBase
import utils

if DESCRAMBLE_DIR not in sys.path:
    sys.path.insert(0, DESCRAMBLE_DIR)


class Gather(GatherAdcBase):
    def __init__(self, **kwargs):  # noqa F401
        super().__init__(**kwargs)

        dmethod = self._method_properties["descramble_method"]
        print("Using descramble method {}".format(dmethod))

        self._descramble_m = __import__(dmethod).Descramble
        self._descramble = self._descramble_m(**self._method_properties)

    def initiate(self):
        self._descramble.run()

    def _load_data(self):
        pass

    def _write_data(self):
        pass
