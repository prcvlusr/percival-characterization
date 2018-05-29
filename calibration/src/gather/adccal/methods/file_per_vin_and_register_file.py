"""
Takes one file per Vin plus an additional register file as input and gathers
in into the default format.
"""
import h5py
import numpy as np

import __init__
from gather_adccal_base import GatherAdcBase
import utils


class Gather(GatherAdcBase):
    """Converts the input file(s) into the standard gathered format.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # if this is not set to "gathererd" later processing will not work
        self._output = self._get_output_dir(run_dir="gathered")

        self._n_runs = None
        self._n_frames = None
        self._raw_shape = None
        self._transpose_order = None
        self._register = None
        self._n_frames_per_run = None

    def initiate(self):
        """Sets up the method attributes.
        """

        # mandatory variable to be set before any parent class function can
        # me used are:
        # self._n_runs
        # self._n_frames_per_run
        # self._n_frames
        # self._n_runs

        self._read_register()

        self._n_runs = len(self._register)

        self._set_n_frames_per_run()

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
        self._set_data_to_write()

        self._raw_shape = (-1,
                           self._n_rows_per_group,
                           self._n_adc,
                           self._n_cols)

        # (n_frames, n_groups, n_rows, n_cols)
        # is transposed to
        # (n_rows, n_cols, n_frames, n_groups)
        self._transpose_order = (2, 3, 0, 1)

    def _read_register(self):
        print("meta_fname", self._meta_fname)

        with open(self._meta_fname, "r") as metafile:
            file_content = metafile.read().splitlines()

        # data looks like this: <V_in>  <file_prefix>
        file_content = [s.split("\t") for s in file_content]
        for i, string in enumerate(file_content):
            try:
                string[0] = float(string[0])
            except ValueError:
                if string == ['']:
                    # remove empty lines
                    del file_content[i]
                else:
                    raise
#                print("file_content", file_content)

        self._register = sorted(file_content)

    def _set_n_frames_per_run(self):
        self._n_frames_per_run = []

        for i in self._register:
            in_fname = self._in_fname.format(prefix=i[1])

            try:
                with h5py.File(in_fname, "r") as infile:
                    n_frames = infile[self._paths["sample"]].shape[0]
                    self._n_frames_per_run.append(n_frames)
            except OSError:
                print("in_fname", in_fname)
                raise

    def _load_data(self):
        # for convenience
        s_coarse = self._data_to_write["s_coarse"]["data"]
        s_fine = self._data_to_write["s_fine"]["data"]
        s_gain = self._data_to_write["s_gain"]["data"]

        r_coarse = self._data_to_write["r_coarse"]["data"]
        r_fine = self._data_to_write["r_fine"]["data"]
        r_gain = self._data_to_write["r_gain"]["data"]

        vin = self._data_to_write["vin"]["data"]

        #  split the raw data in slices to handle the size
        load_idx_rows = slice(0, self._n_rows)
        load_idx_cols = slice(self._part * self._n_cols,
                              (self._part + 1) * self._n_cols)
        idx = (Ellipsis, load_idx_rows, load_idx_cols)

        for i, (vin_value, prefix) in enumerate(self._register):
            in_fname = self._in_fname.format(prefix=prefix)

            # read in data for this slice
            print("in_fname", in_fname)
            with h5py.File(in_fname, "r") as in_f:
                in_sample = in_f[self._paths["sample"]][idx]
                in_reset = in_f[self._paths["reset"]][idx]

            # determine where this data block should go in the result
            # matrix
            start = i * self._n_frames_per_run[i]
            stop = (i + 1) * self._n_frames_per_run[i]
            t_idx = slice(start, stop)
            print("Getting frames {} to {} of {}"
                  .format(start, stop, s_coarse.shape[0]))

            # split the 16 bit into coarse, fine and gain
            # and set them on the correct position in the result matrix
            coarse, fine, gain = utils.split(in_sample)
            s_coarse[t_idx, Ellipsis] = coarse
            s_fine[t_idx, Ellipsis] = fine
            s_gain[t_idx, Ellipsis] = gain

            coarse, fine, gain = utils.split(in_reset)
            r_coarse[t_idx, Ellipsis] = coarse
            r_fine[t_idx, Ellipsis] = fine
            r_gain[t_idx, Ellipsis] = gain

            vin[i] = vin_value

        # split the rows into ADC groups
        print(s_coarse.shape)
        s_coarse.shape = self._raw_shape
        s_fine.shape = self._raw_shape
        s_gain.shape = self._raw_shape

        r_coarse.shape = self._raw_shape
        r_fine.shape = self._raw_shape
        r_gain.shape = self._raw_shape
        print(s_coarse.shape)

        # optimize memory layout for further processing
        s_coarse = s_coarse.transpose(self._transpose_order)
        s_fine = s_fine.transpose(self._transpose_order)
        s_gain = s_gain.transpose(self._transpose_order)

        r_coarse = r_coarse.transpose(self._transpose_order)
        r_fine = r_fine.transpose(self._transpose_order)
        r_gain = r_gain.transpose(self._transpose_order)
        print(s_coarse.shape)

        # the transpose is not done on the original arrays but creates a copy
        self._data_to_write["s_coarse"]["data"] = s_coarse
        self._data_to_write["s_fine"]["data"] = s_fine
        self._data_to_write["s_gain"]["data"] = s_gain

        self._data_to_write["r_coarse"]["data"] = r_coarse
        self._data_to_write["r_fine"]["data"] = r_fine
        self._data_to_write["r_gain"]["data"] = r_gain
