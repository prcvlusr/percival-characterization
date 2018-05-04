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

### Config file


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
