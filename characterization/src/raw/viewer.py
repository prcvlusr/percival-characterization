from collections import namedtuple
import h5py
import matplotlib.pyplot as plt
import numpy as np
import os

from load_raw import LoadRaw
import utils


class Plot():
    LoadedData = namedtuple("loaded_data", ["data"])

    def __init__(self,
             input_fname_templ,
             output_dir,
             adc,
             col,
             rows,
             loaded_data=None):

        self._input_fname = input_fname_templ
        self._output_dir = os.path.normpath(output_dir)
        self._frame = adc
        self._col = col
        self._rows = rows

        loader = LoadRaw(input_fname=self._input_fname,
                         output_dir=self._output_dir,
                         frame=self._frame)

        if loaded_data is None:
            self._data = loader.load_data()
        else:
            self._data = loaded_data.data

    def get_data(self):
        """Exposes data outside the class.

        Return:
            A named tuble with the loaded data. Entries
                x: filled up Vin read (to match the dimension of data)
                data: sample and reset data
        """

        return Plot.LoadedData(data=self._data)

    def plot_sample(self):
        pass

    def plot_reset(self):
        pass

    def plot_combined(self):

        fig, ax = plt.subplots(2, 3, sharex=True, sharey=True)

        tracker = utils.IndexTracker(fig, ax, self._data)

        # connect to mouse wheel
        fig.canvas.mpl_connect("scroll_event", tracker.onscroll)

        # connect to arrow keys
        fig.canvas.mpl_connect("key_press_event", tracker.on_key_press)

        plt.show()
