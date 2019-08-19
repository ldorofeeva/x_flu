# `X_flu` 
X_flu is a GUI application for X-ray fluorescence map visualization.

Application supports visualization of files with extensions *.hdf5, .nxs, .nex*, 
with one or multiple entries.
                        
User can choose one of the two visualization methods:
* render data as a set of overlapping **patches** (very time consuming);
* **interpolate** data on a grid before visualization.
default is the **interpolate** method.

## Installation
Install the package (optional):

    $ python setup.py install

## Launch as script
    $ python x_flu.py

## Usage
1. Select an x-ray fluorescence map file;
2. Select entry;
2. Enter desired energy region;
3. Select preferred Colour map;
4. (optional) choose preferred visualization method;
5. Press "Render" button or simply press Enter to visualize the data.