# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 12:40:21 2023

@author: smdicher
"""

def create_list_IRIs(class_list,IRI_json_filename = 'iriDictionary'):
        f= open('{}.json'.format(IRI_json_filename))
        txt= open('Class_IRIs.txt', 'a')
        onto_dict = json.load(f)
        f.close()
        match_dict={}
        
        for entity in class_list:
            match_dict = search_value_in_nested_dict(entity,onto_dict,match_dict)
            
        for key,value in match_dict.items():
            
            iri_class = key + '  # ' + value +'\n'
            txt.write(iri_class) 
        txt.close()               
        return match_dict
    
    
def search_value_in_nested_dict(value, onto_dict, match_dict):
    for k in onto_dict.keys():              # diese zeile kann dann weg wenn nur eine Ontologie betrachtet wird.
        for IRI in onto_dict[k].keys() :    # hier muss dann k rausgenommen werden. abhängig davon wie wein Dictionary aussieht
            for key, val in onto_dict[k][IRI].items():
                if value == val:
                    match_dict[IRI]=val
                else:
                    continue
            
    return match_dict