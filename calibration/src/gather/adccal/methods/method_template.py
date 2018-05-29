"""A template to be used as reference for method development.
"""
import numpy as np

import __init__
from gather_adccal_base import GatherAdcBase


class Gather(GatherAdcBase):
    """A template class to be used as reference for method development.

    Available variables:
    Defined in the configuration:
        _input: directory where the input files can be found
        _output: directory where output is stored
        _run: the run ID
        _n_cols: number of columns per file

        _method_properties: -> all method properties defined in the method section

    Set in analyse:
        _in_fname: input file name (absolute path as template)
        _out_fname: output file name (absolute path)
        _meta_fname: metadata file name (absolute path)
        _n_rows: 1484

    Set in adccal gather base:
        _n_adc: 7
        _n_rows_per_group: _n_rows // _n_adc
        _paths: {
            "sample": "data",
            "reset": "reset"
        }
        _part: ...

        # Set in class method set_data_to_write:
            _metadata: ...
            _data_to_write: ...
            _raw_tmp_shape: ...
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._n_runs = 5
        self._n_frames_per_run = [2, 2, 2, 2, 2]
        self._n_frames = np.sum(self._n_frames_per_run)

        # self._data_to_write is predefined in GatherAdcBase to have one
        # format to be used in processing
        # it has the entries:
        #    "s_coarse" - np.array of shape (n_frames, n_rows, n_cols)
        #    "s_fine" - np.array of shape (n_frames, n_rows, n_cols)
        #    "s_gain" - np.array of shape (n_frames, n_rows, n_cols)
        #    "r_coarse" - np.array of shape (n_frames, n_rows, n_cols)
        #    "r_fine" - np.array of shape (n_frames, n_rows, n_cols)
        #    "r_gain" - np.array of shape (n_frames, n_rows, n_cols)
        #    "vin" - np.array of shape (n_runs)
        # need the xlass attribute _n_runs, _n_frames_per_run and _n_frames to
        # be set
        self._set_data_to_write()

    def _load_data(self):
        s_coarse = np.zeros(self._raw_tmp_shape)
        s_fine = np.zeros(self._raw_tmp_shape)
        s_gain = np.zeros(self._raw_tmp_shape)

        r_coarse = np.zeros(self._raw_tmp_shape)
        r_fine = np.zeros(self._raw_tmp_shape)
        r_gain = np.zeros(self._raw_tmp_shape)

        self._data_to_write["s_coarse"]["data"] = s_coarse
        self._data_to_write["s_fine"]["data"] = s_fine
        self._data_to_write["s_gain"]["data"] = s_gain

        self._data_to_write["r_coarse"]["data"] = r_coarse
        self._data_to_write["r_fine"]["data"] = r_fine
        self._data_to_write["r_gain"]["data"] = r_gain
