from collections import namedtuple
import glob
import h5py
import numpy as np
import os

from load_gathered import LoadGathered


class PlotBase():
    LoadedData = namedtuple("loaded_data", ["x",
                                            "data"])

    def __init__(self,
             input_fname_templ,
             output_dir,
             adc,
             col,
             rows,
             loaded_data=None):

        self._input_fname_templ = input_fname_templ
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._col = col
        self._rows = rows

        loader = LoadGathered(input_fname_templ=self._input_fname_templ,
                              output_dir=self._output_dir,
                              adc=self._adc,
                              col=self._col,
                              rows=self._rows)

        if loaded_data is None:
            self._x, self._data = loader.load_data()
        else:
            self._x = loaded_data.x
            self._data = loaded_data.data

    def create_dir(self):
        if not os.path.exists(self._output_dir):
            print("Output directory {} does not exist. Create it."
                  .format(self._output_dir))
            os.makedirs(self._output_dir)

    def get_data(self):
        """Exposes data outside the class.

        Return:
            A named tuble with the loaded data. Entries
                x: filled up Vin read (to match the dimension of data)
                data: sample and reset data
        """

        return PlotBase.LoadedData(x=self._x,
                                   data=self._data)

    def _generate_single_plot(self, x, data, plot_title, label, out_fname):
        print("_generate_single_plot method is not implemented.")

    def plot_sample(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc, self._col)
        suffix = "_adc{}_col{}".format(self._adc, self._col)
        out = self._output_dir+"/"

        self._generate_single_plot(x=self._x,
                                   data=self._data["s_coarse"],
                                   plot_title="Sample Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"sample_coarse"+suffix)
        self._generate_single_plot(x=self._x,
                                   data=self._data["s_fine"],
                                   plot_title="Sample Fine, "+pos,
                                   label="Fine",
                                   out_fname=out+"sample_fine"+suffix)
        self._generate_single_plot(x=self._x,
                                   data=self._data["s_gain"],
                                   plot_title="Sample Gain, "+pos,
                                   label="Gain",
                                   out_fname=out+"sample_gain"+suffix)

    def plot_reset(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc, self._col)
        suffix = "_adc{}_col{}".format(self._adc, self._col)
        out = self._output_dir+"/"

        self._generate_single_plot(x=self._x,
                                   data=self._data["r_coarse"],
                                   plot_title="Reset Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"reset_coarse"+suffix)
        self._generate_single_plot(x=self._x,
                                   data=self._data["r_fine"],
                                   plot_title="Reset Fine, "+pos,
                                   label="Fine",
                                   out_fname=out+"reset_fine"+suffix)
        self._generate_single_plot(x=self._x,
                                   data=self._data["r_gain"],
                                   plot_title="Reset Gain, "+pos,
                                   label="Gain",
                                   out_fname=out+"reset_gain"+suffix)

    def plot_combined(self):
        pass
