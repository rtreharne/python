#!/usr/bin/env python

""" -------------------------------------------------------------------------
Multi-layer-model GUI version 2.0
This script allows the user to build a multi-layer structure by importing material n and k data. The transfer matrix is then used to calculate T and R. A slider permits the user to change the thickness of each layer within the structure.
----------------------------------------------------------------------------"""

import pygtk
import gtk
from numpy import *
from pylab import *
from math import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
import re
import cmath as c

class Window():
    def destroy(self, widget, data=None):
        gtk.main_quit()

    def open_file(self, widget):
        # open file dialog
        dialog = gtk.FileChooserDialog("Choose a substrate", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        dialog.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("text files")
        filter.add_mime_type(".txt")
        filter.add_pattern("*.txt")
        dialog.add_filter(filter)
        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            #format filename for appending to combobox            
            self.folder = dialog.get_current_folder()
            self.root = dialog.get_filename()
            folder = '%s.' %self.folder
            root = '%s.' %self.root
            self.filename = re.sub(folder, '', root) 
            filename = '%s.' %self.filename
            self.filename = re.sub('.txt..', '', filename)                        
        elif response == gtk.RESPONSE_CANCEL:
            print "no file selected"           
            
        dialog.destroy()

        #load data from file
        self.lam = loadtxt(self.root, unpack = True, usecols=[0])
        self.n = loadtxt(self.root, unpack = True, usecols=[1])
        self.k = loadtxt(self.root, unpack = True, usecols=[2])
        #consolidate n and k into single complex list
        self.nk.append(self.n-1j*self.k)
        
        #following first load (substrate) activate plot, add, delete buttons and slider
        self.subs_but.set_sensitive(False)
        self.plot_TR.set_sensitive(True)
        self.plot_nk_but.set_sensitive(True)
        self.add_but.set_sensitive(True)
        self.delete_but.set_sensitive(True)
        self.add_combo(widget)

        #add default d value to d list
        self.combo.set_active(len(self.nk)-1)
        self.index = self.combo.get_active()
        self.d.append(self.hscale.get_value())
        #convert list nk to units of admittance
        self.Y.append(self.nk[self.combo.get_active()]*2.6544e-3)
        #prepare M list for calcs
        self.M.append([])
        self.T = [0]*len(self.lam)
        for i in range(0,len(self.lam)):
            self.M[self.index].append([0])
            
        self.subs = []
        self.subs = array([self.Y[0]/self.Y[0],self.Y[0]])
        self.matrix(widget)
        #self.check1(widget)

        

    def add_combo(self, widget):
        #include new filename in combobox
        self.combo.append_text(self.filename)
        self.hscale.set_sensitive(True)

    def plot_nk(self,widget):
        #plot n and k of film selected in combobox
        
        self.fig1.clf()
        self.ax1 = self.fig1.add_subplot(111)
        self.ln = self.ax1.plot(self.lam, real(self.nk[self.index]), '-', color = 'orange')
        self.ax1.set_xlabel('$\lambda$ (nm)', fontsize = 16)
        self.ax1.set_ylabel('n', fontsize = 16)

        self.ax2 = self.ax1.twinx()
        self.lk = self.ax2.plot(self.lam, -imag(self.nk[self.index]), '-', color = 'green')
        self.ax2.set_ylabel('k', fontsize = 16)
        self.canvas.draw()

    def delete(self, widget):
        #delete film
        self.index = self.combo.get_active()
        #remove associated n and k from complex list
        del self.nk[self.index]
        #remove associated d from d list
        del self.d[self.index]
        # remove associated M from M list       
        del self.M[self.index]
        #remove entry from combobox and reset
        self.combo.remove_text(self.index)
        self.combo.set_active(self.index-1)
        #if deleted film is substrate then re-initialize buttons
        if self.index == 0:
            self.plot_nk_but.set_sensitive(False)                      
            self.add_but.set_sensitive(False)
            self.delete_but.set_sensitive(False)
            self.subs_but.set_sensitive(True)
            self.plot_TR.set_sensitive(False)
            self.fig1.clf()
            self.canvas.draw()
            self.combo.set_active(-1)
        self.matrix(widget)

    #def check1(self, widget):
        #this method remembers the last thickness set for each selected film
        #also, if substrate selected then slider is de-activated       
        
            
        #if self.index == 0:
           # self.hscale.set_sensitive(False)
        #elif self.index >= 0:
            #self.hscale.set_sensitive(True)

    def matrix(self, widget):
        #get active thickness value
        self.index = self.combo.get_active()
        self.d[self.index]=self.adj1.get_value()
        T2=[0]*len(self.lam)
        
             
        
        
        #calculate delta
        
        
        for i in range(0, len(self.lam)):
            delta = 2*math.pi*self.nk[self.index][i]*self.d[self.index]/self.lam[i]
            self.M[self.index][i] =array([[c.cos(delta), (1j*c.sin(delta)/self.Y[self.index][i])], [1j*self.Y[self.index][i]*c.sin(delta), c.cos(delta)]])
            MP = []
            MP = array([[1,0],[0,1]]) 
            for j in range (1,len(self.nk)):
                MP = dot(MP,self.M[j][i])
            B1 = self.subs[0][i]*MP[0][0]
            B2 = self.subs[1][i]*MP[0][1]
            C1 = self.subs[0][i]*MP[1][0]
            C2 = self.subs[1][i]*MP[1][1]
            B = B1+B2
            C = C1+C2
            X = (2.6544e-3*B+C)
            Y = (2.6544e-3*B+C).conjugate()
            Ta = (4*2.6544e-3*real(self.Y[0][i])/(X*Y))
            Tb = ((1/2.6544e-3)*(4*real(self.Y[0][i]))/((1/2.6544e-3*real(self.Y[0][i]))+1)**2)
            self.T[i] = Ta*Tb
            T2[i] = Ta

        self.fig1.clf()
        self.fig1.patch.set_alpha(1)
        self.ax1 = self.fig1.add_subplot(111)
        self.ln = self.ax1.plot(self.lam, real(self.T), '-', color = 'purple', linewidth = 2)
        self.ln2 = self.ax1.plot(self.lam, real(T2), '--', color = 'purple', linewidth = 1)
        self.ax1.set_xlabel('$\lambda$ (nm)', fontsize = 16)
        self.ax1.set_ylabel('T', fontsize = 16)
        self.ax1.set_ylim(0,1)
        self.ax1.set_xlim(min(self.lam),max(self.lam))
        self.ax1.patch.set_alpha(0.75)
        self.canvas.draw()
 
            
        
  

        
        
        

        
          

    def __init__(self):
        #instantiation
        #configures all plots, buttons sliders and lists

        #initialize global lists
        self.nk = []
        self.Y = []
        self.subs_Y = []
        self.d = []
        self.T = []
        self.R = []
        self.M = []
        self.delta = []

        self.win = gtk.Window()
        self.win.set_size_request(980,600)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_title('MLM 2.0')         

        self.subs_but = gtk.Button("Load Substrate")
        self.subs_but.connect("clicked", self.open_file)
        
        self.plot_nk_but = gtk.Button('Plot n & k')
        self.plot_nk_but.set_sensitive(False)
        self.plot_nk_but.connect("clicked", self.plot_nk)

        self.add_but = gtk.Button("Add film")
        self.add_but.set_sensitive(False)
        self.add_but.connect("clicked", self.open_file)

        self.delete_but = gtk.Button("Delete film")
        self.delete_but.set_sensitive(False)
        self.delete_but.connect("clicked", self.delete)

        self.plot_TR = gtk.Button('Plot T and R')
        #self.plot_TR.connect("clicked", self.matrix)
        self.plot_TR.set_sensitive(False)
       
        self.fig1 = Figure()
        self.canvas = FigureCanvas(self.fig1)

        self.combo = gtk.combo_box_entry_new_text()
        #self.combo.connect("changed", self.check1)

        self.adj1 = gtk.Adjustment(500.0, 0.0, 1001.0, 1.0, 1.0, 1.0)
        self.adj1.connect("value_changed", self.matrix)
        self.hscale = gtk.HScale(self.adj1)
        self.hscale.set_sensitive(False)      
        
                
        self.box1 = gtk.HBox()
        self.box1.set_size_request(980,500)
        self.box1.pack_start(self.canvas)

        self.box2 = gtk.HBox()
        self.box2.pack_start(self.subs_but)
        self.box2.pack_start(self.plot_TR)
        self.box2.pack_start(self.plot_nk_but)
        self.box2.pack_start(self.add_but)
        self.box2.pack_start(self.delete_but)
        self.box2.pack_start(self.combo)
        
        self.box3 = gtk.VBox()
        self.box3.set_size_request(980, 50)
        self.box3.pack_start(self.hscale)      

        self.box4 = gtk.VBox()
        self.box4.pack_start(self.box1)
        self.box4.pack_start(self.box2)
        self.box4.pack_start(self.box3)
                       
        self.win.add(self.box4)        
                
        self.win.show_all()
        self.win.connect("destroy", self.destroy)        

    def main(self):
        gtk.main()

if __name__ == "__main__":
    window = Window()
    window.main()
        

