# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 18:04:51 2022

@author: 49157
"""
import pyenzyme as pe

# load an existing EnzymeML.xlsm document
# Attention: pH value not detected as a float !
# Output: Titel, Reactants, Proteins, Complexes and Reactions
enzmldoc = pe.EnzymeMLDocument.fromTemplate("./EnzymeML_Template_18-8-2021_ohne pH.xlsm")

enzmldoc.printDocument(measurements=True)