#!/usr/bin/env python

""" -------------------------------------------------------------------------
STAR_2.3
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

    def add_file(self,widget):
        self.open_file(widget)
        self.build(widget)

    def open_file(self, widget):
        # open file dialog
        dialog = gtk.FileChooserDialog("Open", None, 
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

    def save(self,widget):
        dialog = gtk.FileChooserDialog("Save",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(".txt")
        #filter.add_mime_type("text/txt")

        filter.add_pattern("*.txt")

        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            print dialog.get_filename(), 'has been saved'
            self.filename = str(dialog.get_filename())
            #data = (self.lam, real(self.T), real(self.R))
            #savetxt(dialog.get_filename(), transpose([data]))
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()


    def build(self, widget):

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
        self.textboxmin.set_sensitive(True)
        self.textboxmax.set_sensitive(True)

        # run function "add_combo"
        self.add_combo(widget)

        #add default d value to d list
        self.combo.set_active(len(self.nk)-1)
        self.index = self.combo.get_active()
        self.d.append(self.hscale.get_value())
        self.dmin.append(int(self.textboxmin.get_text()))
        self.dmax.append(int(self.textboxmax.get_text()))
        #convert list nk to units of admittance
        self.Y.append(self.nk[self.combo.get_active()]*2.6544e-3)
        
        #prepare M list for calcs
        self.M.append([])
        self.T = [0]*len(self.lam)
        self.R = [0]*len(self.lam)

        for i in range(0,len(self.lam)):
            self.M[self.index].append([0])


        
        # declare substrate identity
        if len(self.nk) == 1:   
            self.subs = []
            self.subs = array([self.Y[0]/self.Y[0],(self.Y[0]/self.Y[0])*2.6544e-3])
            self.exit = []
            self.exit.append((self.Y[0]/self.Y[0]))

        if len(self.nk) == 0:
            self.exit = []
            
        

        # run function "matrix"
        
        if self.index >=1:
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
        del self.dmin[self.index]
        del self.dmax[self.index]
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

       
        
        self.T2=[0]*len(self.lam)
        self.R2 = [0]*len(self.lam)

        for i in range(self.indmin, self.indmax):
            MP = []               
            MP = array([[1,0],[0,1]])

            for j in range (1,len(self.nk)):
                delta = 2*math.pi*self.nk[j][i]*self.d[j]/self.lam[i]
                self.M[j][i] =array([[c.cos(delta),   
                                       (1j*c.sin(delta)/self.Y[j][i])], 
                                       [1j*self.Y[j][i]*c.sin(delta), 
                                        c.cos(delta)]])
                MP = dot(MP,self.M[j][i])

            B1 = MP[0][0]*self.subs[0][i]
            B2 = MP[0][1]*self.subs[1][i]
            C1 = MP[1][0]*self.subs[0][i]
            C2 = MP[1][1]*self.subs[1][i]
            B = B1+B2
            C = C1+C2
            X = (self.Y[0][i]*B+C)
            Y = (self.Y[0][i]*B+C).conjugate()
            Z = (self.Y[0][i]*B-C)

            """TRANSMISSION-----------------------------------------------"""
            # Calculate transmission through single air/substrate interface
            Ta = ((1/2.6544e-3)*(4*real(self.Y[0][i]))/
                                ((1/2.6544e-3*real(self.Y[0][i]))+1)**2)
            # Calculate transmission through stack
            Tb = (4*self.Y[0][i]*real(self.exit[0][i]*2.6544e-3))/(X*Y)
            
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
            
        if self.fitindex == 0:
            self.plot_TR(widget)
            self.av_T()
            
            
        

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
        
        

    def av_T(self):
        area = 0
        for i in range(self.indmin+1, self.indmax):
            area+=real((self.T[i-1]+self.T[i])*(self.lam[i]-self.lam[i-1])/2)
        self.average_T = area/(self.xmax-self.xmin)
        


    def func1(self, x):
        
        self.fitindex+=1
        if self.fitindex>=100:
            sum = 0
            return sum
        
        sum = 0.0
        sum2 = 0
        for i in range (0,len(x)):
            self.d[i+1] = x[i]
            
            if self.d[i+1] <= 0:
                self.d[i+1] = 0
                x[i] = 0
            self.matrix(x)
            #self.plot_TR(x)
            self.av_T()
                                 
            sum+=(1-self.average_T)
            
            
        print self.fitindex,sum,self.average_T    
        return sum
    
    def run_min(self, x):
        self.fitindex = 1
        d = []
        for i in range (0,len(self.d)-1):
            print self.d[i+1]
            d.append(self.d[i+1])
                    
        #print d, self.d
        
        x, fx, conv_flag, nfe, nres = nelmin.minimize(self.func1, d)
        for i in range (0, len(self.d)-1):            
            self.d[i+1] = x[i]
        
        self.fitindex = 0
        print x, self.d
        print "--------"
        self.matrix(x)
        print x, self.d, nfe
        
              
        

    def about_win(self, widget):
        about = gtk.AboutDialog()
        about.set_position(gtk.WIN_POS_CENTER)
        about.set_program_name("Film S.T.A.R.")
        about.set_version("v2.0")
        about.set_copyright("(c) R. E. Treharne, Feb 2013")
        about.set_comments('(Simulated Transmission, Absorption and Reflection)')
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
            print self.d
            
            
            self.adj1.set_lower(self.dmin[self.index])
            self.adj1.set_upper(self.dmax[self.index])
            self.textboxmin.set_text("%.0f" % self.dmin[self.index])
            self.textboxmax.set_text("%.0f" % self.dmax[self.index])
            self.hscale.set_sensitive(True)
            self.d_label.set_sensitive(True)
            self.adj1.set_value(self.d[self.index])
            print self.d

    def change_d_scale(self,widget):
        
        lower = int(self.textboxmin.get_text())
        upper = int(self.textboxmax.get_text())
        value = self.adj1.get_value()      

        if lower >= value:
            self.adj1.set_lower(value)
        if upper <= value:
            self.adj1.set_upper(value)

        if lower <= value and upper >= value:        
          self.adj1.set_lower(lower)
          self.adj1.set_upper(upper)

        self.dmin[self.index]=self.adj1.get_lower()
        self.dmax[self.index]=self.adj1.get_upper()

    def scale_change(self, widget):
        
        #get active thickness value
             
        self.index = self.combo.get_active()
        self.d[self.index]=self.adj1.get_value()
        self.matrix(widget)
        
            

    def onselect(self, xmin, xmax):
        self.indmin, self.indmax = np.searchsorted(self.unit[self.unit_index],(xmin,xmax))
        self.xmin = xmin
        self.xmax = xmax
        self.plot_TR(self)
        self.av_T()
        

    def signal_plot(self,widget):
        self.xmin = min(self.unit[self.unit_index])
        self.xmax = max(self.unit[self.unit_index])
        self.indmin, self.indmax = np.searchsorted(self.unit[self.unit_index],(self.xmin,self.xmax))
        self.matrix(widget)

    def export(self, widget):
        self.save(widget)
        data = (self.lam, real(self.T), real(self.R))
        savetxt(self.filename, transpose([data]))

    
        
        

   
        

#""" Options Window and funcitons -------------------------------------------"""

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
        self.mininput = gtk.Entry()
        self.maxinput = gtk.Entry()

        self.set_but = gtk.Button("Set")
        self.set_but.set_size_request(100,50)
        self.set_but.connect("clicked", self.range_set)

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
        box1.pack_start(self.mininput)

        box2 = gtk.VBox()
        box2.set_size_request(100,50)
        box2.pack_start(maxlabel)
        box2.pack_start(self.maxinput)

        box3 = gtk.HBox()
        box3.pack_start(box1)
        box3.pack_start(box2)
        box3.pack_start(self.set_but)

        box4 = gtk.VBox()
        box4.pack_start(self.showTcheck)
        box4.pack_start(self.showRcheck)
        box4.pack_start(self.showinfcheck)

        self.exitmed_but = gtk.Button("Set exit medium")
        self.exitmed_but.connect("clicked", self.set_exit)
        self.exit_nk = gtk.Button("Plot exit n & k")
        self.spare2 = gtk.Button("spare")

        box5 = gtk.VBox()
        box5.pack_start(self.exitmed_but)
        box5.pack_start(self.exit_nk)
        box5.pack_start(self.spare2)
       
        box6 = gtk.HBox()
        box6.pack_start(box5)
        box6.pack_start(box4)
      

        box7 = gtk.VBox()
        box7.pack_start(box3)
        box7.pack_start(box6)    

        self.options_window.add(box7)
        self.options_window.show_all()

    def range_set(self, widget):
        self.xmin = int(self.mininput.get_text())
        self.xmax = int(self.maxinput.get_text())
        self.indmin, self.indmax = np.searchsorted(self.unit[self.unit_index],(self.xmin,self.xmax))
        self.matrix(widget)

    def set_exit(self, widget):
        self.exit = []
        self.open_file(widget)
        
        self.n = loadtxt(self.root, unpack = True, usecols=[1])
        self.k = loadtxt(self.root, unpack = True, usecols=[2])
        #consolidate n and k into single complex list
        self.exit.append(self.n-1j*self.k)

        self.subs = array([self.Y[0]/self.Y[0],(self.exit[0])*2.6544e-3])
        self.plot_TR(widget)

#Materials Window and functions -----------------------------------------------

    def model_win(self, widget):
        #Define window and buttons, etc
        self.model_win = gtk.Window()
        self.model_win.set_title("Material Toolbox")
        self.model_win.set_size_request(300,650)
        self.model_win.set_position(gtk.WIN_POS_CENTER)
        (x,y) = self.win.get_position()
        self.model_win.move(x-305,y)

        self.mod_combo1 = gtk.combo_box_entry_new_text()
        self.mod_combo1.set_size_request(150, 30)
        self.mod_combo1.connect("changed", self.mod_combo1_change)
                    
        self.mod_new = gtk.Button("New")
        #self.mod_new.set_size_request(75, 30)
  
        self.mod_save = gtk.Button("Save")
        #self.mod_save.set_size_request(75, 30)
 
        self.mod_open = gtk.Button("Open")
        #self.mod_open.set_size_request(75, 30)
        self.mod_open.connect("clicked", self.open_material)

        self.mod_combo2 = gtk.combo_box_entry_new_text()
        self.mod_combo2.set_size_request(150,30)
        self.mod_combo2.append_text("Constant n")
        self.mod_combo2.append_text("Lorentz")
        self.mod_combo2.append_text("Drude")
        self.mod_combo2.append_text("Extended Drude")
        self.mod_combo2.append_text("Non Parabolic Drude")
        self.mod_combo2.append_text("Direct Band Gap")
        self.mod_combo2.append_text("Indirect Band Gap")
        self.mod_combo2.append_text("Burstein-Moss")
        self.mod_combo2.append_text("Urbach Tail")

        self.mainbox = gtk.ScrolledWindow()
        self.mainbox.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
       
        self.model = gtk.ListStore( str, float,bool) #@+
        self.treeview = gtk.TreeView(self.model)        
        self.treeview.connect("cursor-changed", self.get_selected)


        #individual columns
        # URL column
        col = gtk.TreeViewColumn( "Parameter")
        self.treeview.append_column( col)
        cell = gtk.CellRendererText()
        col.pack_start( cell, expand=False)
        col.set_attributes( cell, text=0)
        col.set_sort_column_id( 0)

        col = gtk.TreeViewColumn( "Value")
        self.treeview.append_column( col)
        cell = gtk.CellRendererText()
        cell.set_property("editable",True)
        col.pack_start( cell, expand=False)
        col.set_attributes( cell, text=1)
        col.set_sort_column_id( 1)
        cell.connect("edited", self.value_changed, 1)

        col = gtk.TreeViewColumn( "Fit?")
        self.treeview.append_column( col)
        cell = gtk.CellRendererToggle()
        cell.set_property( "activatable", True)
        col.pack_start( cell, expand=False)
        col.set_attributes( cell, active=2)
        col.set_sort_column_id( 2)
        cell.connect('toggled', self._download_toggled, 2)

        self.dummy(self)
        self.populate(self)  

        self.mainbox.add(self.treeview1[0])

        self.mod_add_model = gtk.Button("Add Model")
        self.mod_add_model.connect("clicked", self.add_model)

        self.add_stack_but = gtk.Button("Add to stack")
        self.add_stack_but.connect("clicked", self.add_stack)

        self.mod_label = gtk.Label("")
      
        box1 = gtk.HBox()
        box1.set_size_request(300, 30)
        box1.pack_start(self.mod_combo1)
        box1.pack_start(self.mod_new)
        box1.pack_start(self.mod_save)
        box1.pack_start(self.mod_open)

        box2 = gtk.HBox()
        box2.set_size_request(300, 30)
        box2.pack_start(self.mod_combo2)
        box2.pack_start(self.mod_add_model)

        box3 = gtk.VBox()
        box3.set_size_request(300,150)
        box3.pack_start(self.mainbox)

        box4 = gtk.HBox()
        box4.set_size_request(300, 30)
        box4.pack_start(self.add_stack_but)

        box5 = gtk.HBox()
        box5.set_size_request(300,370)
        box5.pack_start(self.mod_label)

        box6 = gtk.VBox()
        box6.pack_start(box1)
        box6.pack_start(box2)
        box6.pack_start(box3)
        box6.pack_start(box4)
        box6.pack_start(box5)

        self.model_win.add(box6)
        self.model_win.show_all()

        self.create_register = []
        self.create_register.append([0,-1])
 
    def open_material(self, widget):
        self.open_file(widget)
        print "filename =", self.root
        print "path = ", self.filename

        self.mod_combo1.append_text(str(self.root))
        self.model1.append(gtk.ListStore(str,float,bool))

        #str(param) = loadtxt(self.root, unpack = True, usecols=[0])
        #value = loadtxt(self.root, unpack = True, usecols=[1])
        #fit = loadtxt(self.root, unpack = True, usecols=[2])

        param = loadtxt(self.root, str, unpack = True, usecols=[0])
        value = loadtxt(self.root, float, unpack = True, usecols=[1])
        fit = loadtxt(self.root, bool, unpack = True, usecols=[2])

        pos = len(self.model1)-1

        for i in range (0, len(param)):            
            self.model1[pos].append([param[i], value[i], fit[i]])

        self.treeview1.append(gtk.TreeView(self.model1[pos]))
        
        self.populate(widget)
        self.mod_combo1.set_active(pos)
        

        
        
        

    def dummy(self, widget):
        #set dummy data
        self.model1 = []
        self.treeview1 = []
        
        #self.model1.append(gtk.ListStore(str,float,bool))
        
        self.mod_combo1.append_text("new1")
        self.mod_combo1_val = self.mod_combo1.get_active()
        self.mod_combo1.set_active(self.mod_combo1_val+1)
        self.mod_combo1_indexold = self.mod_combo1.get_active()
        self.model1.append(gtk.ListStore(str,float,bool))
        self.model1[0].append(["Tom", 1.0, True])
        self.model1[0].append(["Dick", 2.0, False])
        self.model1[0].append(["Harry", 3.0, True])
        self.treeview1.append(gtk.TreeView(self.model1[0]))

       
    def populate(self, widget):
        #individual columns
        # URL column

        for i in range (0, len(self.model1)):
            col = gtk.TreeViewColumn( "Parameter")
            self.treeview1[i].append_column( col)
            cell = gtk.CellRendererText()
            col.pack_start( cell, expand=False)
            col.set_attributes( cell, text=0)
            col.set_sort_column_id( 0)

            col = gtk.TreeViewColumn( "Value")
            self.treeview1[i].append_column( col)
            cell = gtk.CellRendererText()
            cell.set_property("editable",True)
            col.pack_start( cell, expand=False)
            col.set_attributes( cell, text=1)
            col.set_sort_column_id( 1)
            cell.connect("edited", self.value_changed, 1)

            col = gtk.TreeViewColumn( "Fit?")
            self.treeview1[i].append_column( col)
            cell = gtk.CellRendererToggle()
            cell.set_property( "activatable", True)
            col.pack_start( cell, expand=False)
            col.set_attributes( cell, active=2)
            col.set_sort_column_id( 2)
            cell.connect('toggled', self._download_toggled, 2)
            print "i=", i

        print "treeview length = ", len(self.treeview1)

        
        #self.mainbox.remove(self.treeview1[0])
        #self.mainbox.add(self.treeview1[1])

    def mod_combo1_change(self,widget):
        print "indexold = ",self.mod_combo1_indexold
        self.mainbox.remove(self.treeview1[self.mod_combo1_indexold])
        self.mod_combo1_indexnew = self.mod_combo1.get_active()
        self.mainbox.add(self.treeview1[self.mod_combo1_indexnew])
        self.mod_combo1_indexold = self.mod_combo1_indexnew
        self.model_win.show_all()
        print "indexold = ",self.mod_combo1_indexold
        print "Hello Rob"    

    def add_model(self, widget):
        self.mod_combo2_index = self.mod_combo2.get_active()
        print self.mod_combo2_index
        self.modnk = [0]*len(self.nk)
        
        if self.mod_combo2_index == 0:
            param = "const n"
            value = 2.6
            fit = False
            self.model.append([param, value, fit])
            self.modnk = [0]*len(self.lam)
            
            for i in range (0, len(self.lam)):
                self.modnk[i] = value
     
        if self.mod_combo2_index == 1:
            self.model.append(["LorentzA", 1.0, False])
            self.model.append(["LorentzB", 1.0, False])
            self.model.append(["LorentzC", 1.0, False])
         
    def _download_toggled( self, w, row, column):
        print "index = ", self.mod_combo1_indexold
        print "tallyho = ", self.model1[self.mod_combo1_indexold][row][column]
        self.model1[self.mod_combo1_indexold][row][column] = not self.model1[self.mod_combo1_indexold][row][column]
        

    def get_selected(self, widget):
        selection = self.treeview.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        model, tree_iter = selection.get_selected()
        self.selected = model.get_value(tree_iter, 1)
        text = model.get_value(tree_iter, 0)
        print text, self.selected      

    def value_changed(self, w, row, new_value, column):
        self.model[row][column] = float(new_value)

    def add_stack(self, widget):
        self.combo.append_text("new1")
        self.hscale.set_sensitive(True) 
        self.nk.append(self.modnk)   

        for i in range(0,len(self.lam)):
            self.M[self.index].append([0])
        self.combo.set_active(len(self.nk)-1)
        
        self.index = self.combo.get_active()
        self.d.append(self.hscale.get_value())
        self.dmin.append(int(self.textboxmin.get_text()))
        self.dmax.append(int(self.textboxmax.get_text()))
        self.Y.append([])       

        self.M.append([])
        self.T = [0]*len(self.lam)
        self.R = [0]*len(self.lam)

        for i in range(0,len(self.lam)):
            self.Y[self.index].append(self.nk[self.index][i]*2.6544e-3)
            self.M[self.index].append([0])

        if self.index >=1:
            self.matrix(widget)

        
        
              
            
        
        
        
    
        

    def __init__(self):
        #instantiation
        #configures all plots, buttons sliders and lists

        #initialize global lists
        self.nk = []
        self.Y = []
        self.subs_Y = []
        self.d = []
        self.dmin = []
        self.dmax = []        
        self.T = []
        self.R = []
        self.M = []
        self.delta = []
        self.unit_label = ("$\lambda$ (nm)", "Energy (eV)", "Wavenumber (1/cm)")        
        self.unit_index = 0
        self.inc = 0
        self.flag = 0
        self.fitindex = 0
        self.exit = 1
        

        self.win = gtk.Window()
        self.win.set_size_request(980,650)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_title('Film S.T.A.R.')         

        self.subs_but = gtk.Button("Load Subs.")
        self.subs_but.connect("clicked", self.add_file)
        
        self.plot_nk_but = gtk.Button("Plot n & k")
        self.plot_nk_but.set_size_request(100,50)
        self.plot_nk_but.set_sensitive(False)
        self.plot_nk_but.connect("clicked", self.plot_nk)

        self.plot_e_but = gtk.Button('Plot e1 & e2')
        self.plot_e_but.set_size_request(100,50)
        self.plot_e_but.connect("clicked", self.plot_e)
        

        self.add_but = gtk.Button("Add film")
        self.add_but.set_sensitive(False)
        self.add_but.connect("clicked", self.add_file)

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

        self.export_but = gtk.Button("Export")
        self.export_but.connect("clicked", self.export)

       
        self.fig1 = Figure()
        self.ax1 = self.fig1.add_subplot(111).axis('off')
        self.canvas = FigureCanvas(self.fig1)
        
        self.combo = gtk.combo_box_entry_new_text()
        self.combo.connect("changed", self.combo_change)

        self.textboxmin = gtk.Entry()
        self.textboxmin.set_size_request(10,25)
        self.textboxmin.set_text("0")
        self.textboxmin.set_sensitive(False)
        self.textboxmin.connect("activate", self.change_d_scale)
        
        self.textboxmax = gtk.Entry()
        self.textboxmax.set_size_request(10,25)
        self.textboxmax.set_text("1000")
        self.textboxmax.set_sensitive(False)
        self.textboxmax.connect("activate", self.change_d_scale)

        self.adj1 = gtk.Adjustment(500.0, 0.0, 1001.0, 1.0, 1.0, 1.0)
        self.adj1.connect("value_changed", self.scale_change)
        self.hscale = gtk.HScale(self.adj1)
        self.hscale.set_size_request(800, 20)
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
        self.box2.pack_start(self.export_but)
        self.box2.pack_start(self.units_but)

        
        #self.box5.pack_start(self.options_but) 
        
        self.box3 = gtk.HBox()
        self.box3.set_size_request(980, 75)
        self.box3.pack_start(self.textboxmin)
        self.box3.pack_start(self.hscale)
        self.box3.pack_start(self.textboxmax)
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
        

