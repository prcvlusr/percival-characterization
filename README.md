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

N.B.: Testing procedures are underdevelopment.  

## Installation

Starting from scratch:
```
% git clone https://github.com/percival-desy/percival-characterization.git
``` 

To update the framework:
```
% cd <percial characterization directory>
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
usage: analyse.py [-h] -i IN_BASE_DIR -o OUT_BASE_DIR -r RUN_ID -m METHOD -t
                  RUN_TYPE
 
Calibration tools for P2M
 
optional arguments:
  -h, --help            show this help message and exit
  -i IN_BASE_DIR, --input IN_BASE_DIR
                        Path of input directory containing HDF5 files to
                        analyse
  -o OUT_BASE_DIR, --output OUT_BASE_DIR
                        Path of output directory for storing files
  -r RUN_ID, --run RUN_ID
                        Non-changing part of file name
  -m METHOD, --method METHOD
                        Method to use during the analysis:
                        process_adccal_default, None
  -t RUN_TYPE, --type RUN_TYPE
                        Run type: gather, process

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
% cd <percial characterization directory>
% python3 characterization/src/run_characerization.py --help
usage: run_characterization.py [-h] -i INPUT_DIR -o OUTPUT_DIR [--adc ADC]
                          [--col COL] [--row ROWS [ROWS ...]] [--plot_sample]
                          [--plot_reset]
 
Characterization tools of P2M
 
optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input INPUT_DIR
                        Path of input directory containing HDF5 files to
                        characterize. These have to be the ouput of 'gather'.
  -o OUTPUT_DIR, --output OUTPUT_DIR
                        Path of output directory to create plots in.
  --adc ADC             The ADC to create plots for. (default: 0)
  --col COL             The column of the data to create plots for. (default:
                        100)
  --row ROWS [ROWS ...]
                        The row(s) of the ADC group to create plots for.
                        Options: specify one value, e.g. --rows 0 means take
                        only first row of ADC groupspecify start and stop
                        value, e.g. --rows 0 5 means to take the first 5 rows
                        of the ADC groupdo not set this paramater: meaning
                        take everything
  --plot_sample         Plot only the sample data
  --plot_reset          Plot only the reset data
```

To run the characterization: 

```
% python3 characterization/src/run_characterization.py --config_file my_config.yaml
```

