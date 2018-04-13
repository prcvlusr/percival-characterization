import argparse
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
print(BASE_DIR)

METHOD_DIR = os.path.join(BASE_DIR, "src", "methods")

if METHOD_DIR not in sys.path:
    sys.path.insert(0, METHOD_DIR)

def get_arguments():
    parser = argparse.ArgumentParser(description="Characterization tools of "
                                                 "gathered results for P2M")
    parser.add_argument("-i", "--input",
                        dest="input_dir",
                        required=True,
                        type=str,
                        help="Path of input directory containing HDF5 files to "
                             "characterize. These have to be the ouput of 'gather'.")
    parser.add_argument("-o", "--output",
                        dest="output_dir",
                        required=True,
                        type=str,
                        help="Path of output directory to create plots in.")
    parser.add_argument("--adc",
                        type=int,
                        default=0,
                        help="The ADC to create plots for. (default: 0)")
    parser.add_argument("--col",
                        type=int,
                        default=100,
                        help=("The column of the data to create plots for. "
                              "(default: 100)"))
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
                             "do not set this paramater: meaning take everything")

    parser.add_argument("--method",
                        type=str,
                        nargs="+",
                        required=True,
                        help="The plot type to use")

    parser.add_argument("--plot_sample",
                        action="store_true",
                        default=False,
                        help="Plot only the sample data")
    parser.add_argument("--plot_reset",
                        action="store_true",
                        default=False,
                        help="Plot only the reset data")

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = get_arguments()

    input_dir = args.input_dir
    output_dir = args.output_dir
    adc = args.adc
    col = args.col
    rows = args.rows
    method_list = args.method

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

    input_fname_templ = os.path.join(input_dir, "col{col_start}-{col_stop}_gathered.h5")

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
