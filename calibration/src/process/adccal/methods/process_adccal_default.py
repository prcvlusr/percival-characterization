import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
        shapes = {
            "offset": (self._n_cols, self._n_adcs)
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

        # convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
        self._merge_groups_with_frames(data["s_coarse"])

        # create as many entries for each vin as there were original frames
        vin = self._fill_up_vin(data["vin"])  # noqa F841

        # TODO
        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                # x = ... (subset of vin)
                # y = ... (subset of data["s_coarse"][adc, col, :])
                # res = self._fit_linear(x, y)
                pass

        print("Start computing means and standard deviations ...", end="")
        offset = np.mean(data["s_coarse"], axis=2).astype(np.int)
        self._result["s_coarse_offset"]["data"] = offset

        self._result["stddev"]["data"] = data["s_coarse"].std(axis=2)
        print("Done.")
