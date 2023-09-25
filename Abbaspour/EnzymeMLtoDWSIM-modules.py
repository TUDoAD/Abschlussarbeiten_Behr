# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 13:58:00 2023

@author: Alexander Behr
"""


####################################################
## Ontology Manipulation
####################################################

from owlready2 import *
import pyenzyme as pe
from pyenzyme import EnzymeMLDocument, EnzymeReaction, Complex, Reactant, Protein, Creator
from pyenzyme.enzymeml.models import KineticModel, KineticParameter


## 
# To make sure, owlready2 is able to use HermiT for reasoning, configure the path to the java interpreter
# e.g.:
# owlready2.JAVA_EXE = "C://Users//..//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"
##

## USER INPUT
# load base ontology
onto_world = owlready2.World()
onto = onto_world.get_ontology("./ontologies/BaseOnto.owl").load()

# Ohne diese Definition wird die Ontologie für set_relations(test_dict, onto) nicht gefunden
BaseOnto = onto

## USER INPUT
# Load EnzymeML Excel-file
# Make sure, Macros are turned OFF, else the pH-value might not be parsed correctly
enzmldoc = pe.EnzymeMLDocument.fromTemplate("./ELNs/EnzymeML_Template_18-8-2021_KR.xlsm")


"""
# visualize first measurement
fig = enzmldoc.visualize(use_names=True, trendline=True, measurement_ids=["m0"])
"""
