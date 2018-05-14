import h5py
import numpy as np

import __init__  # noqa F401
from gather_adccal_base import GatherAdcBase
import utils


class Gather(GatherAdcBase):
    def __init__(self, **kwargs):  # noqa F401
        super().__init__(**kwargs)

        self._descrample_method = "APy3_descramble_tcpdump_2018_03_15AD"
        self._descramble = __import__(self._descrample_method).Descramble(**kwargs)

    def initiate(self):
        self._descramble.run()

    def _load_data(self):
        pass
