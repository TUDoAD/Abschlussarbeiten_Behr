# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 09:23:25 2022

@author: Alexander Behr
"""
##
# Gets all words from a trained Word2Vec model and searches them in an existing
# ontology. Existing classes in the ontologies then get -based on the Word2Vec
# model the top X words assigned as children of the existing class.
##

## ToDo: Danach vllt. noch ein Check, wie viele der ursprünglichen Keys jetzt 
#        in der Ontologie gelandet sind?

from owlready2 import *
import LocalOntologies
import OntoClassSearcher
import re
import json
import types

from gensim.models import Word2Vec
import clustering
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd


model_name = 'methanation_only_text_mc10'
onto_name = 'Allotrope_OWL'

[class_dict, desc_dict] = OntoClassSearcher.onto_loader([onto_name])
Onto_World = owlready2.World()
onto_local = Onto_World.get_ontology('./ontologies/' + onto_name + '.owl').load()
class_list = (onto_local.classes())

labels_to_classes_dict = {i.prefLabel[0] : i for i in list(Onto_World.classes())}

##
#   conceptList = Liste mit Konzepten aus MC = 10, die auch in AFO drin sind?
##

model_test = Word2Vec.load('./models/' + model_name)

conceptList = model_test.wv.index_to_key

resDict = {}
for loaded_onto in desc_dict:
    summary = []
    description_set =  list(desc_dict[loaded_onto].keys())
    for i in description_set: # comparison of labels
        try:
            r = re.compile(str("[a-zA-Z0-9]*^" + i + "$"),re.IGNORECASE)
            newlist = list(filter(r.match, conceptList))
            if newlist: # entry found
                summary.append(newlist)
        except:
            print("Passed '{}', Ontology: {}".format(i,loaded_onto))
    resDict[loaded_onto] = summary

with open('FoundClasses' + model_name + '.json', 'w') as jsonfile:
    json.dump(resDict, jsonfile)
    
# List of classes in Vectorspace and 
# current selected ontology (onto_local) = resDict[onto_name]

for concept in resDict[onto_name]:
    # iterates through classes of resDict and temp_class = class of the 
    # onto_name ontology with same label
    temp_class = labels_to_classes_dict[concept[0]]  
    model_test.wv.similar_by_word[concept[0]]
    #temp_class.new_class("")
    '''
    defstring = ''.join(desc_dict[loaded_onto][concept[0]]) if desc_dict[loaded_onto][concept[0]] != concept[0] else "" 
    
    if defstring:
        comment_string =  defstring + "\nFound by [AB] in [" + loaded_onto + "]"
    else:
        comment_string = "[AB] Class with same label also contained in [{}]".format(loaded_onto)
    #print("{}: {}\n".format(concept[0],comment_string))
    temp_class.comment.append(comment_string)
    '''
    # onto_local.search_one(prefLabel = 'tensor datum') gibt die Klasse zum PrefLabel aus
    #
onto_local.save(file = './' + onto_name + '_ext_' + model_name + '.owl') 
