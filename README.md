# PERCIVAL characterization software framework

The PERCIVAL characterization software framework

This project allow users to calibrate and characterize the PERCIVAL detector.

## Dependencies

This package is developed with Python 3.6.

System dependencies:
  * Python (3.6)
  * pip - Python package manager
  * HDF5 libraries
  * Numpy - library for scientific computing with Python   
  * Matplotlib - 2D plotting library for Python
  * YAML -  human-readable data serialization language
  * Tkinter - standard Python interface to the Tk GUI toolkit 

To check if you have one of these packages:
```
% pip list | grep <package>
```

To install one of the packages:
```
% pip install h5py
% pip install numpy
% pip install matplotlib
% pip install pyyaml
```

N.B.: Testing procedures are underdevelopment.  

## Installation

Starting from scratch:
```
% git clone https://github.com/percival-desy/percival-characterization.git
``` 

To update the framework:
```
% cd /path/to/percival-characterisation
% git pull
```

## Execution

### Calibration

#### Config file

```
general:
    run_type: <runType>
    n_cols: <numberOfColumns>
 
    measurement: <measurementType>
 
    run: DLSraw
 
    n_processes: 1
 
all:
    input: &input /path/to/input/files
    output: &output /path/to/output/files
 
gather:
    method: null
 
    input: *input
    output: *output
 
process:
    method: <processMethod>
 
    input: *output
    output: *output
```

#### Run

```
% cd /path/to/percival-characterisation
% python3 calibration/src/analyse.py -- help
usage: run_characterization.py [-h] [-i INPUT]
                               [--metadata_fname METADATA_FNAME] [-o OUTPUT]
                               [--data_type {raw,gathered,processed}]
                               [--adc ADC] [--frame FRAME] [--col COL]
                               [--row ROW [ROW ...]] [-m METHOD [METHOD ...]]
                               [--plot_sample] [--plot_reset]
                               [--plot_combined] [--config_file CONFIG_FILE]

Characterization tools of P2M

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of input directory containing HDF5 files or in
                        the case of data_type raw to the input file to
                        characterize
  --metadata_fname METADATA_FNAME
                        File name containing the metadata information.
  -o OUTPUT, --output OUTPUT
                        Path of output directory to create plots in.
  --data_type {raw,gathered,processed}
                        The data type to analyse
  --adc ADC             The ADC to create plots for.
  --frame FRAME         The frame to create plots for.
  --col COL             The column of the data to create plots for.
  --row ROW [ROW ...]   The row(s) of the ADC group to create plots for.
                        Options: specify one value, e.g. --row 0 means take
                        only first row of ADC groupspecify start and stop
                        value, e.g. --row 0 5 means to take the first 5 rows
                        of the ADC groupdo not set this paramater: take
                        everything
  -m METHOD [METHOD ...], --method METHOD [METHOD ...]
                        The plot type to use
  --plot_sample         Plot only the sample data
  --plot_reset          Plot only the reset data
  --plot_combined       Plot the sample data combined with reset data
  --config_file CONFIG_FILE
                        The name of the config file to use
```

To run a analysis according to a configuration file:

```
 % python3 calibration/src/analyse.py --config_file my_config.yaml
```


### Characterization

#### Config file

```
general:
    data_type: <data type>
    run_id: <run Id>
 
    plot_sample: <plotting option - True or False>
    plot_reset: True
    plot_combined: True
 
 
raw:
    input: /path/to/rawHDF5/files
    metadata_file: /path/to/medataData.dat
 
    output: path/to/output/directory
     
    measurement: <measurement type>
 
    adc: null
    frame: 2
    col: 100
    row: 100
 
    method: [image, plot_coarse_vs_fine]
 
gathered:
    input: /path/to/input/gathered/data
    output: /path/to/output/gathered/data
 
    measurement: <measurement type>
 
    adc: 0
    frame: null
    col: 100
    row: null
 
    method: <method to use - plot, hist, hist_2d>
 
processed:
    input: /path/to/input/processed/data
    output: /path/to/output/processed/data
 
    measurement: <measurement type>
 
    adc: 0
    frame: null
    col: 100
    row: null
 
    method: <method to use - plot, hist, hist_2d>
```

#### Run

```
% cd /path/to/percival-characterisation
% python3 characterization/src/run_characerization.py --help
usage: run_characterization.py [-h] [-i INPUT]
                               [--metadata_fname METADATA_FNAME] [-o OUTPUT]
                               [--data_type {raw,gathered,processed}]
                               [--adc ADC] [--frame FRAME] [--col COL]
                               [--row ROW [ROW ...]] [-m METHOD [METHOD ...]]
                               [--plot_sample] [--plot_reset]
                               [--plot_combined] [--config_file CONFIG_FILE]

Characterization tools of P2M

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of input directory containing HDF5 files or in
                        the case of data_type raw to the input file to
                        characterize
  --metadata_fname METADATA_FNAME
                        File name containing the metadata information.
  -o OUTPUT, --output OUTPUT
                        Path of output directory to create plots in.
  --data_type {raw,gathered,processed}
                        The data type to analyse
  --adc ADC             The ADC to create plots for.
  --frame FRAME         The frame to create plots for.
  --col COL             The column of the data to create plots for.
  --row ROW [ROW ...]   The row(s) of the ADC group to create plots for.
                        Options: specify one value, e.g. --row 0 means take
                        only first row of ADC groupspecify start and stop
                        value, e.g. --row 0 5 means to take the first 5 rows
                        of the ADC groupdo not set this paramater: take
                        everything
  -m METHOD [METHOD ...], --method METHOD [METHOD ...]
                        The plot type to use
  --plot_sample         Plot only the sample data
  --plot_reset          Plot only the reset data
  --plot_combined       Plot the sample data combined with reset data
  --config_file CONFIG_FILE
                        The name of the config file to use.
```

To run the characterization with a configuration file different from the default configuration file: 

```
% python3 characterization/src/run_characterization.py --config_file my_config.yaml
```

