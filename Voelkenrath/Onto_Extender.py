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
    # temp_class = labels_to_classes_dict[concept[0]]  
    temp_class = onto_local.search_one(prefLabel = concept[0])
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
    
'''
model_test.wv.similar_by_word('reactor')
Out[78]: 
[('bed', 0.9994844198226929),
 ('outlet', 0.9993471503257751),
 ('tube', 0.999320924282074),
 ('inlet', 0.9993012547492981),
 ('heat', 0.9992453455924988),
 ('temperature', 0.999235987663269),
 ('salt', 0.9992288947105408),
 ('ﬂow', 0.9992184638977051),
 ('pressure', 0.9992129802703857),
 ('feed', 0.9991992712020874)]

model_test.wv.similar_by_word('bed')
Out[79]: 
[('reactor', 0.9994844794273376),
 ('salt', 0.9994573593139648),
 ('parameter', 0.9994072318077087),
 ('tube', 0.999401330947876),
 ('time', 0.9993911385536194),
 ('temperature', 0.9993727803230286),
 ('coolant', 0.9993698000907898),
 ('drop', 0.999361515045166),
 ('mass', 0.9993523955345154),
 ('pressure', 0.9993463754653931)]

model_test.wv.similar_by_word('outlet')
Out[80]: 
[('inlet', 0.9996315836906433),
 ('feed', 0.9995215535163879),
 ('pressure', 0.9994890689849854),
 ('temperature', 0.999485194683075),
 ('gas', 0.9994626045227051),
 ('rate', 0.9994502663612366),
 ('composition', 0.999421238899231),
 ('flow', 0.9994135499000549),
 ('concentration', 0.9993895292282104),
 ('ﬂow', 0.9993889331817627)]
'''
    

onto_local.save(file = './' + onto_name + '_ext_' + model_name + '.owl') 
