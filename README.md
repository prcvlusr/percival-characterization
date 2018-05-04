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
    run_type: gather
    n_cols: 32
 
    measurement: adccal
 
    run: DLSraw
 
    n_processes: 1
 
all:
    input: &input /home/kuhnm/percival/raw/PSVoltFromVin
    output: &output /home/kuhnm/percival/processed
 
gather:
    method: null
 
    input: *input
    output: *output
 
process:
    method: process_adccal_default
 
    input: *output
    output: *output
```
