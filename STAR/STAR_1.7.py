#!/usr/bin/env python

""" -------------------------------------------------------------------------
STAR_1.6
This script allows the user to build a multi-layer structure by importing material n and k data. The transfer matrix is then used to calculate T and R. A slider permits the user to change the thickness of each layer within the structure.
----------------------------------------------------------------------------"""

import pygtk
import gtk
from numpy import *
from pylab import *
from math import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.widgets import SpanSelector
import re
import cmath as c
import sys
sys.path.append(r"/home/team_treharne/Documents/python_projects/STAR")
import nelmin

class Window():
    def destroy(self, widget, data=None):
        gtk.main_quit()

    def open_file(self, widget):
        # open file dialog
        dialog = gtk.FileChooserDialog("Choose a substrate", None, 
                                       gtk.FILE_CHOOSER_ACTION_OPEN, 
                                      (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                       gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        # look for .txt files only
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

        # declare list "unit" - three rows: lambda, eV and cm**-1
        self.unit = ([0]*len(self.lam), [0]*len(self.lam), [0]*len(self.lam)) 
        
        # calculate units
        for i in range (0, len(self.lam)):
            self.unit[0][i] = self.lam[i]
            self.unit[1][i] = (6.63e-34*3e8)/(self.lam[i]*1e-9*1.602e-19)
            self.unit[2][i] = 1/(self.lam[i]*1e-7)
        
        # set initial plot range of x-axis
        self.xmin = min(self.unit[self.unit_index])
        self.xmax = max(self.unit[self.unit_index])
        # find index of min and max values
        self.indmin, self.indmax = np.searchsorted(self.unit[self.unit_index],
                                                  (self.xmin,self.xmax))        
        
        #following first load (substrate) activate plot, add, delete buttons 
        #and slider
        self.subs_but.set_sensitive(False)
        self.subs_but.hide()
        self.plot_TR_but.set_sensitive(True)
        self.plot_nk_but.set_sensitive(True)
        self.add_but.set_sensitive(True)
        self.add_but.show()
        self.delete_but.set_sensitive(True)
        self.fit_win_but.set_sensitive(True)
        self.model_win_but.set_sensitive(True)

        # run function "add_combo"
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
        self.R = [0]*len(self.lam)

        for i in range(0,len(self.lam)):
            self.M[self.index].append([0])
        
        # declare substrate identity    
        self.subs = []
        self.subs = array([self.Y[0]/self.Y[0],self.Y[0]])

        # run function "matrix"
        self.matrix(widget)

    def add_combo(self, widget):
        #include new filename in combobox
        self.combo.append_text(self.filename)
        self.hscale.set_sensitive(True)  

    def plot_nk(self,widget):
        # This function plots the n and k values of the film
        # that is currently selected by the combo box
        
        self.press = 1
        self.plot_nk_but.hide()
        self.plot_e_but.show()
        
        # Get active layer
        self.index = self.combo.get_active()

        # prepare plot        
        self.fig1.clf()
        self.ax1 = self.fig1.add_subplot(111)
        self.ln = self.ax1.plot(self.unit[self.unit_index], 
                  real(self.nk[self.index]), '-', color = 'red', linewidth = 2)
        self.ax1.set_xlabel(self.unit_label[self.unit_index], fontsize = 16, )
        self.ax1.set_ylabel('n', fontsize = 16, color = 'red')
        self.ax1.set_xlim(min(self.unit[self.unit_index]),
                          max(self.unit[self.unit_index]))
        if self.unit_index >=1:
            self.ax1.invert_xaxis()
        self.ax2 = self.ax1.twinx()
        self.lk = self.ax2.plot(self.unit[self.unit_index],
                                -imag(self.nk[self.index]), '-', 
                                 color = 'green', linewidth = 2)
        self.ax2.set_ylabel('k', fontsize = 16, color = 'green')        
        self.ax2.set_xlim(min(self.unit[self.unit_index]),
                          max(self.unit[self.unit_index]))
        self.canvas.draw()

    def plot_e(self, widget):
        # this function plots e1 and e2 of the selected layer

        self.press = 2
        self.plot_e_but.hide()
        self.plot_nk_but.show()

        # get active layer
        self.index = self.combo.get_active()

        # calculate e1 and e2 from n and k values
        e1 = real(self.nk[self.index])**2-imag(self.nk[self.index])**2
        e2 = -2*real(self.nk[self.index])*imag(self.nk[self.index])
        
        # prepare plot
        self.fig1.clf()
        self.ax1 = self.fig1.add_subplot(111)
        self.ln = self.ax1.plot(self.unit[self.unit_index], e1, '-', 
                                color = 'red', linewidth = 2)
        self.ax1.set_xlabel(self.unit_label[self.unit_index], fontsize = 16)
        self.ax1.set_ylabel('e1', fontsize = 16, color = 'red')
        self.ax1.set_xlim(min(self.unit[self.unit_index]),
                          max(self.unit[self.unit_index]))
        if self.unit_index >=1:
            self.ax1.invert_xaxis()
        self.ax2 = self.ax1.twinx()
        self.lk = self.ax2.plot(self.unit[self.unit_index], e2, '-', 
                                color = 'green', linewidth = 2)
        self.ax2.set_ylabel('e2', fontsize = 16, color = 'green')
        self.ax2.set_xlim(min(self.unit[self.unit_index]),
                              max(self.unit[self.unit_index]))
        self.canvas.draw()        

    def delete(self, widget):
        # this function deletes the selected film
        self.index = self.combo.get_active()
        #remove associated values from lists
        del self.nk[self.index]
        del self.d[self.index]
        del self.M[self.index]
        del self.Y[self.index]

        #remove entry from combobox and reset
        self.combo.remove_text(self.index)
        self.combo.set_active(self.index-1)

        #if deleted film is substrate then re-initialize buttons
        if self.index == 0:
            self.plot_nk_but.set_sensitive(False)
            self.add_but.hide()                      
            self.add_but.set_sensitive(False)
            self.delete_but.set_sensitive(False)
            self.subs_but.show()
            self.subs_but.set_sensitive(True)
            self.plot_TR_but.set_sensitive(False)
            self.fig1.clf()
            self.canvas.draw()
            self.combo.set_active(-1)

        # run function "matrix" to update plot
        self.matrix(widget)

    def matrix(self, widget):
        # This function calculates all the components of the transfer matrix.
        # It then calculates T and R

        #get active thickness value
        self.index = self.combo.get_active()
        self.d[self.index]=self.adj1.get_value()
        self.T2=[0]*len(self.lam)
        self.R2 = [0]*len(self.lam)

        for i in range(0, len(self.lam)):
            delta = 2*math.pi*self.nk[self.index][i]*self.d[self.index]/self.lam[i]
            self.M[self.index][i] =array([[c.cos(delta),   
                                       (1j*c.sin(delta)/self.Y[self.index][i])], 
                                       [1j*self.Y[self.index][i]*c.sin(delta), 
                                        c.cos(delta)]])
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
            Z = (2.6544e-3*B-C)

            """TRANSMISSION-----------------------------------------------"""
            # Calculate transmission through single air/substrate interface
            Ta = ((1/2.6544e-3)*(4*real(self.Y[0][i]))/
                                ((1/2.6544e-3*real(self.Y[0][i]))+1)**2)
            # Calculate transmission through stack
            Tb = (4*2.6544e-3*real(self.Y[0][i])/(X*Y))
            
            # Calculate transmission through finite substrate + stack
            self.T[i] = Ta*Tb
            # Transmission through infinite substrate + stack
            self.T2[i] = Tb

            """REFLECTANCE------------------------------------------------"""
            ZX = Z/X
            ZXconj = ZX.conjugate()

            # Calculate reflectance from single air/substrate interface
            Ra1 = (1-self.nk[0][i])/(1+self.nk[0][i])
            Ra2 = Ra1.conjugate()
            Ra = Ra1*Ra2
            
            # Calculate reflectance from stack
            Rb = ZX*ZX.conjugate()

            # Calculate reflectance from finite substrate + stack
            self.R[i] = (Ra+Rb-(2*Ra*Rb))/(1-(Ra*Rb))

            # Calculate reflectance from infinite substrate + stack
            self.R2[i] = Rb         
            

        self.plot_TR(widget)
        print self.d

    def plot_TR(self, widget):
        self.press = 0

        self.fig1.clf()
        self.fig1.patch.set_alpha(1)
        self.ax1 = self.fig1.add_subplot(111)
        if self.showTcheck.get_active() == True:
            self.ln = self.ax1.plot(self.unit[self.unit_index], real(self.T), '-', color = 'purple', linewidth = 2)
            if self.showinfcheck.get_active() == True:
                self.ln2 = self.ax1.plot(self.unit[self.unit_index], real(self.T2), '--', color = 'purple', linewidth = 1)
        
        self.ax1.set_xlabel(self.unit_label[self.unit_index], fontsize = 16)
        self.ax1.set_ylabel('T', fontsize = 16, color = 'purple')
        self.ax1.set_ylim(0,1)
        self.ax1.set_xlim(self.xmin,self.xmax)

        if self.unit_index >=1:
            self.ax1.invert_xaxis()       

        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel('R', fontsize = 16, color = 'orange')
        self.ax2.set_ylim(0,1)
        self.ax2.set_xlim(self.xmin,self.xmax)
        if self.showRcheck.get_active() == True:
            self.lnR = self.ax2.plot(self.unit[self.unit_index], real(self.R), '-', color = 'orange', linewidth = 2)
            if self.showinfcheck.get_active() == True:        
                self.lnR2 = self.ax2.plot(self.unit[self.unit_index], real(self.R2), '--', color = 'orange', linewidth =1)

        self.span2 = SpanSelector(self.ax2, self.onselect, 'horizontal', useblit=True,
                                 rectprops=dict(alpha=0.4, facecolor='blue'))
       
        
        self.canvas.draw()

    def func1(self, x):
        n = len(x)
        sum = 0.0
        for i in range(n):
            sum+=(x[i]-12)**2
        return sum
    
    def run_min(self, x):
        x, fx, conv_flag, nfe, nres = nelmin.minimize(self.func1, [0,0,0])
        print x    
              
        

    def about_win(self, widget):
        about = gtk.AboutDialog()
        about.set_position(gtk.WIN_POS_CENTER)
        about.set_program_name("Film S.T.A.R.")
        about.set_version("v1.6")
        about.set_copyright("(c) R. E. Treharne, Feb 2013")
        about.set_comments('(Simulated Transmission and Reflection)')
        about.set_website("http://www.robtreharne.co.uk")
        self.pix = gtk.gdk.pixbuf_new_from_file("hollow-star.png")
        self.pix = self.pix.scale_simple(200,200, gtk.gdk.INTERP_BILINEAR)  
        about.set_logo(self.pix)
        about.run()
        about.destroy()

    def fit_win(self, widget):        

        self.fit_win = gtk.Window()
        self.fit_win.set_title("Fit Toolbox")
        self.fit_win.set_size_request(300,650)
        self.fit_win.set_position(gtk.WIN_POS_CENTER)
        (x, y) = self.win.get_position()
        self.fit_win.move(x+985,y)
        self.fit_win.show()

        self.max_T_but = gtk.Button("Maximize T")
        self.max_T_but.set_size_request(100,50)
        self.max_T_but.connect("clicked", self.run_min)

        box1 = gtk.VBox()
        box1.pack_start(self.max_T_but)

        self.fit_win.add(box1)
        self.fit_win.show_all()

    def model_win(self, widget):
        self.model_win = gtk.Window()
        self.model_win.set_title("Material Toolbox")
        self.model_win.set_size_request(300,650)
        self.model_win.set_position(gtk.WIN_POS_CENTER)
        (x,y) = self.win.get_position()
        self.model_win.move(x-305,y)
        self.model_win.show()

    def change_units(self,widget):          
        self.unit_index = self.unit_index + 1
        if self.unit_index == 3:
            self.unit_index = 0

        if self.press == 0:
            self.xmin = self.unit[self.unit_index][self.indmin]
            self.xmax = self.unit[self.unit_index][self.indmax]
            self.plot_TR(widget)
        if self.press ==1:
            self.xmin = self.unit[self.unit_index][self.indmin]
            self.xmax = self.unit[self.unit_index][self.indmax]
            self.plot_nk(widget)
        if self.press ==2:
            self.xmin = self.unit[self.unit_index][self.indmin]
            self.xmax = self.unit[self.unit_index][self.indmax]
            self.plot_e(widget)

    def combo_change(self,widget):
        self.index = self.combo.get_active()
        if self.index == 0:
            self.hscale.set_sensitive(False)
            self.d_label.set_sensitive(False)
        elif self.index >= 0:
            self.hscale.set_sensitive(True)
            self.d_label.set_sensitive(True)
            

    def onselect(self, xmin, xmax):
        self.indmin, self.indmax = np.searchsorted(self.unit[self.unit_index],(xmin,xmax))
        self.xmin = xmin
        self.xmax = xmax

        self.plot_TR(self)

    def signal_plot(self,widget):
        self.xmin = min(self.unit[self.unit_index])
        self.xmax = max(self.unit[self.unit_index])
        self.indmin, self.indmax = np.searchsorted(self.unit[self.unit_index],(self.xmin,self.xmax))
        self.plot_TR(widget)

    def options_win(self, widget):
                
        if self.inc >=1:
            self.inc = 0
            self.options_window.destroy()
        self.options_window = gtk.Window()
        self.options_window.set_title("Options")
        self.options_window.set_size_request(300,150)
        self.options_window.set_position(gtk.WIN_POS_CENTER)
        (x, y) = self.win.get_position()
        self.options_window.move(x-305,y+685)
        
        self.inc = self.inc+1

        minlabel = gtk.Label("x(min)")
        maxlabel = gtk.Label("x(max)")
        mininput = gtk.Entry()
        maxinput = gtk.Entry()

        set_but = gtk.Button("Set")
        set_but.set_size_request(100,50)

        self.showTcheck = gtk.CheckButton("Show T")
        self.showTcheck.connect("toggled", self.plot_TR)
        self.showRcheck = gtk.CheckButton("Show R")
        self.showRcheck.connect("toggled", self.plot_TR)
        self.showinfcheck = gtk.CheckButton("Inf. subs")
        self.showinfcheck.connect("toggled", self.plot_TR)

        self.showTcheck.set_active(True)
        self.showRcheck.set_active(True)
        self.showinfcheck.set_active(False)            

        box1 = gtk.VBox()
        box1.set_size_request(100,50)
        box1.pack_start(minlabel)
        box1.pack_start(mininput)

        box2 = gtk.VBox()
        box2.set_size_request(100,50)
        box2.pack_start(maxlabel)
        box2.pack_start(maxinput)

        box3 = gtk.HBox()
        box3.pack_start(box1)
        box3.pack_start(box2)
        box3.pack_start(set_but)

        box4 = gtk.VBox()
        box4.pack_start(self.showTcheck)
        box4.pack_start(self.showRcheck)
        box4.pack_start(self.showinfcheck)

        box5 = gtk.VBox()
        box5.pack_start(box3)
        box5.pack_start(box4)

        
        
        
        self.options_window.add(box5)

        self.options_window.show_all()
        
        
        
    
        

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
        self.unit_label = ("$\lambda$ (nm)", "Energy (eV)", "Wavenumber (1/cm)")        
        self.unit_index = 0
        self.inc = 0

        

        self.win = gtk.Window()
        self.win.set_size_request(980,650)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_title('Film S.T.A.R.')         

        self.subs_but = gtk.Button("Load Subs.")
        self.subs_but.connect("clicked", self.open_file)
        
        self.plot_nk_but = gtk.Button("Plot n & k")
        self.plot_nk_but.set_size_request(100,50)
        self.plot_nk_but.set_sensitive(False)
        self.plot_nk_but.connect("clicked", self.plot_nk)

        self.plot_e_but = gtk.Button('Plot e1 & e2')
        self.plot_e_but.set_size_request(100,50)
        self.plot_e_but.connect("clicked", self.plot_e)
        

        self.add_but = gtk.Button("Add film")
        self.add_but.set_sensitive(False)
        self.add_but.connect("clicked", self.open_file)

        self.delete_but = gtk.Button("Delete film")
        self.delete_but.set_sensitive(False)
        self.delete_but.connect("clicked", self.delete)

        self.plot_TR_but = gtk.Button('Plot T and R')
        self.plot_TR_but.connect("clicked", self.signal_plot)
        self.plot_TR_but.set_sensitive(False)

        self.about_but = gtk.Button("About")
        self.about_but.connect("clicked", self.about_win)

        self.fit_win_but = gtk.Button("Fit")
        self.fit_win_but.set_size_request(50,50)
        self.fit_win_but.connect("clicked", self.fit_win)
        self.fit_win_but.set_sensitive(False)

        self.model_win_but = gtk.Button("Create")
        self.model_win_but.set_size_request(50,50)
        self.model_win_but.connect("clicked", self.model_win)
        self.model_win_but.set_sensitive(False)

        self.units_but = gtk.Button(" ")
        self.units_but.set_size_request(5, 50)
        self.units_but.connect("clicked",self.change_units)
        self.units_but.set_tooltip_text("Change units")

        self.options_but = gtk.Button("")
        self.options_but.set_size_request(10,10)
        self.options_but.set_tooltip_text("Options")
        self.options_but.connect("clicked", self.options_win)

       
        self.fig1 = Figure()
        self.ax1 = self.fig1.add_subplot(111).axis('off')
        self.canvas = FigureCanvas(self.fig1)
        
        self.combo = gtk.combo_box_entry_new_text()
        self.combo.connect("changed", self.combo_change)

        self.adj1 = gtk.Adjustment(500.0, 0.0, 1001.0, 1.0, 1.0, 1.0)
        self.adj1.connect("value_changed", self.matrix)
        self.hscale = gtk.HScale(self.adj1)
        self.hscale.set_sensitive(False)

        self.d_label = gtk.Label("film thickness (nm)")  
        self.d_label.set_size_request(940,20)
        self.d_label.set_sensitive(False)       
                
        self.box1 = gtk.HBox()
        self.box1.set_size_request(980,500)
        self.box1.pack_start(self.canvas)

        self.box2 = gtk.HBox()
        #self.box2.pack_start(self.options_but)
        self.box2.pack_start(self.about_but)        
        self.box2.pack_start(self.plot_TR_but)
        self.box2.pack_start(self.plot_nk_but)
        self.box2.pack_start(self.plot_e_but)
        self.box2.pack_start(self.subs_but)
        self.box2.pack_start(self.add_but)
        self.box2.pack_start(self.delete_but)
        self.box2.pack_start(self.combo)
        self.box2.pack_start(self.model_win_but)
        self.box2.pack_start(self.fit_win_but)
        self.box2.pack_start(self.units_but)

        
        #self.box5.pack_start(self.options_but) 
        
        self.box3 = gtk.VBox()
        self.box3.set_size_request(980, 75)
        self.box3.pack_start(self.hscale)
        #self.box3.pack_start(self.d_label)
        
        self.box5 = gtk.HBox()
        self.box5.set_size_request(980,20)
        self.box5.pack_start(self.options_but)
        self.box5.pack_start(self.d_label)
          

        self.box4 = gtk.VBox()
        self.box4.pack_start(self.box1)
        self.box4.pack_start(self.box2)
        self.box4.pack_start(self.box3)
        self.box4.pack_start(self.box5)
                       
        self.win.add(self.box4)        
                
        self.win.show_all()

        self.plot_e_but.hide()
        self.add_but.hide()
        self.win.connect("destroy", self.destroy)

        self.options_win(self)
        self.options_window.destroy()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    window = Window()
    window.main()
        

