import h5py

import __init__
import utils
from _version import __version__


class DescrambleBase():
    def __init__(self, **kwargs):  # noqa F401

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._data_to_write = {
            "sample": {
                "path": "data",
                "data": None,
            },
            "reset": {
                "path": "reset",
                "data": None,
            }
        }

    def set_input(self, input):
        """To run the same descrambling for another set of input files.

        Args:
            input (list): List of input files (aboslute path)
        """
        self._input = input

    def run(self):
        pass

    def _write_data(self):
        """Writes the data into a file.
        """

        with h5py.File(self._output_fname, "w", libver='latest') as f:

            for key, dset in self._data_to_write.items():
                try:
                    if "type" in dset:
                        f.create_dataset(dset['path'],
                                         data=dset['data'],
                                         dtype=dset['type'])
                    else:
                        f.create_dataset(dset['path'],
                                         data=dset['data'])
                except:
                    if dset["data"] is None:
                        msg = ("No {} data set. Abort saving to file."
                               .format(key))
                        raise Exception(msg)
                    else:
                        raise

            gname = "collection"

            name = "{}/{}".format(gname, "version")
            f.create_dataset(name, data=__version__)

            f.flush()

    def get_data(self):
        return self_data_to_write
