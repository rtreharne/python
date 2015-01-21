#!/usr/bin/env python

#plot of 2D data from two column .csv file

from pylab import *
import numpy as np
import matplotlib.pyplot as plt
import csv
import re
import sys

filename = sys.argv[1]
linestyle = sys.argv[2]


# Check to see if first row in .csv file contains alpha characters
afile = open(filename, 'r+')
csvreader = csv.reader(afile)
row = csvreader.next()
lst = list(row[0])
header =  re.sub('  +', ',', row[0])
header = header.split(',')

skip = 0

for i in range (0,len(lst)):
  if lst[i].isalpha() == True:
    skip = 1

fname = 'data.csv'

x = loadtxt(fname, unpack = True, usecols = [0], skiprows = skip)
y = loadtxt(fname, unpack = True, usecols = [1], skiprows = skip) 

plot(x,y, linestyle, color='red')
xlabel(header[0])
ylabel(header[1])

show()


