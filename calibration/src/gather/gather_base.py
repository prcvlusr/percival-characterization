import h5py
import numpy as np
import os
import sys
import time
import glob


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
                 meta_fname,
                 runs):

        self._in_fname = in_fname
        self._out_fname = out_fname
        self._meta_fname = meta_fname

        self.runs = [int(r) for r in runs]

        self._data_path = "data"
        self._data = None

        self._n_parts = 1

        self._n_rows_total = 128
        self._n_cols_total = 512

        print("\nStart gather\n"
              "in_fname = {}\n"
              "out_fname ={}\n"
              "data_path = {}"
              .format(self._in_fname,
                      self._out_fname,
                      self._data_path))

    def run(self):
        totalTime = time.time()

        self._load_data()

        print("Start saving at {} ... ".format(self._out_fname), end="")
        self._write_data()
        print("Done.")

        print("Gather took time:", time.time() - totalTime, "\n")

    def _load_data(self):

        self.metadata = {}

        for run_idx, run_number in enumerate(self.runs):
            print("\nrun {}".format(run_number))

            for i in range(self._n_parts):
                fname = self._in_fname.format(run_number=run_number, part=i)
                print("Loading file {}".format(fname))

                with h5py.File(fname, "r") as f:
                    data = f[self._data_path][()]

                # load metadata seperatly
                excluded = [self._data_path]
                file_content = utils.load_file_content(fname, excluded)

                self.metadata[fname] = file_content

        self._data = data[...]

    def _write_data(self):

        with h5py.File(self._out_fname, "w", libver='latest') as f:
            f.create_dataset("data", data=self._data, dtype=np.int16)

#            # save metadata from original files
#            idx = 0
#            for set_name, set_value in iter(self.metadata.items()):
#                    gname = "metadata_{}".format(idx)
#
#                    name = "{}/source".format(gname)
#                    f.create_dataset(name, data=set_name)
#
#                    for key, value in iter(set_value.items()):
#                        try:
#                            name = "{}/{}".format(gname, key)
#                            f.create_dataset(name, data=value)
#                        except:
#                            print("Error in", name, value.dtype)
#                            raise
#                    idx += 1

            f.flush()
