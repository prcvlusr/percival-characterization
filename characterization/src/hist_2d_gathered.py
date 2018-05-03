import glob
import h5py
import matplotlib
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
import numpy as np
import os

from plot_base import PlotBase

class Hist2dGathered(PlotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _generate_single_plot(self, x, data, plot_title, label, out_fname, nbins):

        fig = plt.figure(figsize=None)
        if len(data.shape) == 1:
            stacked_x = x
            stacked_data = data
        else:
            stacked_x = np.tile(x, data.shape[0]).astype(np.float)
            stacked_data = np.hstack(data).astype(np.int)

        plt.hist2d(stacked_x, stacked_data, bins=100)#, cmin=1)
        plt.colorbar()

        fig.suptitle(plot_title)
        plt.xlabel("V")
        plt.ylabel("ADU")

        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)
