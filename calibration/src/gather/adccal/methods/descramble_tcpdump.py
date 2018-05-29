"""
Descramble tcpdump input files into files suitable for the
file_per_vin_and_register_file gather method.
"""
import copy
# import json
import os

import __init__
from gather_adccal_base import GatherAdcBase

class Gather(GatherAdcBase):
    """Calls the descrambling method.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        dmethod = self._method_properties["descramble_method"]
        print("Using descramble method {}".format(dmethod))

        try:
            descr_kwargs = copy.deepcopy(self._method_properties[dmethod])
        except KeyError:
            descr_kwargs = {}

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
        """Initiate all parameters and performs presteps before the gather.
        """
        self._descramble.run()

    def _load_data(self):
        pass

    def _write_data(self):
        pass
