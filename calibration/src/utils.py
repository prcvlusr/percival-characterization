from __future__ import print_function

import os
import sys
import numpy as np
import h5py
import collections

import logging
from logging.config import dictConfig


def create_dir(directory_name):
    """Creates a directory including supdirectories if it does not exist.

    Args:
        direcoty_name: The path of the direcory to be created.
    """
    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
            print("Dir '{0}' does not exist. Create it."
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
        excluded (optional): The data paths which should be excluded from loading.

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
