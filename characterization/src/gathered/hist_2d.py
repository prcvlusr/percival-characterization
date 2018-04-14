import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F811
        super().__init__(**kwargs)

    def _generate_single_plot(self, x, data, plot_title, label, out_fname):
        n_bins = 100

        fig = plt.figure(figsize=None)

        cmap = matplotlib.pyplot.cm.jet
        cmap.set_under(color='white')

        plt.hist2d(x, data, bins=n_bins, cmap=cmap, vmin=0.1)

        plt.colorbar()

        fig.suptitle(plot_title)
        plt.xlabel("V")
        plt.ylabel("ADU")

        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)
