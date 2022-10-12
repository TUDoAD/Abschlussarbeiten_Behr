# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 13:43:11 2022

@author: User
"""
from owlready2 import *

onto_name = 'Allotrope_OWL'
Onto_World = owlready2.World()
onto_local = Onto_World.get_ontology('./ontologies/' + onto_name + '.owl').load()


with onto_local:
    class Test('reactor'):
        pass
    
    
onto_local.save(file = './testtest.owl') 
onto_local.search_one(prefLabel = 'vector double datum')

wordlist = ['reactor', model_test.wv.similar_by_word('reactor')[0][0], model_test.wv.similar_by_word('reactor')[0][0]]
