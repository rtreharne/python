from pylab import *
import tkFileDialog
import nelmin

class Plot:
    def __init__(self):
        fig = figure(figsize = (7, 7))
        self.ax = subplot(111)
        openit = axes([0.01, 0.01, 0.2, 0.03])
        interpit = axes([0.22, 0.01, 0.2, 0.03])
        self.openbut = Button(openit, 'Open', hovercolor = '0.5')
        self.openbut.on_clicked(self.openfile)
        self.interpbut = Button(interpit, 'Interpolate', hovercolor = '0.5')
        self.interpbut.on_clicked(self.interpolate)
        

    def openfile(self, widget):
        self.filename = tkFileDialog.askopenfilename()
        filename = self.filename
        self.datax = loadtxt(filename, unpack = True, usecols=[0])
        self.datay = loadtxt(filename, unpack = True, usecols=[1])
        self.ax.plot(self.datax, self.datay)
        self.smooth()
        

    def interpolate(self, widget):
        self.xvals = linspace(self.x[0], self.x[-1], 300)
        self.yinterp = interp(self.xvals, self.x, self.y)
        self.ax.plot(self.xvals, self.yinterp, 'o', alpha = 0.5)

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
        
        
                
        
    
plot1 = Plot()

show()

