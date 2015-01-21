from pylab import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata

data = 'output'
x = loadtxt(data, unpack=True, usecols=[0])
y = loadtxt(data, unpack=True, usecols=[1])
z = loadtxt(data, unpack=True, usecols=[3])

z = ((z*8065.8)*2*pi*3e10)**2*0.44*8.85e-12*9.11e-31/(1e6*1.602e-19**2)

print min(z), max(z)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


fig = plt.figure()
ax = fig.gca(projection='3d')

xi = np.linspace(min(x), max(x))
yi = np.linspace(min(y), max(y))

X, Y = np.meshgrid(xi, yi)
Z = griddata(x, y, z, X, Y)

surf = ax.plot_surface(X, Y, Z, rstride=2, cstride=2, cmap=cm.summer,
                       linewidth=0.0, antialiased=True)

ax.set_zlim3d(np.min(Z), np.max(Z))
fig.colorbar(surf)

plt.show()
