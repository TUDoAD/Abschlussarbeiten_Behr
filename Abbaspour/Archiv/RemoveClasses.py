# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:40:11 2023

@author: 49157
"""
# load an existing ontology and remove classes 

import owlready2
import types
from owlready2 import *

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

local_world = owlready2.World()
onto = local_world.get_ontology("./py-merge-ontos.owl").load()

print("showing classes:")
print( list(onto.classes()) )
print()

destroy_entity(onto.search_one(iri='*Still'))

onto.save("removeClasses.owl")