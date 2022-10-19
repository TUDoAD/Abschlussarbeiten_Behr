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


'''
PICKLES
'''

## Create Pickle
import pickle
  
# Create a variable
myvar = [{'This': 'is', 'Example': 2}, 'of',
         'serialisation', ['using', 'pickle']]
  
# Open a file and use dump()
with open('file.pkl', 'wb') as file:
      
    # A new file will be created
    pickle.dump(myvar, file)
    
## Load Pickle
    
import pickle
  
# Open the file in binary mode
with open('file.pkl', 'rb') as file:
      
    # Call load method to deserialze
    myvar = pickle.load(file)
  
    print(myvar)