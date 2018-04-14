import argparse
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CHARACTERIZATION_DIR = os.path.dirname(CURRENT_DIR)
BASE_DIR = os.path.dirname(CHARACTERIZATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

CONFIG_DIR = os.path.join(CHARACTERIZATION_DIR, "conf")
SRC_DIR = os.path.join(CHARACTERIZATION_DIR, "src")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils  # noqa E402


def get_arguments():
    desciption = "Characterization tools of P2M"
    parser = argparse.ArgumentParser(description=desciption)

    parser.add_argument("-i", "--input",
                        dest="input",
                        type=str,
                        help="Path of input directory containing HDF5 files "
                             "to characterize.")
    parser.add_argument("-o", "--output",
                        dest="output",
                        type=str,
                        help="Path of output directory to create plots in.")

    parser.add_argument("--data_type",
                        type=str,
                        choices=["gathered"],
                        help="The data type to analyse")

    parser.add_argument("--adc",
                        type=int,
                        help="The ADC to create plots for.")
    parser.add_argument("--col",
                        type=int,
                        help="The column of the data to create plots for.")
    parser.add_argument("--rows",
                        type=int,
                        nargs="+",
                        default=None,
                        help="The rows of the ADC group to create plots for.\n"
                             "Options:\n"
                             "specify one value, e.g. --rows 0 means take "
                             "only first row of ADC group"
                             "specify start and stop value, e.g. --rows 0 5 "
                             "means to take the first 5 rows of the ADC group"
                             "do not set this paramater: take everything")

    parser.add_argument("-m", "--method",
                        dest="method",
                        type=str,
                        nargs="+",
                        help="The plot type to use")

    parser.add_argument("--plot_sample",
                        action="store_true",
                        default=False,
                        help="Plot only the sample data")
    parser.add_argument("--plot_reset",
                        action="store_true",
                        default=False,
                        help="Plot only the reset data")

    parser.add_argument("--config_file",
                        type=str,
                        default="default.yaml",
                        help="The name of the config file to use.")

    args = parser.parse_args()

    args.config_file = os.path.join(CONFIG_DIR, args.config_file)
    if not os.path.exists(args.config_file):
        msg = ("Configuration file {} does not exist."
               .format(args.config_file))
        parser.error(msg)

    return args


def insert_args_into_config(args, config):

    # general
    c_general = config["general"]

    data_type = c_general["data_type"]

    # data type specific

    c_data_type = config[data_type]

    try:
        c_data_type["input"] = args.input or c_data_type["input"]
    except:
        raise Exception("No input specified. Abort.")
        sys.exit(1)

    try:
        c_data_type["output"] = args.output or c_data_type["output"]
    except:
        raise Exception("No output specified. Abort.")
        sys.exit(1)

    try:
        c_data_type["method"] = args.method or c_data_type["method"]
    except:
        raise Exception("No method specified. Abort.")
        sys.exit(1)

    if data_type != "raw":
        # for adc equals 0 ".. or .." does not work
        if args.adc is not None:
            c_data_type["adc"] = args.adc
        elif "adc" not in c_data_type:
            raise Exception("No ADC specified. Abort.")
            sys.exit(1)

        # for col equals 0 ".. or .." does not work
        if args.col is not None:
            c_data_type["col"] = args.col
        elif "col" not in c_data_type:
            raise Exception("No column specified. Abort.")
            sys.exit(1)

        # for row equals 0 ".. or .." does not work
        if args.rows is not None:
            c_data_type["rows"] = args.rows
        elif "rows" not in c_data_type:
            raise Exception("No rows specified. Abort.")
            sys.exit(1)


class Analyse(object):
    def __init__(self):
        args = get_arguments()

        config = utils.load_config(args.config_file)
        insert_args_into_config(args, config)

        self.data_type = config["general"]["data_type"]
        self.input_dir = config[self.data_type]["input"]
        self.output_dir = config[self.data_type]["output"]
        self.adc = config[self.data_type]["adc"]
        self.col = config[self.data_type]["col"]
        self.rows = config[self.data_type]["rows"]
        self.method_list = config[self.data_type]["method"]

        if self.rows is None:
            self.rows = slice(self.rows)
        elif len(self.rows) == 1:
            self.row = self.rows[0]
        else:
            self.rows = slice(*self.rows)

        self.plot_sample = args.plot_sample
        self.plot_reset = args.plot_reset

        # if both options where not set plot sample and reset
        if not self.plot_sample and not self.plot_reset:
            self.plot_sample = True
            self.plot_reset = True

        self.load_methods()

    def load_methods(self):
        """Load data type specific methods.
        """

        DATA_TYPE_DIR = os.path.join(SRC_DIR, self.data_type)

        if DATA_TYPE_DIR not in sys.path:
            sys.path.insert(0, DATA_TYPE_DIR)

    def run(self):

        file_name = "col{col_start}-{col_stop}_gathered.h5"
        input_fname_templ = os.path.join(self.input_dir, file_name)

        kwargs = dict(
            input_fname_templ=input_fname_templ,
            output_dir=None,
            adc=self.adc,
            col=self.col,
            rows=self.rows
        )

        loaded_data = None
        for method in self.method_list:
            print("loading method: {}".format(method))
            method_m = __import__(method).Plot

            kwargs["output_dir"] = os.path.join(self.output_dir, method)
            plotter = method_m(**kwargs, loaded_data=loaded_data)

            if self.plot_sample:
                print("Plot sample")
                plotter.plot_sample()

            if self.plot_reset:
                print("Plot reset")
                plotter.plot_reset()

            loaded_data = plotter.get_data()


if __name__ == "__main__":
    obj = Analyse()
    obj.run()
