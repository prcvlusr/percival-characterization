from collections import namedtuple
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
    LinearFitResult = namedtuple("linear_fit_result", ["solution",
                                                       "residuals",
                                                       "rank",
                                                       "singular_values",
                                                       "r_squared"])

    def __init__(self, **kwargs):

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

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

    def _fit_linear(self, x, y, mask=None, enable_r_squared=False):
        """Solves the equation y = mx+ b for a given x and y.

        Args:
            x (numpy array): The x values corresponding to the data points to
                             fit.
            y (numpy array): The data points to fix.
            mask (optional): A mask of entries to not consider for the fitting.
            enable_r_squared (optional): enables the calculation of the
                                         coefficient of determination

        Return:
            A namped tuple with the fitting results and additionally quality
            measurements.
        """

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

        y_mean = np.mean(y_masked)
        y_diff = y_masked - y_mean
        all_zero = not np.any(y_diff)

        if all_zero:
            # the y values are constant
            slope = 0
            offset = y_mean

            res = [
                (slope, offset),  # solution
                None,  # residuals
                None,  # rang
                None  # singular_values
            ]

        else:
            # lstsq returns: Least-squares solution (i.e. slope and offset),
            #                residuals,
            #                rank,
            #                singular values
            res = np.linalg.lstsq(A, y_masked)

        if enable_r_squared:
            if all_zero:
                r_squared = 1
            else:
                try:
                    ss_tot = np.dot(y_diff, y_diff)
                    ss_res = res[1]  # this are the residuals given by lstsq

                    r_squared = 1 - ss_res/ss_tot
                except:
                    print("ERROR when calculating r squared.")
                    print("ss_tot", ss_tot)
                    print("ss_res", ss_res)
                    raise

        else:
            r_squared = None

        new_res = ProcessBase.LinearFitResult(solution=res[0],
                                              residuals=res[1],
                                              rank=res[2],
                                              singular_values=res[3],
                                              r_squared=r_squared)

        return new_res

    def _write_data(self):
        """Writes the result dictionary and additional metadata into a file.
        """

        with h5py.File(self._out_fname, "w", libver='latest') as f:

            # write data

            for key in self._result:
                if "type" in self._result[key]:
                    f.create_dataset(self._result[key]['path'],
                                     data=self._result[key]['data'],
                                     dtype=self._result[key]['type'])
                else:
                    f.create_dataset(self._result[key]['path'],
                                     data=self._result[key]['data'])

            # write metadata

            metadata_base_path = "collection"

            today = str(date.today())
            f.create_dataset("{}/creation_date".format(metadata_base_path),
                             data=today)

            name = "{}/{}".format(metadata_base_path, "version")
            f.create_dataset(name, data=__version__)

            name = "{}/{}".format(metadata_base_path, "method")
            f.create_dataset(name, data=self._method)

            f.flush()
