import glob
import h5py
import matplotlib
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
import numpy as np
import os

from plot_base import PlotBase

class HistGathered(PlotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _generate_single_plot(self, x, data, plot_title, label, out_fname, nbins):

        # plot data
        fig = plt.figure(figsize=None)

        plt.hist(data, bins=nbins)
        plt.xlabel('ADU');
        plt.ylabel('#values');

        fig.suptitle(plot_title)
        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)
