""" A template to be used as reference for method development.
"""
import __init__  # noqa F401

from descramble_base import DescrambleBase


class Descramble(DescrambleBase):
    """ A template to be used as reference for method development.


    Set in descramble_base:
    _data_to_write: -> to ensure data is written the same way as standard
                       gather script needs it to be

    Set in gather method:
    _input_fnames: list of input file names (absolute paths)
    _output_fname: output file name (absolute path)


    In addition to that all parameters set in the descrambling method section
    of the config file are added as class attributes.
    """

    def __init__(self, **kwargs):  # noqa F401
        super().__init__(**kwargs)

        # in the method and the method section of the config file the following
        # parameters have to be defined:
        #   n_adc
        #   n_grp
        #   n_pad
        #   n_col_in_blk
        #   input_fnames
        #   save_file
        #   output_fname
        #   clean_memory
        #   verbose

    def run(self):
        pass
