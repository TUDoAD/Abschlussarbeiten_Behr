# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 15:39:00 2023

@author: smdicher
"""
from owlready2 import *

onto_test = get_ontology("./ontology_sniplet/CHEBI_classes.owl").load()
a = list(onto_test.classes())
dict_temp_value_out = []
for entry in a:
    dict_temp_key = entry.iri
    subclass_list = list(entry.subclasses())
    if subclass_list: 
        dict_temp_value = [i.iri for i in subclass_list]
    else: 
       dict_temp_value = []
   
    dict_temp_value_out.append({dict_temp_key:dict_temp_value})
    for i in dict_temp_value:
        for k,v in i.items():
            if not v:
                
            