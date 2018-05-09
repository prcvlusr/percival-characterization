import h5py
import os

import utils


class LoadRaw():
    def __init__(self,
                 input_fname,
                 metadata_fname,
                 output_dir,
                 frame=None,
                 row=None,
                 col=None):

        self._input_fname = input_fname
        self._metadata_fname = metadata_fname
        self._output_dir = os.path.normpath(output_dir)

        # to enable value 0
        if frame is None:
            self._frame = slice(None)
        else:
            self._frame = frame

        if row is None:
            self._row = slice(None)
        else:
            self._row = row

        if col is None:
            self._col = slice(None)
        else:
            self._col = col

        self._data_type = "raw"

        self._paths = {
            "sample": "data",
            "reset": "reset",
        }

        self._n_frames_per_vin = None

        self._n_frames = None
        self._n_groups = None
        self._n_total_frames = None

    def load_data(self):
        """Loads the input data.

        Return:
            A dictionary containing the data. The entries are:
            s_coarse - The coarse data of the sample
            s_fine - The fine data of the sample
            s_gain - The gain data of the sample
            r_coarse - The coarse data of the reset
            r_fine - The fine data of the reset
            r_gain - The gain data of the reset
        """

        idx = (self._frame, self._row, self._col)

        data = {}
        with h5py.File(self._input_fname, "r") as f:
            # sample
            path = self._paths["sample"]
            coarse, fine, gain = utils.split(f[path][idx])
            data["s_coarse"] = coarse
            data["s_fine"] = fine
            data["s_gain"] = gain

            # reset
            path = self._paths["reset"]
            coarse, fine, gain = utils.split(f[path][idx])
            data["r_coarse"] = coarse
            data["r_fine"] = fine
            data["r_gain"] = gain

        return data

    def get_vin(self):
        """Get the Voltage corresponding to the data.

        Return:
            The voltage as float.
        """
        if self._metadata_fname is None:
            return None
        else:
            print("Opening metadata file {}".format(self._metadata_fname))
            with open(self._metadata_fname, "r") as f:
                file_content = f.read().splitlines()

            # data looks like this: <V_in>  <file_prefix>
            file_content = [s.split("\t") for s in file_content]
            for i, s in enumerate(file_content):
                try:
                    s[0] = float(s[0])
                except:
                    if s == ['']:
                        # remove empty lines
                        del file_content[i]
                    else:
                        raise
    #                print("file_content", file_content)

            filename = os.path.split(self._input_fname)[-1]
            vin = [content for content in file_content
                   if filename.startswith(content[1])]

            if len(vin) != 1:
                print("vin", vin)
                msg = "More than one possible Vin found in metadata file."
                raise Exception(msg)

            return float(vin[0][0])
