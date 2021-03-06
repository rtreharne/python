from pylab import *
import tkFileDialog
import nelmin
from Calcs import *
from Model import *
from matplotlib.widgets import Slider

class Plot:
    def __init__(self):
        #self.L = Model(2.7, 1.08, 1.0, 1.1, 0.1, 0.01, 3.3, 20)
        self.L = Model(2.55, 1.05, 0.99, 1.21, 0.1, 0.12, 3.35, 20)
        fig = figure(figsize = (7, 7))
        self.ax = subplot(111)
        openit = axes([0.01, 0.01, 0.2, 0.03])
        fitit = axes([0.22, 0.01, 0.2, 0.03])
        axd = axes([0.55, 0.01, 0.3, 0.03])
        self.openbut = Button(openit, 'Open', hovercolor = '0.5')
        self.openbut.on_clicked(self.openfile)
        self.fitbut = Button(fitit, 'Fit!', hovercolor = '0.5')
        self.sd = Slider(axd, '$d$ (nm)', 200, 1000, valinit = 254)
        self.sd.on_changed(self.update)
        self.openfile(None)
        self.interpolate()
        self.d = self.sd.val
        L = self.L
        self.dummy(self.sd.val, L)
        self.fitbut.on_clicked(self.fit)
        
        
  
    def openfile(self, widget):
        self.filename = tkFileDialog.askopenfilename()
        filename = self.filename
        self.datax = loadtxt(filename, unpack = True, usecols=[0])
        self.datay = loadtxt(filename, unpack = True, usecols=[1])
        #self.ax.plot(self.datax, self.datay)
        self.smooth()

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
        x = self.xvals
        ax = self.ax
        y = self.yinterp
        L = self.L
        C = Calcs(x, 1.48, self.L, self.d)
        A = C.matrix(x)
        p = C.peak_pick(x, A)        
        d = C.prefit(x, y, L, ax)
        print d
        self.update(d)
        p = self.C.p_fit(x, y, L)
        print p
        self.L = Model(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])
        self.update(d)
        self.d = d
        
    
plot1 = Plot()

show()

