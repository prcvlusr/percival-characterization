import h5py
import numpy as np
import os
import sys
import yaml


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


def load_config(config_file, config={}):
    """ Loads the config from a ini_file and overwrites already exsiting config.

    Overwriting an existing configuration dictionary enables multi-layered
    configs.

    Args:
        config_file (str): Name of the ini file from which the config should be
                        loaded.
        config (optional, dict): Dictionary with already existing config to be
                                 overwritten.

    Return:
        Configuration dictionary. Values in the config file onverwrite the ones
        in the passed config dictionary.
    """

    with open(config_file) as f:
        new_config = yaml.load(f)

    config.update(new_config)

    return config


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
    def __init__(self, fig, ax, data):
        self.fig = fig

        if len(ax) != 2 or len(ax[0]) != 3:
            raise Exception("Figure has wrong layout. Need subplots(2,3)")
        self.ax = ax

        self.data = data

        self.slices, rows, cols = data["s_coarse"].shape
        self.frame = 0

        self.im_s_coarse = ax[0][0].imshow(self.data["s_coarse"][self.frame])
        self.im_s_fine = ax[0][1].imshow(self.data["s_fine"][self.frame])
        self.im_s_gain = ax[0][2].imshow(self.data["s_gain"][self.frame])

        self.im_r_coarse = ax[1][0].imshow(self.data["r_coarse"][self.frame])
        self.im_r_fine = ax[1][1].imshow(self.data["r_fine"][self.frame])
        self.im_r_gain = ax[1][2].imshow(self.data["r_gain"][self.frame])

        self.ax[0][0].set_title("sample coarse")
        self.ax[0][1].set_title("sample fine")
        self.ax[0][2].set_title("sample gain")
        self.ax[1][0].set_title("reset coarse")
        self.ax[1][1].set_title("reset fine")
        self.ax[1][2].set_title("reset gain")

        self.update()

    def onscroll(self, event):
        """How to react if the mouse wheel is scrolled.
        """

#        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.frame = (self.frame + 1) % self.slices
        else:
            self.frame = (self.frame - 1) % self.slices
        self.update()

    def on_key_press(self, event):
        """How to react if a key is pressed.
        """

        if event.key in ["right", "up"]:
            self.frame = (self.frame + 1) % self.slices
        elif event.key in ["left", "down"]:
            self.frame = (self.frame - 1) % self.slices
        self.update()

    def update(self):
        """Updates the plots.
        """

        self.im_s_coarse.set_data(self.data["s_coarse"][self.frame])
        self.im_s_fine.set_data(self.data["s_fine"][self.frame])
        self.im_s_gain.set_data(self.data["s_gain"][self.frame])
        self.im_r_coarse.set_data(self.data["s_coarse"][self.frame])
        self.im_r_fine.set_data(self.data["r_fine"][self.frame])
        self.im_r_gain.set_data(self.data["r_gain"][self.frame])

        self.fig.suptitle("Frame {}".format(self.frame))

        self.fig.canvas.draw()
