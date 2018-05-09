import copy
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
import os  # noqa E402

from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["frame"] = None
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def plot_sample(self):
        self.create_dir()

        title = ("Vin={}V, Sample: Row={}, Col={}"
                 .format(self._vin, self._row_title, self._col_title))
        out = os.path.join(self._output_dir,
                           "sample_coarse-fine_vs_image_row{}_col{}"
                           .format(self._row_title, self._col_title))

        self._generate_single_plot(x=range(self._data["s_coarse"].shape[0]),
                                   data_coarse=self._data["s_coarse"],
                                   data_fine=self._data["s_fine"],
                                   plot_title=title,
                                   out_fname=out)

    def plot_reset(self):
        self.create_dir()

        title = ("Vin={}V, Reset: Row={}, Col={}"
                 .format(self._vin, self._row_title, self._col_title))
        out = os.path.join(self._output_dir,
                           "reset_coarse-fine_vs_image_row{}_col{}"
                           .format(self._row_title, self._col_title))

        self._generate_single_plot(x=range(self._data["r_coarse"].shape[0]),
                                   data_coarse=self._data["r_coarse"],
                                   data_fine=self._data["r_fine"],
                                   plot_title=title,
                                   out_fname=out)

    def plot_combined(self):
        pass

    def _generate_single_plot(self,
                              x,
                              data_coarse,
                              data_fine,
                              plot_title,
                              out_fname):
        fig, ax1 = plt.subplots()

        ax2 = ax1.twinx()
        ax1.plot(x, data_coarse, 'bo', mfc="None")
        ax2.plot(x, data_fine, 'rx')

        ax1.set_xlabel('images')
        ax1.set_ylabel('coarse[ADU]', color='b')
        ax2.set_ylabel('fine[ADU]', color='r')

        ax1.tick_params(axis='y', colors='blue')
        ax2.tick_params(axis='y', colors='red')

        fig.suptitle(plot_title)
        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)
