from math import *
from pylab import *

class Model:
    def __init__(self, db, pf, cross, width, s_low, s_high, res, amp):
        self.db = db
        self.pf, self.cross, self.width, self.s_low, self.s_high = pf, cross, width, s_low, s_high
        self.res = res
        self.amp = amp

    def group(self):
        x = ([self.db, self.pf, self.cross, self.width,
              self.s_low, self.s_high, self.res, self.amp])
        return x
               

    def nmtoev(self, x):
        y = (6.63e-34*3e8)/(x*1e-9*1.602e-19)
        return y

    def eton(self, x):
        n = ((sqrt(real(x)**2+imag(x)**2)+real(x))/2)**0.5
        k = ((sqrt(real(x)**2+imag(x)**2)-real(x))/2)**0.5
        N = n-1j*k
        return N

    def background(self, x):
        db = self.db
        y = db*x/x
        return y

    def ext_drude(self, x):
        pf, cross, width, s_low, s_high = self.pf, self.cross, self.width, self.s_low, self.s_high
        x = self.nmtoev(x)
        scatt = s_low - ((s_low-s_high)/pi)*(arctan((x - cross)/width)+pi/2)       
        y = -pf**2/(x**2+1j*scatt)
        return y

    def direct(self, x):
        res, amp = self.res, self.amp
        x = self.nmtoev(x)
        im = zeros(len(x))
        re = zeros(len(x))
        xx = x*x
        p = 2*(x[0]-x[1])/pi
        for i in range (0, len(x)):
            if x[i] > res:
                im[i] = (amp/x[i]**2)*(x[i]-res)**0.5        
        for i in range (0, len(x)):
            mask = x !=x[i]
            re[i] = sum(x[mask]*im[mask]/(xx[mask]-x[i]*x[i]))
        re = re*p+1
        y = re+1j*im
        return y 


    
    
