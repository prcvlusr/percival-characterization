from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    """A template class to be used as reference for method development.

    Available variables:
    Defined in the configuration:
        _run: the run ID
        _input: input file name (absolute path as template)
        _output: output base directory
        _metadata_fname: metadata file name (absolute path)

        _adc: ...
        _col: ...
        _frame: ...
        _row: ...

        _method_properties: -> all method properties defined in the method section

    Set in run_characterization:
        _input_fname: input file name (absolute path as template)
        _output_dir: <output>/<data_type>/<method_name>

    Set in plot_base:
        # to ease naming plots (converts slices)
        _adc_title: ...
        _col_title: ...
        _frame_title: ...
        _row_title: ...

        _dims_overwritten: ...

        # loaded load_raw
        _data:
            r_coarse: ...
            r_fine: ...
            r_gain: ...
            s_coarse: ...
            s_fine: ...
            s_gain: ...
        _vin: ...
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

     # The PlotBase class calls the class method _generate_single_plot for
     # each data set (coarse, fine and gain). If this is not what you want,
     # overwrite plot_sample and/or plot_reset.
     # plot_sample is ment to contain plots only concerning sample whereas
     # plot_reset is only ment for reset data.
#    def plot_sample(self):
#        pass

#    def plot_reset(self):
#        pass

    # If the plot_sample and/or plot_reset methods from the PlotBase is used
    # the _generate_single_plot class method has to be implemented.
    # If they are both overwritten, the _generate_single_plot class method is
    # not needed.
    def _generate_single_plot(self, data, plot_title, label, out_fname):
        pass

    # If sample and reset data should be combined or connected the
    # plot_combined class method can be implemented.
#    def plot_combined(self):
#        pass
