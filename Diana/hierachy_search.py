# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 15:39:00 2023

@author: smdicher
"""
from owlready2 import *
import csv, types

def create_onto_dict (onto_name, output ='iri'):
    new_world = owlready2.World()
    onto_test = new_world.get_ontology("./ontology_sniplet/{}_classes.owl".format(onto_name)).load()
    a = list(onto_test.classes())
    data = []
    for entry in a:
        if output =='iri':
            temp_key = entry.iri
        else:
            temp_key = entry.label[0]
        subclass_list = list(entry.subclasses())
        if subclass_list: 
            for c in subclass_list:
                if output =='iri':
                    pc= [c.iri,temp_key]
                else:
                    pc= [c.label[0],temp_key]
                
                data.append(pc)        
            #dict_temp_value = [i.iri for i in subclass_list]
        else: 
           continue
        
    roots = set()
    mapping = {}
    for child,parent in data:        
               childitem = mapping.get(child,None)
               if childitem is None:
                   childitem =  {}
                   mapping[child] = childitem
               else:
                   roots.discard(child)
               parentitem = mapping.get(parent,None)
               if parentitem is None:
                   mapping[parent] = {child:childitem}
                   roots.add(parent)
               else:
                   parentitem[child] = childitem
            #dict_temp_value_out.append({dict_temp_key:dict_temp_value})
    tree = { id : mapping[id] for id in roots }
    return tree
tree=create_onto_dict('CHEBI','label')
print(tree)
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
"""        
list_1=[{'E1':[]},{'E2':['E1','E3']}, {'E4':[]}, {'E5':['E4']},{'E6':['E2','E5']}]
data={}
for item in dict_temp_value_out:
    for key,value in item.items():
        data[key]=value

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

for entry in a:
    temp_key = entry.iri
    subclass_list = list(entry.subclasses())
    if subclass_list: 
        for c in subclass_list:
            pc= [c,temp_key]
            data_out.append(pc)
            
        #dict_temp_value = [i.iri for i in subclass_list]
    else: 
       continue
"""   
    #dict_temp_value_out.append({dict_temp_key:dict_temp_value})

#data = [['a','x'], ['b','x'], ['c','x'], ['x','y'], ['t','y'], ['c','p']]


'''
for root in roots:
    print(mapping[root])
'''
"""
def find_classes(tree, onto,onto_test):
    onto =get_ontology("./ontologies/afo.owl").load()
    found_keys=[]
    stack = [tree]
    while stack:
        current =stack.pop()
        if isinstance(current,dict):
            for key, value in current.items():
                entity=onto_test.search_one(iri= key)
                if onto.search_one(label=entity.label[0]):
                    found_keys.append(key)
                stack.append(value)
    return found_keys    
"""

def find_classes(tree, onto_name):
    
    new_world2= owlready2.World()
    onto =new_world2.get_ontology("./ontologies/{}.owl".format(onto_name)).load()
    found_keys=[]
    stack = [tree]
    while stack:
        current =stack.pop()
        if isinstance(current,dict):
            for key, value in current.items():
                with onto:
                    if onto.search_one(label=key) and key not in found_keys:
                        found_keys.append(key)
                    stack.append(value)
    return found_keys                 
keys=find_classes(tree, 'afo')     
#found_entities= find_classes(tree, onto, onto_test)


#onto= get_ontology("./ontologies/afo_upd.owl").load()
#onto_test=('.ontology_sniplet/CHEBI_classes.owl"')
#onto.search_one(label='atom').equivalent_to.append(onto_test.search_one(label='atom'))
