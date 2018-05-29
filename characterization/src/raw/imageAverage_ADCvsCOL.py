## coded by Trixi with help from Manuela & Alessandro
## average data from a given ADC (over many rows, and also over many frames), show image of this for all ADCs
## uses ALL row groups even if there is a restriction in the yaml or command line on rows.


### triple comment lines were inserted to attempt to get interactive response, need Manuela
### to figure out how to get this to work ... .


import copy
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
import numpy 
###import utils # added in hopes of getting interactive functionality

from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["col"] = None    
        new_kwargs["row"] = None    # note if you remove this fix how ADCs are identified!
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def _check_dimension(self, data):
        if data.shape[0] != 1:
            raise("Plot method one image can only show one image at the time.")

    def _generate_single_plot(x, data, plot_title, label, out_fname):

        fig = plt.figure(figsize=None)
        # print(type(data))
        # print(data.shape)
	
        Prep_dataPerADCs = data.reshape((212,7,1440))
        # note cols change the most often, then ADCs, then row groups (thus they stand 1st)
       
        # now average over the 212 row groups for a given ADC:
        averageDataPerADCs = numpy.average(Prep_dataPerADCs, axis=0)
    
        plt.imshow(averageDataPerADCs, aspect='auto', interpolation='none')
        plt.colorbar()
        plt.xlabel("columns")
        plt.ylabel("ADCs")

        fig.suptitle(plot_title)
        fig.savefig(out_fname)

        ### # copied the following 3 lines from raw/viewer.py in hopes of getting interactive
        ###fig, ax = plt.subplots(2, 3, sharex=True, sharey=True)
        ###tracker = utils.IndexTracker(fig, ax, x)
        ###plt.show()

        # commented out the following 2 lines in hopes of getting interactive behaviour
        fig.clf()
        plt.close(fig)
