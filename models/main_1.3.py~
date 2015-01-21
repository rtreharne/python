from models1 import *
from math import *
from pylab import *
import cmath as c
import nelmin

"""nelmin fit of parameters (except thickness)"""

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

def fit(x,L,C):
    fit.fitindex = 0
    p = L.group()
    
    for i in range (0,4):
        result, fx, conv_flag, nfe, res = nelmin.minimize(func, p)
        p = result
    return p

def func(p):
    fit.fitindex += 1    
    L = Model(p[0],p[1], p[2], p[3], p[4], p[5], p[6], p[7])
    C = Calcs(x, 1.48, L, 200)
    
    sum = 0
    A = C.matrix(x)
    for i in range (0, len(x)):
        sum += sqrt((T[i]-A[i])**2)
        print fit.fitindex, sum

    return sum
    
    
    
x = linspace(250,2500, 250)
L1 = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
L2 = Model(2.61, 1.01, 1.0, 1.0, 0.5, 0.01, 3.8, 8)
C1 = Calcs(x, 1.48, L1, 200)
C2 = Calcs(x, 1.48, L2, 200)
T = C2.matrix(x)
p = fit(x,L1,C1)
print p

L3 = Model(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])
C3 = Calcs(x, 1.48, L3, 200)

#plot(x, C1.matrix(x))
plot(x, C2.matrix(x), 'o')
plot(x, C3.matrix(x), '--')
#plot(x, C1.matrix(x))


show()
