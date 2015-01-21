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

    def d_coarse(self, x, T, p):
        L = self.L
        u = []
        v = []
        a = 100
        b = 550
        c = 50
        d = (b-a)/c    
        
        for i in range (a, b, d):
            C1 = Calcs(x, 1.48, L1, i)
            
            A = C1.matrix(x)
            
            n = C1.peak_pick(x, A)
            suma = 0
            for j in range (0, len(p)):
                suma += sqrt((p[j])**2)
            sumb = 0
            for k in range (0, len(n)):
                sumb += sqrt((n[k])**2)
            #print C1.dval(), sqrt((suma-sumb)**2), len(p), len(n), n[0]/sqrt((n[0])**2), p[0]/sqrt((p[0])**2)
            s = sqrt((suma-sumb)**2)          
            u.append(i)
            v.append(s)
        print u[v.index(min(v))]     
        return n, u, v

    def fit(self, x, T):
        pdata = self.peak_pick(x, T)
        n, u, v= self.d_coarse(x, T, pdata)
        return n, u, v

     
x = linspace(400, 800, 500)
L1 = Model(2.75, 1.4, 1.0, 1.0, 0.2, 0.05, 3.6, 10)
L2 = Model(2.5, 1.0, 1.0, 1.0, 0.2, 0.05, 3.6, 10)
C2 = Calcs(x, 1.48, L2, 121)
T = C2.matrix(x)
pdata = C2.peak_pick(x, T)
C1 = Calcs(x, 1.48, L1, 121)
n, u, v = C1.fit(x, T)
C3 = Calcs(x, 1.48, L1, 397)
A = C3.matrix(x)
x = linspace(250, 2500, 500)
C2 = Calcs(x, 1.48, L2, 121)
C3 = Calcs(x, 1.48, L1, 127)
T = C2.matrix(x)
A = C3.matrix(x)
plot(x, T)
plot(x, A, '--')



 



show()
