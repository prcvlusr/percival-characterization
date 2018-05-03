from collections import namedtuple
import glob
import h5py
import numpy as np
import os

from load_gathered import LoadGathered
from load_processed import LoadProcessed


class PlotBase():
    LoadedData = namedtuple("loaded_data", ["x",
                                            "gathered_data",
                                            "constants"])
    def __init__(self,
             input_fname_templ,
             metadata_fname,
             output_dir,
             adc,
             frame,
             row,
             col,
             loaded_data=None,
             dims_overwritten=False):

        self._input_fname_templ = input_fname_templ
        self._metadata_fname = metadata_fname
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._frame = frame
        self._row = row
        self._col = col
        self._dims_overwritten = dims_overwritten

        gathered_loader = LoadGathered(
            input_fname_templ=self._input_fname_templ,
            output_dir=self._output_dir,
            adc=self._adc,
            frame=self._frame,
            row=self._row,
            col=self._col
        )

        processed_loader = LoadProcessed(
            input_fname_templ=self._input_fname_templ,
            output_dir=self._output_dir,
            adc=self._adc,
            row=self._row,
            col=self._col
        )

        if loaded_data is None or self._dims_overwritten:
            self._x, self._data = gathered_loader.load_data()
            self._constants = processed_loader.load_data()
        else:
            self._x = loaded_data.x
            self._data = loaded_data.gathered_data
            self._constants = loaded_data.constants

    def create_dir(self):
        if not os.path.exists(self._output_dir):
            print("Output directory {} does not exist. Create it."
                  .format(self._output_dir))
            os.makedirs(self._output_dir)

    def get_dims_overwritten(self):
        """If the dimension originally configures overwritten.

        Return:
            A boolean if the config war overwritten or not.
        """
        return self._dims_overwritten

    def get_data(self):
        """Exposes data outside the class.

        Return:
            A named tuble with the loaded data. Entries
                x: filled up Vin read (to match the dimension of data)
                data: sample and reset data

        """

        return PlotBase.LoadedData(x=self._x,
                                   gathered_data=self._data,
                                   constants=self._constants)

    def _generate_single_plot(self, x, data, plot_title, label, out_fname):
        print("_generate_single_plot method is not implemented.")

    def plot_sample(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc, self._col)
        suffix = "_adc{}_col{}".format(self._adc, self._col)
        out = self._output_dir+"/"

        self._generate_single_plot(x=self._x,
                                   data=self._data["s_coarse"],
                                   constants=self._constants["s_coarse"],
                                   plot_title="Sample Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"sample_coarse"+suffix)
#        self._generate_single_plot(x=self._x,
#                                   data=self._data["s_fine"],
#                                   constants=self._constants["s_fine"],
#                                   plot_title="Sample Fine, "+pos,
#                                   label="Fine",
#                                   out_fname=out+"sample_fine"+suffix)
#        self._generate_single_plot(x=self._x,
#                                   data=self._data["s_gain"],
#                                   constants=self._constants["s_gain"],
#                                   plot_title="Sample Gain, "+pos,
#                                   label="Gain",
#                                   out_fname=out+"sample_gain"+suffix)

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass
