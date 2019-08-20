# `X_flu` 
X_flu is a python GUI application for X-ray fluorescence map visualization.

Application supports visualization of files with extensions *.hdf5, .nxs, .nex*, 
with one or multiple entries.
                        
User can choose one of the two visualization methods:

* render data as a set of overlapping **patches** (very time consuming);
* **interpolate** data on a grid before visualization.

default is the **interpolate** method.

## Requirements
    python>=3.7
    
    tk
    numpy>=1.16
	scipy>=1.3
    h5py>=2.9
    matplotlib>=3

## Installation
In your python 3.7 environment:

    $ python setup.py install

## Launch
In your python 3.7 environment:

**On Windows**

    $ python -m x_flu
    
**On Linux**

    $ x_flu

## Usage
1. Select an x-ray fluorescence map file;
2. Select entry;
2. Enter desired energy region;
3. Select preferred Colour map;
4. (optional) choose preferred visualization method;
5. Press "Render" button or simply press Enter to visualize the data.