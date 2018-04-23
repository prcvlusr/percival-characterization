import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
        shapes = {
            "offset": (self._n_cols, self._n_adcs)
        }

        self._result = {
            # must have entries for correction
            "s_coarse_offset": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/offset",
                "type": np.int16
            },
            "s_coarse_slope":{
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/slope",
                "type": np.int16
            },

            # additional information
            "stddev": {
                "data": np.empty(shapes["offset"]),
                "path": "stddev",
                "type": np.int16
            },
        }

    def _calculate(self):
        '''
          Method which calculates fit of ADC outputs as a function of Vin.
          It looks for a range in which the fit should be applied.
          It returns fit results (slope), offset and standard deviation.  
        '''
        np.set_printoptions(threshold=np.nan)

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)
        print("Done.")

        #print(data["s_coarse"][self._n_adcs - 1, self._n_cols - 1, 0, :])
       
        # convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
        
        sample_coarse = self._merge_groups_with_frames(data["s_coarse"])

        #print(sample_coarse[self._n_adcs - 1, self._n_cols - 1, :]) # All values corresponding to one ADC of one column
        #print(sample_coarse[1, 100, :]) # All values corresponding to one ADC of one column

        # create as many entries for each vin as there were original frames
<<<<<<< HEAD
        vin = self._fill_up_vin(data["vin"])
        slope = self._result["s_coarse_slope"]["data"]
        offset = self._result["s_coarse_offset"]["data"]

        fit_result_list = []
        for adc in range(self._n_adcs):
            #print(adc)
            for col in range(33, self._n_cols):
                adu_coarse = sample_coarse[adc, col, :]
                fit_result = self._fit_linear(vin, adu_coarse)
                slope[adc, col] = fit_result[0]
                offset[adc, col] = fit_result[1]
                self._result["s_coarse_slope"]["data"] = slope
                self._result["s_coarse_offset"]["data"] = offset



                #fit_result = self._fit_linear(vin, adu_coarse)
                #fit_result_list.append(fit_result[0])
                #fit_result.append(self._fit_linear(vin, adu_coarse))
                #self._result["s_coarse_offset"]["data"] = fit_result[0]
                #print(fit_result[0])
                #print(adu_coarse)
                #print(adu_coarse)
                #idx_max = np.where(adu_coarse < 30)      
                #idx_min = np.where(adu_coarse > 0 )
                #if(idx_max[0][0]):
                #    print(idx_max[0][0])
                #print(idx_min[-1][-1])

                #print("(", idx_max[0], ", ", idx_min[-1], ")")
               
                #print(idx_max[0], idx_min[0])
                #idx_max = np.where(np.all(adu_coarse < 25))[0]
                #idx_min = np.where(np.all(adu_coarse > 5))[0]

                #if (idx_max-idx_min).all():
                #if (idx_max[0][0] and idx_min[-1][-1]): 
                #    print("here")
                #    fit_result = self._fit_linear(vin[idx_max[0][0]:idx_min[-1][-1]], adu_coarse[idx_max[0][0]:idx_min[-1][-1]])
                #else:
                #    fit_result = self._fit_linear(vin, adu_coarse)
                #print(idx_max, idx_min)
                ##if idx:
                ##    print(idx)
                ##    print("oui oui")
                ##    fit_result = self._fit_linear(vin[idx], adu_coarse[idx])
                ##else:
                ##    fit_result = self._fit_linear(vin, adu_coarse)
                #fit_result_list.append(fit_result[0])
=======
        vin = self._fill_up_vin(data["vin"])  # noqa F841

        # TODO
        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                # x = ... (subset of vin)
                # y = ... (subset of data["s_coarse"][adc, col, :])
                # res = self._fit_linear(x, y)
                pass
>>>>>>> master

        #print(fit_result_list)
        #self._result["s_coarse_offset"]["data"] = fit_result_list
        #print(self._result["s_coarse_offset"]["data"])
        #print(np.argwhere(aduCoarse == np.argmin(aduCoarse)))
        #print("Start computing means and standard deviations ...", end="")
        #offset = np.mean(data["s_coarse"], axis=2).astype(np.int)
        #self._result["s_coarse_offset"]["data"] = offset

        self._result["stddev"]["data"] = data["s_coarse"].std(axis=2)
        print("Done.")
