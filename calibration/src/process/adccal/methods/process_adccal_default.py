''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
        shapes = {
            "offset": (self._n_adcs, self._n_cols),
            "vin_size": (self._n_frames * self._n_groups) 
        }

        if self._method_properties["fit_adc_part"] == "coarse":
            self._result = {
                "s_coarse_offset": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/coarse/offset",
                },
                "s_coarse_slope": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/coarse/slope"
                },
                "s_coarse_residuals": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/coarse/residuals"
                }
           }

        if self._method_properties["fit_adc_part"] == "fine":
            self._result = {
                "s_fine_offset": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/fine/offset"
                },
                "s_fine_slope": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/fine/slope"
                }
            }

    def _calculate(self):
        ''' Perform a linear fit on sample ADC coarse and fine.
            The offsets and slopes are stored in a HDF5 file.
        '''

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)

        if self._method_properties["fit_adc_part"] == "coarse":
            print("Data loaded, fitting coarse data...")
            # convert (n_adcs, n_cols, n_groups, n_frames)
            #      -> (n_adcs, n_cols, n_groups * n_frames)
            self._merge_groups_with_frames(data["s_coarse"])
            # create as many entries for each vin as there were original frames
            vin = self._fill_up_vin(data["vin"])
            sample = data["s_coarse"]
            fitting_range = self._method_properties["coarse_fitting_range"]
            offset = self._result["s_coarse_offset"]["data"]
            slope = self._result["s_coarse_slope"]["data"]
            residuals = self._result["s_coarse_residuals"]["data"]

            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    adu = sample[adc, col, :]
                    idx_fit = np.where(np.logical_and(adu < fitting_range[1], 
                                                      adu > fitting_range[0]))
                    if np.any(idx_fit):
                        fit_result = self._fit_linear(vin[idx_fit], adu[idx_fit])
                        slope[adc, col], offset[adc, col] = fit_result.solution
                        #offset[adc, col] = slope[adc, col] * vin[0] + offset[adc, col]
                        print(fit_result.residuals)
                        residuals[adc, col] = fit_result.residuals
                    else:
                        slope[adc, col] = np.NaN
                        offset[adc, col] = np.NaN
                        residuals[adc, col] = np.NaN
            
            self._result["s_coarse_slope"]["data"] = slope
            self._result["s_coarse_offset"]["data"] = offset
            self._result["s_coarse_residuals"]["data"] = residuals

        elif self._method_properties["fit_adc_part"] == "fine":
            print("Data loaded, fitting fine data...")
            # convert (n_adcs, n_cols, n_groups, n_frames)
            #      -> (n_adcs, n_cols, n_groups * n_frames)
            self._merge_groups_with_frames(data["s_fine"])
            self._merge_groups_with_frames(data["s_coarse"])
            # create as many entries for each vin as there were original frames
            vin = self._fill_up_vin(data["vin"])
            sample = data["s_fine"]
            sample_coarse = data["s_coarse"]
            fitting_range = self._method_properties["fine_fitting_range"]
            offset = self._result["s_fine_offset"]["data"]
            slope = self._result["s_fine_slope"]["data"]

            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    adu = sample[adc, col, :]
                    idx_fit = np.where(sample_coarse[adc, col, :] == fitting_range)
                    if np.any(idx_fit):
                        fit_result = self._fit_linear(vin[idx_fit], adu[idx_fit])
                        slope[adc, col], offset[adc, col] = fit_result.solution
                        offset[adc, col] = slope[adc, col] * vin[idx_fit][0] + offset[adc, col]
                    else:
                        slope[adc, col] = np.NaN
                        offset[adc, col] = np.NaN
            
            self._result["s_fine_slope"]["data"] = slope
            self._result["s_fine_offset"]["data"] = offset
