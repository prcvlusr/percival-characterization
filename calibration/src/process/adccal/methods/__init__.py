import os
import sys

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

BASE_DIR = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(CURRENT_DIR)
                    )
                )
           )
SRC_DIR = os.path.join(BASE_DIR, "src")
PROCESS_DIR = os.path.join(SRC_DIR, "process")
ADCCAL_DIR = os.path.join(PROCESS_DIR, "adccal")

if ADCCAL_DIR not in sys.path:
    sys.path.insert(0, ADCCAL_DIR)
