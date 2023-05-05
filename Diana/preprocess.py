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

lib = spacy.load('en_core_web_sm')

doc = lib(u'My sister has a dog. She loves him.')

"""neuralcoref.add_to_pipe(lib)
doc._.has_coref
doc._.coref_clusters"""
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
file.close()    
    



    