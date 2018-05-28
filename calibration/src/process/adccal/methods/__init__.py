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
SRC_DIR = os.path.join(CALIBRATION_DIR, "src")
PROCESS_DIR = os.path.join(SRC_DIR, "process")
ADCCAL_DIR = os.path.join(PROCESS_DIR, "adccal")

if PROCESS_DIR not in sys.path:
    sys.path.insert(0, PROCESS_DIR)

if ADCCAL_DIR not in sys.path:
    sys.path.insert(0, ADCCAL_DIR)
