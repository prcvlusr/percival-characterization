import h5py
import numpy as np
import os
import sys

from utils_config import *  # noqa F401
from utils_data import *  # noqa F401


def create_dir(directory_name):
    """Creates a directory including supdirectories if it does not exist.

    Args:
        direcoty_name: The path of the direcory to be created.
    """
    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
            print("Dir '{}' does not exist. Create it."
                  .format(directory_name))
        except IOError:
            if os.path.isdir(directory_name):
                pass


def check_file_exists(file_name, quit=True):
    """Checks if a file already exists.

    Args:
        file_name: The file to check for existence
        quit (optional): Quit the program if the file exists or not.
    """

    print("file_name = {}".format(file_name))
    if os.path.exists(file_name):
        print("File already exists")
        if quit:
            sys.exit(1)
    else:
        print("File: ok")


def load_file_content(fname, excluded=[]):
    """Load the HDF5 file into a dictionary.

    Args:
        fname: The name of the HDF5 file to be loaded.
        excluded (optional): The data paths which should be excluded from
        loading.

    Return:
        A dictionary containing the content of the content of the file where
        the keys are the paths in the original file.

        HDF5 file:
            my_group
                my_dataset: numpy array

        dictionary:
            "mygroup/mydataset": numpy array
    """

    file_content = {}

    def get_file_content(name, obj):
        if isinstance(obj, h5py.Dataset) and name not in excluded:
            file_content[name] = obj[()]
            # if object types are not converted writing gives the error
            # TypeError: Object dtype dtype('O') has no native HDF5 equivalent
            if (isinstance(file_content[name], np.ndarray) and
                    file_content[name].dtype == object):
                file_content[name] = file_content[name].astype('S')

    with h5py.File(fname, "r") as f:
        f.visititems(get_file_content)

    return file_content


class IndexTracker(object):
    def __init__(self, data, method_properties):

        self._data = data
        self._method_properties = method_properties
        self._slice = None
        self._window_title = None
        self._fig = None

        self.initiate()

        self.set_data()

        self._update()

    def initiate(self):
        """Initiate the canvas and all needed plot attributes.
        """

        msg = "initiate is not implementated. Abort."
        raise Exception(msg)

    def set_data(self):
        """Creates the plot and assign the data to it.
        """

        msg = "set_data is not implementated. Abort."
        raise Exception(msg)

    def update_plots(self):
        """What plots should be updated on the events and how.
        """
        msg = "update_plots is not implemented. Abort."
        raise Exception(msg)

    def get_fig(self):
        """Returns the self._fig figure on which the canvas was created.

        Returns:
            The matplotlib.figure.Figure object initiated in the initiate
            method.
        """

        return self._fig

    def onscroll(self, event):
        """How to react if the mouse wheel is scrolled.

        Args:
            event: Event that you can connect to.
        """

#        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self._frame = (self._frame + 1) % self._slices
        else:
            self._frame = (self._frame - 1) % self._slices

        self._update()

    def on_key_press(self, event):
        """How to react if a key is pressed.

        Args:
            event: Event that you can connect to.
        """

        if event.key in ["right", "up"]:
            self._frame = (self._frame + 1) % self._slices
        elif event.key in ["left", "down"]:
            self._frame = (self._frame - 1) % self._slices

        self._update()

    def _update(self):
        """Updates the plots.
        """

        self.update_plots()

        self._fig.suptitle(self._window_title)

        self._fig.canvas.draw()
