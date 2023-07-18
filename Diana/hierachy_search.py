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


onto_classes
#onto= get_ontology("./ontologies/afo_upd.owl").load()
#onto_test=('.ontology_sniplet/CHEBI_classes.owl"')
#onto.search_one(label='atom').equivalent_to.append(onto_test.search_one(label='atom'))
