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

CALIBRATION_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils  # noqa E402
from _version import __version__  # noqa E402


class ProcessBase(object):
    def __init__(self, in_fname, out_fname):

        self._in_fname = in_fname
        self._out_fname = out_fname

        self._result = {}

        print("\n\nStart process")
        print("in_fname:", self._in_fname)
        print("out_fname:", self._out_fname)
        print()

    def _load_data(self, in_fname):
        pass

    def run(self):
        total_time = time.time()

        self._initiate()

        self._calculate()

        print("Start saving results at {} ... ".format(self._out_fname),
              end='')
        self._write_data()
        print("Done.")

        print("Process took time: {}\n".format(time.time() - total_time))

    def _initiate(self):
        pass

    def _calculate(self):
        pass

    def _get_mask(self, data):
        # find out if the col was effected by frame loss
        return (data == 0)

    def _mask_out_problems(self, data, mask=None):
        if mask is None:
            mask = self._get_mask(data)

        # remove the ones with frameloss
        m_data = np.ma.masked_array(data=data, mask=mask)

        return m_data

    def _fit_linear(self, x, y, mask=None):
        if mask is None:
            y_masked = y
            x_masked = x
        else:
            y_masked = y[~mask]
            x_masked = x[~mask]

        number_of_points = len(x_masked)
        try:
            A = np.vstack([x_masked, np.ones(number_of_points)]).T
        except:
            print("number_of_points", number_of_points)
            print("x (after masking)", x_masked)
            print("y (after masking)", y_masked)
            print("len y_masked", len(y_masked))
            raise

        # lstsq returns: Least-squares solution (i.e. slope and offset),
        #                residuals,
        #                rank,
        #                singular values
        res = np.linalg.lstsq(A, y_masked)

        return res

    def _write_data(self):
        with h5py.File(self._out_fname, "w", libver='latest') as f:
            for key in self._result:
                if "type" in self._result[key]:
                    f.create_dataset(self._result[key]['path'],
                                     data=self._result[key]['data'],
                                     dtype=self._result[key]['type'])
                else:
                    f.create_dataset(self._result[key]['path'],
                                     data=self._result[key]['data'])

            metadata_base_path = "collection"

            today = str(date.today())
            f.create_dataset("{}/creation_date".format(metadata_base_path),
                             data=today)

            name = "{}/{}".format(metadata_base_path, "version")
            f.create_dataset(name, data=__version__)

            f.flush()
