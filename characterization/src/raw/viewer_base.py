import copy
from collections import namedtuple
import matplotlib.pyplot as plt

from plot_base import PlotBase


class ViewerBase(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["frame"] = None
        new_kwargs["col"] = None
        new_kwargs["row"] = None
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

        self._tracker = None

    def plot_sample(self):
        pass

    def plot_reset(self):
        pass

    def plot_combined(self):
        if self._tracker is None:
            msg = "No tracker specified. Abort."
            raise Exception(msg)

        fig = self._tracker.get_fig()

        # connect to mouse wheel
        fig.canvas.mpl_connect("scroll_event", self._tracker.onscroll)

        # connect to arrow keys
        fig.canvas.mpl_connect("key_press_event", self._tracker.on_key_press)

        plt.show()
