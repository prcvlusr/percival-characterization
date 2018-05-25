"""Base class for all descrambling methods.
"""
import h5py

import __init__
from _version import __version__

class DescrambleBase():
    """Descramble base class.
    """
    def __init__(self, **kwargs):

        self._input = None
        self._output_fname = None

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

    def set_input(self, input_files):
        """To run the same descrambling for another set of input files.

        Args:
            input_files (list): List of input files (absolute path)
        """
        self._input = input_files

    def run(self):
        """Running the descrambling.
        """
        pass

    def _write_data(self):
        """Writes the data into a file.
        """

        with h5py.File(self._output_fname, "w", libver='latest') as out_f:

            for key, dset in self._data_to_write.items():
                try:
                    if "type" in dset:
                        out_f.create_dataset(dset['path'],
                                             data=dset['data'],
                                             dtype=dset['type'])
                    else:
                        out_f.create_dataset(dset['path'],
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
            out_f.create_dataset(name, data=__version__)

            out_f.flush()

    def get_data(self):
        """Return the descrambled data.
        """
        return self._data_to_write
