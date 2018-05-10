import matplotlib.pyplot as plt

from utils import IndexTracker
from viewer_base import ViewerBase


class ViewTracker(IndexTracker):
    def initiate(self):
        self._subplots_rows = 2
        self._subplots_cols = 3

        self._n_rows = 1440
        self._n_cols = 1484

        self._fig, self._ax = plt.subplots(nrows=self._subplots_rows,
                                           ncols=self._subplots_cols,
                                           figsize=(14, 8))
#                                           figsize=(12.5, 8))
#                                           sharex=True,
#                                           sharey=True)

        plt.subplots_adjust(wspace=0.35, hspace=0.35)

        self._slices, _, _ = self._data["s_coarse"].shape
        self._frame = 0

        self._cmap = plt.cm.jet
        self._cmap.set_under(color='white')

        self._label_x = "col"
        self._label_y = "row"

        self._plot_kwargs = dict(
            interpolation="none",
            cmap=self._cmap,
            vmin=self._method_properties["err_below"]
        )

        # initiate with None as placeholder
        self._im = [[None for i in range(self._subplots_cols)]
                    for j in range(self._subplots_rows)]

    def set_data(self):
        """
        2D scatter plot of Smpl/Rst, Gn/Crs/Fn, give mark as error (white)
        the values << err_below.
        """

        # for convenience
        d = self._data
        f = self._frame

        self._im[0][0] = self._ax[0][0].imshow(d["s_gain"][f],
                                               **self._plot_kwargs)
        self._im[0][1] = self._ax[0][1].imshow(d["s_coarse"][f],
                                               **self._plot_kwargs)
        self._im[0][2] = self._ax[0][2].imshow(d["s_fine"][f],
                                               **self._plot_kwargs)

        self._im[1][0] = self._ax[1][0].imshow(d["r_gain"][f],
                                               **self._plot_kwargs)
        self._im[1][1] = self._ax[1][1].imshow(d["r_coarse"][f],
                                               **self._plot_kwargs)
        self._im[1][2] = self._ax[1][2].imshow(d["r_fine"][f],
                                               **self._plot_kwargs)

        # settings applying to all axes
        c_bar = [[None for i in range(self._subplots_cols)]
                 for j in range(self._subplots_rows)]
        for i, ax_rows in enumerate(self._ax):
            for j, a in enumerate(ax_rows):
                a.set_xlabel(self._label_x)
                a.set_ylabel(self._label_y)

                a.set_xlim([0, self._n_rows])
                a.set_ylim([0, self._n_cols])

                a.invert_xaxis()
                a.invert_yaxis()

                c_bar[i][j] = self._fig.colorbar(self._im[i][j],
                                                 ax=self._ax[i][j],
                                                 fraction=0.047,
                                                 pad=0.04)

        self._ax[0][0].set_title("Sample Gain")
        c_bar[0][0].set_clim(0, 3)
        self._ax[0][1].set_title("Sample Coarse")
        c_bar[0][1].set_clim(0, 31)
        self._ax[0][2].set_title("Sample Fine")
        c_bar[0][2].set_clim(0, 255)

        self._ax[1][0].set_title("Reset Gain")
        c_bar[1][0].set_clim(0, 3)
        self._ax[1][1].set_title("Reset Coarse")
        c_bar[1][1].set_clim(0, 31)
        self._ax[1][2].set_title("Reset Fine")
        c_bar[1][2].set_clim(0, 255)

    def update_plots(self):
        """Updates the plots.
        """
        self._im[0][0].set_data(self._data["s_gain"][self._frame])
        self._im[0][1].set_data(self._data["s_coarse"][self._frame])
        self._im[0][2].set_data(self._data["s_fine"][self._frame])

        self._im[1][0].set_data(self._data["r_gain"][self._frame])
        self._im[1][1].set_data(self._data["r_coarse"][self._frame])
        self._im[1][2].set_data(self._data["r_fine"][self._frame])

        self._window_title = "Frame {}".format(self._frame)


class Plot(ViewerBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._tracker = ViewTracker(data=self._data,
                                    method_properties=self._method_properties)
