import h5py
import os
import sys
import time


try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

BASE_PATH = os.path.dirname(os.path.dirname(CURRENT_DIR))
SRC_PATH = os.path.join(BASE_PATH, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import utils  # noqa E402


class GatherBase(object):
    def __init__(self,
                 in_fname,
                 out_fname,
                 meta_fname):

        self._in_fname = in_fname
        self._out_fname = out_fname
        self._meta_fname = meta_fname

        self._data_to_write = {}

        print("\nStart gather\n"
              "in_fname = {}\n"
              "out_fname ={}\n"
              .format(self._in_fname, self._out_fname))

    def run(self):
        totalTime = time.time()

        self._load_data()

        print("Start saving at {} ... ".format(self._out_fname), end="")
        self._write_data()
        print("Done.")

        print("Gather took time:", time.time() - totalTime, "\n")

    def _load_data(self):
        pass

    def _write_data(self):
        if self._data_to_write == {}:
            raise Exception("Write data: No data found.")

        with h5py.File(self._out_fname, "w", libver='latest') as f:

            for key, dset in self._data_to_write.items():
                f.create_dataset(dset["path"],
                                 data=dset["data"],
                                 dtype=dset["type"])

            # save metadata from original files
            for key, value in iter(self._metadata.items()):
                gname = "collection"

                name = "{}/{}".format(gname, key)
                try:
                    f.create_dataset(name, data=value)
                except:
                    print("Error in", name, value.dtype)
                    raise

            f.flush()
