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
        Ta = 4*subs*(2.6544e-3)**2/(U*U.conjugate())
        Tb = (4*1.48)/(1+1.48)**2
        return real(Ta*Tb)  

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

    def d_coarse(self, x, p):
        L = self.L
        d = self.d
        u = []
        v = []
        w = []
        check1=[]
        check2 = []
        a = int(d-(d*0.2))
        b = int(d+(d*0.2))
        c = 50
        r = ((b-a)/c)
        
        r = int(r)
        
        
        for i in range (a, b, r):
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
            check1.append(len(n)-len(p))
            check2.append(n[0]*p[0]/(sqrt((p[0]*n[0])**2)))

        for j in range (0, len(u)):
            if check1[j] == 0 and check2[j]>0:
                w.append(v[j])

        return u[v.index(min(w))]
        

    def fit(self, x, T):
        pdata = self.peak_pick(x, T)
        d= self.d_coarse(x, T, pdata)
        return d
    
    def prefit(self, C, d):
        self.d = d
        L = self.L
        l = []
        D = []
        for i in range (0, 5):
            x = linspace(400+i*10, 800+i*10, 50)
            C = Calcs(x, 1.48, L2, d)
            T = C.matrix(x)        
            p = C.peak_pick(x, T)
            d= self.d_coarse(x, p)
            C3 = Calcs(x, 1.48, L1, d)
            A = C3.matrix(x)
            sum = 0
            for j in range(0, len(T), 10):
                sum += sqrt((T[i]-A[i])**2)
            l.append(sum)
            #plot(x, A)
            D.append(d)
            #print D[i], l[i]

        return D[l.index(min(l))]

    def d_fine(self, C, k):
        self.index = 0
        self.k = k
        d = self.dval()
        result, fx, conv_flag, nfe, res = nelmin.minimize(self.func2, [d])
        return result
  
    def p_fit(self, x, L):
        self.fitindex = 0
        p = L.group()
        print self.dval()
        
        
        
        for i in range(0,3):
            result, fx, conv_flag, nfe, res = nelmin.minimize(self.func, p)
            self.p = result
              
        return self.p

    def func(self, p):
        self.fitindex += 1
        d = self.dval()
        L = Model(p[0],p[1], p[2], p[3], p[4], p[5], p[6], p[7])
        C = Calcs(x, 1.48, L, d)

        sum = 0
        A = C.matrix(x)
        for i in range (0, len(x)):
            sum += sqrt((T[i]-A[i])**2)
            #print self.fitindex, sum
        return sum

    def func2(self, d):
        self.index += 1
        k = self.k
  
        if self.index >200:
            sum = 0
            return sum
        x = linspace(400, 800, 50)
        C = Calcs(x, 1.48, L1, d)
        C2 = Calcs(x, 1.48, L2, k)
        T = C2.matrix(x)
        A = C.matrix(x)
        sum = 0
        for i in range (0, len(x)):
            sum += sqrt((T[i]-A[i])**2)
        return sum
        
        
  
