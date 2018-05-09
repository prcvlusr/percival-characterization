import matplotlib.pyplot as plt

from utils import IndexTracker
from viewer_base import ViewerBase


class ViewTracker(IndexTracker):
    def initiate(self):
        self._fig, self._ax = plt.subplots(2, 3, sharex=True, sharey=True)

        self._slices, _, _ = self._data["s_coarse"].shape
        self._frame = 0

    def set_data(self):
        # for convenience
        d = self._data
        f = self._frame

        self._im_s_coarse = self._ax[0][0].imshow(d["s_coarse"][f])
        self._im_s_fine = self._ax[0][1].imshow(d["s_fine"][f])
        self._im_s_gain = self._ax[0][2].imshow(d["s_gain"][f])

        self._im_r_coarse = self._ax[1][0].imshow(d["r_coarse"][f])
        self._im_r_fine = self._ax[1][1].imshow(d["r_fine"][f])
        self._im_r_gain = self._ax[1][2].imshow(d["r_gain"][f])

        self._ax[0][0].set_title("sample coarse")
        self._ax[0][1].set_title("sample fine")
        self._ax[0][2].set_title("sample gain")
        self._ax[1][0].set_title("reset coarse")
        self._ax[1][1].set_title("reset fine")
        self._ax[1][2].set_title("reset gain")

    def update_plots(self):
        """Updates the plots.
        """
        self._im_s_coarse.set_data(self._data["s_coarse"][self._frame])
        self._im_s_fine.set_data(self._data["s_fine"][self._frame])
        self._im_s_gain.set_data(self._data["s_gain"][self._frame])
        self._im_r_coarse.set_data(self._data["r_coarse"][self._frame])
        self._im_r_fine.set_data(self._data["r_fine"][self._frame])
        self._im_r_gain.set_data(self._data["r_gain"][self._frame])

        self._window_title = "Frame {}".format(self._frame)


class Plot(ViewerBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._tracker = ViewTracker(data=self._data)
