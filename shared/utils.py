import h5py
import numpy as np
import os
import sys

from reading_config import *


def create_dir(directory_name):
    """Creates a directory including supdirectories if it does not exist.

    Args:
        direcoty_name: The path of the direcory to be created.
    """
    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
            print("Dir '{}' does not exist. Create it."
                  .format(directory_name))
        except IOError:
            if os.path.isdir(directory_name):
                pass


def check_file_exists(file_name, quit=True):
    """Checks if a file already exists.

    Args:
        file_name: The file to check for existence
        quit (optional): Quit the program if the file exists or not.
    """

    print("file_name = {}".format(file_name))
    if os.path.exists(file_name):
        print("File already exists")
        if quit:
            sys.exit(1)
    else:
        print("File: ok")


def load_file_content(fname, excluded=[]):
    """Load the HDF5 file into a dictionary.

    Args:
        fname: The name of the HDF5 file to be loaded.
        excluded (optional): The data paths which should be excluded from
        loading.

    Return:
        A dictionary containing the content of the content of the file where
        the keys are the paths in the original file.

        HDF5 file:
            my_group
                my_dataset: numpy array

        dictionary:
            "mygroup/mydataset": numpy array
    """

    file_content = {}

    def get_file_content(name, obj):
        if isinstance(obj, h5py.Dataset) and name not in excluded:
            file_content[name] = obj[()]
            # if object types are not converted writing gives the error
            # TypeError: Object dtype dtype('O') has no native HDF5 equivalent
            if (isinstance(file_content[name], np.ndarray) and
                    file_content[name].dtype == object):
                file_content[name] = file_content[name].astype('S')

    with h5py.File(fname, "r") as f:
        f.visititems(get_file_content)

    return file_content


def decode_dataset_8bit(arr_in, bit_mask, bit_shift):
    """Masks out bits and shifts.

    For every entry in the input array is the undelying binary representation
    of the integegers the bit-wise AND is computed with the bit mask.
    Bit wise AND means:
    e.g. number 13 in binary representation: 00001101
         number 17 in binary representation: 00010001
         The bit-wise AND of these two is:   00000001, or 1
    Then the result if shifted and converted to uint8.

    Args:
        arr_in: Array to decode.
        bit_mask: Bit mask to apply on the arra.
        bit_shift: How much the bits should be shifted.

    Return:
        Array where for each entry in the input array the bit mask is applied,
        the result is shifted and converted to uint8.

    """

    arr_out = np.bitwise_and(arr_in, bit_mask)
    arr_out = np.right_shift(arr_out, bit_shift)
    arr_out = arr_out.astype(np.uint8)

    return arr_out


def split_Alessandro(raw_dset):
    """Extracts the coarse, fine and gain bits.

    Readout bit number
    15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
    C0  C1  C2  C3  C4  F0  F1  F2  F3  F4  F5  F6  F7  B0  B1  -
    ADC bit numbers

    C: ADC coarse
    F: ADC fine
    B: Gain bit

    Args:
        raw_dset: Array containing 16 bit entries.

    Return:
        Each a coarse, fine and gain bit array.

    """

    # 0xF800 -> 1111100000000000
    coarse_adc = decode_dataset_8bit(arr_in=raw_dset,
                                     bit_mask=0xF800,
                                     bit_shift=1+2+8)

    # 0x07F8 -> 0000011111111000
    fine_adc = decode_dataset_8bit(arr_in=raw_dset,
                                   bit_mask=0x07F8,
                                   bit_shift=1+2)

    # 0x0006 -> 0000000000000110
    gain_bits = decode_dataset_8bit(arr_in=raw_dset,
                                    bit_mask=0x0006,
                                    bit_shift=1)

    return coarse_adc, fine_adc, gain_bits


def split_Ulrik(raw_dset):
    """Extracts the coarse, fine and gain bits.

    Readout bit number
    15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
    -   C0  C1  C2  C3  C4  F0  F1  F2  F3  F4  F5  F6  F7  B0  B1
    ADC bit numbers

    C: ADC coarse
    F: ADC fine
    B: Gain bit

    Args:
        raw_dset: Array containing 16 bit entries.

    Return:
        Each a coarse, fine and gain bit array.

    """

    # 0x7C00 -> 0111110000000000
    coarse_adc = decode_dataset_8bit(arr_in=raw_dset,
                                     bit_mask=0x7C00,
                                     bit_shift=2+8)

    # 0x03FC -> 0000001111111100
    fine_adc = decode_dataset_8bit(arr_in=raw_dset,
                                   bit_mask=0x03FC,
                                   bit_shift=2)

    # 0x0003 -> 0000000000000011
    gain_bits = decode_dataset_8bit(arr_in=raw_dset,
                                    bit_mask=0x0003,
                                    bit_shift=0)

    return coarse_adc, fine_adc, gain_bits


def split(raw_dset):
    """Extracts the coarse, fine and gain bits.

    Readout bit number
    0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
    -   B0  B1  F0  F1  F2  F3  F4  F5  F6  F7  C0  C1  C2  C3  C4
    ADC bit numbers

    C: ADC coarse (5 bit)
    F: ADC fine (8 bit)
    B: Gain bit (2 bit)

    Args:
        raw_dset: Array containing 16 bit entries.

    Return:
        Each a coarse, fine and gain bit array.

    """

    # 0x1F   -> 0000000000011111
    coarse_adc = decode_dataset_8bit(arr_in=raw_dset,
                                     bit_mask=0x1F,
                                     bit_shift=0)

    # 0x1FE0 -> 0001111111100000
    fine_adc = decode_dataset_8bit(arr_in=raw_dset,
                                   bit_mask=0x1FE0,
                                   bit_shift=5)

    # 0x6000 -> 0110000000000000
    gain_bits = decode_dataset_8bit(arr_in=raw_dset,
                                    bit_mask=0x6000,
                                    bit_shift=5+8)

    return coarse_adc, fine_adc, gain_bits


class IndexTracker(object):
    def __init__(self, data, method_properties):

        self._data = data
        self._method_properties = method_properties
        self._slice = None
        self._window_title = None
        self._fig = None

        self.initiate()

        self.set_data()

        self._update()

    def initiate(self):
        """Initiate the canvas and all needed plot attributes.
        """

        msg = "initiate is not implementated. Abort."
        raise Exception(msg)

    def set_data(self):
        """Creates the plot and assign the data to it.
        """

        msg = "set_data is not implementated. Abort."
        raise Exception(msg)

    def update_plots(self):
        """What plots should be updated on the events and how.
        """
        msg = "update_plots is not implemented. Abort."
        raise Exception(msg)

    def get_fig(self):
        """Returns the self._fig figure on which the canvas was created.

        Returns:
            The matplotlib.figure.Figure object initiated in the initiate
            method.
        """

        return self._fig

    def onscroll(self, event):
        """How to react if the mouse wheel is scrolled.

        Args:
            event: Event that you can connect to.
        """

#        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self._frame = (self._frame + 1) % self._slices
        else:
            self._frame = (self._frame - 1) % self._slices

        self._update()

    def on_key_press(self, event):
        """How to react if a key is pressed.

        Args:
            event: Event that you can connect to.
        """

        if event.key in ["right", "up"]:
            self._frame = (self._frame + 1) % self._slices
        elif event.key in ["left", "down"]:
            self._frame = (self._frame - 1) % self._slices

        self._update()

    def _update(self):
        """Updates the plots.
        """

        self.update_plots()

        self._fig.suptitle(self._window_title)

        self._fig.canvas.draw()
