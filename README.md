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

TODO 

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

