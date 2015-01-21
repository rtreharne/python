from pylab import *
import tkFileDialog
import nelmin
from Calcs13 import *
from Model import *
from matplotlib.widgets import Slider
import time

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
        fitallit = axes([0.22, 0.05, 0.2, 0.03])
        axd = axes([0.55, 0.01, 0.3, 0.03])
        saveit = axes([0.6, 0.05, 0.2, 0.03])
        
        self.openbut = Button(openit, 'Open', hovercolor = '0.5')
        self.openbut.on_clicked(self.openfile)
        self.fitbut = Button(fitit, 'Fit!', hovercolor = '0.5')
        self.nextbut = Button(nextit, 'Next', hovercolor = '0.5')
        self.fitallbut = Button(fitallit, 'Fit all', hovercolor = '0.5')
        self.savebut = Button(saveit, 'Save', hovercolor = '0.5')
        self.sd = Slider(axd, '$d$ (nm)', 100, 1000, valinit = 532)
        self.sd.on_changed(self.update)
        self.openfile(None)
        
        self.d = self.sd.val
        L = self.L
        self.dummy(self.sd.val, L)
        self.fitbut.on_clicked(self.fit)
        self.nextbut.on_clicked(self.next)
        self.fitallbut.on_clicked(self.pattern)
        self.savebut.on_clicked(self.save)
 
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
        self.fitD = []
        self.fitN = []

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
        for i in range (0, 2):
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
            self.p = p
            self.L = Model(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])
            self.update(d)
            self.d = int(d[0])
        finish = time.time()
        print (finish-start), self.d
        self.fitD.append(self.d)
        self.fitN.append(self.n)
        self.output = (self.fitN, self.fitD)
        self.sd.val = self.d
        #print self.n, self.d

    def save(self, widget):
        savetxt('manual', transpose([self.output]))
        

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

    def next2(self):
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
       

    def pattern(self, widget):
        m = 0
        D = [self.d]
        X = []
        Y = []
        W = []
        l = int(sqrt(len(self.data[0])-1))
        
        
        for i in range (0,len(self.data[0])-1,l):
            
            
            if ((i/l)+1)%2 == 1:
                for j in range(i, i+l):
                    #print 'a', j, -((i+l)/l-(floor(l/2)+1)), j-i-floor(l/2)
                    self.n = j+1
                    self.next2()
                    self.fit(self.d)
                    D.append(self.d)
                    W.append(self.p[1])
                    X.append(j-i-floor(l/2))
                    Y.append(-((i+l)/l-(floor(l/2)+1)))
                    m += 1
                    self.d = D[m] - ((D[m-1]-D[m]))/2
                    if j == i+1:
                        self.d = D[m]
                    print m, D[m], D[m-1]-D[m], self.d
                    
            if ((i/l)+1)%2 == 0:
                if i > l**2-l:
                    break
                for k in range(0, l):
                    #print 'b', l+i-k-1, -((i+l)/l-(floor(l/2)+1)), -(k-floor(l/2))
                    self.n = l+i-k
                    self.next2()
                    self.fit(self.d)
                    D.append(self.d)
                    W.append(self.p[1])
                    X.append(-(k-floor(l/2)))
                    Y.append(-((i+l)/l-(floor(l/2)+1)))
                    m += 1
                    self.d = D[m] - ((D[m-1]-D[m]))/2
                    print m, D[m], D[m-1]-D[m], self.d
        B = D[1:len(D)]          
        output = (X, Y, B, W)
        savetxt('output', transpose([output]))


    def fitall(self, widget):
        D = []
        Q = []
        W = []
        for i in range (0, 2):
            self.fit(self.d)
            self.next(widget)
            D.append(self.d)
            Q.append(i)
            W.append(self.p)
        #print D
        output = (Q, D, W)
        savetxt('manual', transpose([output]))
        
    
plot1 = Plot()

show()

