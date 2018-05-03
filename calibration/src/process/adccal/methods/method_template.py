import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
        # what should be calculated and
        # how should it be written into the result file
        self._result = {}

    def _calculate(self):
        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)
        print("Done.")

        # convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
#        self._merge_groups_with_frames(data["s_coarse"])

        # create as many entries for each vin as there were original frames
#        vin = self._fill_up_vin(data["vin"])  # noqa F841

        # returns: Least-squares solution (i.e. slope and offset),
        #          residuals,
        #          rank,
        #          singular values
#        res = self._fit_linear(x, y)
