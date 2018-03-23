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

        plt.plot(x, data, ".", markersize=0.5, label=label)

        plt.legend()

        fig.suptitle(plot_title)
        plt.xlabel("V")
        plt.ylabel("ADU")

        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)
