from pylab import *
import matplotlib
from matplotlib.font_manager import FontProperties
import math

def open_files():
    exp = 'rawoutput.txt'
    fit = 'fitoutput.txt'
    Noutput = 'Noutput.txt'
    
    xexp = loadtxt(exp, unpack = True, usecols=[0])
    yexp = loadtxt(exp, unpack = True, usecols=[1])
    xfit = loadtxt(fit, unpack = True, usecols=[0])
    yfit = loadtxt(fit, unpack = True, usecols=[1])
    N = loadtxt(Noutput, unpack = True, usecols = [1])
    K = loadtxt(Noutput, unpack = True, usecols = [2])
    return xexp, yexp, xfit, yfit, N, K

def plot(xexp, yexp, xfit, yfit, N, K):
    fig = figure(figsize=(9, 6))
    ax = fig.add_subplot(111)
    ax.tick_params(axis='both', which='major', labelsize = 18)
    inset = axes([0.25,0.2,0.30,0.45])
    inset.tick_params(axis='both', which='major', labelsize = 16)
    xbg = xfit[:30]
    ybg = yfit[:30]
    xint = linspace(xfit[38], xfit[-1], 100)
    yint = interp(xint, xfit, yfit)
    #ax.plot(xfit, yfit, 'o', markersize = 8, alpha = 0.5)
    ax.plot(xbg, ybg, 'o', color = 'blue', markersize = 8, alpha = 0.75)
    l1, = ax.plot(xint, yint, 'o', color = 'blue', markersize = 8, alpha = 0.75)
    l2, = ax.plot(xexp, yexp, '-', linewidth = 2, color = 'red')
    ax.set_xlim(250, 2400)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Wavelength, $\lambda$ (nm)', fontsize = 18)
    ax.set_ylabel('$T$ $(\%)$ ', fontsize = 18)
    leg1 = ax.legend((l1, l2), ('Experiment', 'Model fit'), 'upper right')
    leg1.get_frame().set_alpha(0.0)
    l3, =inset.plot(xfit, N, '-', color = 'blue')
    l4, =inset.plot(xfit, -K, '-', color = 'red')
    inset.set_xlim(300, 2400)
    inset.set_ylim(-0.2, 2.2)
    inset.set_xlabel('$\lambda$ (nm)', fontsize =16)
    inset.set_ylabel('$n$, $\kappa$', fontsize = 16)
    leg2 = inset.legend((l3, l4), ('$n$', '$\kappa$'), 'upper right')
    leg2.get_frame().set_alpha(0.0)

def plotalpha(xexp, T, x, k):
    fig = figure(figsize=(9, 6))
    eV = (6.63e-34*3e8)/(x*1e-9*1.602e-19)
    eV3 = (6.63e-34*3e8)/(xexp*1e-9*1.602e-19)
    ax = fig.add_subplot(121)
    alpha2 = -((4*pi*k)/(x*1e-7))
    ax.plot(eV, alpha2, '-o')
    ax.set_xlim(3.0, 4.0)
    #ax.set_ylim(0, 1.2e10)
    alpha3 = (-log((T/100))/453e-7*eV3)/2.0
    ax.plot(eV3, alpha3, 'o')
 
    

if __name__ == "__main__":
    a, b, c, d, e, f = open_files()
    plot(a, b, c, d, e, f)
    plotalpha(c, d, c,f)
    show()
    
