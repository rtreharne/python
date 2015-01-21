from models1 import *
from math import *
from pylab import *
import cmath as c
import nelmin

class Calcs:
    def __init__(self, x, subs, L, d):
        self.subs = subs
        self.L = L
        self.e = L.background(x) + L.ext_drude(x) + L.direct(x)
        self.d = d

    def dval(self):
        x = self.d
        return x

    def eval(self):
        e = self.e
        return e
        
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
        Tb = (4*self.subs)/(1+self.subs)**2
        T = Ta*Tb*100
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

    def d_coarse(self, x, xmin, xmax, L, p):
        
        d = self.dval()
        u = []
        v = []
        w = []
        check1=[]
        check2 = []
        a = int(d-(d*0.002))
        b = int(d+(d*0.002))
        c = 50
        r = ((b-a)/c)
        r = int(r)+1
        
        for i in range (a, b, r):
            C = Calcs(x, self.subs, L, i)
            A = C.matrix(x)
            x1 = x[xmin:xmax]
            A1 = A[xmin:xmax]
            
            #n = C.peak_pick(x, A)
            n = C.peak_pick(x1,A1)

            if len(n) == 0:
                return d
            
                        
            suma = 0
            for j in range (0, len(p)):
                suma += sqrt((p[j])**2)
            sumb = 0
            for k in range (0, len(n)):
                sumb += sqrt((n[k])**2)
            s = sqrt((suma-sumb)**2)          
            u.append(i)
            v.append(s)
            check1.append(len(n)-len(p))
            check2.append(n[0]*p[0]/(sqrt((p[0]*n[0])**2)))
            
        for j in range (0, len(u)):
            if check1[j] == 0 and check2[j]>0:
                w.append(v[j])

        if len(w) == 0:
            #print i, 'no dice'
            return d
        else:
            #print i, 'check'
            return u[v.index(min(w))]
        

    def fit(self, x, T):
        pdata = self.peak_pick(x, T)
        d= self.d_coarse(x, T, pdata)
        return d
    
    def prefit(self, x, y, L, ax):
        d = self.dval()
        C = Calcs(x, self.subs, L, self.dval())
        A = C.matrix(x)
        p = C.peak_pick(x, A)
        l = []
        D = []
        for i in range (0, 5):
            for position, item in enumerate(x):
                if item == min(x, key=lambda x:abs(x-(300+i*20))):
                    xmin = position
            for position, item in enumerate(x):
                if item == min(x, key=lambda x:abs(x-(800+i*20))):
                    xmax = position
       
            x1 = x[xmin:xmax]
            y1 = y[xmin:xmax]
            A1 = A[xmin:xmax]
            p = self.peak_pick(x1, y1)
            
            d= self.d_coarse(x, xmin, xmax, L, p)
            
            
            C = Calcs(x, self.subs, L, d)
            A = C.matrix(x)
            sum = 0
            for j in range(xmin, xmax, 10):
                sum += sqrt((y[j]-A[j])**2)
            l.append(sum)
            #plot(x, A)
            D.append(d)
        if len(l) == 0:
            print 'cannot fit'
        else:
            d = D[l.index(min(l))]
        
       
        d = self.d_fine(x, y, L, xmin, xmax, d)
        return d

    def d_fine(self, x, y, L, xmin, xmax, d):
        self.x = x
        self.y = y
        self.L = L
        self.xmin = xmin
        self.xmax = xmax
        self.index = 0
        result, fx, conv_flag, nfe, res = nelmin.minimize(self.func2, [d])
        return result
  
    def p_fit(self, x, y, L):
        self.x = x
        self.y = y
        self.fitindex = 0
        p = L.group()
        
        for i in range(0,2):
            result, fx, conv_flag, nfe, res = nelmin.minimize(self.func, p)
            self.p = result
              
        return self.p

    def func(self, p):
        x = self.x
        y = self.y
        self.fitindex += 1
        d = self.dval()
        L = Model(p[0],p[1], p[2], p[3], p[4], p[5], p[6], p[7])
        C = Calcs(x, self.subs, L, d)

        for i in range (0, len(p)):
            p[i] = sqrt(p[i]**2)
        p[4] = 2*p[5]
        sum = 0
        A = C.matrix(x)
        for i in range (0, len(x)):
            sum += sqrt((y[i]-A[i])**2)/len(x)
        #print sum
        return sum

    def func2(self, d):
        self.index += 1
        C = Calcs(self.x, self.subs, self.L, d)
        A = C.matrix(self.x)
        if self.index >50:
            sum = 0
            return sum
        
        sum = 0
        for i in range (self.xmin, self.xmax):
            sum += sqrt((self.y[i]-A[i])**2)
        
        return sum
        
        
  
