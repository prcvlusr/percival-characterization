import os

from plot_gathered import PlotGathered
from hist_gathered import HistGathered
from hist_2d_gathered import Hist2dGathered

if __name__ == "__main__":
    input_dir = "/gpfs/cfel/fsds/labs/agipd/calibration/scratch/user/kuhnm/percival_tests/DLSraw_gathered"
    output_dir = "/gpfs/cfel/fsds/labs/agipd/calibration/scratch/user/kuhnm/percival_tests/plots/DLSraw_plots/"

#    input_fname_templ = "/gpfs/cfel/fsds/labs/agipd/calibration/scratch/user/kuhnm/percival_tests/raw_uint16_gathered/col{col_start}-{col_stop}_gathered.h5"
#    output_dir = "/gpfs/cfel/fsds/labs/agipd/calibration/scratch/user/kuhnm/percival_tests/plots/raw_uint16_plots/"

    adc = 0
    col = 100

    # single row
    rows = 0

    # subset of rows
#    rows = slice(0, 2)

    # all rows
    rows = slice(None)

    plot_sample = True
    plot_reset = True

    input_fname_templ = os.path.join(input_dir, "col{col_start}-{col_stop}_gathered.h5")

    plotter = PlotGathered(input_fname_templ=input_fname_templ,
                           output_dir=output_dir+"/plots",
                           adc=adc,
                           col=col,
                           rows=rows)
    hist_creator = HistGathered(input_fname_templ=input_fname_templ,
                                output_dir=output_dir+"/hists",
                                adc=adc,
                                col=col,
                                rows=rows)
    hist_2d_creator = Hist2dGathered(input_fname_templ=input_fname_templ,
                                     output_dir=output_dir+"/hists_2d",
                                     adc=adc,
                                     col=col,
                                     rows=rows)

    if plot_sample:
        print("Plot sample")
        plotter.plot_sample()
        hist_creator.plot_sample(nbins=30)
        hist_2d_creator.plot_sample(nbins=100)

    if plot_reset:
        print("Plot reset")
        plotter.plot_reset()
        hist_creator.plot_reset(nbins=30)
        hist_2d_creator.plot_sample(nbins=100)
