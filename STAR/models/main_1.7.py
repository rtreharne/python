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
       
        #d = self.dval()
        #A = self.matrix(x)
        #pmodel = self.peak_pick(x, A)
        #find the wavelength ranges over which T and A have the
        #same number of maxima
        #print p[0], p[-1]
        x = linspace(p[0], p[-1], 500)
        a = 0
        b = 1000
        d = 30
        c = (b-a)/d
        for l in range (0, 1):
            u = []
            v = []
            for i in range (a, b, c):
                sum = 0
                u.append(i)
                C = Calcs(x, 1.48, L, i)
                A = C.matrix(x)
                pmodel = C.peak_pick(x, A)
                if len(pmodel)<len(p):
                    s = len(pmodel)
                else:
                    s = len(p)
            
                for j in range (0, s):
                    sum =+ ((p[j]-pmodel[j]))**2
                v.append(sum)
            m = v.index(min(v))
            
            
            if m == 0:
                a == u[m]
            else:
                a = u[m-1]
            if m == len(v)-1:
                b = u[m]
            else:
                b = u[m+1]
            
            if  (b-a)/d< 1:
                return b
                break
            c = (b-a)/d
     
        return b, u, v

    def fit(self, x, T, L1):
        pdata = self.peak_pick(x, T)
        d, u, v = self.d_coarse(x, T, pdata)
        return d, u, v

     
x = linspace(250,2500, 500)
L1 = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)
L2 = Model(2.75, 1.5, 1.0, 1.0, 0.2, 0.01, 3.2, 10)

#for i in range (300, 400, 10):
    #C2 = Calcs(x, 1.48, L2, i)
    #C1 = Calcs(x, 1.48, L1, 500)
    #T = C2.matrix(x)
    #d = C1.fit(x, T, L1)
    #C1 = Calcs(x, 1.48, L1, d)
    #A = C1.matrix(x)
    #d1 = C2.dval()
    #print d, d1, (sqrt((d1-d)**2)/d1)*100, len(C2.peak_pick(x, T)), len(C1.peak_pick(x, A))
#plot(x, T)
#plot(x, C1.matrix(x), '--')
C3 = Calcs(x, 1.48, L2, 500)
C4 = Calcs(x, 1.48, L1, 500)
T = C3.matrix(x)
d, u, v = C4.fit(x, T, L1)
C4 = Calcs(x, 1.48, L1, d)
A = C4.matrix(x)
#plot(x, T)
plot(u, v, 'o-')
 



show()
