# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 15:39:00 2023

@author: smdicher
"""
from owlready2 import *
import copy

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




'''
onto_main = get_ontology("./ontologies/afo.owl").load()
def search_class(data,onto_snip, onto2):
    for key, value in data.items():
        label = onto_snip.search_one(iri=key).label[0]
        if onto2.search(label=label):
            print(label)
            children = search_class({val:[] for val in value}, onto_snip, onto2)

search_class(hierarchy, onto_snip=onto_test,onto2= onto_main)
'''          
list_1=[{'E1':[]},{'E2':['E1','E3']}, {'E4':[]}, {'E5':['E4']},{'E6':['E2','E5']}]
data={}
for item in dict_temp_value_out:
    for key,value in item.items():
        data[key]=value
"""
def build_hierarchy(data, values=None):
    data_out = {}
    keys = list(data.keys())
    data = copy.deepcopy(data)
    
    if not values:
        values=list(data.values())
        len_keys_all= len(list(data.keys()))
    for k in keys:
        for i in values:
            if k in i :
                value = data[k] 
                #data_temp.append(data)
                data.pop(k)#data_temp[n][key]
                
                i[i.index(k)] = {k: value}
                
                print(data)
                data = build_hierarchy(data)
                 
        return data
"""                    
def build_hierarchy(data):
    result = {}

    keys = list(data.keys())
    for key in keys:
        value = data[key]
        if value:
            children = build_hierarchy([{val: []} for val in value])
            result[key] = children
            for i, child in enumerate(children):
                if isinstance(child, dict):
                    child_key = list(child.keys())[0]
                    child[child_key] = value[i]
    else:
            result[key] = []

    return result
hierarchy = build_hierarchy(data=data)
print(hierarchy)