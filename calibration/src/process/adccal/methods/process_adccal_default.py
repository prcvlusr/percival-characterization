import sys
import numpy as np
import os

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

BASE_PATH = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(CURRENT_DIR)
                    )
                )
            )
SRC_PATH = os.path.join(BASE_PATH, "src")
PROCESS_PATH = os.path.join(SRC_PATH, "process")
ADCCAL_PATH = os.path.join(PROCESS_PATH, "adccal")

if ADCCAL_PATH not in sys.path:
    sys.path.insert(0, ADCCAL_PATH)

from process_adccal_base import ProcessAdccalBase

class ProcessAdccalMethod(ProcessAdccalBase):
    #def __init__(self, in_fname, out_fname, runs):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def initiate(self):
        self.shapes = {
            "offset": (self.n_rows, self.n_cols)
        }

        self.result = {
            # must have entries for correction
            "offset": {
                "data": np.empty(self.shapes["offset"]),
                "path": "offset",
                "type": np.int16
            },
            # additional information
            "stddev": {
                "data": np.empty(self.shapes["offset"]),
                "path": "stddev",
                "type": np.int16
            },
        }

    def calculate(self):
        print("Start loading data from {} ...".format(self.in_fname), end="")
        data = self.load_data(self.in_fname)
        print("Done.")

        print("Start computing means and standard deviations ...", end="")
        offset = np.mean(data, axis=0).astype(np.int)
        self.result["offset"]["data"] = offset

        self.result["stddev"]["data"] = data.std(axis=0)
        print("Done.")
