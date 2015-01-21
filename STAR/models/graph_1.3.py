from pylab import *
import tkFileDialog
import nelmin
from Calcs13 import *
from Model import *
from matplotlib.widgets import Slider
import time
import pyglet

class Plot:
    def __init__(self):
        #self.L = Model(2.7, 1.08, 1.0, 1.1, 0.1, 0.01, 3.3, 20)
        self.L = Model(2.5, 1.0, 1.0, 1.108, 0.07616, 0.001, 3.3, 20.0488) 
        fig = figure(figsize = (14, 7))
        subplots_adjust(bottom=0.2)
        self.ax = subplot(111)
        self.ax.axis((250, 2500, 0, 100))
        
        openit = axes([0.01, 0.1, 0.2, 0.03])
        fitit = axes([0.22, 0.1, 0.2, 0.03])
        nextit = axes([0.01, 0.05, 0.2, 0.03])
        axd = axes([0.55, 0.01, 0.3, 0.03])
        
        self.openbut = Button(openit, 'Open', hovercolor = '0.5')
        self.openbut.on_clicked(self.openfile)
        self.fitbut = Button(fitit, 'Fit!', hovercolor = '0.5')
        self.nextbut = Button(nextit, 'Next', hovercolor = '0.5')
        self.sd = Slider(axd, '$d$ (nm)', 100, 1000, valinit = 532)
        self.sd.on_changed(self.update)
        self.openfile(None)
        
        self.d = self.sd.val
        L = self.L
        self.dummy(self.sd.val, L)
        self.fitbut.on_clicked(self.fit)
        self.nextbut.on_clicked(self.next)
 
    def openfile(self, widget):
        self.n = 1
        self.ax.clear()
        self.filename = tkFileDialog.askopenfilename()
        filename = self.filename
        self.data = loadtxt(filename)
        self.datax = loadtxt(filename, unpack = True, usecols=[0])
        self.datay = loadtxt(filename, unpack = True, usecols=[self.n])
        #self.ax.plot(self.datax, self.datay)
        self.x = self.datax
        self.y = self.datay
        self.interpolate()
        self.smooth()        
        self.dummy(self.sd.val, self.L)

    def dummy(self, d, L):
        
        self.p = self.L.group()
        self.C = Calcs(self.xvals, 1.48, self.L, d) 
        T = self.C.matrix(self.xvals)
        self.ax.plot(self.xvals, T)
        
    def update(self, d):
        self.d = d
        self.ax.clear()
        self.ax.plot(self.xvals, self.yinterp)
        #self.ax.plot(self.datax, self.datay)
        self.dummy(d, self.L)
 
    def interpolate(self):
        self.xvals = linspace(self.x[0], self.x[-1], 200)
        self.yinterp = interp(self.xvals, self.x, self.y)
        self.ax.plot(self.xvals, self.yinterp, color = 'red')

    def smooth(self):
        y = self.datay
        x = self.datax
        n= 5
        w = 5
        for k in range (0, n):
            ysmooth =[]
            xsmooth = []        
            for i in range (w, len(x)-w):
                sum = 0
                for j in range (-w, w):
                    
                    sum += y[i+j]
                    average = sum/(2*w)
                ysmooth.append(average)
            xsmooth = x[w:len(x)-w]
            x = []
            x = xsmooth
            y = ysmooth
        self.x = x
        self.y = y
        self.ax.plot(x, y, '-', color = 'red')

    def fit(self, d):
        start = time.time()
        for i in range (0, 3):
            x = self.xvals
            ax = self.ax
            y = self.yinterp
            L = self.L
            C = Calcs(x, 1.48, self.L, self.d)
            A = C.matrix(x)
            p = C.peak_pick(x, A)        
            d = C.prefit(x, y, L, ax)
            self.update(d)
            p = self.C.p_fit(x, y, L)
            #print p
            self.L = Model(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])
            self.update(d)
            self.d = int(d[0])
        finish = time.time()
        print (finish-start), self.d

    def next(self, widget):
        self.n += 1
        filename = self.filename
        self.datax = loadtxt(filename, unpack = True, usecols=[0])
        self.datay = loadtxt(filename, unpack = True, usecols=[self.n])
        self.ax.plot(self.datax, self.datay)
        self.x = self.datax
        self.y = self.datay
        self.ax.clear()
        self.interpolate()
        self.smooth()        
        self.dummy(self.sd.val, self.L)
        
    
plot1 = Plot()

show()

