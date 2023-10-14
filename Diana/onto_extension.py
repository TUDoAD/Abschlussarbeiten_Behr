# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 15:43:18 2023

@author: smdicher
"""
import spacy
import re
import pandas as pd
from preprocess_onto import *




def preprocess_classes(categories, sup_cat, rel_synonym, chem_list, missing_all, match_dict_all, onto_list, onto_new,onto_old):
    global nlp
    nlp = spacy.load('en_core_web_sm')
    classes = {}
    spans_dict = {}
    support = []
    list_all = []
    heads = []
    chem_e=[]
    chem_list.extend([str(i) for i in rel_synonym.values()]) 
    for entity,l in categories.items():
        if entity in classes.keys():
            continue
        else:
            spans_dict[entity] = []
            spans_n = []
        if l == 'Catalyst':
                support = []
                if "based" in entity:
                    e_snip = None
                    based_m = re.search('based',entity)
                    if based_m.start() != 0 or entity[:based_m.start()-1].lower() != 'catalyst': 
                        e_snip = entity[:based_m.start()-1]
                        e_cleaned = e_snip
                        for c in chem_list:
                            pattern ='\\b'+c+'\\b'
                            if re.search(pattern,e_snip): 
                                e_snip= e_snip[e_snip.index(c)+len(c)+1:]
                                c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                                if c_t not in spans_n:    
                                    spans_n.append(c_t)
                                if re.search('[Ss]upported', e_snip):
                                    e_cleaned = e_snip[re.search('[sS]upported',e_snip).end()+1:]
                                    support.append(c_t)
                                    continue
                                e_snip=e_snip.replace(c,'')
                                #if 'catalyst' in e_cleaned:
                                #    classes,_ = check_in_snip(e_snip, classes,nlp, entity,l,chem_list)
                                
                        #if re.search('[Ss]upported', e_cleaned):
                            #e_cleaned = e_snip[re.search('[Ss]upported',e_snip).end()+1:]   
                            if 'catalyst' in e_cleaned:
                                classes,_ = check_in_snip(e_cleaned, classes, entity,l,chem_list)
                        if entity[based_m.end()+1:] != 'catalyst':
                            s_on = False
                            e_snip = entity[based_m.end()+1:]
                            if ' on ' in e_snip: #based on/ based exclusivelly on
                                if re.search('supported on', e_snip):
                                    s_on = True
                                    sup_i = True
                                    #Rh-Co based system supported on alumina, titania and silica
                                    e_btwn=e_snip[re.search('supported on', e_snip).end():]
                                else:
                                    based_m = re.search('on',entity)
                                e_snip = entity[based_m.end()+1:]
                                
                                if re.search('supported', e_snip) and s_on==False: 
                                        #based on silica supported bimetallic catalysts
                                        e_btwn = e_snip[:re.search('supported', e_snip).start()-1]    
                                        sup_i = True
                                else:
                                    sup_i = False
                                
                                for c in chem_list:
                                    pattern ='\\b'+c+'\\b'
                                    if re.search(pattern,e_snip):
                                        c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                                        if sup_i == True and c in e_btwn:
                                                support.append(c_t)                    
                                        if c_t not in spans_n:    
                                            spans_n.append(c_t)  
                                     
                                if 'catalyst' in e_snip:
                                    classes,_ = check_in_snip(e_snip, classes,nlp, entity,l,chem_list)
                elif entity not in chem_list and not set(entity.split()).issubset(chem_list):
                    sup_i = False
                    entity_n = entity
                    #e_before= None
                    if re.search('supported on', entity):
                        #Rh-Co based system supported on alumina, titania and silica                                    
                        e_btwn=entity[re.search('supported on ', entity).end():]
                        sup_i=True                            
                    elif re.search('supported', entity): #bimetallic SiO2-supported RhCo3 cluster catalyst
                        if '-' in entity and entity.index('-')==re.search('supported',entity).start()-1:
                            entity_n= entity[:entity.index('-')]+ ' '+entity[entity.index('-')+1:]
                            spans_dict
                        e_btwn=entity[:re.search('supported', entity).start()-1]
                        sup_i = True                 
                    for c in chem_list:
                        pattern='\\b'+c+'\\b'
                        if re.search(pattern,entity_n):
                            c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                            if sup_i==True and c in e_btwn:
                                support.append(c_t)                    
                            if c_t not in spans_n:    
                                spans_n.append(c_t)                    
                    """
                    if re.search('supported on', entity):
                        #RhCo supported on alumina, titania and silica                                    
                        e_btwn = entity[re.search('supported on ', entity).end():]
                        e_before = entity[:re.search('supported on', entity).start()-1]
                        sup_i=True                            
                    elif re.search('supported', entity): #bimetallic SiO2-supported RhCo3 cluster catalyst
                        if '-' in entity and entity.index('-') == re.search('supported',entity).start()-1:
                            entity_n = entity[:entity.index('-')] + ' '+entity[entity.index('-')+1:]# remove hyphen to make split possible
                        e_before = None
                        e_btwn = entity[:re.search('supported', entity).start()-1]
                        sup_i = True                 
                    for c in chem_list:
                        pattern = '\\b'+c+'\\b'
                        if e_before != None and set(e_before.split()).issubset(chem_list) or e_before in chem_list:
                            c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                            if c_t not in spans_n:    
                                spans_n.append(c_t)   
                            if sup_i==True:
                                support.append(c_t)  
                        elif re.search(pattern,entity_n):
                            c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                            if sup_i == True and c in e_btwn:
                                support.append(c_t)                    
                            if c_t not in spans_n:    
                                spans_n.append(c_t)     
                    """
                    classes,_ = check_in_snip(entity, classes,entity,l,chem_list)                 
                if support:
                    snaps_n = [c for c in spans_n if c not in support] 
                    for i in support:
                        if i in sup_cat.keys():
                            sup_cat[i].extend([c for c in snaps_n if c not in sup_cat[i]])
                        else:
                            sup_cat[i] = snaps_n
        
        elif l == 'Reaction':
            classes,head = check_in_snip(entity, classes,entity,l,chem_list)
            if head and head not in heads and head != 'reaction':
                heads.append(head)
            for c in chem_list: #hydride hydroformulation
                pattern = '\\b'+c+'\\b'
                if re.search(pattern,entity):
                    c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                    if c_t not in spans_n:    
                        spans_n.append(c_t) 
        spans_dict[entity].extend(spans_n)                
        
        if entity in chem_list or set(entity.split()).issubset(chem_list):            
            if entity in rel_synonym.keys():
                c_list = [rel_synonym[entity]]
            elif entity in rel_synonym.values():
                c_list = [entity]
            else: 
                c_list = []
                for c in entity.split():
                    c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                    c_list.append(c_t)
            list_all.append([' '.join(c_list),[],[' '.join(c_list)],categories[entity]])    #changed entity! prop-1-ene instead propylene
            chem_e.append(' '.join(c_list))
            for i in range(len(c_list)):
                if c_list[i] in sup_cat.keys(): #'ZSM-5' instead of 'ZSM-5 zeolite' (change to second)
                    if c_list[i] not in rel_synonym.keys():
                        rel_synonym[c_list[i]] = ' '.join(c_list)
                    sup_cat[' '.join(c_list)] = sup_cat[c_list[i]] 
                    print('{} was replaced with {} in support-catalyst dictionary'.format(c_list[i],' '.join(c_list)))
                    del sup_cat[c_list[i]]
        elif entity.split()[-1] in chem_list and entity not in classes.keys():
            #light olefin
            classes,_ = check_in_snip(entity, classes, entity, l,chem_list)
            c_t = rel_synonym[entity.split()[-1]] if entity.split()[-1] in rel_synonym.keys() else entity.split()[-1]
            spans_dict[entity].append(c_t)        
    for k,v in spans_dict.items():
        for c in chem_e:
            set(c.split()).issubset(cems)
            if c in k:
                ### implement deletion of zeolite
    not_del = [] 
    classes_n = {}    
    for k_1,v_1 in classes.items():            
            v_1.sort(key = lambda x: len(x.split()), reverse=False)
            
            classes_n[k_1] = []
            for k,v in classes.items():
                i = len(v_1)-1
                ele_old = None
                while i >= 0:
                    if k != k_1 and v_1[i] not in classes_n[k_1]: 
                        if v_1[i] in v:
                            classes_n,ele_old = shortcut_add_class(ele_old, classes_n, not_del, value=v_1, i=i, key=k_1 )
                            
                        elif ele_old:
                            not_del.append(ele_old)
                        i -= 1
                    else:                    
                         break 
            i = len(v_1)-1
            ele_old=None
            while i >= 0:
                if  v_1[i] not in classes_n[k_1]: 
                    classes_n,ele_old = shortcut_add_class(ele_old, classes_n, not_del, value=v_1, i=i, key=k_1 )
                elif ele_old:
                    not_del.append(ele_old)
                i -= 1
    v_all = []
    if heads:
        v_all.extend(heads)
    print('classes_n:{}'.format(classes_n))    
    for k,v in classes_n.items():
        list_all.append([k,v,spans_dict[k],categories[k]])
        v_all.extend(v)
    df_entity = pd.DataFrame(list_all, columns=['entity','classes', 'cems', 'category'])
    #missing,match_dict = create_list_IRIs(v_all, onto_list,onto_new,onto_old, IRI_json_filename = 'iriDictionary') 
    #missing_all.extend(missing)   
    #match_dict_all.update(match_dict)      
      
    return df_entity,rel_synonym#,missing_all, match_dict_all

def shortcut_add_class(ele_old,classes_n, not_del, value, i, key ):
       
    classes_n[key].append(value[i])
    if ele_old != None and ele_old not in not_del:
            classes_n[key].remove(ele_old)
    if i!=0:
        if len(value[i].split()) > len(value[i-1].split()):
            ele_old = value[i-1]
            print('ele_old:{}'.format(ele_old))
        else:
            ele_old = None
    
    return classes_n, ele_old

def check_in_snip(e_snip, classes, entity, l,chem_list):
    classes[entity] = []
    doc_snip = nlp(e_snip)
    head = None
    if l == 'Catalyst':
        classes[entity] = ['catalyst role']
        if e_snip == entity:
            if 'catalyst' in entity:
                token_new = 'catalyst role'
                if [t.text for t in [token for token in doc_snip if token.text=='catalyst'][0].children if t.text != "catalyst"]: 
                    token_new = 'catalyst role'
                    for i in reversed(range(len([t.text for t in [token for token in doc_snip if token.text == 'catalyst'][0].children if t.text != "catalyst"]))):
                        if list([token for token in doc_snip if token.text == 'catalyst'][0].children)[i].text in chem_list:
                            continue
                        else:
                            token_new = [t.text.lower() for t in [token for token in doc_snip if token.text == 'catalyst'][0].children][i] +' ' + token_new
                            classes[entity].append(token_new) # from 'bimetallic SiO2-supported RhCo3 cluster catalyst' only 'cluster catalyst role'
            else:
                print('no catalyst in entity:{}'.format(entity))
        else:            
            for token in doc_snip:
                if token.head.text == 'catalyst' or token.pos_=='VERB':
                    if token.text != 'catalyst':
                        if not  re.search(r'[Ss]upported',token.text):
                            token_new=token.text.lower()+' catalyst role'
                            classes[entity].append(token_new)
                        if token.children:
                            for i in reversed(range(len([t.text for t in token.children if t.text != "catalyst"]))):
                                token_new=[t.text.lower() for t in token.children][i] +' ' + token_new
                                classes[entity].append(token_new) 
    
    elif l=='Reaction':
        if len(doc_snip)>1:
            for token in doc_snip:
                if token.head.text==token.text:
                    token_new=token.head.text
                    head=token_new
                else:
                    continue
                list_token=[]
                classes[entity].extend(check_in_children(token, token_new,list_token))
        else:
            classes[entity].append(e_snip)         
    classes[entity] = [*set(classes[entity])] 
    if len(classes[entity])>1 and l=='Catalyst':
        classes[entity].remove('catalyst role')
    return classes,head

def check_in_children(token, token_new,list_token):
    if token.children:
       for t in token.children:
                token=t
                token_new=t.text.lower() +' ' + token_new
                list_token= check_in_children(token, token_new,list_token)
                list_token.append(token_new)
    return list_token        


sup_cat={}
rel_synonym= {'rhodium oxide': 'oxorhodium',
 'rhodium': 'rhodium atom',
 'oxide': 'oxide',
 '1,3-butadiene': 'buta-1,3-diene',
 'propyl': 'propyl',
 'hydride': 'hydride',
 'Zn': 'zinc atom',
 'propene': 'prop-1-ene',
 'La': 'lanthanum atom',
 'SiO2': 'silicon dioxide',
 'Si': 'silicon atom',
 'O': 'oxygen atom',
 'Ir': 'iridium atom',
 'Zr': 'zirconium atom',
 'zeolite': 'zeolite',
 'propylene': 'prop-1-ene',
 'Rh': 'rhodium atom',
 'Co': 'cobalt atom',
 'C': 'carbon atom',
 'Ni': 'nickel atom',
 'Cobalt': 'cobalt atom',
 'RhCo': 'cobalt(2+);rhodium(3+)',
 'Sr': 'strontium atom',
 'Cu': 'copper atom',
 'acetic acid': 'acetic acid',
 'acid': 'acid',
 'Rh2O3': 'Rh2O3',
 'Al': 'aluminium atom'}

missing_all=[]
match_dict_all={}
chem_list=['rhodium oxide',
 '1,3-butadiene',
 'propyl',
 'hydride',
 'Zn',
 'propene',
 'La',
 'SiO2',
 'Ir',
 'Zr',
 'zeolite',
 'propylene',
 'RhCo3(CO)12',
 'Ni',
 'alkene',
 'Cobalt',
 'RhCo',
 'olefin',
 'Sr',
 'Cu',
 'Co',
 'oxide',
 'acetic acid',
 'Rh',
 'Rh2O3',
 'MCM-41',
 'rhodium',
 'Al',
 'ZSM-5']
onto_list ={
            'CHEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            #'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            'CHMO' : 'http://purl.obolibrary.org/obo/chmo.owl',
            'AFO'  : "./ontologies/afo.owl"
            }
onto_new='afo'
onto_old='afo'
categories={'ZSM-5 zeolite': 'Catalyst',
 'naphtha': 'Reactant',
 'catalytic cracking': 'Reaction',
 'Sr, Zr, La-supported on ZSM-5 zeolite': 'Catalyst',
 'metal-incorporated ZSM-5 zeolite': 'Catalyst',
 'hydride transfer reaction': 'Reaction',
 'alkene': 'Product',
 'light olefin': 'Product',
 'Zr-supported on ZSM-5 zeolite': 'Catalyst',
 'HZSM-5': 'Catalyst',
 'RhCo catalyst': 'Catalyst',
 'heterogeneous rhodium oxide catalyst encapsulated within microporous silicalite-1  (S-1) ': 'Catalyst',
 'Rh2O3@S-1': 'Catalyst',
 'Supported catalyst based on the RhCo': 'Catalyst',
 'vapor phase hydroformylation': 'Reaction',
 'olefin': 'Reactant',
 'RhCo3(CO)12': 'Catalyst',
 'Cobalt complex': 'Catalyst',
 'rhodium based catalyst': 'Catalyst',
 'heterogeneous ethylene': 'Reactant',
 'hydroformylation': 'Reaction',
 'Rh,Co based catalyst': 'Catalyst',
 'Supported catalyst based on the RhCo couple': 'Catalyst',
 'propene': 'Reactant',
 'RhCo based catalyst': 'Catalyst',
 'reduction': 'Treatment',
 'Rh based catalyst': 'Catalyst',
 'DRC': 'Characterization',
 'propylene': 'Reactant',
 'hydrogenation': 'Reaction',
 'propyl specie': 'Product',
 'Rh-based heterogeneous catalyst': 'Catalyst',
 'Rh': 'Catalyst',
 'Rh-based alloy catalyst': 'Catalyst',
 'heterogeneous hydroformylation': 'Reaction',
 'monometallic Rh supported on MCM-41': 'Catalyst',
 'Rh-based bimetallic catalyst': 'Catalyst',
 'RhM3,M =  M= ,Co Co, Ni,Cu Zn': 'Catalyst',
 'ethylene': 'Reactant',
 'Bimetallic heterogeneous catalyst based on rhodium supported on various oxide': 'Catalyst',
 'Rh, Ir-based atomically dispersed catalyst': 'Catalyst',
 'dimerization': 'Reaction',
 '1,3-butadiene': 'Reactant',
 'methane': 'Reactant',
 'acetic acid': 'Product'}
df_entity, rel_synonym=preprocess_classes(categories, sup_cat, rel_synonym, chem_list, missing_all, match_dict_all, onto_list, onto_new,onto_old)