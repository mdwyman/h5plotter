#!/APSshare/anaconda3/Bluesky/bin/python3 

'''

Filepath PV
9idDetectorSim:HDF1:FilePath_RBV

Generally trying to keep simDet files in:
/net/s8iddata/export/8-id-g/2023-1/bsTests/simdet/

Full file path PV
9idDetectorSim:HDF1:FullFileName_RBV


'''

import sys
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog, QAction, QTextEdit, QLabel, QTabWidget, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import numpy as np
import math
import h5py

import os
import re
import math
from pathlib import Path



#TODO -- can these be made into optional command-line arguments?  OR
#TODO -- maybe instead, make DEFAULT_H5_DIR the current directory?
H5_DATA_TREE = 'entry/data/data'
DEFAULT_H5_DIR = '/net/s8iddata/export/8-id-g/2023-1/bsTests/simdet/'

COLOR_MAPS = ['hot','cool','plasma','inferno','magma']
h5_cmap = COLOR_MAPS[0]

def getData(h5file, h5_data_tree):      

    f = h5py.File(h5file, 'r')
    try:
        data = f[h5_data_tree][:]  #Returns 3-d array of (ScanY, DataY, DataX)

    except:
        # Add error dialog about h5_data_tree
        data = None
        print("Didn't get data")
        
    return data

class h5PlotterWindow(QMainWindow):
    def __init__(self, uifilename, parent=None):
        super().__init__()
        uic.loadUi(uifilename, self)
        
        # a figure instance to plot on
        self.fig = plt.figure()

        self.x_lim = [-500,500]
        self.y_lim = [-500,500]
        self.t_lim = [0,1e4]
        
        self.index = 0

        self.canvas = FigureCanvas(self.fig)
        self.plotView.addWidget(self.canvas)
       
        self.frameNum.setInputMask('0000')
 
        self.plotColorMap.clear()
        self.plotColorMap.addItems(COLOR_MAPS)

    def clear_plot(self):
        self.fig.clear()
        self.canvas.draw()
        
    def plot(self, data, index, cMap = h5_cmap):
        self.fig.clear()

        gs = self.fig.add_gridspec(2, 2,  width_ratios=(1, 4), height_ratios=(1, 4),
                      left=0.1, right=0.9, bottom=0.1, top=0.9,
                      wspace=0.05, hspace=0.05)

        self.h5_axis = self.fig.add_subplot(gs[1,1])
        self.cX_axis = self.fig.add_subplot(gs[0,1], sharex=self.h5_axis)
        self.cY_axis = self.fig.add_subplot(gs[1,0], sharey=self.h5_axis)
        
        self.cX_axis.tick_params(axis='x', which='both', bottom=False, top=False,         
            labelbottom=False) 
        self.cX_axis.tick_params(axis='y', which='both', left=True, right=False,         
            labelright=False, labelleft=True) 
        self.cY_axis.tick_params(axis='x', which='both', bottom=True, top=False,         
            labelbottom=True) 
        self.cY_axis.tick_params(axis='y', which='both', left=False, right=False,         
            labelleft=False) 
        self.cY_axis.invert_xaxis()
       
        self.h5_axis.tick_params(axis='y', which='both', bottom=False, top=True,
            right=True, left=False, labelleft=False, labelright=True, 
            labelbottom=False, labeltop=False)           
        
        self.plot_h5(data, index, cMap)
       
        self.cX_axis.plot(np.sum(data[index,:,:], axis = 0))
        self.cY_axis.plot(np.sum(data[index,:,:], axis = 1), range(data.shape[1]))
        
        # refresh canvas
        self.canvas.draw()  
        self.canvas.update()

    def plot_h5(self, data, index=0, cMap = h5_cmap):
        if len(data.shape) == 3:
            h5image = data[index,:,:]
            im = self.h5_axis.imshow(h5image, cmap = cMap, aspect = 'auto')
        else:
            print('Data has unexpected shape: ',data.shape)
            
class h5plotter:

    def __init__(self, model, view):
        self.h5Filename = ''
        self.h5Dir = DEFAULT_H5_DIR
        self._getData = model
        self._view = view
        self._connectSignalsAndSlots()
        self.data = None
        self.index = 0
        self.maxIndex = 0
        self.cMap = COLOR_MAPS[0]
        self.h5_data_tree = H5_DATA_TREE
        
    def plot(self):
        self._view.plot(self.data, index = self.index, cMap = self.cMap)
        self._view.frameNum.setText(str(self.index))
        self.change_title()
        self.change_status()
        
    def file_open(self):
        fname = QFileDialog.getOpenFileName(self._view, 'Open File',self.h5Dir)
        if fname[0]:
            fname_array = fname[0].split('/')
            self.h5Filename = fname_array[-1]               
            self.data = self._getData(fname[0], h5_data_tree = self.h5_data_tree)
            
            if self.data is not None:
                self.index = 0
                self.plot()
                self.maxIndex = self.data.shape[0]-1
    
    def change_title(self):
        self._view.titleBar.setText(self.h5Filename+', Frame: '+str(self.index))
    
    def change_status(self):
        self._view.statusbar.showMessage('Filename: '+self.h5Filename+'  |  Data: ' + self.h5_data_tree + '  |  Frame: '+str(self.index))
                
    def change_color_map(self, i):
        self.cMap = COLOR_MAPS[i]
        self.plot()
         
    def change_index(self):
        s = self._view.frameNum.text()
        if self.h5Filename != '':
            self.index = max(min(int(s), self.maxIndex), 0)
            self.plot()
         
    def increment_index(self, direction):
        if direction in {'up','down'}:
            if direction == 'up':
                self.index = min(self.maxIndex, self.index+1)
            else:
                self.index = max(0, self.index-1)
            self.plot()
        else:
            pass
        

    def close_application(self):
        sys.exit()
        
    def _connectSignalsAndSlots(self):

        self._view.actionOpen.triggered.connect(self.file_open)
        self._view.actionExit.triggered.connect(self.close_application)
        self._view.frameIncDown.clicked.connect(lambda x : self.increment_index('down'))
        self._view.frameIncUp.clicked.connect(lambda x : self.increment_index('up'))
        self._view.frameNum.returnPressed.connect(self.change_index)
        self._view.plotColorMap.currentIndexChanged.connect(self.change_color_map)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    dirpath = Path(__file__).resolve().parent
    ui_filename = 'h5_plotter.ui' 
    ui_path = dirpath / ui_filename

    plotterWindow = h5PlotterWindow(ui_path)
    plotterWindow.show()
    
    ctrlr = h5plotter(model=getData, view=plotterWindow)

    sys.exit(app.exec_())
