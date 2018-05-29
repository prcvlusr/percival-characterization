"""A template to be used as reference for method development.
"""
import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):
    """A template class to be used as reference for method development.

    Available variables:
    Defined in the configuration:
        _run: the run ID
        _method: the method name used

        _method_properties: -> all method properties defined in the method section

    Set in analyse:
        _in_fname: input file name (absolute path as template)
        _out_fname: output file name (absolute path)
        _meta_fname: metadata file name (absolute path)
        _n_rows: 1484

    Set in adccal process base:
        _paths: {
            "n_frames_per_run": "collection/n_frames_per_run",
            "r_coarse": "reset/coarse",
            "r_fine": "reset/fine",
            "r_gain": "reset/gain",
            "s_coarse": "sample/coarse",
            "s_fine": "sample/fine",
            "s_gain": "sample/gain",
            "vin": "vin"
        }
        # determined on basis of the data
        _n_adcs: ...
        _n_cols: ...
        _n_frames: ...
        _n_groups: ...
        _n_total_frames: ...
        _n_frames_per_vin: ...

    """

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
