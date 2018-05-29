"""Load the environment.
"""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

CALIBRATION_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(CURRENT_DIR)
        )
    )
)
BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")
GATHER_DIR = os.path.join(CALIBRATION_DIR, "src", "gather")
ADCCAL_DIR = os.path.join(GATHER_DIR, "adccal")

DESCRAMBLE_BASE_DIR = os.path.join(GATHER_DIR, "descramble")
DESCRAMBLE_DIR = os.path.join(DESCRAMBLE_BASE_DIR, "methods")

if ADCCAL_DIR not in sys.path:
    sys.path.insert(0, ADCCAL_DIR)

if DESCRAMBLE_BASE_DIR not in sys.path:
    sys.path.insert(0, DESCRAMBLE_BASE_DIR)

if DESCRAMBLE_DIR not in sys.path:
    sys.path.insert(0, DESCRAMBLE_DIR)

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)
