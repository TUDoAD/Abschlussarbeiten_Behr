# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:36:09 2023

@author: smdicher
"""

from owlready2 import *
def
new_world = owlready2.World()
onto_test = new_world.get_ontology("./ontology_sniplet/{}_classes.owl".format(onto_name)).load()
new_world2= owlready2.World()
onto =new_world2.get_ontology("./ontologies/{}.owl".format(onto_name)).load()
a = list(onto_test.classes().label)
