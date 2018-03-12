#!/usr/bin/python3

import os
import sys
import datetime
import time
import glob

import utils

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SRC_PATH = os.path.join(BASE_PATH, "src")

PROCESS_PATH = os.path.join(SRC_PATH, "process")
ADCCAL_METHOD_PATH = os.path.join(PROCESS_PATH, "adccal", "methods")
PTCCAL_METHOD_PATH = os.path.join(PROCESS_PATH, "ptccal", "methods")

if ADCCAL_METHOD_PATH not in sys.path:
    sys.path.insert(0, ADCCAL_METHOD_PATH)


class Analyse(object):
    def __init__(self, in_base_dir, out_base_dir, run_type, meas_type, method):
        self.in_base_dir = in_base_dir
        self.out_base_dir = out_base_dir

        self.runs = "0"
        self.run_type = run_type

        self.meas_type = meas_type
        self.method = method

    def run(self):
        print("\nStarted at", str(datetime.datetime.now()))
        t = time.time()

        if self.run_type == "gather":
            self.run_gather()
        elif self.run_type == "process":
            self.run_process()
        else:
            print("Unsupported argument: run_type {}".format(self.run_type))

        print("\nFinished at", str(datetime.datetime.now()))
        print("took time: ", time.time() - t)

    def generate_raw_path(self, base_dir):
        return base_dir, "{run}_raw_uint16.h5"

    def generate_metadata_path(self, base_dir):
        return base_dir, "file.dat"

    def generate_gather_path(self, base_dir):
        return base_dir, "gathered.h5"

    def generate_process_path(self, base_dir):
        return base_dir, "processed.h5"

    def run_gather(self):
        if self.meas_type == "adccal":
            from gather.gather_adccal import Gather
            #from gather.gather_base import GatherBase as Gather
        elif self.meas_type == "ptccal":
            #from gather.gather_ptccal import Gather
            from gather.gather_base import GatherBase as Gather
        else:
            print("Unsupported type.")

        # define input files
        in_dir, in_file_name = self.generate_raw_path(self.in_base_dir)
        in_fname = os.path.join(in_dir, in_file_name)

        # define metadata file
        meta_dir, meta_file_name = self.generate_metadata_path(self.in_base_dir)
        meta_fname = os.path.join(meta_dir, meta_file_name)

        # define output files
        out_dir, out_file_name = self.generate_gather_path(self.out_base_dir)
        out_fname = os.path.join(out_dir, out_file_name)


#        if os.path.exists(out_fname):
#            print("output filename = {}".format(out_fname))
#            print("WARNING: output file already exist. Skipping gather.")
#        else:
#            utils.create_dir(out_dir)

        if True:
            obj = Gather(in_fname=in_fname,
                         out_fname=out_fname,
                         meta_fname=meta_fname,
                         runs=self.runs)
            obj.run()

    def run_process(self):
        self.process_m = __import__(self.method).ProcessAdccalMethod

        # define input files
        # the input files for process is the output from gather
        in_dir, in_file_name = self.generate_gather_path(self.in_base_dir)
        in_fname = os.path.join(in_dir, in_file_name)

        # define output files
        out_dir, out_file_name = self.generate_process_path(self.out_base_dir)
        out_fname = os.path.join(out_dir, out_file_name)

#        if os.path.exists(out_fname):
#            print("output filename = {}".format(out_fname))
#            print("WARNING: output file already exist. Skipping process.")
#        else:
#            utils.create_dir(out_dir)

        if True:
            # generate out_put
            self.process_m(in_fname=in_fname,
                           out_fname=out_fname,
                           runs=self.runs)

    def cleanup(self):
        # remove gather dir
        pass


if __name__ == "__main__":
    in_base_dir = "/nfs/fs/fsds/percival/P2MemulatedData/ADCcorrection/58_W08_01_TS1.2PIX_PB5V2_-40_N02_25MHz_1ofmany_all_coldFingerT-40/P2Mdata_coldFingerT-40"
    #in_base_dir = BASE_PATH
    out_base_dir = BASE_PATH

    run_type = "gather"
    meas_type = "adccal"
    method = None

    g_obj = Analyse(in_base_dir, out_base_dir, run_type, meas_type, method)
    g_obj.run()

#    del g_obj

#    run_type = "process"
#    meas_type = "adccal"
#    method = "process_adccal_default"

#    p_obj = Analyse(in_base_dir, out_base_dir, run_type, meas_type, method)
#    p_obj.run()
