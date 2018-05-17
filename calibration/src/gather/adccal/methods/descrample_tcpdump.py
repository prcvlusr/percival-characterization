import copy
import h5py
import json
import numpy as np
import os
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

        descr_kwargs = copy.deepcopy(self._method_properties)

        # convert file names to absolute paths
        descr_kwargs["input_fnames"] = [
            os.path.join(self._input, fname)
            for fname in self._method_properties["input"]
        ]

        output_prefix = self._method_properties["output_prefix"]
        fname = "{}_dscrmbld_{}.h5".format(output_prefix, self._run)
        descr_kwargs["output_fname"] = os.path.join(self._output, fname)

#        print(json.dumps(descr_kwargs, sort_keys=True, indent=4))

        self._descramble_m = __import__(dmethod).Descramble
        self._descramble = self._descramble_m(**descr_kwargs)

    def initiate(self):
        self._descramble.run()

    def _load_data(self):
        pass

    def _write_data(self):
        pass
