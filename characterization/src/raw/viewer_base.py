from collections import namedtuple
import matplotlib.pyplot as plt

from load_raw import LoadRaw


class ViewerBase():
    LoadedData = namedtuple("loaded_data", ["data"])

    def __init__(self, loaded_data=None, dims_overwritten=False, **kwargs):

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._dims_overwritten = dims_overwritten

        if self._frame is not None:
            self._frame = None
            self._dims_overwritten = True

        loader = LoadRaw(input_fname=self._input_fname,
                         metadata_fname=self._metadata_fname,
                         output_dir=self._output_dir,
                         frame=self._frame)

        if loaded_data is None or self._dims_overwritten:
            self._data = loader.load_data()
        else:
            self._data = loaded_data.data

        self._tracker = None

    def get_dims_overwritten(self):
        """If the dimension originally configures overwritten.

        Return:
            A boolean if the config war overwritten or not.
        """
        return self._dims_overwritten

    def get_data(self):
        """Exposes data outside the class.

        Return:
            A named tuble with the loaded data. Entries
                x: filled up Vin read (to match the dimension of data)
                data: sample and reset data
        """

        return ViewerBase.LoadedData(data=self._data)

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
