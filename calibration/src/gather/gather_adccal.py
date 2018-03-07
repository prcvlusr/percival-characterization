import h5py
import numpy as np
import os
import sys
import time
import glob

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from gather_base import GatherBase

class Gather(GatherBase):
    def __init__(self,
                 in_fname,
                 out_fname,
                 runs):
        super().__init__(in_fname, out_fname, runs)
