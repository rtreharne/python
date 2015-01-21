from pylab import *
import tkFileDialog
import nelmin
from Calcs import *
from Model import *
from matplotlib.widgets import Slider

class Plot:
    def __init__(self):
        fig = figure(figsize = (7, 7))
        self.ax = subplot(111)
        openit = axes([0.01, 0.01, 0.2, 0.03])
        fitit = axes([0.22, 0.01, 0.2, 0.03])
        axd = axes([0.55, 0.01, 0.3, 0.03])
        self.openbut = Button(openit, 'Open', hovercolor = '0.5')
        self.openbut.on_clicked(self.openfile)
        self.fitbut = Button(fitit, 'Fit!', hovercolor = '0.5')
        self.sd = Slider(axd, '$d$ (nm)', 200, 1000, valinit = 400)
        self.sd.on_changed(self.update)
        self.openfile(None)
        self.dummy(self.sd.val)
        self.interpolate()
        self.fitbut.on_clicked(self.fit)
        
  
    def openfile(self, widget):
        self.filename = tkFileDialog.askopenfilename()
        filename = self.filename
        self.datax = loadtxt(filename, unpack = True, usecols=[0])
        self.datay = loadtxt(filename, unpack = True, usecols=[1])
        #self.ax.plot(self.datax, self.datay)
        self.smooth()

    def dummy(self, d):
        self.L = Model(2.8, 1.3, 1.0, 1.1, 0.1, 0.01, 3.3, 20)
        self.p = self.L.group()
        self.C = Calcs(self.x, 1.48, self.L, d) 
        T = self.C.matrix(self.x)
        T = T*100
        self.ax.plot(self.x, T)

    def update(self, d):
        self.ax.clear()
        self.ax.plot(self.x, self.y)
        #self.ax.plot(self.datax, self.datay)
        self.dummy(d)
 
    def interpolate(self):
        self.xvals = linspace(self.x[0], self.x[-1], 500)
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

    def fit(self, widget):
        x = self.xvals
        ax = self.ax
        y = self.yinterp
        L = self.L
        C = Calcs(x, 1.48, self.L, self.C.dval())
        A = C.matrix(x)
        p = C.peak_pick(x, A)
        print p
        self.C.prefit(x, y, L, ax)
        
        #for position, item in enumerate(l):
            #if item == min(l, key=lambda x:abs(x - 400)):
                #print position, l[position]
            #if item == min(l, key=lambda x:abs(x - 800)):
                #print position, l[position]
        
        
    
        
        
                
        
    
plot1 = Plot()

show()

