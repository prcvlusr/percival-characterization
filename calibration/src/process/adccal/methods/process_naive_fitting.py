import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
        shapes = {
            "offset": (self._n_adcs, self._n_cols)
        }

        self._result = {
            # must have entries for correction
            "s_coarse_slope": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/slope",
            },
            "s_coarse_offset": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/offset",
            }
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

        # for convenience
        offset = self._result["s_coarse_offset"]["data"]
        slope = self._result["s_coarse_slope"]["data"]

        print("Start fitting ...")
        for adc in range(self._n_adcs):
            print("adc", adc)
            for col in range(self._n_cols):
                x = vin
                y = data["s_coarse"][adc, col, :]

                # returns: Least-squares solution (i.e. slope and offset),
                #          residuals,
                #          rank,
                #          singular values
                res = self._fit_linear(x, y)
                # res = self._fit_linear(x, y, enable_r_squared=True)

                slope[adc, col] = res.solution[0]
                offset[adc, col] = res.solution[1]

        print("Done.")
