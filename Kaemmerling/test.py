# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 12:46:33 2022

@author: Lucky Luciano
"""

bla = {}
for i in range(5):
    if i != 0:
        bla["variable%s" % i] = i

print (bla)