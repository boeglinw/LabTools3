# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 14:36:37 2016

@author: boeglinw
"""

file = 'LT/plotting.py'

d = open(file).readlines()

o = open('xx.py','w')
for l in d:
    o.write(l.replace('\t',8*' '))
o.close()
