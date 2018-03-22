#!/usr/bin/python3

import os
import sys
import datetime
import time
import glob

import utils
import argparse

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SRC_PATH = os.path.join(BASE_PATH, "src")

PROCESS_PATH = os.path.join(SRC_PATH, "process")
ADCCAL_METHOD_PATH = os.path.join(PROCESS_PATH, "adccal", "methods")
PTCCAL_METHOD_PATH = os.path.join(PROCESS_PATH, "ptccal", "methods")

if ADCCAL_METHOD_PATH not in sys.path:
    sys.path.insert(0, ADCCAL_METHOD_PATH)


class Analyse(object):
    def __init__(self,
                 in_base_dir,
                 out_base_dir,
                 run_id,
                 run_type,
                 meas_type,
                 n_cols,
                 method):

        self.in_base_dir = in_base_dir
        self.out_base_dir = out_base_dir

        self._n_rows_total = 1484
        self._n_cols_total = 1440

        self._n_rows = self._n_rows_total
        if n_cols is None:
            self._n_cols = self._n_cols_total
        else:
            self._n_cols = n_cols

        self._n_parts = self._n_cols_total // self._n_cols

        self._run_id = run_id
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
        return base_dir, "{run}_" + "{}.h5".format(self._run_id)
        #return base_dir, "{run}_raw_uint16.h5"
        #return base_dir, "{run}_DLSraw.h5"

    def generate_metadata_path(self, base_dir):
        return base_dir, "file.dat"

    def generate_gather_path(self, base_dir):
        return base_dir, "col{col_start}-{col_stop}_gathered.h5"

    def generate_process_path(self, base_dir):
        return base_dir, "col{col_start}-{col_stop}_processed.h5"

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

        #for p in range(1):
        for p in range(self._n_parts):
            col_start = p * self._n_cols
            col_stop = (p+1) * self._n_cols

            out_f = out_fname.format(col_start=col_start, col_stop=col_stop)

#            if os.path.exists(out_f):
#                print("output filename = {}".format(out_f))
#                print("WARNING: output file already exist. Skipping gather.")
#            else:
#                utils.create_dir(out_dir)

            obj = Gather(in_fname=in_fname,
                         out_fname=out_f,
                         meta_fname=meta_fname,
                         n_rows=self._n_rows,
                         n_cols=self._n_cols,
                         part=p)
            obj.run()

    def run_process(self):
        self.process_m = __import__(self.method).Process

        # define input files
        # the input files for process is the output from gather
        in_dir, in_file_name = self.generate_gather_path(self.in_base_dir)
        in_fname = os.path.join(in_dir, in_file_name)

        # define output files
        out_dir, out_file_name = self.generate_process_path(self.out_base_dir)
        out_fname = os.path.join(out_dir, out_file_name)

        for p in range(1):
            col_start = p * self._n_cols
            col_stop = (p+1) * self._n_cols

            in_f = in_fname.format(col_start=col_start,
                                   col_stop=col_stop)
            out_f = out_fname.format(col_start=col_start,
                                     col_stop=col_stop)

#            if os.path.exists(out_f):
#                print("output filename = {}".format(out_f))
#                print("WARNING: output file already exist. Skipping process.")
#            else:
#                utils.create_dir(out_dir)

            # generate out_put
            obj = self.process_m(in_fname=in_f,
                                 out_fname=out_f)

            obj.run()

    def cleanup(self):
        # remove gather dir
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Calibration tools for P2M")
    parser.add_argument("-i", "--input", dest = "in_base_dir", type = str,
                        help = "Path of input directory containing HDF5 files to analyse")
    parser.add_argument("-o", "--output", dest = "out_base_dir", type = str,
                        help = "Path of output directory for storing files")
    parser.add_argument("-r", "--run", dest = "run_id", type = str,
                        help = "Run id")
    parser.add_argument("-m", "--method", dest = "method", type = str,
                        help = "Method to use during the analysis: "  
                               "process_adccal_default, "
                               "None")
    parser.add_argument("-t", "--type", dest = "run_type", type = str,
                        help = "Run type: "
                               "gather, " 
                               "process")
    args = parser.parse_args()

    run_id = args.run_id
    run_type = args.run_type
    method = args.method
    n_cols = None
    meas_type = "adccal"
    if run_type == "gather":
        in_base_dir = args.in_base_dir
        out_base_dir = args.out_base_dir + "{}_gathered".format(run_id)
    else:
        in_base_dir = args.in_base_dir + "{}_gathered".format(run_id)
        out_base_dir = args.out_base_dir + "{}_processed".format(run_id)
    
    obj = Analyse(in_base_dir,
                  out_base_dir,
                  run_id,
                  run_type,
                  meas_type,
                  n_cols,
                  method)
    obj.run()
     
    #in_base_dir = args.in_base_dir + "{}_gathered".format(run_id)
    #out_base_dir = args.out_base_dir +"{}_processed".format(run_id)
    #method = args.method

   # run_id = "DLSraw"
   #in_base_dir = "/gpfs/cfel/fsds/labs/agipd/calibration/scratch/user/kuhnm/percival_tests/P2M_ADCcor_crs_reduced"
    #n_cols = None

#    in_base_dir = "/nfs/fs/fsds/percival/P2MemulatedData/ADCcorrection/58_W08_01_TS1.2PIX_PB5V2_-40_N02_25MHz_1ofmany_all_coldFingerT-40/P2Mdata_coldFingerT-40"
#    run_id = "raw_uint16"
#    n_cols = 64

    #g_out_base_dir = "/gpfs/cfel/fsds/labs/agipd/calibration/scratch/user/kuhnm/percival_tests/{}_gathered".format(run_id)
    #p_out_base_dir = "/gpfs/cfel/fsds/labs/agipd/calibration/scratch/user/kuhnm/percival_tests/{}_processed".format(run_id)

   # run_type = "gather"
   # meas_type = "adccal"
   # method = None

    # run gather
#    g_obj = Analyse(in_base_dir,
#                    g_out_base_dir,
#                    run_id,
#                    run_type,
#                    meas_type,
#                    n_cols,
#                    method)
#    g_obj.run()

#    del g_obj

 #   run_type = "process"
 #   meas_type = "adccal"
    #method = "process_adccal_default"

    # run process
#    p_obj = Analyse(in_base_dir,
#                    out_base_dir,
#                    run_id,
#                    run_type,
#                    meas_type,
#                    n_cols,
#                    method)
#    p_obj.run()

