from models1 import *
from math import *
from pylab import *
import cmath as c
import nelmin

class Calcs:
    def __init__(self, x, subs, L, d):
        self.subs = subs*(x/x)
        self.L = L
        self.e = L.background(x) + L.ext_drude(x) + L.direct(x)
        self.d = d

    def dval(self):
        x = self.d
        return x
        
    def matrix(self, x):
        L = self.L
        e = self.e
        d = self.d
        subs = self.subs
        I = ([subs/subs], [2.6544e-3])
        N = L.eton(e)
        Y = N*2.6544e-3
        delta = 2*pi*N*d/x
        M = array([[cos(delta), 1j*sin(delta)/Y], [1j*Y*sin(delta), cos(delta)]])
        
        B = M[0][0]*I[0][0] + M[0][1]*I[1][0]
        C = M[1][0]*I[0][0] + M[1][1]*I[1][0]

        U = (subs*2.6544e-3*B)+C
        T = 4*subs*(2.6544e-3)**2/(U*U.conjugate())
        return real(T)

def fit(L, C):
    
    param = L.group()
    param.append(C.dval())
    result, fx, conv_flag, nfe, res = nelmin.minimize(func, param)
    return result

def func(p):
    L1 = Model(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])
    C1 = Calcs(x, 1.48, L1, p[8])
    sum = 0
    
    A = C1.matrix(x)
    for i in range (0, len(x)):
        sum += sqrt((T[i]-A[i])**2)
    
    print  sum        
    return sum
    
    

x = linspace(250,2500, 1000)
L1 = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
L2 = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
C1 = Calcs(x, 1.48, L1, 500)
C2 = Calcs(x, 1.48, L2, 480)
T = C2.matrix(x)
#print fit(L1,C1)

plot(x, C1.matrix(x))
plot(x, C2.matrix(x))
#plot(x, -imag(N))


show()
