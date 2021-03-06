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

    def peak_pick(self, x, T):
        dT = []
        ddT = []
        dx = []
        peaks = []
        for i in range (1, len(x)):
            dT.append(T[i-1]-T[i])
            dx.append(x[i-1])
            
        for i in range (1, len(dx)):
            ddT.append(dT[i-1]-dT[i])           
            if (dT[i-1]*dT[i]) < 0:
                if (ddT[i-1]) <0 :
                    peaks.append((dx[i-1]+dx[i])/2)
                elif ddT[i-1] > 0:
                    peaks.append(-(dx[i-1]+dx[i])/2)
   
        return peaks

 

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

def fit_d(x, C):
    fit_d.fitindex = 0
    d = C.dval()
    d = d_coarse()
    p = [d]
    #result, fx, conv_flag, nfe, res = nelmin.minimize(d_fine, p)
    #return result

def d_coarse():
    L = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
    for i in range (0,100):
        d = i*10
        C = Calcs(x, 1.48, L, d)
        A = C.matrix(x)
        sum = len(peaks) - len(C.peak_pick(x, A))
        if sum == 0:
            return d

def d_fine(p):
    fit_d.fitindex += 1
    L = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
    C = Calcs(x, 1.48, L, p[0])
    A = C.matrix(x)
    p = C.peak_pick(x, A)
    sum = 0
    for i in range (0, len(p)):
        sum += peaks[i] - p[i]
    print fit_d.fitindex, sum
    return sum
        
    
     
x = linspace(250,2500, 500)
L1 = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
L2 = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
C1 = Calcs(x, 1.48, L1, 500)
C2 = Calcs(x, 1.48, L2, 345.9)
T = C2.matrix(x)
peaks = C2.peak_pick(x, T)
#d = fit_d(x, C1)
y = []
s = []
for i in range (330, 500, 10):
    y.append(i)    
    C = Calcs(x, 1.48, L2, i)
    A = C.matrix(x)
    p = C1.peak_pick(x, A)
    sum = 0
    for j in range (0, len(p)):
        sum += (peaks[j] - p[j])**2
    s.append(sum)

plot(y,s)








show()
