# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 11:55:11 2023

@author: Lucky Luciano
"""

dict2 = {}
list2 = [9.57, 1.0]
compoundscompoundflow = {"Water" : 9.57, 'Ethanol' : 1.0}

#for key in compoundscompoundflow:
 #   dict2[key] = 






















list3 = list(compoundscompoundflow.keys())

for key in list3:
    for value in list2:
        dict2[key] = value
        list2.remove(value)
        break