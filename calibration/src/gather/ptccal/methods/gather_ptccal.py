import os

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

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

if GATHER_DIR not in sys.path:
    sys.path.insert(0, GATHER_DIR)

from gather_base import GatherBase  # noqa E402


class Gather(GatherPtcBase):
    pass
