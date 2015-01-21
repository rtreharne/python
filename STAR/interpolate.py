""" -------------------------------------------------------------------------
script name: interpolate.py
version: 1.0
author: Robert Treharne
e-mail: R.Treharne@liverpool.ac.uk
date: 17/03/14


description: This script is for use with optical data files which have a column format - wavelength, n, k. The script allows the user to re-interpolate data with respect to a map file which has already been formatted accordingly.

user_guide:

1) run script - e.g. python interpolate.py
3) select "map" file which has already been formatted with the required wavelength values
3) select file that needs to be interpolated
4) enter filename of new interpolated file - WARNING: SCRIPT WILL NOT PREVENT OVERWRITE IF ORIGINAL FILENAME SELECTED
----------------------------------------------------------------------------"""



import sys
import numpy as np
from pylab import *
import pygtk
import gtk
from scipy.interpolate import interp1d

def get_filename(text):
     dialog = gtk.FileChooserDialog(text,
                                    None,  
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
     
     dialog.set_default_response(gtk.RESPONSE_OK)
     filter = gtk.FileFilter()
     filter.set_name("text files")
     filter.add_mime_type(".txt")
     filter.add_pattern("*.txt")
     dialog.add_filter(filter)
     response = dialog.run()
     
     if response == gtk.RESPONSE_OK:
         root = dialog.get_filename()
         return root
     elif response == gtk.RESPONSE_CANCEL:
         print "no file selected"
         
     dialog.destroy()
     
def save_file():
    dialog = gtk.FileChooserDialog("Save interpolated file as",
                                   None,
                                   gtk.FILE_CHOOSER_ACTION_SAVE,
                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_SAVE, gtk.RESPONSE_OK))
                                    
    dialog.set_default_response(gtk.RESPONSE_OK)
    response = dialog.run()
  
    if response == gtk.RESPONSE_OK:
        save_filename = dialog.get_filename()
        return save_filename
  
    dialog.destroy()
    
def interpolate(map, open, save):

    xinterp = np.loadtxt(map, unpack = True, usecols=[0])
    x = np.loadtxt(open, unpack = True, usecols=[0])
    n = np.loadtxt(open, unpack = True, usecols=[1])
    k = np.loadtxt(open, unpack = True, usecols=[2])
    
    ninterp = interp(xinterp, x, n)
    kinterp = interp(xinterp, x, k)
    
    savetxt(save, transpose([xinterp, ninterp, kinterp]))
    

if __name__ == "__main__":
    map_file = get_filename('Open template file')
    open_file = get_filename('Open file to be interpolated')
    save_filename = save_file()
    interpolate(map_file, open_file, save_filename)
    
    
