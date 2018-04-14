import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):
    def __init__(self, **kwargs):  # noqa F811
        super().__init__(**kwargs)

    def _initiate(self):
        shapes = {
            "offset": (self._n_rows, self._n_adcs)
        }

        self._result = {
            # must have entries for correction
            "s_coarse_offset": {
                "data": np.empty(shapes["offset"]),
                "path": "sample/coarse/offset",
                "type": np.int16
            },
            # additional information
            "stddev": {
                "data": np.empty(shapes["offset"]),
                "path": "stddev",
                "type": np.int16
            },
        }

    def _calculate(self):
        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)
        print("Done.")

        print("Start computing means and standard deviations ...", end="")
        offset = np.mean(data["s_coarse"], axis=3).astype(np.int)
        self._result["s_coarse_offset"]["data"] = offset

        self._result["stddev"]["data"] = data["s_coarse"].std(axis=3)
        print("Done.")
