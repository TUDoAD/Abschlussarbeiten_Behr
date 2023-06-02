# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 17:49:34 2022

@author: 49157
"""
# Load an EnzymeML document from OMEX

import pyenzyme as pe
enzmldoc = pe.EnzymeMLDocument.fromFile("./Experiment_ohne_Reaktionen.omex")
enzmldoc.printDocument(measurements=True)

