# `X_flu` 
X_flu is a python GUI application for X-ray fluorescence map visualization.

Application supports visualization of files with extensions 
*.hdf5*, *.nxs*, *.nex*, with one or multiple entries.
                        
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

**Patch visualization parameters:**

* **patch_size** - equal to the actual size of the beam in millimeters.

**Interpolate visualization parameters:**

* **grid_step** - size of the interpolation grid cell in millimiters;
* **method** - interpolation method (either nearest neighbour or linear).

*Additional feature*:
On energy region selection, the application searches for 
X-ray K + L Emission Lines in the region and prints out 
corresponding periodic table elements if less than 4 lines are found.
Periodic Table and X-ray energies data are taken from BRUKER.