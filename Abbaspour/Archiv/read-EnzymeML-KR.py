# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 18:28:27 2022

@author: 49157
"""

import pyenzyme as pe
from pyenzyme import EnzymeMLDocument, EnzymeReaction, Complex, Reactant, Protein, Creator
from pyenzyme.enzymeml.models import KineticModel, KineticParameter

# load an EnzymeML.xlsm document
# Attention: pH value not detected as a float !
# Even if the separators were set manually


# normal EnzymeML-Document
# enzmldoc = pe.EnzymeMLDocument.fromTemplate("./EnzymeML_Template_18-8-2021_KR - Kopie.xlsm")
# enzmldoc.printDocument(measurements=True)


# load EnzymeML without makros
enzmldoc = pe.EnzymeMLDocument.fromTemplate("./EnzymeML_Template_V2_KR_kinetic.xlsm")


# print measurements -> Output: Titel, Reactants, Proteins, Complexes and Reactions
enzmldoc.printDocument(measurements=True)


# Visualize all measurements and add trendline
fig = enzmldoc.visualize(use_names=True, trendline=True)

# Interactive visualisation are returned when interactive argumennt ist set to true
# enzmldoc.visualize(interactive=True, trendline=True, use_names=True)

# Visualize specific measurements
enzmldoc.visualize(interactive=False, use_names=True, trendline=True, measurement_ids=["m1"])

# Every entity of an EnzymeML document is stored in its corresponding
# dictionary. This example serves as a get-go solution to access all
# other objects
for reaction in enzmldoc.reaction_dict.values():
    print()
    educts = reaction.educts
    print(educts)
    
    print()
    products = reaction.products
    print(products)
    
    print()
    pH = reaction.ph
    print(pH)
    
    print()
    T = reaction.temperature
    T_u = reaction.temperature_unit
    print(T, T_u)
