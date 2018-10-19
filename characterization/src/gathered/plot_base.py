from collections import namedtuple
import os

from load_gathered import LoadGathered
import utils


class PlotBase():
    LoadedData = namedtuple("loaded_data", ["vin",
                                            "data"])

    def __init__(self, loaded_data=None, dims_overwritten=False, **kwargs):

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._dims_overwritten = dims_overwritten

        loader = LoadGathered(input_fname_templ=self._input_fname,
                              output_dir=self._output_dir,
                              adc=self._adc,
                              frame=self._frame,
                              row=self._row,
                              col=self._col)

        if loaded_data is None or self._dims_overwritten:
            self._vin, self._data = loader.load_data()
        else:
            self._vin = loaded_data.vin
            self._data = loaded_data.data

        if self._dims_overwritten:
            print("Overwritten configuration " +
                  "(adc={}, frame={}, row={}, col={})"
                  .format(self._adc, self._frame, self._row, self._col))

        # to ease nameing plots
        self._adc_title = utils.convert_slice_to_tuple(self._adc)
        self._frame_title = utils.convert_slice_to_tuple(self._frame)
        self._row_title = utils.convert_slice_to_tuple(self._row)
        self._col_title = utils.convert_slice_to_tuple(self._col)

    def create_dir(self):
        if not os.path.exists(self._output_dir):
            print("Output directory {} does not exist. Create it."
                  .format(self._output_dir))
            os.makedirs(self._output_dir)

    def get_dims_overwritten(self):
        """If the dimension originally configures overwritten.

        Return:
            A boolean if the config war overwritten or not.
        """
        return self._dims_overwritten

    def get_data(self):
        """Exposes data outside the class.

        Return:
            A named tuble with the loaded data. Entries
                x: filled up Vin read (to match the dimension of data)
                data: sample and reset data
        """

        return PlotBase.LoadedData(vin=self._vin,
                                   data=self._data)

    def _generate_single_plot(self, x, data, plot_title, label, out_fname):
        print("_generate_single_plot method is not implemented.")

    def plot_sample(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc_title, self._col_title)
        suffix = "_adc{}_col{}".format(self._adc_title, self._col_title)
        out = self._output_dir + "/"

        self._generate_single_plot(x=self._vin,
                                   data=self._data["s_coarse"],
                                   plot_title="Sample Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"sample_coarse"+suffix)
        self._generate_single_plot(x=self._vin,
                                   data=self._data["s_fine"],
                                   plot_title="Sample Fine, "+pos,
                                   label="Fine",
                                   out_fname=out+"sample_fine"+suffix)
        self._generate_single_plot(x=self._vin,
                                   data=self._data["s_gain"],
                                   plot_title="Sample Gain, "+pos,
                                   label="Gain",
                                   out_fname=out+"sample_gain"+suffix)

    def plot_reset(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc_title, self._col_title)
        suffix = "_adc{}_col{}".format(self._adc_title, self._col_title)
        out = self._output_dir + "/"

        self._generate_single_plot(x=self._vin,
                                   data=self._data["r_coarse"],
                                   plot_title="Reset Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"reset_coarse"+suffix)
        self._generate_single_plot(x=self._vin,
                                   data=self._data["r_fine"],
                                   plot_title="Reset Fine, "+pos,
                                   label="Fine",
                                   out_fname=out+"reset_fine"+suffix)
        self._generate_single_plot(x=self._vin,
                                   data=self._data["r_gain"],
                                   plot_title="Reset Gain, "+pos,
                                   label="Gain",
                                   out_fname=out+"reset_gain"+suffix)

    def plot_combined(self):
        pass
