## coded by Trixi (with Manuelas & Alessandros help)
## look at distribution of fines for different coarses as 2d histogram crs vs fine


import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

from plot_base import PlotBase  # noqa E402o
import copy
import os


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["frame"] = None
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def plot_sample(self):
        self.create_dir()

#        title = ("Vin={}V, Sample: Row={}, Col={}"
#                 .format(self._vin, self._row, self._col))
        title = ("allFrames, Sample: Row={}, Col={}"
                 .format(self._row, self._col))
        out = os.path.join(self._output_dir,
                           "raw_2dHist_coarse_vs_fine_row{}_col{}"
                           .format(self._row, self._col))


        fig = plt.figure(figsize=None)

        cmap = matplotlib.pyplot.cm.jet
        cmap.set_under(color='white')

#        plt.hist2d(x, data, bins=n_bins, cmap=cmap, vmin=0.1)
        plt.hist2d(self._data["s_coarse"].flatten(), self._data["s_fine"].flatten(), cmap=cmap, vmin=0.1, bins=[32,244], range=[[0,32],[0,244]])

        plt.colorbar()

        fig.suptitle(title)
        plt.xlabel("crs")
        plt.ylabel("fn")

        fig.savefig(out)

        fig.clf()
        plt.close(fig)

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass
    
