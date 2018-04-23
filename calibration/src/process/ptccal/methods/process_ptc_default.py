import numpy as np

from process_base import ProcessPtcBase


class ProcessPtcMethod(ProcessPtcBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def initiate(self):
        self.n_offsets = len(self.runs)

        self.shapes = {
            "offset": (self.n_offsets,
                       self.n_memcells,
                       self.n_rows,
                       self.n_cols),
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
        for i, run_number in enumerate(self.runs):
            in_fname = self.in_fname.format(run_number=run_number)

            print("Start loading data from {} ...".format(in_fname), end="")
            analog, digital = self.load_data(in_fname)
            print("Done.")

            print("Start computing means and standard deviations ...", end="")
            offset = np.mean(analog, axis=0).astype(np.int)

            self.result["offset"]["data"][i, ...] = offset

            s = self.result["stddev"]["data"][i, ...]
            for cell in np.arange(self.n_memcells):
                s[cell, ...] = analog[:, cell, :, :].std(axis=0)
            print("Done.")
