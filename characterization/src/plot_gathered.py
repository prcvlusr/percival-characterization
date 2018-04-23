import matplotlib
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
import numpy as np

from plot_base import PlotBase

class PlotGathered(PlotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _generate_single_plot(self, x, data, plot_title, label, out_fname, nbins):

        fig = plt.figure(figsize=None)
        if len(data.shape) == 1:
            stacked_x = x
            stacked_data = data
        else:
            stacked_x = np.tile(x, data.shape[0])
            stacked_data = np.hstack(data)

        plt.plot(stacked_x, stacked_data, ".", markersize = 0.5, label = label)

        plt.legend()

        fig.suptitle(plot_title)
        plt.xlabel("V")
        plt.ylabel("ADU")

        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)
