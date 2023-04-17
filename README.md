#### h5plotter
Qt tool for view HDF5 files

### Files

## h5_plot.py
Python code to support parsing HDF5 files, extracting data and plotting image data along with x-,y-profiles

## h5_plotter.ui
XML file from Qt designer

### Use
Meant to run on APS file system (access to APSshare required).  If not run from APS or an alternate python environment is desired, the 1st line of h5_plot.py will need to be updated.

To run:
> ./h5_plot.py

In File menu, choose 'Open HDF5 File' and select file.

Plotter displays the first frame from the stack.  To navigate to other frames, use the <, > buttons or enter the frame number directly.
