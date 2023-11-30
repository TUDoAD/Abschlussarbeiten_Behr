# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 17:11:20 2023

@author: smdicher
"""

#reasoning
from owlready2 import *
JAVA_EXE='C:\Program Files\Java\jdk-11.0.17\bin\java.exe'

with onto:
    sync_reasoner()
onto.save('./ontologies/{}_inf.owl'.format(onto_name))