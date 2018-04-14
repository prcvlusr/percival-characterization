import argparse
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CHARACTERIZATION_DIR = os.path.dirname(CURRENT_DIR)
BASE_DIR = os.path.dirname(CHARACTERIZATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

CONFIG_DIR = os.path.join(CHARACTERIZATION_DIR, "conf")
METHOD_DIR = os.path.join(CHARACTERIZATION_DIR, "src", "methods")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils  # noqa E402

if METHOD_DIR not in sys.path:
    sys.path.insert(0, METHOD_DIR)


def get_arguments():
    parser = argparse.ArgumentParser(description="Characterization tools of "
                                                 "gathered results for P2M")
    parser.add_argument("-i", "--input",
                        dest="input",
                        type=str,
                        help="Path of input directory containing HDF5 files "
                             "to characterize. These have to be the ouput of "
                             "'gather'.")
    parser.add_argument("-o", "--output",
                        dest="output",
                        type=str,
                        help="Path of output directory to create plots in.")
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
                        help="The name of the config file to use.")

    args = parser.parse_args()

    required_arguments_set = (
        args.input
        and args.output
        and args.col
        and args.adc
        and args.method
    )

    if args.config_file is not None:
        args.config_file = os.path.join(CONFIG_DIR, args.config_file)
        if not os.path.exists(args.config_file):
            msg = ("Configuration file {} does not exist."
                   .format(args.config_file))
            parser.error(msg)
    elif not required_arguments_set:
        msg = ("Either specify a config_file or the command line parameters:"
               "-i/--input, -o/--output, --col, --adc, --rows, -m/--method")
        parser.error(msg)

    return args


def insert_args_into_config(args, config):

    # general
    c_general = config["general"]

    try:
        c_general["input"] = args.input or c_general["input"]
    except:
        raise Exception("No input specified. Abort.")
        sys.exit(1)

    try:
        c_general["output"] = args.output or c_general["output"]
    except:
        raise Exception("No output specified. Abort.")
        sys.exit(1)

    # for adc equals 0 ".. or .." does not work
    if args.adc is not None:
        c_general["adc"] = args.adc
    elif "adc" not in c_general:
        raise Exception("No ADC specified. Abort.")
        sys.exit(1)

    # for col equals 0 ".. or .." does not work
    if args.col is not None:
        c_general["col"] = args.col
    elif "col" not in c_general:
        raise Exception("No column specified. Abort.")
        sys.exit(1)

    # for row equals 0 ".. or .." does not work
    if args.rows is not None:
        c_general["rows"] = args.rows
    elif "rows" not in c_general:
        raise Exception("No rows specified. Abort.")
        sys.exit(1)

    try:
        c_general["method"] = args.method or c_general["method"]
    except:
        raise Exception("No method specified. Abort.")
        sys.exit(1)


if __name__ == "__main__":
    args = get_arguments()

    if args.config_file is None:
        config = {"general": {}}
    else:
        config = utils.load_config(args.config_file)

    insert_args_into_config(args, config)

#    input_dir = args.input_dir
#    output_dir = args.output_dir
#    adc = args.adc
#    col = args.col
#    rows = args.rows
#    method_list = args.method

    input_dir = config["general"]["input"]
    output_dir = config["general"]["output"]
    adc = config["general"]["adc"]
    col = config["general"]["col"]
    rows = config["general"]["rows"]
    method_list = config["general"]["method"]

    if rows is None:
        rows = slice(rows)
    elif len(rows) == 1:
        row = rows[0]
    else:
        rows = slice(*rows)

    plot_sample = args.plot_sample
    plot_reset = args.plot_reset

    # if both options where not set plot sample and reset
    if not plot_sample and not plot_reset:
        plot_sample = True
        plot_reset = True

    input_fname_templ = os.path.join(input_dir,
                                     "col{col_start}-{col_stop}_gathered.h5")

    kwargs = dict(
        input_fname_templ=input_fname_templ,
        output_dir=None,
        adc=adc,
        col=col,
        rows=rows
    )

    for method in method_list:
        print("loading method: {}".format(method))
        method_m = __import__(method).Plot

        kwargs["output_dir"] = os.path.join(output_dir, method)
        plotter = method_m(**kwargs)

        if plot_sample:
            print("Plot sample")
            plotter.plot_sample()

        if plot_reset:
            print("Plot reset")
            plotter.plot_reset()
