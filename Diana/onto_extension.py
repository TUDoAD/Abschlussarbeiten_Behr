# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 15:43:18 2023

@author: smdicher
"""
import os
import spacy
import re
import pandas as pd
from preprocess_onto import *
from chemdataextractor import Document
import time
from text_mining import add_publication
def preprocess_classes(categories,abbreviation, onto_new_dict, sup_cat, rel_synonym, chem_list, missing_all, match_dict_all,entities_raw):
    """
    

    Parameters
    ----------
    categories : TYPE
        DESCRIPTION.
    sup_cat : TYPE
        DESCRIPTION.
    rel_synonym : TYPE
        DESCRIPTION.
    chem_list : TYPE
        DESCRIPTION.
    missing_all : TYPE
        DESCRIPTION.
    match_dict_all : TYPE
        DESCRIPTION.

    Returns
    -------
    df_entity : TYPE
        DESCRIPTION.
    rel_synonym : TYPE
        DESCRIPTION.
    missing_all : TYPE
        DESCRIPTION.
    match_dict_all : TYPE
        DESCRIPTION.

    """
    global nlp
    global comment_treat
    global comment_charac
    global entities_raw1
    entities_raw1=entities_raw
    not_process=['Characterization','Treatment']
    nlp = spacy.load('en_core_web_sm')
    classes = {}
    spans_dict = {}
    support = []
    list_all = []
    heads = []
    chem_e = []
    chem_list.extend([str(i) for i in rel_synonym.values()]) 
    pop=[]
    comment_treat=[]
    comment_charac=[]
    values_comp = [i for v in onto_new_dict.values() for i in v if i]
    for k, v in sup_cat.items():
        new_values=[]
        for i in v :
            if i in rel_synonym.keys():
                new_values.append(rel_synonym[i])
            else:
                new_values.append(i)
        sup_cat[k]=new_values
    for k in sup_cat.keys():   
        sup_cat[k]=[*set(sup_cat[k])]
        if k in rel_synonym.keys():
            if rel_synonym[k] in sup_cat.keys():
                sup_cat[rel_synonym[k]].extend(sup_cat[k])                  
            else:
                pop.append({rel_synonym[k]:sup_cat[k]})
            pop.append(k)
    for i in pop:
        if type(i) == dict:
            if list(i.keys())[0] in sup_cat.keys():
                sup_cat[list(i.keys())[0]].extend(list(i.values())[0])                    
            else:
                sup_cat.update(i)
        else:
            sup_cat.pop(i)
    for entity,l in categories.items():
        print(entity)
        if l in not_process:
            if l == 'Treatment':
                comment_treat.append(entity)
            else:
                comment_charac.append(entity)
        elif entity in classes.keys():
            continue
        else:
            entity_raw=entity
            chem_all=[cem for cem in chem_list if cem in entity]
            seen_items = set()
            
            # Create a new list to store the filtered items
            chem_entity = []

            # Iterate through the items and filter out substrings
            for item in chem_all:
                # Check if the item is not a substring of any seen item
                if not any(item in seen_item for seen_item in seen_items):
                    chem_entity.append(item)
                    seen_items.add(item)
            if entity not in chem_list and entity in values_comp:
                chem_entity.append(entity)
                chem_list.append(entity)
            # Create a set to keep track of entities to remove
            entities_to_remove = set()

            # Iterate through the entities and check if they are substrings of others
            for i, cem1 in enumerate(chem_entity):
                for j, cem2 in enumerate(chem_entity):
                    if i != j and cem1 in cem2:
                        entities_to_remove.add(cem1)

            # Filter out entities that are substrings of others
            chem_entity = [c for c in chem_entity if c not in entities_to_remove]
            print(entity+':')
            print(chem_entity)
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
                        for c in chem_entity:
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

                        if 'catalyst' in e_cleaned:
                                classes,_ = check_in_snip(e_cleaned, classes, entity,l,chem_entity)
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
                                
                            for c in chem_entity:
                                    pattern ='\\b'+c+'\\b'
                                    if re.search(pattern,e_snip):
                                        c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                                        if sup_i == True and c in e_btwn:
                                                support.append(c_t)                    
                                        if c_t not in spans_n:    
                                            spans_n.append(c_t)  
                                     
                            if 'catalyst' in e_snip:
                                    classes,_ = check_in_snip(e_snip, classes, entity,l,chem_entity)
                elif entity not in chem_list and not set(entity.split()).issubset(chem_list):
                    sup_i = False
                    entity_n = entity
                    if re.search('supported on', entity) or re.search('encapsulated within', entity):
                        #Rh-Co supported on alumina, titania and silica                                    
                        if 'supported on' in entity:
                            e_btwn=entity[re.search('supported on ', entity).end():]
                        else:
                            e_btwn=entity[re.search('encapsulated within ', entity).end():]
                        sup_i=True                            
                    elif re.search('supported', entity) and re: #bimetallic SiO2-supported RhCo3 cluster catalyst 
                        if '-' in entity and entity.index('-')==re.search('supported',entity).start()-1:
                            entity_n= entity[:entity.index('-')]+ ' '+entity[entity.index('-')+1:]
                            
                        e_btwn=entity[:re.search('supported', entity).start()-1]
                        sup_i = True                 
                    
                    for c in chem_entity:
                        if ('(' and')') in c: #Rh(111)
                            d=c
                            d=d.replace('(','\\(')
                            d=d.replace(')', '\\)')
                            pattern=d
                        else:
                            pattern='\\b'+c+'\\b'
                        if re.search(pattern,entity_n):
                            c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                            if sup_i==True and c in e_btwn:
                                eq_idx=e_btwn.find('=') #RhM3/MCM-41, M = Fe, Co, Ni, Cu, or Zn
                                if eq_idx != -1: 
                                    if re.search(pattern,entity_n).start() < eq_idx:
                                        support.append(c_t)
                                else: 
                                    support.append(c_t)
                            if c_t not in spans_n:    
                                spans_n.append(c_t)                    
                    classes,_ = check_in_snip(entity, classes,entity,l,chem_entity)                 
                if support:
                    snaps_n = [c for c in spans_n if c not in support] 
                    for i in support:
                        if i in sup_cat.keys():
                            sup_cat[i].extend([c for c in snaps_n if c not in sup_cat[i]])
                        else:
                            sup_cat[i] = snaps_n
        
            elif l == 'Reaction':
                classes,head = check_in_snip(entity, classes,entity,l,chem_entity)
                if head and head not in heads and head != 'reaction':
                    heads.append(head)
                for c in chem_entity: #hydride hydroformulation
                    pattern = '\\b'+c+'\\b'
                    if re.search(pattern,entity):
                        c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                        if c_t not in spans_n:    
                            spans_n.append(c_t) 
            spans_dict[entity].extend(spans_n)                
            if entity!=entity_raw:
                if entity in entities_raw1.keys():
                    entities_raw1[entity].extend(entities_raw1[entity_raw])
                    entities_raw1[entity]=[*set(entities_raw1[entity])]
                else:
                    entities_raw1[entity]=entities_raw1[entity_raw]
        if entity in chem_list or set(entity.split()).issubset(chem_list):            
            if entity in rel_synonym.keys():
                c_list = [rel_synonym[entity]]
            elif entity in rel_synonym.values():
                c_list = [entity]
            else: 
                c_list = []
                for c in entity.split():
                    c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                    if "atom" in c_t:
                       c_list=[entity]
                       break
                    c_list.append(c_t)
            
            list_all.append([' '.join(c_list),[],[' '.join(c_list)],categories[entity]])    #changed entity! prop-1-ene instead propylene
            if len(entity.split()) > 1 and set(entity.split()).issubset(chem_list):    
                chem_e.append(' '.join(c_list))
                print('changed entity:'+' '.join(c_list))
        elif entity.split()[-1] in chem_list and entity not in classes.keys():
            #i.e. light olefin
            classes,_ = check_in_snip(entity, classes, entity, l,chem_list)
            c_t = rel_synonym[entity.split()[-1]] if entity.split()[-1] in rel_synonym.keys() else entity.split()[-1]
            spans_dict[entity].append(c_t) #
        elif entity not in classes.keys() and l in ['Product','Reactant']: 
            for c in chem_entity:
                c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                spans_dict[entity].append(c_t) #muss für entities wie "phenolic species", alkyl group erweitert werden  
            list_all.append([entity,['chemical substance'],[],l])
    for k,v in spans_dict.items(): #replacement of parts of chemical entities with full name. i.e. ['zeolite', 'ZSM-5']-> ['ZSM-5 zeolite'] if 'ZSM-5 zeolite' is in entity
        for c in chem_e:
            for i in range(len(c.split())):
                if c.split()[i] in sup_cat.keys(): #'ZSM-5' instead of 'ZSM-5 zeolite' (change to second)
                    if c.split()[i] not in rel_synonym.keys():
                        rel_synonym[c.split()[i]] = c
                    sup_cat[c] = sup_cat[c.split()[i]] 
                    print('{} was replaced with {} in support-catalyst dictionary'.format(c.split()[i],c))
                    sup_cat.pop(c.split()[i],None)
            if c in k:
                spans_dict[k]=list(filter(lambda x: x not in c.split(), v))
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
        v_all.append(k)
        v_all=[*set(v_all)]
    df_entity = pd.DataFrame(list_all, columns=['entity','classes', 'cems', 'category'])
    df_entity=df_entity.drop_duplicates(['entity']).reset_index()
    missing,match_dict = create_list_IRIs(v_all, IRI_json_filename = 'iriDictionary') 
    missing_all.extend(missing)   
    match_dict_all.update(match_dict)      
    comment_treat=[*set(comment_treat)]
    comment_charac=[*set(comment_charac)]
    print('comment_treat:{}'.format(comment_treat))
    print('comment_charac:{}'.format(comment_charac))
    return df_entity, rel_synonym, missing_all, match_dict_all

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

def check_in_snip(e_snip, classes, entity, l, chem_list):
    classes[entity] = []
    doc_snip = nlp(e_snip)
    head = None
    if chem_list:
        chem_list.extend([c for c in [cem.split() for cem in chem_list]][0])
        c_i=[]
        for c in chem_list:
            if '-' in c:
                c_i=c.split('-')
                c_i.append('-')
        chem_list.extend(c_i)
        chem_list=[*set(chem_list)]
    if l == 'Catalyst':
        classes[entity] = ['catalyst role']
        if e_snip == entity:
            if 'catalyst' in entity:
                #token_new = 'catalyst role'
                try:
                    if [t.text for t in [token for token in doc_snip if token.text=='catalyst'][0].children if t.text != "catalyst" and t.text not in chem_list]: 
                        for t in [token for token in doc_snip if token.text=='catalyst'][0].children:
                            if t.text != "catalyst" and t.text!='containing' and t.text not in chem_list:
                                print(t.text)
                                if not re.search(r'[Ss]upported',t.text):
                                    token_new=t.text.lower()+' catalyst role'
                                    classes[entity].append(token_new)
                                if t.children:
                                    children=list(t.children)
                                    for i in reversed(range(len([k.text for k in children if k.text != "catalyst" and k.text not in chem_list and 'supported' not in k.text]))):
                                        token_new=[t.text.lower() for t in children if t.text != "catalyst" and t.text not in chem_list and 'supported' not in t.text][i] +' ' + token_new
                                        classes[entity].append(token_new) 
                except:
                    print('\nDependency parsing could not be performed.\nAssigned class for "{}" is "catalyst role"\n'.format(entity))
                            
                    """
                            for i in reversed(range(len([t.text for t in [token for token in doc_snip if token.text!='catalyst'][0].children if t.text != "catalyst" and t.text not in chem_list]))):
                                    token_new =  [t.text.lower() for t in [token for token in doc_snip if token.text == 'catalyst'][0].children][i]+' ' + token_new
                                    classes[entity].append(token_new) # Problem: from 'bimetallic SiO2-supported RhCo3 cluster catalyst' only 'cluster catalyst role' 
                            """
            else:
                print('no catalyst in entity:{}'.format(entity))
        else:            
            for token in doc_snip:
                if token.head.text == 'catalyst' or token.pos_=='VERB':
                    token_new=' catalyst role'
                    if token.text != 'catalyst':
                        if not  re.search(r'[Ss]upported',token.text) and token.text not in chem_list:
                            token_new=token.text.lower()+token_new
                            classes[entity].append(token_new)
                        if token.children:
                            for i in reversed(range(len([t.text for t in token.children if t.text != "catalyst" and t.text not in chem_list and 'supported' not in t.text]))):
                                token_new=[t.text.lower() for t in token.children if t.text != "catalyst" and t.text not in chem_list and 'supported' not in t.text][i] +' ' + token_new
                                classes[entity].append(token_new) 
    
    elif l=='Reaction':
        if len(doc_snip) > 1:
            if '-' in doc_snip.text:
                doc_snip = nlp(e_snip.replace('-',' '))
            for token in reversed(list(doc_snip)):
                if token.text=='reaction':
                    token_new = token.text
                    head=token_new
                elif token.head.text == token.text and head==None:
                    token_new = token.head.text
                    head=token_new
                else:
                    continue
                list_token=[]
                classes[entity].extend(check_in_children(token, token_new,list_token))
        else:
            classes[entity].append(e_snip)            
    classes[entity] = [*set(classes[entity])] 
    if len(classes[entity])>1 and l == 'Catalyst':
        classes[entity].remove('catalyst role')
    return classes, head

def check_in_children(token, token_new,list_token):
    if token.children:
        for t in reversed(list(token.children)):
                token = t
                token_new = t.text.lower() +' ' + token_new
                list_token = check_in_children(token, token_new,list_token)
                list_token.append(token_new)
    return list_token        

def create_classes_onto(abbreviation, sup_cat, missing, match_dict, df_entity,reac_dict,p_id,rel_synonym,chem_list,onto_new_dict):
    global num
    global classes_all
    print(entities_raw1)
    nlp = spacy.load('en_core_web_sm')
    num = 0 
    sup_sub_df = pd.DataFrame(columns=['super_class','subclass'])
    new_world = owlready2.World()
    super_classes=['molecule','support material','chemical substance' ]
    
    onto = new_world.get_ontology('./ontologies/{}.owl'.format(onto_new)).load()
    created_classes =[]
    classes_all=[i.label[0].lower() for i in onto.classes() if i.label]
    #onto.set_base_iri('http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#',rename_entities=False)
    chem_sub = {}
    chem_list.extend([str(i) for i in rel_synonym.values()])
    onto_names={}
    idx_abb=[]
    for v in match_dict.values():
        onto_names[v[0]]=v[1]
    for row in df_entity.itertuples():
        if row.entity in abbreviation.values():
            idx_abb.append(row.Index)
            continue
        classes_parent = []
        classes = sorted(list(row.classes),reverse = False, key = len)

        if row.cems:                     
            for c in row.cems:
                if c in onto_names.keys():
                        if c.lower() not in [i.label[0].lower() for i in onto.individuals() if i.label]:
                            cem = onto.search_one(label = onto_names[c])
                            print('cem:{}'.format(c))
                            onto,_ = add_individum(onto,cem, c,p_id = p_id)
                else:
                    if len(c.split()) > 1:
                        for i in range(len(c.split())):
                            if c.split()[i] in onto_names.keys():
                                sup_sub_df = sup_sub_df.append({'super_class':onto_names[c.split()[i]], 'subclass': c},ignore_index = True)                         
                        if c in sup_cat.keys():
                            sup_sub_df = sup_sub_df.append({'super_class':'support material', 'subclass': c},ignore_index = True)
                        elif c not in list(sup_sub_df['subclass']):
                            sup_sub_df = sup_sub_df.append({'super_class':'molecule', 'subclass': c},ignore_index = True)
                    elif c in sup_cat.keys():
                        sup_sub_df = sup_sub_df.append({'super_class':'support material', 'subclass': c},ignore_index = True)                       
                    else:
                        sup_sub_df = sup_sub_df.append({'super_class':'molecule', 'subclass': c},ignore_index = True)
            if row.cems[0] != row.entity:
                if nlp(row.entity)[-1].text in chem_list and 'supported' not in row.entity:
                    sup_sub_df = sup_sub_df.append({'super_class':row.cems[0], 'subclass': row.entity},ignore_index=True)
                """
                if row.entity in abbreviation.values():
                     sup_sub_df = sup_sub_df.append({'super_class':[k for k,v in abbreviation.items() if v==row.entity][0], 'subclass': row.entity},ignore_index=True)  
                     """
                if row.category == 'Catalyst' and row.entity not in sup_sub_df['subclass'] : # and "based" not in row.entity
                    sup_sub_df = sup_sub_df.append({'super_class':'chemical substance', 'subclass': row.entity},ignore_index=True)
        if row.classes==['chemical substance']:
            sup_sub_df = sup_sub_df.append({'super_class':'chemical substance', 'subclass': row.entity},ignore_index=True)      
        if row.category =='Catalyst':
            k = 0
            while k < len(row.classes):
                classes_parent.append(classes[k])
                
                if k != 0:
                    if len(classes[k-1].split()) < len(classes[k].split()):
                        sup_sub_df = sup_sub_df.append({'super_class':classes[k-1],'subclass':classes[k]},ignore_index=True)
                        classes_parent.remove(classes[k-1]) 
                    else:                        
                        sup_sub_df = sup_sub_df.append({'super_class':'catalyst role','subclass':classes[k]},ignore_index=True)
                        
                elif classes[k] != 'catalyst role':
                        sup_sub_df = sup_sub_df.append({'super_class':'catalyst role','subclass':classes[k]},ignore_index=True)
                k += 1  
            
            if row.entity not in list(sup_sub_df['subclass']) and not row.cems:   
                sup_sub_df = sup_sub_df.append({'super_class':'chemical substance', 'subclass': row.entity},ignore_index=True)
                """
                if row.entity not in abbreviation.values():
                    sup_sub_df = sup_sub_df.append({'super_class':'chemical substance', 'subclass': row.entity},ignore_index=True)
                else:
                    idx_abb.append(row.Index) #in case catalyst is a chemical substance and have an abbreviation it will not be created as entity but will be added in the annotations of its abbreviation
                    """
                """
                for i in classes_parent:
                    sup_sub_df = sup_sub_df.append({'super_class':i, 'subclass':row.entity},ignore_index = True)
                 """   
            if classes_parent:
                chem_sub[row.entity] = classes_parent
        elif row.category == 'Reaction':
            k=0
            while k<len(row.classes):
                classes_parent.append(row.classes[k])
                if k != 0:
                    if len(classes[k-1].split()) < len(classes[k].split()):
                        sup_sub_df = sup_sub_df.append({'super_class':classes[k-1],'subclass':classes[k]},ignore_index=True)
                        classes_parent.remove(classes[k-1])                  
                k += 1
            for k in classes_parent:    
                i = len(k.split())-1
                    
                if k in onto_names.keys() and k not in [c.label[0] for c in onto.individuals() if c.label]:
                    onto, _ = add_individum(onto,onto.search_one(label = onto_names[k]), k,p_id = p_id)     
                elif k in onto_names.values() and k not in [c.label[0] for c in onto.individuals() if c.label]:
                    onto, _ = add_individum(onto,onto.search_one(label = k), k,p_id = p_id)
                elif k.split()[i] in onto_names.keys():
                    
                    sup_sub_df = sup_sub_df.append({'super_class': onto_names[k.split()[i]], 'subclass':k},ignore_index=True)
                else:
                    sup_sub_df = sup_sub_df.append({'super_class': 'chemical reaction (molecular)', 'subclass':k},ignore_index = True)
    df_entity_all=df_entity            
    df_entity= df_entity.drop(index=idx_abb)                   
    with onto:
        
        support_mat = onto.search_one(label='support material')
        if not support_mat:
            support_mat = types.new_class('DC_{:02d}{:02d}'.format(p_id,num), (onto.search_one(label = 'material'),))
            support_mat.label.append('support material')
            num += 1
            created_classes.append('support material')

        try:
            support_role_i = [i for i in list(onto.search(label='support role')) if i in list(onto.individuals())][0]
        except:
            onto, support_role_i = add_individum(onto,onto.search_one(label='support role'),'support role',p_id)
        if 'Product' in list(df_entity.category):
            try:
                prod_role_i = [i for i in list(onto.search(label='product role')) if i in list(onto.individuals())][0]
            except:      
                onto, prod_role_i = add_individum(onto,onto.search_one(label='product role'), 'product role',p_id=p_id)        
        if 'Reactant' in list(df_entity.category):
            try:
                reac_role_i = [i for i in list(onto.search(label='reactant role')) if i in list(onto.individuals())][0]
            except:
                onto, reac_role_i = add_individum(onto,onto.search_one(label='reactant role'), 'reactant role',p_id)
        if 'Catalyst' in list(df_entity.category):
            try:
                cat_role_i = [i for i in list(onto.search(label='catalyst role')) if i in list(onto.individuals())][0]
            except:
                onto, cat_role_i = add_individum(onto,onto.search_one(label='catalyst role'), 'catalyst role',p_id)
        
        indecies = []
        entities = [i for i in df_entity['entity'] if i]

        for s in sup_sub_df.itertuples():            
            if s.index in indecies:
                continue                                 
            elif s.super_class in super_classes or s.super_class in chem_list :
                indecies, onto,_,created_classes = create_sub_super(missing, onto,s.Index, indecies,entities, sup_sub_df,created_classes,chem_list,abbreviation,p_id,s.subclass)            
            else:
                indecies, onto,_,created_classes = create_sub_super(missing, onto,s.Index, indecies,entities, sup_sub_df,created_classes,chem_list,abbreviation,p_id = p_id)
        
        
        for row in df_entity.itertuples():
                
                if row.cems:
                    e_ind=[]
                    if row.category == 'Catalyst' and row.entity in chem_sub.keys():
                        e_ind = [i for i in list(onto.search(label=row.entity)) if i in list(onto.individuals())][0]
                        for c in chem_sub[row.entity]: #assign catalyst roles
                            print(row.entity+':'+c)
                            try:
                                cat_cl = [i for i in list(onto.search(label=c)) if i in list(onto.individuals())][0]
                            except:
                                onto,cat_cl =add_individum(onto,list(onto.search(label = c))[0], c ,p_id)
                                
                            e_ind.RO_0000087.append(cat_cl) #'has role' = RO_0000087
                    for c in row.cems:
                        if c != row.entity and not row.classes:
                            
                            if [i for i in list(onto.search(label=c)) if i in list(onto.classes())]:
                                onto, ind = add_individum(onto,[i for i in list(onto.search(label=c)) if i in list(onto.classes())][0], row.entity,p_id)
                            else:
                                onto, ind = add_individum(onto,[i for i in list(onto.search(label=c+' (molecule)')) if i in list(onto.classes())][0], row.entity,p_id)
                                
                        else:
                            try:
                                ind = [i for i in list(onto.search(label = c)) if i in list(onto.individuals())][0]
                            except:
                                print('c in row.cems individuum added:{}'.format(c))
                                onto, ind = add_individum(onto,list(onto.search(label = c))[0], c,p_id)
                            
                            if c in sup_cat.keys():
                                ind.RO_0000087.append(support_role_i) #'has role' = RO_0000087
                                ind.support_component_of.append(e_ind)
                                for k in row.cems:
                                    if k in sup_cat[c]:
                                        try:
                                            cat=[i for i in list(onto.search(label=k)) if i in list(onto.individuals())][0]
                                        except:
                                            onto, cat=add_individum(onto,list(onto.search(label=k))[0], c,p_id)
                                        cat.supported_on.append(ind)
                                        cat.catalytic_component_of.append(e_ind)  
                        if row.category== 'Product':
                            ind.RO_0000087.append(prod_role_i)
                        elif row.category =='Reactant':
                            ind.RO_0000087.append(reac_role_i)
                        elif row.category=='Catalyst':
                            if c==row.entity:
                                ind.RO_0000087.append(cat_role_i) #'has role' = RO_0000087
                            elif e_ind and e_ind not in ind.support_component_of:                          
                                ind.catalytic_component_of.append(e_ind)
                
                if row.category== 'Reaction':
                    if row.entity in reac_dict.keys():
                        try:
                            ind= [i for i in list(onto.search(label=row.entity)) if i in list(onto.individuals())][0] 
                        except:
                            onto,ind=add_individum(onto,[i for i in list(onto.search(label=row.classes[0])) if i in list(onto.classes())][0], row.entity,p_id)
                        for r in reac_dict[row.entity]:
                            c_t=rel_synonym[r] if r in rel_synonym.keys() else r
                            try:
                                cem_i=[i for i in list(onto.search(label=r)) if i in list(onto.individuals())][0]  
                            except:
                                try:
                                    cem_i=[i for i in list(onto.search(label=c_t)) if i in list(onto.individuals())][0]   
                                except:
                                    try:
                                        cem_i=[i for i in list(onto.search(label=c_t+' (molecule)')) if i in list(onto.individuals())][0]
                                    except:
                                        print(r+" was skipped in reac_dict")
                                        continue
                            ind.RO_0000057.append(cem_i) #'has participant' = RO_0000057
                if row.entity in abbreviation.keys():
                    try: # check for abbreviations
                        e_ind.comment.append(abbreviation[row.entity])
                    except:
                        e_ind = [i for i in list(onto.search(label=row.entity)) if i in list(onto.individuals())][0]
                        e_ind.comment.append(abbreviation[row.entity])

        for sup,v in sup_cat.items():
            sup = rel_synonym[sup] if sup in rel_synonym.keys() else sup
            try:
                sup = [i for i in list(onto.search(label=sup)) if i in list(onto.individuals())][0]
            except:
                try:
                    onto, sup=add_individum(onto,list(onto.search(label=sup))[0], sup,p_id)
                except:
                    sup_mat=[i for i in list(onto.search(label='support material')) if i in onto.classes()][0]
                    new_cl = types.new_class(sup, (sup_mat,))
                    onto, sup = add_individum(onto,new_cl, sup,p_id)
            sup.RO_0000087.append(support_role_i)
            
            for cat in v:
                cat = rel_synonym[cat] if cat in rel_synonym.keys() else cat
                try:
                    cat = [i for i in list(onto.search(label=cat)) if i in list(onto.individuals())][0]
                except:
                    try:
                        onto, cat = add_individum(onto,list(onto.search(label=cat))[0], cat,p_id)
                    except:
                        mol=[i for i in list(onto.search(label='molecule')) if i in onto.classes()][0]
                        new_cl = types.new_class(cat, (mol,))
                        onto, cat = add_individum(onto,new_cl, cat,p_id)
                cat.RO_0000087.append(cat_role_i)    #has role catalyst role
                cat.supported_on.append(sup)
        entities_pub = []
        entities_pub.extend([c for c in df_entity.entity])
        entities_pub.extend([i for c in df_entity_all.cems if c for i in c if i not in entities_pub])
        entities_pub = [*set(entities_pub)]
        pub_new = onto.search_one(iri='*publication{}'.format(p_id))
        if comment_treat:
            pub_new.comment.append('treatment: '+', '.join(comment_treat))
        if comment_charac:
            pub_new.comment.append('characterization: '+', '.join(comment_charac))
        for entity in entities_pub:
            print('entity:{}'.format(entity))
            try:
                ind = [i for i in list(onto.search(label = entity)) if i in list(onto.individuals())][0]
            except:
                continue
            ind.mentioned_in.append(pub_new)
            if entity in entities_raw1.keys() and entity != entities_raw1[entity][0]:
                for i in entities_raw1[entity]:
                    ind.comment.append(i)
        for short,entity in rel_synonym.items():
            inds = [i for i in list(onto.search(label=entity))]
            for i in inds:
                i.comment.append(short)
    onto = create_comp_relation(onto,list(onto_names.keys()), rel_synonym,p_id,onto_new_dict)
                
    onto.save('./ontologies/{}.owl'.format(onto_new))
    return created_classes, sup_sub_df       
          
def create_comp_relation(onto,values, rel_synonym,p_id,onto_new_dict):
    global num
    #global onto_new_dict
    short = []
    pub_new = onto.search_one(iri='*publication{}'.format(p_id))
    with onto:
        for k,v in onto_new_dict.items():
            if k in values or len(v) == 1:
                continue

            else:
                try:
                    mol = [m for m in onto.search(label = k) if m in onto.individuals()][0]
                except:
                    try:
                        onto,mol = add_individum(onto,onto.search_one(label = k),k,p_id)
                    except:
                        continue
                print('mol:{}'.format(mol))
                for c in v:
                    comp = onto.search(label=c)
                    if not comp:
                        continue
                    elif len(comp) == 1:
                        onto,c_i = add_individum(onto,comp[0],c,p_id)
                    else:
                        c_i = [i for i in comp if i in onto.individuals()][0]
                    short = [i for i in rel_synonym.keys() if rel_synonym[i] == c]
                    if short:
                        for i in short:
                            if i not in list(c_i.comment):
                                c_i.comment.append(i)
                                
                    mol.BFO_0000051.append(c_i) #"has part" relation between classes or individuals? chosen individuals because of reasoning time
                    c_i.mentioned_in.append(pub_new)
    return onto

    
def create_subclass(onto,subclass,entities,super_class,created_classes,chem_list,abbreviation,p_id ):
    global num
    new_sub = None  
    created_ind = [i.label[0].lower() for i in onto.individuals() if i.label]
    
    if [c for c in chem_list if re.search(r'\b[\d.,%]*{}\b'.format(re.escape(c)),subclass) if c != subclass]:
        print('subclass:{}'.format(subclass))
        if subclass.lower() not in created_ind:
            onto, new_i = add_individum(onto,super_class,subclass,p_id)            
        else:
            new_i = onto.search_one(label = subclass)
            new_i.is_a.append(super_class)  
    elif subclass in abbreviation.values():
        if subclass.lower() not in created_ind:
            onto, new_i = add_individum(onto,super_class,subclass,p_id)
    elif subclass.lower() == super_class.label[0].lower() or ("role" in super_class.label[0] and "role" not in subclass):    #to implement for reaction
         onto, new_i = add_individum(onto,super_class, subclass,p_id)
    elif subclass.lower() not in created_classes and subclass.lower() not in classes_all:
          class_name = 'DC_{:02d}{:02d}'.format(p_id, num)
          num += 1
          new_sub = types.new_class(class_name,(super_class,))      
          new_sub.label.append(subclass)
          created_classes.append(subclass.lower())
          if subclass in entities:
              if subclass.lower() not in created_ind:
                  onto, new_i = add_individum(onto,new_sub, subclass,p_id)
              elif subclass.lower() in created_ind:
                  new_i = onto.search_one(label=subclass)
                  new_i.is_a.append(super_class)
    elif subclass.lower() not in classes_all and subclass in entities:
        super_class=[i for i in onto.search(label=subclass.lower()) if i in onto.classes()][0]
        if subclass.lower() not in created_ind:
            onto, new_i = add_individum(onto,super_class, subclass,p_id)
        elif subclass in created_ind:
            new_i = [i for i in onto.search(label=subclass) if i in onto.individuals()][0] 
            new_i.is_a.append(super_class)
    if new_sub:
        new_sub.comment.append('created automatically')    

    return onto, created_classes

def add_individum(onto,super_class, ind,p_id):
    global num
    with onto:
        new_i = [i for i in onto.search(label=ind) if i in onto.individuals()]
        if new_i:
            new_i = new_i[0]
        else:
            new_i =  super_class('DC_{:02d}{:02d}'.format(p_id,num))
            num += 1
            
            new_i.label.append(ind)
            new_i.comment.append('created automatically')                
    return onto, new_i        

def create_sub_super(missing, onto, idx, indecies, entities, sup_sub_df, created_classes, chem_list, abbreviation,p_id, subclass = None ):
    global num
    super_class_l = sup_sub_df.loc[idx, 'super_class']
    with onto:
        if super_class_l not in missing or super_class_l in created_classes or super_class_l in classes_all:
            try:
                super_class = [c for c in onto.search(label=super_class_l) if c in onto.classes()][0]
            except:
                try:
                    super_class = [c for c in onto.search(prefLabel=super_class_l) if c in onto.classes()][0]
                except:
                    try:
                        super_class = [c for c in onto.search(label=super_class_l.lower()) if c in onto.classes()][0]
                    except:    
                        super_class = onto.search_one(label=super_class_l+ ' (molecule)')
            if not subclass:
                onto, created_classes = create_subclass(onto, sup_sub_df.loc[idx, 'subclass'], entities, super_class,created_classes,chem_list,abbreviation,p_id=p_id)
        elif super_class_l in list(sup_sub_df['subclass']):
            query = sup_sub_df.query('subclass == "{}"'.format(super_class_l))
            idx = query.index[0]
            subclass=super_class_l
            indecies.extend(list(query.index))
            indecies, onto, super_class,created_classes = create_sub_super(missing, onto, idx, indecies,entities,sup_sub_df,created_classes,chem_list,abbreviation,p_id,subclass=subclass)
            query = sup_sub_df.query('super_class == "{}"'.format(super_class_l))
            if query.empty == False:
                indecies.extend(list(query.index))
                for q in range(len(query)):
                    subclass = query['subclass'].iloc[q]
                    onto, created_classes=create_subclass(onto,subclass,entities,super_class,created_classes,chem_list,abbreviation,p_id=p_id)
                    subclass = None 
        
        else: 
            class_name = 'DC_{:02d}{:02d}'.format(p_id, num)
            num += 1
            super_class = types.new_class(class_name, (Thing,))
            super_class.comment.append('created automatically') 
            super_class.label.append(super_class_l)
            created_classes.append(super_class_l.lower())
        if subclass:
            if subclass.lower() not in created_classes and subclass.lower() not in classes_all:
                if super_class_l== 'chemical substance' or super_class_l in chem_list: #or super_class_l in abbreviation.keys()
                    onto, _ = add_individum(onto,super_class, subclass,p_id)
                    new_sub = super_class
                else:
                    class_name = 'DC_{:02d}{:02d}'.format(p_id, num)
                    num += 1
                    new_sub = types.new_class( class_name,(super_class,))        
                    new_sub.comment.append('created automatically') 
                    new_sub.label.append(subclass)
                    created_classes.append(subclass.lower())
            else:
                new_sub = onto.search_one(label= subclass)
            super_class = new_sub
        if super_class_l.lower() not in created_classes:
            created_classes.append(super_class_l.lower())    

    return  indecies, onto,super_class, created_classes



"""

sup_cat={'SiO2': ['Rh2P', 'RhCo3', 'Rh'],
 'MCM-41': ['RhCo3'],
 'Al2O3': ['Rh', 'Rh', 'Rh', 'Co', 'Co'], #problem mit duplikaten gelöst!
 'Al': ['Rh']}
rel_synonym= {'OH': 'hydroxide',
 'O': 'oxygen atom',
 'H': 'hydrogen atom',
 'Cobalt': 'cobalt atom',
 'Rhodium': 'rhodium atom',
 'hydrotalcite': 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'Rh': 'rhodium atom',
 'hexane': 'hexane',
 'cobalt': 'cobalt atom',
 'Rh3+': 'rhodium',
 'C10': '(z)-13-methyltetradec-2-enoic acid',
 'C': 'carbon atom',
 '1-octene': '1-octene',
 'olefin': 'olefin',
 'Pd': 'palladium',
 'rhodium': 'rhodium atom',
 'aldehyde': 'aldehyde',
 'Fe': 'iron atom',
 'C7H14': '1-heptene',
 'alkene': 'alkene',
 '1-Hexene': '1-hexene',
 '1-decene': '1-decene',
 'Ru': 'ruthenium atom',
 '1-Octene': '1-octene',
 'CoRh': 'cobalt;rhodium',
 'Co': 'cobalt atom',
 '1-Heptene': '1-heptene',
 'Rh3': 'rhodium',
 'C8H16': '1-octene',
 'H2': 'dihydrogen',
 'Pt': 'platinum',
 '1-Decene': '1-decene'}
missing=['dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'Cobalt Rhodium HT',
 'CoRhHT-2',
 'cobalt hydrotalcite',
 'T',
 'CoRh-HT',
 'CoRhHT-3',
 'HT',
 'CoRh-HT-3',
 'heptene',
 'C10H20,96.0',
 'Cobalt Rhodium',
 'α-Co(OH)2',
 'CoRhHT',
 'cobalt;rhodium',
 'CoRh-HT-2',
 'CoRh-HT-1',
 'rhodium',
 'hydroformylation',
 'isomerization',
 'hydroxylation',
 'redox reaction',
 'condensation',
 'washed',
 'ht catalyst role',
 'heterogeneous catalyst role',
 'isomerization',
 'hydroxylation',
 'redox reaction',
 'condensation',
 'washed',
 'ht catalyst role']
match_dict={'http://purl.obolibrary.org/obo/CHEBI_25805': ['oxygen atom', 'oxygen atom'],
 'http://purl.obolibrary.org/obo/CHEBI_87148': ['(z)-13-methyltetradec-2-enoic acid',
  '(Z)-13-methyltetradec-2-enoic acid'],
 'http://purl.obolibrary.org/obo/CHEBI_29021': ['hexane', 'hexane'],
 'http://purl.obolibrary.org/obo/CHEBI_46708': ['1-octene', '1-octene'],
 'http://purl.obolibrary.org/obo/CHEBI_18248': ['iron atom', 'iron atom'],
 'http://purl.obolibrary.org/obo/CHEBI_33641': ['olefin', 'olefin'],
 'http://purl.obolibrary.org/obo/CHEBI_49637': ['hydrogen atom',
  'hydrogen atom'],
 'http://purl.obolibrary.org/obo/CHEBI_17478': ['aldehyde', 'aldehyde'],
 'http://purl.obolibrary.org/obo/CHEBI_16234': ['hydroxide', 'hydroxide'],
 'http://purl.obolibrary.org/obo/CHEBI_33359': ['rhodium atom',
  'rhodium atom'],
 'http://purl.obolibrary.org/obo/CHEBI_27594': ['carbon atom', 'carbon atom'],
 'http://purl.obolibrary.org/obo/CHEBI_32878': ['alkene', 'alkene'],
 'http://purl.obolibrary.org/obo/CHEBI_87315': ['1-decene', '1-decene'],
 'http://purl.obolibrary.org/obo/CHEBI_30682': ['ruthenium atom',
  'ruthenium atom'],
 'http://purl.obolibrary.org/obo/CHEBI_27638': ['cobalt atom', 'cobalt atom'],
 'http://purl.obolibrary.org/obo/CHEBI_33363': ['palladium', 'palladium'],
 'http://purl.obolibrary.org/obo/CHEBI_186747': ['1-heptene', '1-Heptene'],
 'http://purl.obolibrary.org/obo/CHEBI_33364': ['platinum', 'platinum'],
 'http://purl.obolibrary.org/obo/CHEBI_24579': ['1-hexene', '1-hexene'],
 'http://purl.obolibrary.org/obo/CHEBI_18276': ['dihydrogen',
  'dihydrogen (molecule)'],
 'dummy_molecule': ['molecule', 'molecule'],
 'dummy_catalyst role': ['catalyst role', 'catalyst role'],
 'http://purl.obolibrary.org/obo/RXNO_0000272': ['Hydroformylation',
  'hydroformylation'],
 'http://purl.obolibrary.org/obo/MOP_0000369': ['alkylation', 'alkylation'],
 'http://purl.obolibrary.org/obo/MOP_0000589': ['hydrogenation',
  'hydrogenation'],
 'dummy_hydroformylation': ['hydroformylation', 'hydroformylation'],
 'dummy_alkylation': ['alkylation', 'alkylation'],
 'dummy_hydrogenation': ['hydrogenation', 'hydrogenation']}
chem_list=['OH',
 'Cobalt Rhodium HT',
 'hydrotalcite',
 'Rh',
 'hexane',
 'CoRhHT-2',
 'cobalt hydrotalcite',
 'Rh3+',
 'C10',
 '1-octene',
 'olefin',
 'Pd',
 'CoRh-HT',
 'CoRhHT-3',
 'aldehyde',
 'Fe',
 'hydroxide',
 'rhodium',
 'C7H14',
 'CoRh-HT-3',
 'heptene',
 'alkene',
 '1-Hexene',
 '1-decene',
 'C10H20,96.0',
 'Ru',
 '1-Octene',
 'Cobalt Rhodium',
 'CoRh',
 'α-Co(OH)2',
 '1-Heptene',
 'CoRhHT',
 'Rh3',
 'Co',
 'cobalt',
 'C8H16',
 '1-hexene',
 'CoRh-HT-2',
 'H2',
 'CoRh-HT-1',
 'Pt',
 '1-Decene',
 'hydroxide',
 'oxygen atom',
 'hydrogen atom',
 'cobalt atom',
 'rhodium atom',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'rhodium atom',
 'hexane',
 'cobalt atom',
 'rhodium',
 '(z)-13-methyltetradec-2-enoic acid',
 'carbon atom',
 '1-octene',
 'olefin',
 'palladium',
 'rhodium atom',
 'aldehyde',
 'iron atom',
 '1-heptene',
 'alkene',
 '1-hexene',
 '1-decene',
 'ruthenium atom',
 '1-octene',
 'cobalt;rhodium',
 'cobalt atom',
 '1-heptene',
 'rhodium',
 '1-octene',
 'dihydrogen',
 'platinum',
 '1-decene',
 'HT',
 'hydroxide',
 'oxygen atom',
 'hydrogen atom',
 'cobalt atom',
 'rhodium atom',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'rhodium atom',
 'hexane',
 'cobalt atom',
 'rhodium',
 '(z)-13-methyltetradec-2-enoic acid',
 'carbon atom',
 '1-octene',
 'olefin',
 'palladium',
 'rhodium atom',
 'aldehyde',
 'iron atom',
 '1-heptene',
 'alkene',
 '1-hexene',
 '1-decene',
 'ruthenium atom',
 '1-octene',
 'cobalt;rhodium',
 'cobalt atom',
 '1-heptene',
 'rhodium',
 '1-octene',
 'dihydrogen',
 'platinum',
 '1-decene',
 'hydroxide',
 'oxygen atom',
 'hydrogen atom',
 'cobalt atom',
 'rhodium atom',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'rhodium atom',
 'hexane',
 'cobalt atom',
 'rhodium',
 '(z)-13-methyltetradec-2-enoic acid',
 'carbon atom',
 '1-octene',
 'olefin',
 'palladium',
 'rhodium atom',
 'aldehyde',
 'iron atom',
 '1-heptene',
 'alkene',
 '1-hexene',
 '1-decene',
 'ruthenium atom',
 '1-octene',
 'cobalt;rhodium',
 'cobalt atom',
 '1-heptene',
 'rhodium',
 '1-octene',
 'dihydrogen',
 'platinum',
 '1-decene',
 'hydroxide',
 'oxygen atom',
 'hydrogen atom',
 'cobalt atom',
 'rhodium atom',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'rhodium atom',
 'hexane',
 'cobalt atom',
 'rhodium',
 '(z)-13-methyltetradec-2-enoic acid',
 'carbon atom',
 '1-octene',
 'olefin',
 'palladium',
 'rhodium atom',
 'aldehyde',
 'iron atom',
 '1-heptene',
 'alkene',
 '1-hexene',
 '1-decene',
 'ruthenium atom',
 '1-octene',
 'cobalt;rhodium',
 'cobalt atom',
 '1-heptene',
 'rhodium',
 '1-octene',
 'dihydrogen',
 'platinum',
 '1-decene']
categories={'bimetallic cobalt-rhodium layered hydrotalcite-type material': 'Catalyst',
 'CoRh-HT': 'Catalyst',
 'hydroformylation': 'Reaction',
 'alkene': 'Reactant',
 'aldehyde': 'Product',
 'CoRh-based heterogeneous catalyst': 'Catalyst',
 'HRTEM': 'Characterization',
 'powder X-ray diffraction': 'Characterization',
 'X-ray photoelectron spectroscopy': 'Characterization',
 'Hydroformylation': 'Reaction',
 'olefin': 'Reactant',
 'heterogeneous catalyst': 'Catalyst',
 'Fe': 'Catalyst',
 'Co': 'Catalyst',
 'Ru': 'Catalyst',
 'Rh': 'Catalyst',
 'Pd': 'Catalyst',
 'Rh-, Co-, and Pt-based catalyst': 'Catalyst',
 'Rh-and Co-based catalyst': 'Catalyst',
 'linear aldehyde': 'Product',
 'rhodium-and cobalt-based catalyst': 'Catalyst',
 'heterogeneous catalyst based on Rh and Co': 'Catalyst',
 'hydrotalcite (HT)-like material': 'Catalyst',
 'HT-based material': 'Catalyst',
 'alkylation': 'Reaction',
 'isomerization': 'Reaction',
 'hydroxylation': 'Reaction',
 'redox reaction': 'Reaction',
 'condensation': 'Reaction',
 'layered double hydroxide': 'Catalyst',
 'cobalt hydrotalcite': 'Catalyst',
 'rhodium-containing cobalt hydrotalcite': 'Catalyst',
 'in situ sol-gel method': 'Treatment',
 'layered CoRh-HT-type material': 'Catalyst',
 '1-Octene': 'Reactant',
 'C8H16': 'Reactant',
 '1-Decene': 'Reactant',
 'C10H20,96.0': 'Reactant',
 '1-Heptene': 'Reactant',
 'C7H14': 'Reactant',
 '1-Hexene': 'Reactant',
 'layered CoRh-HT type material': 'Catalyst',
 'stirred': 'Treatment',
 'stir': 'Treatment',
 'filtered': 'Treatment',
 'washed': 'Reaction',
 'dried': 'Treatment',
 'CoRhHT-2': 'Catalyst',
 'CoRhHT-3': 'Catalyst',
 'Cobalt Rhodium HT': 'Catalyst',
 'Powder X-ray diffraction': 'Characterization',
 'XRD': 'Characterization',
 'Fourier-transform infrared': 'Characterization',
 'FT-IR': 'Characterization',
 'ICPAES': 'Characterization',
 'X-ray photoelectron spectra': 'Characterization',
 'XPS': 'Characterization',
 '1-hexene': 'Reactant',
 '1-decene': 'Reactant',
 'CoRh-HT catalyst': 'Catalyst',
 '1-octene': 'Reactant',
 'gas chromatography': 'Characterization',
 'layered CoRh-HT': 'Catalyst',
 'rhodium': 'Catalyst',
 'rhodium-containing sample': 'Catalyst',
 'α-Co(OH)2': 'Catalyst',
 'CoRh-HT-3': 'Catalyst',
 'high-resolution transmission electron microscopy': 'Characterization',
 'HR-TEM': 'Characterization',
 'CoRh-HT-1': 'Catalyst',
 'CoRh-HT-2': 'Catalyst',
 'CoRh-HT-type material': 'Catalyst',
 'X-ray photoelectron spectral': 'Characterization',
 'cobalt-rhodium hydrotalcite material': 'Catalyst',
 'Co 2p XPS': 'Characterization',
 'layered CoRh-HT-1 material': 'Catalyst',
 'hydro-formylated product': 'Product',
 'alcohol': 'Product',
 'hydrogenation': 'Reaction',
 'olefin-isomerized product': 'Product',
 'hydroformylated product': 'Product',
 'lower alkene': 'Reactant',
 'hexane': 'Reactant',
 'heptene': 'Reactant',
 'hydroformylation product': 'Product',
 'separated': 'Treatment',
 'isomerized olefin': 'Product',
 'cobalt': 'Catalyst',
 'aldehyde product': 'Product',
 'lighter olefin': 'Reactant',
 'C10': 'Product',
 'C8': 'Product',
 'C7': 'Reactant',
 'isomerized product': 'Product',
 'branched aldehyde': 'Product',
 'linear alkene': 'Reactant',
 'branched alkene': 'Product',
 'pure cobalt hydrotalcite': 'Catalyst',
 'HT': 'Catalyst',
 'layered hydrotalcite-type material': 'Catalyst',
 'Rh3+-containing layered CoRh-HT-type material': 'Catalyst'}
reac_dict={'hydroformylation': ['alkene', 'olefin', 'hydro-formylated product'],
 '1-decene': ['CoRh-HT catalyst'],
 'hydrogenation': ['olefin-isomerized product'],
 'aldehyde': ['lower alkene'],
 'isomerization': ['linear alkene']} #checken warum so
abbreviation={'CoRh-HT': 'bimetallic cobalt-rhodium layered hydrotalcite-type material',
 'FT-IR': 'Fourier-transform infrared',
 'XPS': 'X-ray photoelectron spectral',
 'HR-TEM': 'high-resolution transmission electron microscopy'}
onto_new_dict={'CoRhHT-2': [],
 'CoRhHT-3': [],
 'CoRh-HT-3': [],
 'CoRh-HT-2': [],
 'CoRh-HT-1': [],
 'hydroxide': ['oxygen atom', 'hydrogen atom'],
 'Cobalt Rhodium HT': ['cobalt atom', 'rhodium atom', 'HT'],
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate': ['dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 'rhodium atom': ['rhodium atom'],
 'hexane': ['hexane'],
 'cobalt hydrotalcite': ['cobalt atom',
  'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 'rhodium': ['rhodium atom'],
 '(z)-13-methyltetradec-2-enoic acid': ['carbon atom'],
 '1-octene': ['carbon atom', 'hydrogen atom'],
 'olefin': ['olefin'],
 'palladium': ['palladium'],
 'CoRh-HT': ['cobalt atom', 'rhodium atom'],
 'aldehyde': ['aldehyde'],
 'iron atom': ['iron atom'],
 '1-heptene': ['1-heptene'],
 'heptene': ['heptene'],
 'alkene': ['alkene'],
 '1-hexene': ['1-hexene'],
 '1-decene': ['1-decene'],
 'C10H20,96.0': ['carbon atom', 'hydrogen atom'],
 'ruthenium atom': ['ruthenium atom'],
 'Cobalt Rhodium': ['cobalt atom', 'rhodium atom'],
 'cobalt;rhodium': ['cobalt atom', 'rhodium atom'],
 'α-Co(OH)2': ['cobalt atom', 'oxygen atom', 'hydrogen atom'],
 'CoRhHT': ['cobalt atom', 'rhodium atom', 'hydrogen atom', 'T'],
 'cobalt atom': ['cobalt atom'],
 'dihydrogen': ['hydrogen atom'],
 'platinum': ['platinum']}

entities_raw={'bimetallic cobalt-rhodium layered hydrotalcite-type material': ['bimetallic cobalt-rhodium layered hydrotalcite-type material'],
 'CoRh-HT': ['CoRh-HT'],
 'hydroformylation': ['hydroformylation'],
 'alkene': ['alkene'],
 'aldehyde': ['aldehyde'],
 'CoRh-based heterogeneous catalyst': ['Co-Rh-based heterogeneous catalyst'],
 'HRTEM': ['HRTEM'],
 'powder X-ray diffraction': ['powder X-ray diffraction'],
 'X-ray photoelectron spectroscopy': ['X-ray photoelectron spectroscopy'],
 'Hydroformylation': ['Hydroformylation'],
 'olefin': ['olefin'],
 'heterogeneous catalyst': ['heterogeneous catalyst'],
 'Fe': ['Fe'],
 'Co': ['Co'],
 'Ru': ['Ru'],
 'Rh': ['Rh'],
 'Pd': ['Pd'],
 'Rh-, Co-, and Pt-based catalyst': ['Rh-, Co-, and Pt-based catalyst'],
 'Rh-and Co-based catalyst': ['Rh- and Co-based catalyst'],
 'linear aldehyde': ['linear aldehyde'],
 'rhodium-and cobalt-based catalyst': ['rhodium- and cobalt-based catalyst'],
 'heterogeneous catalyst based on Rh and Co': ['heterogeneous catalyst based on Rh and Co'],
 'hydrotalcite (HT)-like material': ['hydrotalcite (HT)-like material'],
 'HT-based material': ['HT-based material'],
 'alkylation': ['alkylation'],
 'isomerization': ['isomerization'],
 'hydroxylation': ['hydroxylation'],
 'redox reaction': ['redox reaction'],
 'condensation': ['condensation'],
 'layered double hydroxide': ['layered double hydroxide'],
 'cobalt hydrotalcite': ['cobalt hydrotalcite'],
 'rhodium-containing cobalt hydrotalcite': ['rhodium-containing cobalt hydrotalcite'],
 'in situ sol-gel method': ['in situ sol-gel method'],
 'layered CoRh-HT-type material': ['layered CoRh-HT-type material'],
 '1-Octene': ['1-Octene'],
 'C8H16': ['C8H16'],
 '1-Decene': ['1-Decene'],
 'C10H20,96.0': ['C10H20,96.0'],
 '1-Heptene': ['1-Heptene'],
 'C7H14': ['C7H14'],
 '1-Hexene': ['1-Hexene'],
 'layered CoRh-HT type material': ['layered Co-Rh-HT type material'],
 'stirred': ['stirred'],
 'stir': ['stir'],
 'filtered': ['filtered'],
 'washed': ['washed'],
 'dried': ['dried'],
 'CoRhHT-2': ['CoRhHT-2'],
 'CoRhHT-3': ['CoRhHT-3'],
 'Cobalt Rhodium HT': ['Cobalt Rhodium HT'],
 'Powder X-ray diffraction': ['Powder X-ray diffraction'],
 'XRD': ['XRD'],
 'Fourier-transform infrared': ['Fourier-transform infrared'],
 'FT-IR': ['FT-IR'],
 'ICPAES': ['ICP-AES'],
 'X-ray photoelectron spectra': ['X-ray photoelectron spectra'],
 'XPS': ['XPS'],
 '1-hexene': ['1-hexene'],
 '1-decene': ['1-decene'],
 'CoRh-HT catalyst': ['CoRh-HT catalyst'],
 '1-octene': ['1-octene'],
 'gas chromatography': ['gas chromatography'],
 'layered CoRh-HT': ['layered CoRh-HT'],
 'rhodium': ['rhodium'],
 'rhodium-containing sample': ['rhodium-containing sample'],
 'α-Co(OH)2': ['α-Co(OH)2'],
 'CoRh-HT-3': ['CoRh-HT-3'],
 'high-resolution transmission electron microscopy': ['high-resolution transmission electron microscopy'],
 'HR-TEM': ['HR-TEM'],
 'CoRh-HT-1': ['CoRh-HT-1'],
 'CoRh-HT-2': ['CoRh-HT-2'],
 'CoRh-HT-type material': ['CoRh-HT-type material'],
 'X-ray photoelectron spectral': ['X-ray photoelectron spectral'],
 'cobalt-rhodium hydrotalcite material': ['cobalt-rhodium hydrotalcite material'],
 'Co 2p XPS': ['Co 2p XPS'],
 'layered CoRh-HT-1 material': ['layered CoRh-HT-1 material'],
 'hydro-formylated product': ['hydro-formylated product'],
 'alcohol': ['alcohol'],
 'hydrogenation': ['hydrogenation'],
 'olefin-isomerized product': ['olefin-isomerized product'],
 'hydroformylated product': ['hydroformylated product'],
 'lower alkene': ['lower alkene'],
 'hexane': ['hexane'],
 'heptene': ['heptene'],
 'hydroformylation product': ['hydroformylation product'],
 'separated': ['separated'],
 'isomerized olefin': ['isomerized olefin'],
 'cobalt': ['cobalt'],
 'aldehyde product': ['aldehyde product'],
 'lighter olefin': ['lighter olefin'],
 'C10': ['C10'],
 'C8': ['C8'],
 'C7': ['C7'],
 'isomerized product': ['isomerized product'],
 'branched aldehyde': ['branched aldehyde'],
 'linear alkene': ['linear alkene'],
 'branched alkene': ['branched alkene'],
 'pure cobalt hydrotalcite': ['pure cobalt hydrotalcite'],
 'HT': ['HT'],
 'layered hydrotalcite-type material': ['layered hydrotalcite-type material'],
 'Rh3+-containing layered CoRh-HT-type material': ['Rh3+-containing layered CoRh-HT-type material']}
p_id = 1
df_entity, rel_synonym, missing_all, match_dict_all = preprocess_classes(categories, abbreviation, onto_new_dict, sup_cat, rel_synonym, chem_list, missing, match_dict,entities_raw)
created_classes,sup_sub_df = create_classes_onto(abbreviation, sup_cat, missing_all, match_dict_all, df_entity,reac_dict,p_id,rel_synonym,chem_list,onto_new_dict)

match_dict_all={'http://purl.obolibrary.org/obo/CHEBI_18276': ['dihydrogen',
  'dihydrogen (molecule)'],
 'http://purl.obolibrary.org/obo/CHEBI_87315': ['1-decene', '1-decene'],
 'dummy_oxygen atom': ['oxygen atom', 'oxygen atom'],
 'http://purl.obolibrary.org/obo/CHEBI_18248': ['iron atom', 'iron atom'],
 'dummy_rhodium atom': ['rhodium atom', 'rhodium atom'],
 'http://purl.obolibrary.org/obo/CHEBI_33364': ['platinum', 'platinum'],
 'dummy_olefin': ['olefin', 'olefin'],
 'http://purl.obolibrary.org/obo/CHEBI_33363': ['palladium', 'palladium'],
 'dummy_cobalt atom': ['cobalt atom', 'cobalt atom'],
 'http://purl.obolibrary.org/obo/CHEBI_46708': ['1-octene', '1-octene'],
 'dummy_carbon atom': ['carbon atom', 'carbon atom'],
 'dummy_hydrogen atom': ['hydrogen atom', 'hydrogen atom'],
 'http://purl.obolibrary.org/obo/CHEBI_186747': ['1-heptene', '1-Heptene'],
 'dummy_aldehyde': ['aldehyde', 'aldehyde'],
 'http://purl.obolibrary.org/obo/CHEBI_87148': ['(z)-13-methyltetradec-2-enoic acid',
  '(Z)-13-methyltetradec-2-enoic acid'],
 'http://purl.obolibrary.org/obo/CHEBI_24579': ['1-hexene', '1-hexene'],
 'http://purl.obolibrary.org/obo/CHEBI_30682': ['ruthenium atom',
  'ruthenium atom'],
 'http://purl.obolibrary.org/obo/CHEBI_16234': ['hydroxide', 'hydroxide'],
 'http://purl.obolibrary.org/obo/CHEBI_29021': ['hexane', 'hexane'],
 'dummy_alkene': ['alkene', 'alkene'],
 'dummy_molecule': ['molecule', 'molecule'],
 'dummy_catalyst role': ['catalyst role', 'catalyst role'],
 'http://purl.obolibrary.org/obo/RXNO_0000272': ['Hydroformylation',
  'hydroformylation'],
 'http://purl.obolibrary.org/obo/MOP_0000369': ['alkylation', 'alkylation'],
 'http://purl.obolibrary.org/obo/MOP_0000589': ['hydrogenation',
  'hydrogenation']}


missing_all=['rhodium',
 'CoRh-HT-1',
 'Cobalt Rhodium HT',
 'CoRhHT-3',
 'cobalt hydrotalcite',
 'CoRh-HT-2',
 'heptene',
 'Cobalt Rhodium',
 'T',
 'HT',
 'CoRhHT-2',
 'α-Co(OH)2',
 'cobalt;rhodium',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'C10H20,96.0',
 'CoRhHT',
 'hydroformylation',
 'heterogeneous catalyst role',
 'heterogeneous catalyst role',
 'heterogeneous catalyst role',
 'isomerization',
 'hydroxylation',
 'redox reaction',
 'condensation',
 'washed']
chem_list=['Pt',
 'rhodium',
 'Ru',
 'cobalt',
 '1-decene',
 'CoRh-HT-1',
 '1-Decene',
 'Rh3+',
 'Rh3',
 'hydrotalcite',
 'Fe',
 'Cobalt Rhodium HT',
 'CoRhHT-3',
 'OH',
 'cobalt hydrotalcite',
 'CoRh',
 '1-Hexene',
 '1-Octene',
 'C7H14',
 'olefin',
 'CoRh-HT-2',
 'heptene',
 '1-octene',
 'H2',
 'Cobalt Rhodium',
 'C10',
 'Co',
 'CoRhHT-2',
 'α-Co(OH)2',
 'aldehyde',
 '1-Heptene',
 'Rh',
 'C10H20,96.0',
 'CoRh-HT',
 'CoRhHT'
 '1-hexene',
 'C8H16',
 'Pd',
 'hydroxide',
 'hexane',
 'alkene',
 'platinum',
 'rhodium atom',
 'ruthenium atom',
 'cobalt atom',
 '1-decene',
 '1-decene',
 'rhodium',
 'rhodium atom',
 'rhodium',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'iron atom',
 'cobalt atom',
 'rhodium atom',
 'hydroxide',
 'oxygen atom',
 'hydrogen atom',
 'cobalt;rhodium',
 'cobalt atom',
 '1-hexene',
 '1-octene',
 '1-heptene',
 'carbon atom',
 'olefin',
 'dihydrogen',
 '(z)-13-methyltetradec-2-enoic acid',
 'aldehyde',
 '1-heptene',
 '1-octene',
 'palladium',
 'hexane',
 'alkene',
 'HT',
 'platinum',
 'rhodium atom',
 'ruthenium atom',
 'cobalt atom',
 '1-decene',
 '1-decene',
 'rhodium',
 'rhodium atom',
 'rhodium',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'iron atom',
 'cobalt atom',
 'rhodium atom',
 'hydroxide',
 'oxygen atom',
 'hydrogen atom',
 'cobalt;rhodium',
 'cobalt atom',
 '1-hexene',
 '1-octene',
 '1-heptene',
 'carbon atom',
 'olefin',
 'dihydrogen',
 '(z)-13-methyltetradec-2-enoic acid',
 'aldehyde',
 '1-heptene',
 '1-octene',
 'palladium',
 'hexane',
 'alkene',
 'Pt',
 'platinum',
 'rhodium atom',
 'ruthenium atom',
 'cobalt atom',
 '1-decene',
 '1-decene',
 'rhodium',
 'rhodium atom',
 'rhodium',
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'iron atom',
 'cobalt atom',
 'rhodium atom',
 'hydroxide',
 'oxygen atom',
 'hydrogen atom',
 'cobalt;rhodium',
 'cobalt atom',
 '1-hexene',
 '1-octene',
 '1-heptene',
 'carbon atom',
 'olefin',
 'dihydrogen',
 '(z)-13-methyltetradec-2-enoic acid',
 'aldehyde',
 '1-heptene',
 '1-octene',
 'palladium',
 'hexane',
 'alkene']
#categ={'heterogeneous catalyst based on Rh and Co':'Catalyst'}

abbreviation={'bimetallic cobalt-rhodium layered hydrotalcite-type material': 'CoRh-HT',
 'Fourier-transform infrared': 'FT-IR',
 'X': 'XPS',
 'X-ray photoelectron spectra': 'XPS',
 'high-resolution transmission electron microscopy': 'HR-TEM',
 'X-ray photoelectron spectral': 'XPS'}
onto_new_dict={'CoRh-HT-1': [],
 'CoRhHT-3': [],
 'CoRh-HT-2': [],
 'CoRhHT-2': [],
 'platinum': ['platinum'],
 'rhodium atom': ['rhodium atom'],
 'ruthenium atom': ['ruthenium atom'],
 'cobalt atom': ['cobalt atom'],
 '1-decene': ['1-decene'],
 'rhodium': ['rhodium atom'],
 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate': ['dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 'iron atom': ['iron atom'],
 'Cobalt Rhodium HT': ['cobalt atom', 'rhodium atom', 'HT'],
 'hydroxide': ['oxygen atom', 'hydrogen atom'],
 'cobalt hydrotalcite': ['cobalt atom',
  'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 'cobalt;rhodium': ['cobalt atom', 'rhodium atom'],
 '1-hexene': ['1-hexene'],
 '1-octene': ['carbon atom', 'hydrogen atom'],
 '1-heptene': ['1-heptene'],
 'olefin': ['olefin'],
 'heptene': ['heptene'],
 'dihydrogen': ['hydrogen atom'],
 'Cobalt Rhodium': ['cobalt atom', 'rhodium atom'],
 '(z)-13-methyltetradec-2-enoic acid': ['carbon atom'],
 'α-Co(OH)2': ['cobalt atom', 'oxygen atom', 'hydrogen atom'],
 'aldehyde': ['aldehyde'],
 'C10H20,96.0': ['carbon atom', 'hydrogen atom'],
 'CoRhHT': ['cobalt atom', 'rhodium atom', 'hydrogen atom', 'T'],
 'palladium': ['palladium'],
 'hexane': ['hexane'],
 'alkene': ['alkene']}

sup_cat={}
rel_synonym={'Pt': 'platinum',
 'rhodium': 'rhodium atom',
 'Ru': 'ruthenium atom',
 'cobalt': 'cobalt atom',
 '1-decene': '1-decene',
 '1-Decene': '1-decene',
 'Rh3+': 'rhodium',
 'Rh': 'rhodium atom',
 'Rh3': 'rhodium',
 'hydrotalcite': 'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate',
 'Fe': 'iron atom',
 'Cobalt': 'cobalt atom',
 'Rhodium': 'rhodium atom',
 'OH': 'hydroxide',
 'O': 'oxygen atom',
 'H': 'hydrogen atom',
 'CoRh': 'cobalt;rhodium',
 'Co': 'cobalt atom',
 '1-Hexene': '1-hexene',
 '1-Octene': '1-octene',
 'C7H14': '1-heptene',
 'C': 'carbon atom',
 'olefin': 'olefin',
 'H2': 'dihydrogen',
 'C10': '(z)-13-methyltetradec-2-enoic acid',
 'aldehyde': 'aldehyde',
 '1-Heptene': '1-heptene',
 'C8H16': '1-octene',
 'Pd': 'palladium',
 'hexane': 'hexane',
 'alkene': 'alkene'}



entity=['alkene',
 'aldehyde',
 'olefin',
 'iron atom',
 'cobalt atom',
 'ruthenium atom',
 'rhodium atom',
 'palladium',
 'cobalt hydrotalcite',
 '1-octene',
 '1-decene',
 'C10H20,96.0',
 '1-heptene',
 '1-hexene',
 'CoRhHT-2',
 'CoRhHT-3',
 'Cobalt Rhodium HT',
 'α-Co(OH)2',
 'CoRh-HT-1',
 'CoRh-HT-2',
 'hexane',
 'heptene',
 '(z)-13-methyltetradec-2-enoic acid',
 'HT',
 'bimetallic cobalt-rhodium layered hydrotalcite-type material',
 'CoRh-HT',
 'hydroformylation',
 'CoRh-based heterogeneous catalyst',
 'Hydroformylation',
 'heterogeneous catalyst',
 'linear aldehyde',
 'heterogeneous catalyst based on Rh and Co',
 'hydrotalcite (HT)-like material',
 'alkylation',
 'isomerization',
 'hydroxylation',
 'redox reaction',
 'condensation',
 'layered double hydroxide',
 'rhodium-containing cobalt hydrotalcite',
 'layered CoRh-HT-type material',
 'layered CoRh-HT type material',
 'washed',
 'CoRh-HT catalyst',
 'layered CoRh-HT',
 'rhodium-containing sample',
 'CoRh-HT-3',
 'CoRh-HT-type material',
 'cobalt-rhodium hydrotalcite material',
 'layered CoRh-HT-1 material',
 'hydrogenation',
 'lower alkene',
 'isomerized olefin',
 'lighter olefin',
 'branched aldehyde',
 'linear alkene',
 'branched alkene',
 'pure cobalt hydrotalcite',
 'layered hydrotalcite-type material',
 'Rh3+-containing layered CoRh-HT-type material']
classes=[[],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 [],
 ['catalyst role'],
 ['catalyst role'],
 ['hydroformylation'],
 ['heterogeneous catalyst role'],
 ['Hydroformylation'],
 ['heterogeneous catalyst role'],
 [],
 ['heterogeneous catalyst role'],
 ['catalyst role'],
 ['alkylation'],
 ['isomerization'],
 ['hydroxylation'],
 ['redox reaction'],
 ['condensation'],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role'],
 ['washed'],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role'],
 ['hydrogenation'],
 [],
 [],
 [],
 [],
 [],
 [],
 ['catalyst role'],
 ['catalyst role'],
 ['catalyst role']]
cems=[['alkene'],
 ['aldehyde'],
 ['olefin'],
 ['iron atom'],
 ['cobalt atom'],
 ['ruthenium atom'],
 ['rhodium atom'],
 ['palladium'],
 ['cobalt hydrotalcite'],
 ['1-octene'],
 ['1-decene'],
 ['C10H20,96.0'],
 ['1-heptene'],
 ['1-hexene'],
 ['CoRhHT-2'],
 ['CoRhHT-3'],
 ['Cobalt Rhodium HT'],
 ['rhodium'],
 ['α-Co(OH)2'],
 ['CoRhHT-1'],
 ['hexane'],
 ['heptene'],
 ['(z)-13-methyltetradec-2-enoic acid'],
 ['cobalt atom',
  'rhodium',
  'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 [],
 ['cobalt;rhodium'],
 [],
 [],
 ['aldehyde'],
 ['cobalt atom', 'rhodium atom'],
 ['dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 [],
 [],
 [],
 [],
 [],
 ['hydroxide'],
 ['cobalt atom', 'cobalt hydrotalcite', 'rhodium'],
 [],
 ['cobalt;rhodium'],
 [],
 [],
 [],
 ['rhodium'],
 [],
 ['cobalt atom',
  'rhodium',
  'dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 ['CoRhHT-1'],
 [],
 ['alkene'],
 ['olefin'],
 ['olefin'],
 ['aldehyde'],
 ['alkene'],
 ['alkene'],
 ['cobalt atom', 'cobalt hydrotalcite'],
 [],
 ['dialuminum;hexamagnesium;oxygen(2-);carbonate;dodecahydrate'],
 ['rhodium']]
category=['Reactant',
 'Product',
 'Reactant',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Reactant',
 'Reactant',
 'Reactant',
 'Reactant',
 'Reactant',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Reactant',
 'Reactant',
 'Product',
 'Catalyst',
 'Reaction',
 'Catalyst',
 'Reaction',
 'Catalyst',
 'Product',
 'Catalyst',
 'Catalyst',
 'Reaction',
 'Reaction',
 'Reaction',
 'Reaction',
 'Reaction',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Reaction',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Reaction',
 'Reactant',
 'Product',
 'Reactant',
 'Product',
 'Reactant',
 'Product',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst']
d={'entity':entity,'classes':classes,'cems':cems, 'category':category}
df_entity=pd.DataFrame(data=d)


created_classes,sup_sub_df = create_classes_onto(abbreviation, sup_cat, missing_all, match_dict_all, df_entity,reac_dict,p_id,rel_synonym,chem_list,onto_new_dict)

A method for the synthesis of highly crystalline Rh2P nanoparticles on SiO2 support materials and their use as truly heterogeneous
 single-site catalysts for the hydroformylation of ethylene and propylene is presented. The supported Rh2P nanoparticles were investigated 
 by transmission electron microscopy and by infrared analysis of adsorbed CO. The inﬂuence of feed gas composition and reaction temperature 
 on the activity and selectivity in the hydroformylation reaction was evaluated by using high throughput experimentation as an enabling 
 element; core ﬁndings were that beneﬁcial eﬀects on the selectivity were observed at high CO partial pressures and after addition of water
 to the feed gas. The analytical and performance data of the materials gave evidence that high temperature reduction leading to highly 
 crystalline Rh2P nanoparticles is key to achieving active, selective, and long- term stable catalysts. KEYWORDS: hydroformylation, 
 heterogeneous, rhodium, phosphide, nanoparticles, ethylene The reaction mechanisms of heterogeneous hydro- formylation of ethylene and 
 propylene were compared at 413−453 K using RhCo3/MCM-41 as catalysts. The reaction rates of propylene for both hydroformylation and the 
 undesired side reaction of hydrogenation were found to be about one order of magnitude lower than those for ethylene in ﬂow reactor studies.
 The diﬀerence in the kinetic behavior between ethylene and propylene was investigated by measuring the reaction orders and apparent 
 activation energies, and these macrokinetic observables were analyzed using the degree of rate control (DRC) method. In situ diﬀuse 
 reﬂectance infrared Fourier transform spectroscopy (DRIFTS) experiments were performed to characterize the surface intermediates formed
 during the reactions. When the reactant was changed from ethylene to propylene, the IR peak corresponding to adsorbed CO exhibited a 
 signiﬁcant increase, while the IR peaks of the alkyl group decreased in magnitude. Combined with the DRIFTS results, DRC analysis indicates
 that the ﬁrst step of oleﬁn hydroformylation, the formation of an alkyl group on the catalyst surface, plays a key role in the diﬀerence
 between ethylene and propylene. This step is kinetically nonrelevant when ethylene is the reactant, but it is one of the rate-controlling 
 steps for propylene. The low concentration of the adsorbed propyl group, which is a common intermediate shared by both hydroformylation and 
 hydrogenation of propylene, decreases the rates of both reaction pathways as compared to ethylene. KEYWORDS: hydroformylation, ethylene, 
 propylene, kinetics, degree of rate controlA bimetallic SiO2-supported RhCo3 cluster catalyst derived from Rh4(CO)12 and Co2(CO)8 by 
 coimpregnation followed by decarbonylation under H2 at 623 K has been probed by atmospheric ethylene hydroformylation at 423 K. 
 The catalytic behavior is consistent with that of RhCo3/SiO2 derived from RhCo3(CO)12. At the same time, the corresponding binary 
 catalysts prepared from inorganic rhodium and cobalt salts exhibit much lower activities than RhCo3/SiO2 and significantly enhanced 
 activities compared to monometallic catalysts. The results suggest that the increase in catalytic activity by combination of rhodium and 
 cobalt is attributed to the bimetallic catalysis by RhCo3 clusters regardless of the synergistic catalysis by monometallic rhodium and 
 cobalt sites.Intrinsic hydroformylation kinetics have been measured in a high-throughput kinetic test setup at temperatures varying from 
 448 to 498 K, with the total pressure ranging from 1 to 3 MPa. A gaseous feed containing CO, C 2H4 and H2 was used with space times varying
 from 2.7 kgcat s/molC2H4,in to 149 kgcat s/molC2H4,in. Three catalysts have been investigated, i.e., 5%Rh on Al2O3, 1%Co on 
 Al2O3 and 0.5%Co-0.5%Rh on Al2O3. The main products observed were ethane, propanal and propanol. The Rh catalyst showed the highest 
 hydroformylation and hydrogenation site time conversions in the investigated range of operating conditions. Moreover it was found on 
 all investigated catalysts that the hydrogenation activation energy was about 15-20 kJ mol-1 higher than that for hydroformylation. On the
 Rh catalyst, higher ethylene feed concentrations have a more pronounced effect on CO conversion and production of propanal and propanol 
 compared with an increase in the inlet concentration of the other reactants.© 2013 Elsevier B.V. All rights reserved.
 Ethylene hydroformylation and carbon monoxide hydrogenation (leading to methanol and C2-oxygenates) over Rh/SiO2 catalysts share several 
 important common mechanistic features, namely, CO insertion and metal-carbon (acyl or alkyl) bond hydrogenation. However, these processes 
 are differentiated in that the CO hydrogenation also requires an initial CO dissociation before catalysis can proceed. In this study, the 
 catalytic response to changes in particle size and to the addition of metal additives was studied to elucidate the differences in the two 
 processes. In the hydroformylation process, both hydroformylation and hydrogenation of ethylene occurred concurrently. The desirable 
 hydroformylation was enhanced over fine Rh particles with maximum activity observed at a particle diameter of 3.5 nm and hydrogenation was 
 favored over large particles. CO hydrogenation was favored by larger particles. These results suggest that hydroformylation occurs at the 
 edge and corner Rh sites, but that the key step in CO hydrogenation is different from that in hydroformylation and occurs on the surface.
 The addition of group II-VIII metal oxides, such as MoO3, Sc2O3, TiO2, V2O5, and Mn2O3, which are expected to enhance CO dissociation,
 leads to increased rates in CO hydrogenation, but only served to slow the hydroformylation process slightly without any effect on the 
 selectivity. Similar comparisons using basic metals, such as the alkali and alkaline earths, which should enhance selectivity for insertion
 of CO over hydrogenation, increased the selectivity for the hydroformylation over hydrogenation as expected, although catalytic activity
 was reduced. Similarly, the selectivity toward organic oxygenates (a reflection of the degree of CO insertion) in CO hydrogenation was also
 increased.The reduction of cobalt and rhodium salts coadsorbed on silica by aqueous NaBH4 at 273 K in Ar allows the synthesis of catalytic 
 systems formed by very small rhodium crystallites (< 4 nm) and cobalt oxide/hydroxide. The presence of an unreduced cobalt species is well 
 documented by TPR and XPS. The cobalt oxide is probably deposited on the rhodium surface, obscuring a large amount of the active metal 
 centers. As can be judged by FT-IR and XRD data the morphology of the system is not modified by thermal treatments in CO and H2."""
 