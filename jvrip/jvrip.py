"""Take j-v curve from lab computer and extract 
cell parameters (Jsc, FF, Voc, eff)"""

import sys
import numpy as np
from pylab import *
import matplotlib
import glob
import math
import tkFileDialog
import Tkinter
import os
import re
from matplotlib import cm
from matplotlib.mlab import griddata
from mpl_toolkits.mplot3d import axes3d
from operator import itemgetter


global area, n
area = 2.4e-4
n = 1001
def create_plot(x, y):
    fig = figure()
    ax = fig.add_subplot(111)
    ax.plot(x,y, 'o')

def find_folder():
    foldername = tkFileDialog.askdirectory()
    #foldername = "/home/treharne/Documents/python_projects/jv/131122/light"
    return foldername

def find_files(foldername):
    filelist = glob.glob("%s/*.txt" % foldername)
    return filelist 

def open_file(filename):
    x = np.loadtxt(filename, unpack = True, usecols=[0])
    y = np.loadtxt(filename, unpack = True, usecols=[1])/area
    return x, y

def extract_jsc(x, y):
    xvals = np.linspace(min(x), max(x),n)
    yinterp = np.interp(xvals, x, y)
    index = min(list(xvals), key=lambda x:abs(x))
    jsc = yinterp[list(xvals).index(index)]
    return jsc

def extract_voc(x, y):
    yvals = np.linspace(min(y), max(y), n)
    xinterp = np.interp(yvals, y, x)
    index = min(list(yvals), key=lambda x:abs(x))
    voc = xinterp[list(yvals).index(index)]
    return voc

def max_power(x, y):
    xvals = np.linspace(min(x), max(x),n)
    yinterp = np.interp(xvals, x, y)
    power = np.sqrt((xvals*yinterp)**2)
    lst1 = list(power[:int(len(power)/2)])
    lst2 = list(power[int(len(power)/2)+100:])
    p1 = lst1.index(min(lst1))
    p2 = lst2.index(min(lst2))+p1
    if p1 == p2:
        jmp = 0
        vmp = 0
        return jmp, vmp
    else:
        index = list(power).index(max(power[p1:p2]))
        jmp = yinterp[index]
        vmp = xvals[index]
        return jmp, vmp

def extract_ff(x, y):
    jmp, vmp = max_power(x, y)
    jsc = extract_jsc(x, y)
    voc = extract_voc(x, y)
    ff = (jmp*vmp)/(jsc*voc)*100
    return ff

def extract_eff(x, y, i):
    ff = extract_ff(x, y)
    jsc = extract_jsc(x, y)
    voc = extract_voc(x, y)
    eff = np.sqrt(((jsc*1e-3*voc*ff)/100e-3)**2)
    return i, eff, jsc, voc, ff

def histogram(data, foldername, col):
    name = os.path.basename(foldername)
    fig = figure()
    ax = fig.add_subplot(111)
    lst = []
    for i in range (len(data)):
        lst.append(data[i][1])
    mu = mean(lst)
    sigma = std(lst)
    contacts = len(lst)
    #bins = arange(floor(min(lst)), ceil(max(lst)), 0.1)
    bins = arange(5, 15,0.5)
    plot1 = ax.hist(lst, bins, histtype = 'stepfilled', color=col)
    ax.set_xlim(5, 15)
    ax.set_title("Cell Histogram: %s" % name)
    ax.set_xlabel("$\eta$ %", fontsize = 16)
    ax.set_ylabel("Number of Cells", fontsize = 16)
    s = '$\eta = $ {0:.2f} % \n$\sigma = $ {1:.2f} %\n{2} cells \ncell size: 25 mm$^2$'.format((mu), (sigma), (contacts))
    ax.text(5, 5, s , fontsize = 14)
    ax.set_ylim(0, 9)
   

    return ax, plot1

def rip():
    foldername = find_folder()
    filelist = find_files(foldername)
    data = []
    for i in filelist:
        x, y = open_file(i)
        data.append(extract_eff(x, y, i))  
    return data, foldername, filelist

def format_folder(foldername):
    name = os.path.basename(foldername)    
    return name

def contour(data, foldername):
    x = []
    y = []
    z = []
    eff = []
    r = re.compile("(?:-|^)[^-]*")
    name = os.path.basename(foldername)
    filelist = find_files(name)
    filelist = glob.glob("%s/*.txt" % foldername)
    for i in range (0, len(filelist)):
       filelist[i] = os.path.splitext(filelist[i])[0]
       filelist[i] = os.path.basename(filelist[i])
       x.append(int(r.findall(filelist[i])[0]))
       y.append((int(r.findall(filelist[i])[1])-1)*-1)
       z.append(data[i][1])
    
    
    
        
    array = sort(x,y,z)
    #print array
    #print len(data) 
    #x, y, z = smooth(array)
    for i in range (0,len(z)):
        print array[i][0], array[i][1], array[i][2]
    x,y,z = restrict(x,y,z)
    fig = figure()
    ax = fig.gca(projection='3d')
    fig2 = figure()
    fig2.patch.set_alpha(0.0)
    
    ax2 = fig2.add_subplot(111)
    ax2.set_aspect('equal')
    ax2.patch.set_alpha(0.0)
    #ax.set_aspect('equal')
    xi = linspace(1, 6,200)
    yi = linspace(1, 12,200)
    X, Y = meshgrid(xi, yi)
    Z = griddata(x, y, z, X, Y)
    plot = ax.contour(X, Y, Z)
    cset =  ax.contourf(X, Y, Z, zdir='z', offset=min(z), cmap=cm.hot)
    plot = ax.plot_surface(X, Y, Z, rstride = 3, cstride = 3, alpha = 0.5, linewidth = 0.1,)
    ax.set_title('contour plot: {0}'.format(name))
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('$\eta$ ($\%$)')
    ax.set_xlim(1, 12)
    ax.set_ylim(1, 12)
    ax.set_zlim(min(z),max(z))
    ax2.set_ylim(1,12)
    ax2.set_xlim(1,6)
    
    
    lvls = arange(8.5,14.5,0.5)
    #plot2 = ax2.contour(X,Y,Z, colors = 'k', levels = lvls)
    plot2 = ax2.contourf(X, Y,Z, zdir='z', cmap=cm.hot, levels = lvls, alpha = 0.9)
    cbar = colorbar(plot2, ticks = lvls)
    cbar.set_label("Efficiency, $\eta$ (%)")
    
    eqex = arange(2,12,1)
    eqey = []
    for i in range (0, len(eqex)):
        eqey.append(3)
        
    plot2 = ax2.plot(eqex, eqey, '--o')
    
    
    return plot2

def restrict(x, y, z):
    x2 = []
    y2 = []
    z2 = []
    
    for i in range (0, len(z)):
        if (z[i]>6.5 and z[i]<15):
            x2.append(x[i])
            y2.append(y[i])
            z2.append(z[i])
            
    return x2, y2, z2
    
def smooth(array):
    temp=[]
    temp2=[]
    x2 = []
    y2 = []
    z2 = []
    deg = 1
    index = 0
    for k in range (0, len(array)):
        for i in range (-deg, (deg+1)):
            for j in range(-deg*12, (deg+1)*12,12):
                if (i+j+k)<len(array):
                    temp.append(array[i+j+k])
    
        x = temp[4][0]
        y = temp[4][1]
        del temp[4]
    
    
    
        for l in range (0, len(temp)):
            if ((x-temp[l][0])**2<deg**2+1) and ((y-temp[l][1])**2<deg**2+1):
                temp2.append(temp[l][2])
        
        #print mean(temp2)
        if array[k][2]>mean(temp2)-10*std(temp2):
            x2.append(array[k][0])
            y2.append(array[k][1])
            z2.append(array[k][2])
       # else:
           # x2.append(array[k][0])
           # y2.append(array[k][1])
           #z2.append(mean(temp2))
            
            index += 1
        temp=[]
        temp2=[]
    return x2,y2,z2
    
def sort(x,y,z):
    array = []
    for i in range (0, len(z)):
        array.append((x[i], y[i], z[i]))
    array = sorted(array,key=itemgetter(0,1))
    return array



if __name__ == "__main__":
    data, foldername, filelist = rip()
    #eff = []
    #print foldername
    ax, plot1= histogram(data, foldername, col = 'blue') 
    plot4 = contour(data, foldername)
    show()
    
