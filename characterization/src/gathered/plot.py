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

        fig = plt.figure(figsize=None)

        plt.plot(x, data, ".", markersize=0.5, label=label)

        plt.legend()

        fig.suptitle(plot_title)
        plt.xlabel("V")
        plt.ylabel("ADU")

        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)
