from collections import namedtuple
import h5py
#import matplotlib.pyplot as plt
import matplotlib.pyplot
#matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import numpy as np
import os

from load_raw import LoadRaw
import utils


class Plot():
    LoadedData = namedtuple("loaded_data", ["data"])

    def __init__(self,
             input_fname_templ,
             metadata_fname,
             output_dir,
             adc,
             frame,
             col,
             row,
             loaded_data=None,
             dims_overwritten=False):

        self._input_fname = input_fname_templ
        self._metadata_fname = metadata_fname
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._frame = frame
        self._col = col
        self._row = row
        self._dims_overwritten = dims_overwritten
        
        #if self._frame is not None:
        #    self._frame = None
        #    self._dims_overwritten = True

        loader = LoadRaw(input_fname=self._input_fname,
                         metadata_fname=self._metadata_fname,
                         output_dir=self._output_dir,
                         frame=self._frame)

        if loaded_data is None or self._dims_overwritten:
            self._data = loader.load_data()
        else:
            self._data = loaded_data.data

    def get_dims_overwritten(self):
        """If the dimension originally configures overwritten.

        Return:
            A boolean if the config war overwritten or not.
        """
        return self._dims_overwritten

    def get_data(self):
        """Exposes data outside the class.

        Return:
            A named tuble with the loaded data. Entries
                x: filled up Vin read (to match the dimension of data)
                data: sample and reset data
        """

        return Plot.LoadedData(data=self._data)

    def plot_sample(self):
        pass

    def plot_reset(self):
        pass
    
    def plot_combined(self):
        """ 2D scatter plot of Smpl/Rst, Gn/Crs/Fn, give mark as error (white) the values << ErrBelow """      
        cmap = matplotlib.pyplot.cm.jet
        cmap.set_under(color='white') 
        ErrBelow=-0.1
        fig = matplotlib.pyplot.figure()
        label_title= "Img "+ str(self._frame)
        fig.canvas.set_window_title(label_title) 
        label_x="col"; label_y="row"

        #
        GnSmpl= self._data["s_gain"]
        CrsSmpl= self._data["s_coarse"]
        FnSmpl= self._data["s_fine"]
        GnRst= self._data["r_gain"]
        CrsRst= self._data["r_coarse"]
        FnRst= self._data["r_fine"]
        #
        matplotlib.pyplot.subplot(2,3,1)
        matplotlib.pyplot.imshow(GnSmpl, interpolation='none', cmap=cmap, vmin=ErrBelow)
        matplotlib.pyplot.xlabel(label_x)
        matplotlib.pyplot.ylabel(label_y)
        matplotlib.pyplot.title('Sample Gain')
        matplotlib.pyplot.clim(0,3)
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.gca().invert_xaxis();
        #
        matplotlib.pyplot.subplot(2,3,2)
        matplotlib.pyplot.imshow(CrsSmpl, interpolation='none', cmap=cmap, vmin=ErrBelow)
        matplotlib.pyplot.xlabel(label_x)
        matplotlib.pyplot.ylabel(label_y)
        matplotlib.pyplot.title('Sample Coarse')
        matplotlib.pyplot.clim(0,31)
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.gca().invert_xaxis();
        #
        matplotlib.pyplot.subplot(2,3,3)
        matplotlib.pyplot.imshow(FnSmpl, interpolation='none', cmap=cmap, vmin=ErrBelow)
        matplotlib.pyplot.xlabel(label_x)
        matplotlib.pyplot.ylabel(label_y)
        matplotlib.pyplot.title('Sample Fine')
        matplotlib.pyplot.clim(0,255)
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.gca().invert_xaxis();
        #
        matplotlib.pyplot.subplot(2,3,4)
        matplotlib.pyplot.imshow(GnRst, interpolation='none', cmap=cmap, vmin=ErrBelow)
        matplotlib.pyplot.xlabel(label_x)
        matplotlib.pyplot.ylabel(label_y)
        matplotlib.pyplot.title('Reset Gain (not relevant)')
        matplotlib.pyplot.clim(0,3)
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.gca().invert_xaxis();
        #
        matplotlib.pyplot.subplot(2,3,5)
        matplotlib.pyplot.imshow(CrsRst, interpolation='none', cmap=cmap, vmin=ErrBelow)
        matplotlib.pyplot.xlabel(label_x)
        matplotlib.pyplot.ylabel(label_y)
        matplotlib.pyplot.title('Reset Coarse')
        matplotlib.pyplot.clim(0,31)
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.gca().invert_xaxis();
        #
        matplotlib.pyplot.subplot(2,3,6)
        matplotlib.pyplot.imshow(FnRst, interpolation='none', cmap=cmap, vmin=ErrBelow)
        matplotlib.pyplot.xlabel(label_x)
        matplotlib.pyplot.ylabel(label_y)
        matplotlib.pyplot.title('Reset Fine')
        matplotlib.pyplot.clim(0,255)
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.gca().invert_xaxis();
        #
        matplotlib.pyplot.show(block=True)

        

    '''
    def plot_combined(self):
        fig, ax = plt.subplots(2, 3, sharex=True, sharey=True)
        tracker = utils.IndexTracker(fig, ax, self._data)
        # connect to mouse wheel
        fig.canvas.mpl_connect("scroll_event", tracker.onscroll)
        # connect to arrow keys
        fig.canvas.mpl_connect("key_press_event", tracker.on_key_press)
        plt.show()
    '''



