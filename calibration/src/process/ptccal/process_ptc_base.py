import h5py
import sys
import numpy as np
import time
import os
from datetime import date

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

BASE_PATH = os.path.dirname(os.path.dirname(CURRENT_DIR))
SRC_PATH = os.path.join(BASE_PATH, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import utils  # noqa E402


class ProcessPtcBase(object):
    def __init__(self, in_fname, out_fname, runs):

        self._out_fname = out_fname

        # public attributes for use in inherited classes
        self.in_fname = in_fname

        self.runs = runs

        # TODO extract n_cols and n_rows from raw_shape
        self.n_rows = 128
        self.n_cols = 512

        in_fname = self.in_fname.format(run_number=self.runs[0])

        self.shapes = {}
        self.result = {}

        in_fname = self.in_fname.format(run_number=self.runs[0])

        print("\n\n\nStart process")
        print("in_fname:", self.in_fname)
        print("out_fname:", self._out_fname)
        print()

        self.run()

    def load_data(self, in_fname):
        with h5py.File(in_fname, "r") as f:
            data = f['data'][()]

        return data

    def initiate(self):
        pass

    def run(self):

        total_time = time.time()

        self.initiate()

        self.calculate()

        print("Start saving results at {} ... ".format(self._out_fname), end='')
        self.write_data()
        print("Done.")

        print("Process took time: {}\n\n", time.time() - total_time)

    def calculate(self):
        pass

    def write_data(self):
        with  h5py.File(self._out_fname, "w", libver='latest') as f:
            for key in self.result:
                f.create_dataset(self.result[key]['path'],
                                 data=self.result[key]['data'],
                                 dtype=self.result[key]['type'])

            # convert into unicode
            if type(self.runs[0]) == str:
                used_run_numbers = [run.encode('utf8') for run in self.runs]
            else:
                used_run_numbers = ["r{:04d}".format(run).encode('utf8')
                                    for run in self.runs]

            today = str(date.today())
            metadata_base_path = "collection"

            f.create_dataset("{}/run_number".format(metadata_base_path),
                             data=used_run_numbers)
            f.create_dataset("{}/creation_date".format(metadata_base_path),
                             data=today)

            f.flush()
