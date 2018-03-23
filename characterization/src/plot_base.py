import glob
import h5py
import matplotlib
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
import numpy as np
import os

class PlotBase():
    def __init__(self, input_fname_templ, output_dir, adc, col, rows):

        self._input_fname_templ = input_fname_templ
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._col = col
        self._rows = rows

        self._input_fname = self._get_input_fname(self._input_fname_templ,
                                                  self._col)

        self._paths = {
            "s_coarse": "sample/coarse",
            "s_fine": "sample/fine",
            "s_gain": "sample/gain",
            "r_coarse": "reset/coarse",
            "r_fine": "reset/fine",
            "r_gain": "reset/gain",
        }

        self._metadata_paths = {
            "vin": "vin",
            "n_frames_per_run": "collection/n_frames_per_run"
        }

        self._n_frames_per_vin = None

        self._x, self._data = self._load_data(rows)

    def create_dir(self):
        if not os.path.exists(self._output_dir):
            print("Output directory {} does not exist. Create it."
                  .format(self._output_dir))
            os.makedirs(self._output_dir)

    def _get_input_fname(self, input_fname_templ, col):
        files = glob.glob(input_fname_templ.format(col_start="*",
                                                   col_stop="*"))

        # TODO do not use file name but "collections/columns_used" entry in
        # files
        prefix, middle = input_fname_templ.split("{col_start}")
        middle, suffix = middle.split("{col_stop}")

        searched_file = None
        for f in files:
            cols = f[len(prefix):-len(suffix)]
            cols = map(int, cols.split(middle))
            # convert str into int
            cols = list(map(int, cols))

            if cols[0] < col and col < cols[1]:
                searched_file = f
                break

        if searched_file is None:
            raise Exception("No files found which contains column {}."
                            .format(col))

        return searched_file


    def _load_data(self, rows):

        with h5py.File(self._input_fname, "r") as f:
            vin = f[self._metadata_paths["vin"]][()]
            self._n_frames_per_vin = f[self._metadata_paths["n_frames_per_run"]][()]

            data = {}
            for key, path in self._paths.items():
                d = f[path][self._adc, self._col, rows, :]

                data[key] = self._merge_groups_with_frames(d)

            if len(d.shape) == 1:
                n_groups = 1
            else:
                n_groups = d.shape[0]

        vin = self._fill_up_vin(vin, n_groups)

        return vin, data

    def _fill_up_vin(self, vin, n_groups):
        # create as many entries for each vin as there were original frames
        x = [np.full(self._n_frames_per_vin[i] * n_groups, v)
             for i, v in enumerate(vin)]

        x = np.hstack(x)

        return x

    def _merge_groups_with_frames(self, data):
        if len(data.shape) == 1:
            return data
        else:
            # data has the dimension (n_groups, n_frames)
            # should be transformed into (n_groups * n_frames)
            n_groups = data.shape[0]
            n_frames = data.shape[1]

            transpose_order = (1,0)
            tr_data = data.transpose(transpose_order)

            new_data = tr_data.reshape(n_groups * n_frames)

            return new_data

    def _generate_single_plot(self, x, data, plot_title, label, out_fname, nbins):
        print("_generate_singl_plot method is not implemented.")

    def plot_sample(self, nbins=None):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc, self._col)

        self._generate_single_plot(x=self._x,
                                   data=self._data["s_coarse"],
                                   plot_title="Sample Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=self._output_dir+"/"+"sample_coarse",
                                   nbins=nbins)
        self._generate_single_plot(x=self._x,
                                   data=self._data["s_fine"],
                                   plot_title="Sample Fine, "+pos,
                                   label="Fine",
                                   out_fname=self._output_dir+"/"+"sample_fine",
                                   nbins=nbins)
        self._generate_single_plot(x=self._x,
                                   data=self._data["s_gain"],
                                   plot_title="Sample Gain, "+pos,
                                   label="Gain",
                                   out_fname=self._output_dir+"/"+"sample_gain",
                                   nbins=nbins)

    def plot_reset(self, nbins=None):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc, self._col)

        self._generate_single_plot(x=self._x,
                                   data=self._data["r_coarse"],
                                   plot_title="Reset Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=self._output_dir+"/"+"reset_coarse",
                                   nbins=nbins)
        self._generate_single_plot(x=self._x,
                                   data=self._data["r_fine"],
                                   plot_title="Reset Fine, "+pos,
                                   label="Fine",
                                   out_fname=self._output_dir+"/"+"reset_fine",
                                   nbins=nbins)
        self._generate_single_plot(x=self._x,
                                   data=self._data["r_gain"],
                                   plot_title="Reset Gain, "+pos,
                                   label="Gain",
                                   out_fname=self._output_dir+"/"+"reset_gain",
                                   nbins=nbins)
