from math import *
from pylab import *

class Model:   
    def nmtoev(self, x):
        y = (6.63e-34*3e8)/(x*1e-9*1.602e-19)
        return y

    def eton(self, x):
        n = ((sqrt(real(x)**2+imag(x)**2)+real(x))/2)**0.5
        k = ((sqrt(real(x)**2+imag(x)**2)-real(x))/2)**0.5
        N = n+1j*k
        return N
        

    def db(self, x, db):
        y = db*x/x
        return y

    def lorentz(self, x, res, amp, width):
        x = self.nmtoev(x)
        y = amp/(res**2-x**2-1j*width)
        return y

    def drude(self, x, pf, scatt):
        x = self.nmtoev(x)        
        y = - pf**2/(x**2+1j*scatt)
        return y

    def extended_drude(self, x, pf, cross, width, s_low, s_high):
        x = self.nmtoev(x)
        scatt = s_low - ((s_low-s_high)/pi)*(arctan((x - cross)/width)+pi/2)       
        y = -pf**2/(x**2+1j*scatt)
        return y

    def direct(self, x, res, amp):
        x = self.nmtoev(x)
        im = zeros(len(x))
        re = zeros(len(x))
        xx = x*x
        p = 2*(x[0]-x[1])/pi
        for i in range (len(x)):
            if x[i] > res:
                im[i] = (amp/x[i]**2)*(x[i]-res)**0.5        
        for i in range (len(x)):
            mask = x !=x[i]
            re[i] = sum(x[mask]*im[mask]/(xx[mask]-x[i]*x[i]))
        re = re*p+1
        y = re+1j*im
        return y 

L1 = Model()
x = linspace(250, 2500, 1000)
l1 = L1.direct(x, 3.2, 50)
l2 = L1.extended_drude(x, 1.3, 2.2, 1.0, 0.1, 0.01)
l3 = L1.db(x, 2.0)
l = l1+l2+l3
N = L1.eton(l)

plot(x, real(N), '--')
plot(x, imag(N), '--')
plot(x, real(l))
plot(x, imag(l))
#plot(x, real(l2))
#plot(x, real(l3), '--')



show()
    
    
