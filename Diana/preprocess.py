# -*- coding: utf-8 -*-
"""
Created on Thu May  4 15:08:29 2023

@author: smdicher
"""
import spacy
#import neuralcoref
import utils as u
import json
import  pickle
import nltk

#utils.textmining("test")
#text_raw = utils.load_pickle('test_raw')

"""lib = spacy.load('en_core_web_sm')

doc = lib(u'My sister has a dog. She loves him.')

neuralcoref.add_to_pipe(lib)
doc._.has_coref
doc._.coref_clusters
file = open('file.txt', 'a')
sentences = []
for sentence in doc.sents:
    sentences.append(str(sentence))

for s in sentences:
    #sentences_t = []
    dict_new = {}
    s = s.split()
    dict_new["Token"] = s
    file.write(json.dumps(dict_new))
file.close() """   
    
Onto_filenames_ext = ["bao_complete_merged", "chebi", "chmo", "NCIT", "SBO"]
#use_IUPAC_goldbook = True
extend_ontology = "Allotrope_OWL"
#min_counts_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,50,100]   
similarity_threshold_list = [0.8,0.9,0.95,0.99,0.995,0.996,0.997,0.998,0.999]
# to denote automatically annotated strings with [provenance string]
provenance_string = "AB"
use_IUPAC_goldbook = True
mute_prints = True
min_counts_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,50,100]
pickle_name = "methanation_only_text"

metrics_onto_extension = u.ontology_class_extender(Onto_filenames_ext,
                                                         use_IUPAC_goldbook,
                                                         extend_ontology,
                                                         min_counts_list,
                                                         pickle_name,
                                                         similarity_threshold_list,
                                                         provenance_string,
                                                         mute_prints)


    