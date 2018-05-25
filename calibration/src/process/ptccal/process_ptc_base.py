"""Base class for PTC calibration processing
"""
import h5py
import time


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

        print("Start saving results at {} ... ".format(self._out_fname),
              end='')
        self._write_data()
        print("Done.")

        print("Process took time: {}\n\n", time.time() - total_time)

    def calculate(self):
        pass
