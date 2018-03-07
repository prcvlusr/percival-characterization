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

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
SRC_PATH = os.path.join(BASE_PATH, "src")
PROCESS_PATH = os.path.join(SRC_PATH, "process")

if PROCESS_PATH not in sys.path:
    sys.path.insert(0, PROCESS_PATH)

from process_base import ProcessBase


class ProcessAdccalBase(ProcessBase):
    def __init__(self, in_fname, out_fname, runs):
        super().__init__(in_fname, out_fname, runs)
