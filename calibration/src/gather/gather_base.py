"""Base class for all gather methods
"""
import os
import sys
import time
import h5py

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

CALIBRATION_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

from _version import __version__
import utils


class GatherBase(object):
    """Base class for all gather methods
    """
    def __init__(self, **kwargs):

        self._in_fname = None
        self._out_fname = None

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

#        print("attributes in  GatherBase", vars(self))

        self._data_to_write = {}
        self._metadata = {}

        print("\nStart gather\n"
              "in_fname = {}\n"
              "out_fname ={}\n"
              .format(self._in_fname, self._out_fname))

    def _get_output_dir(self, run_dir):
        """Fills up output template and creates output directory.
        Args:
            run_dir (string): String to insert in the output directory
                              template.
        Return:
            The output directory.
        """
        output = self._output.format(run_dir=run_dir)
        utils.create_dir(output)

        return output

    def run(self):
        """Run the gather method
        """
        total_time = time.time()

        self.initiate()

        self._load_data()

        self._write_data()

        print("Gather took time:", time.time() - total_time, "\n")

    def initiate(self):
        """Sets all required parameters
        """
        pass

    def _load_data(self):
        pass

    def _write_data(self):
        print("Start saving at {} ... ".format(self._out_fname), end="")

        if self._data_to_write == {} or self._data_to_write is None:
            raise Exception("Write data: No data found.")

        print("Output: ", self._out_fname)
        with h5py.File(self._out_fname, "w", libver='latest') as out_f:

            for key, dset in self._data_to_write.items():
                out_f.create_dataset(dset["path"],
                                     data=dset["data"],
                                     dtype=dset["type"])

            gname = "collection"
            # save metadata from original files
            for key, value in iter(self._metadata.items()):
                name = "{}/{}".format(gname, key)
                try:
                    out_f.create_dataset(name, data=value)
                except:
                    print("Error in", name, value.dtype)
                    raise

            name = "{}/{}".format(gname, "version")
            out_f.create_dataset(name, data=__version__)

            out_f.flush()

        print("Done.")
