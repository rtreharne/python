
from pylab import *
from numpy import *
import numpy as np
from scipy.optimize import minimize

def rosen(x):
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)

x0=np.array([1.3, 1.2, 0.8, 1.9, 1.2])
res = minimize(rosen, x0, method='nelder-mead', options={'xtol': 1e-8, 'disp': True})

print res.x

n=30
x = linspace(-1,1,n)
y = rosen

xx = linspace(-1,1,n)
plot (x,y,'bo')

show()
