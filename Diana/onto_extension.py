# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 15:43:18 2023

@author: smdicher
"""
import spacy
import re
import pandas as pd
from preprocess_onto import *



def preprocess_classes(categories, sup_cat, rel_synonym, chem_list, missing_all, match_dict_all):
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
                                    classes,_ = check_in_snip(e_snip, classes, entity,l,chem_list)
                elif entity not in chem_list and not set(entity.split()).issubset(chem_list):
                    sup_i = False
                    entity_n = entity
                    if re.search('supported on', entity):
                        #Rh-Co based system supported on alumina, titania and silica                                    
                        e_btwn=entity[re.search('supported on ', entity).end():]
                        sup_i=True                            
                    elif re.search('supported', entity) and re: #bimetallic SiO2-supported RhCo3 cluster catalyst 
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
                                eq_idx=e_btwn.find('=') #RhM3/MCM-41, M = Fe, Co, Ni, Cu, or Zn
                                if eq_idx != -1: 
                                    if re.search(pattern,entity_n).start() < eq_idx:
                                        support.append(c_t)
                                else: 
                                    support.append(c_t)
                            if c_t not in spans_n:    
                                spans_n.append(c_t)                    
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
            if len(entity.split()) > 1 and set(entity.split()).issubset(chem_list):    
                chem_e.append(' '.join(c_list))
                
        elif entity.split()[-1] in chem_list and entity not in classes.keys():
            #i.e. light olefin
            classes,_ = check_in_snip(entity, classes, entity, l,chem_list)
            c_t = rel_synonym[entity.split()[-1]] if entity.split()[-1] in rel_synonym.keys() else entity.split()[-1]
            spans_dict[entity].append(c_t)        
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
    df_entity = pd.DataFrame(list_all, columns=['entity','classes', 'cems', 'category'])
    missing,match_dict = create_list_IRIs(v_all, IRI_json_filename = 'iriDictionary') 
    missing_all.extend(missing)   
    match_dict_all.update(match_dict)      
      
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
                            classes[entity].append(token_new) # Problem: from 'bimetallic SiO2-supported RhCo3 cluster catalyst' only 'cluster catalyst role'
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
        if len(doc_snip) > 1:
            for token in doc_snip:
                if token.head.text == token.text:
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
    return classes,head

def check_in_children(token, token_new,list_token):
    if token.children:
       for t in token.children:
                token = t
                token_new = t.text.lower() +' ' + token_new
                list_token = check_in_children(token, token_new,list_token)
                list_token.append(token_new)
    return list_token        

def create_classes_onto(abbreviation, sub_cat, missing, match_dict, df_entity,reac_dict,p_id,rel_synonym,chem_list):
    global num
    num = 0 
    sup_sub_df = pd.DataFrame(columns=['super_class','subclass'])
    new_world = owlready2.World()
    created_classes = []
    onto = new_world.get_ontology('./ontologies/{}.owl'.format(onto_name)).load()
    chem_sub = {}
    chem_list.extend([str(i) for i in rel_synonym.values()])
    for row in df_entity.itertuples():
        classes_parent = []
        classes = sorted(list(row.classes),reverse = False, key = len)
        if row.cems: 
            if row.category == 'Catalyst' and row.cems[0]!=row.entity:
                sup_sub_df = sup_sub_df.append({'super_class':'chemical substance', 'subclass': row.entity},ignore_index=True)
            for c in row.cems:
                if c in match_dict.values():
                    if c.lower() not in [i.label[0].lower() for i in onto.individuals() if i.label]:
                        cem = onto.search_one(label = c)
                        if not cem:
                            cem = onto.search_one(label = c + ' (molecule)')
                        onto,_ = add_individum(onto,cem, c,p_id = p_id) 
                    
                elif len(c.split()) > 1:
                    for i in range(len(c.split())):
                        if c.split()[i] in match_dict.values(): 
                            sup_sub_df = sup_sub_df.append({'super_class':c.split()[i], 'subclass': c},ignore_index = True)                         
                    if c in sup_cat.keys():
                        sup_sub_df = sup_sub_df.append({'super_class':'support material', 'subclass': c},ignore_index = True)
                    elif c not in list(sup_sub_df['subclass']):
                        sup_sub_df = sup_sub_df.append({'super_class':'molecule', 'subclass': c},ignore_index = True)
                elif c in sup_cat.keys():
                    sup_sub_df = sup_sub_df.append({'super_class':'support material', 'subclass': c},ignore_index = True)                       
                else:
                    sup_sub_df = sup_sub_df.append({'super_class':'molecule', 'subclass': c},ignore_index = True)
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
            
            if row.entity not in list(sup_sub_df['subclass']):    
                for i in classes_parent:
                    sup_sub_df = sup_sub_df.append({'super_class':i, 'subclass':row.entity},ignore_index = True)
            else:
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
                    
                if k in match_dict.values() and k.lower() not in [i.label[0].lower() for i in onto.individuals() if i.label]:
                     onto, _ = add_individum(onto,onto.search_one(label = k), k,p_id = p_id)     

                elif k.split()[i] in match_dict.values():
                    sup_sub_df = sup_sub_df.append({'super_class': k.split()[i], 'subclass':k},ignore_index=True)
                else:
                    sup_sub_df = sup_sub_df.append({'super_class': 'chemical reaction (molecular)', 'subclass':k},ignore_index = True)
                #sup_sub_df=sup_sub_df.append({'super_class':i, 'subclass':row.entity},ignore_index=True) #überdenken
                       
    with onto:
        
        support_mat = onto.search_one(label='support material')
        if not support_mat:
            support_mat = types.new_class('DC_{:02d}{:02d}'.format(p_id,num), (onto.search_one(label = 'material'),))
            support_mat.label.append('support material')
            num += 1
            created_classes.append('support material')
        #print(has_role)
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
            elif s.super_class == 'molecule' or s.super_class == 'support material' or s.super_class == 'chemical substance':
                indecies, onto,_,created_classes = create_sub_super(missing, onto,s.Index, indecies,entities, sup_sub_df,created_classes,chem_list,p_id,s.subclass)
            else:
                indecies, onto,_,created_classes = create_sub_super(missing, onto,s.Index, indecies,entities, sup_sub_df,created_classes,chem_list,p_id = p_id)
        
        
        for row in df_entity.itertuples():
            if row.cems:
                e_ind = [i for i in list(onto.search(label=row.entity)) if i in list(onto.individuals())][0]

                if row.category == 'Catalyst' and row.entity in chem_sub.keys():
                    for c in chem_sub[row.entity]: #assign catalyst roles
                        try:
                            cat_cl = [i for i in list(onto.search(label=c)) if i in list(onto.individuals())][0]
                        except:
                            onto,cat_cl =add_individum(onto,list(onto.search(label = c))[0], c ,p_id)
                        e_ind.RO_0000087.append(cat_cl) #'has role' = RO_0000087
                for c in row.cems:
                    if c != row.entity and not row.classes:
                        onto, ind = add_individum(onto,list(onto.search(label = c))[0], row.entity,p_id)
                    else:
                        try:
                            ind = [i for i in list(onto.search(label = c)) if i in list(onto.individuals())][0]
                        except:
                            print('c in row.cems individuum added:{}'.format(c))
                            onto, ind = add_individum(onto,list(onto.search(label = c))[0], c,p_id)

                        for k in c.split():
                            if k not in sup_cat.keys():
                                k = next((short for short, full in rel_synonym.items() if full == k and short in sup_cat.keys()), None)
                                try:
                                    sup_cat[k]
                                except:
                                    continue
                            print('k as support:{}'.format(k))
                            ind.RO_0000087.append(support_role_i) #'has role' = RO_0000087
                            ind.support_component_of.append(e_ind)
                            for i in sup_cat[k]:
                                c_t = rel_synonym[i] if i in rel_synonym.keys() else i
                                try:
                                    cat=[i for i in list(onto.search(label=c_t)) if i in list(onto.individuals())][0]
                                except:
                                    onto, cat=add_individum(onto,list(onto.search(label=c_t))[0], c_t,p_id)
                                    
                                cat.supported_on.append(ind)
                                cat.catalytic_component_of.append(e_ind)
                            sup_cat.pop(k) 
                            
                    if row.category== 'Product':
                        ind.RO_0000087.append(prod_role_i)
                    elif row.category =='Reactant':
                        ind.RO_0000087.append(reac_role_i)
                    elif row.category=='Catalyst':
                        if c==row.entity:
                            ind.RO_0000087.append(cat_role_i) #'has role' = RO_0000087
                        elif e_ind not in ind.support_component_of:                          
                            ind.catalytic_component_of.append(e_ind)
            
            if row.category== 'Reaction':
                if row.entity in reac_dict.keys():
                    ind= [i for i in list(onto.search(label=entity)) if i in list(onto.individuals())][0]                
                    for r in reac_dict[row.entity]:
                       cem_i=[i for i in list(onto.search(label=r)) if i in list(onto.individuals())][0]         
                       ind.RO_0000057.append(cem_i) #'has participant' = RO_0000057
            if row.entity in abbreviation.keys(): # check for abbreviations
                ind.comment.append(abbreviation[row.entity][0])
                     

        for sup,v in sup_cat.items():
            sup = rel_synonym[sup] if sup in rel_synonym.keys() else sup
            try:
                sup = [i for i in list(onto.search(label=sup)) if i in list(onto.individuals())][0]
            except:
                try:
                    onto, sup=add_individum(onto,list(onto.search(label=sup))[0], sup,p_id)
                except:
                    new_cl = types.new_class(sup, ('support material',))
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
                        new_cl = types.new_class(class_name, ('molecule',))
                        onto, cat = add_individum(onto,new_cl, cat,p_id)
                cat.RO_0000087.append(cat_role_i)    #has role catalyst role
                cat.supported_on.append(sup)
        entities_pub = []
        entities_pub.extend([c for c in df_entity.entity])
        entities_pub.extend([i for c in df_entity.cems if c for i in c if i not in entities_pub])
        entities_pub = [*set(entities_pub)]
        pub_new = onto.search_one(iri='*publication{}'.format(p_id))
        for entity in entities_pub:
            print('entity:{}'.format(entity))
            ind = [i for i in list(onto.search(label = entity)) if i in list(onto.individuals())][0]
            ind.mentioned_in.append(pub_new)
        for short,entity in rel_synonym.items():
            inds = [i for i in list(onto.search(label=entity))]
            for i in inds:
                i.comment.append(short)
    onto = create_comp_relation(onto,match_dict, rel_synonym,p_id)
                
    onto.save('./ontologies/{}.owl'.format(onto_name))
    return created_classes, sup_sub_df        
          
def create_comp_relation(onto,match_dict, rel_synonym,p_id):
    global num
    global onto_new_dict
    short = []
    pub_new = onto.search_one(iri='*publication{}'.format(p_id))
    with onto:
        for k,v in onto_new_dict.items():
            if k in match_dict.values() or len(v) == 1:
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

    
def create_subclass(onto,subclass,entities,super_class,created_classes,chem_list,p_id ):
    global num
    new_sub = None  
    created_ind = [i.label[0].lower() for i in onto.individuals() if i.label]
    
    if [c for c in chem_list if re.search(r'\b[\d.,%]*{}\b'.format(c),subclass) if c != subclass]:
        print('subclass:{}'.format(c))
        if subclass.lower() not in created_ind:
            onto, new_i = add_individum(onto,super_class,subclass,p_id)            
        else:
            new_i = onto.search_one(label = subclass)
            new_i.is_a.append(super_class)  
    
    elif subclass.lower() == super_class.label[0].lower():    #to implement for reaction
         onto, new_i = add_individum(onto,super_class, subclass,p_id)
    elif subclass.lower() not in created_classes:
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
    if new_sub:
        new_sub.comment.append('created automatically')    

    return onto, created_classes,  

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

def create_sub_super(missing, onto, idx, indecies, entities, sup_sub_df, created_classes, chem_list, p_id, subclass = None ):
    global num
    super_class_l = sup_sub_df.loc[idx, 'super_class']
    with onto:
        if super_class_l not in missing or super_class_l in created_classes:
            super_class = onto.search_one(label=super_class_l)
            if not super_class:
                super_class = onto.search_one(prefLabel=super_class_l)
            if not subclass:
                onto, created_classes = create_subclass(onto, sup_sub_df.loc[idx, 'subclass'], entities, super_class,created_classes,chem_list,p_id=p_id)
        elif super_class_l in list(sup_sub_df['subclass']):
            query = sup_sub_df.query('subclass == "{}"'.format(super_class_l))
            idx = query.index[0]
            subclass=super_class_l
            indecies.extend(list(query.index))
            indecies, onto, super_class,created_classes = create_sub_super(missing, onto, idx, indecies,entities,sup_sub_df,created_classes,chem_list,p_id,subclass=subclass)
            query = sup_sub_df.query('super_class == "{}"'.format(super_class_l))
            if query.empty == False:
                indecies.extend(list(query.index))
                for q in range(len(query)):
                    subclass = query['subclass'].iloc[q]
                    onto, created_classes=create_subclass(onto,subclass,entities,super_class,created_classes,chem_list,p_id=p_id)
                    subclass = None 
        else: 
            class_name = 'DC_{:02d}{:02d}'.format(p_id, num)
            num += 1
            super_class = types.new_class(class_name, (Thing,))
            super_class.comment.append('created automatically') 
            super_class.label.append(super_class_l)
            created_classes.append(super_class_l.lower())
        if subclass:
            if subclass.lower() not in created_classes:
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
 
sup_cat={'MCM-41': ['RhCo3', 'Rh', 'RhM3'],
 'SiO2': ['RhCo3', 'Rh', 'RhCo'],
 'Al2O3': ['Rh', 'Co'],
 'Al': ['Rh']}
rel_synonym= {'Co': 'cobalt atom',
 '1,3-butadiene': 'buta-1,3-diene',
 'oxide': 'oxide',
 'lithium aluminum hydride': 'lithium tetrahydroaluminate',
 'lithium': 'lithium atom',
 'aluminum': 'aluminium atom',
 'hydride': 'hydride',
 'olefin': 'olefin',
 'Zn': 'zinc atom',
 'carbon monoxide': 'carbon monoxide',
 'carbon': 'carbon atom',
 'monoxide': 'carbon monoxide',
 'Rh': 'rhodium atom',
 'propyl': 'propyl',
 'ethane': 'ethane',
 'Ir': 'iridium atom',
 'Mn2O3': 'oxo(oxomanganiooxy)manganese',
 'Mn': 'manganese atom',
 'O': 'oxygen atom',
 'aldehyde': 'aldehyde',
 'Zr': 'zirconium atom',
 'methane': 'methane',
 'methanol': 'methanol',
 'MoO3': 'molybdenum trioxide',
 'Mo': 'molybdenum atom',
 'Ethylene': 'ethene',
 'cobalt': 'cobalt atom',
 'alkene': 'alkene',
 'Sc2O3': 'oxo(oxoscandiooxy)scandium',
 'Sc': 'scandium atom',
 'rhodium oxide': 'oxorhodium',
 'rhodium': 'rhodium atom',
 'propylene': 'propene',
 'propanol': 'propan-1-ol',
 'V2O5': 'divanadium pentaoxide',
 'V': 'vanadium atom',
 'Sr': 'strontium atom',
 'P': 'phosphorus atom',
 'acetic acid': 'acetic acid',
 'acetic': 'acetic acid',
 'acid': 'acid',
 'Al': 'aluminium atom',
 'RhCo': 'cobalt;rhodium',
 'C': 'carbon atom',
 'zeolite': 'zeolite',
 'RhCo3': 'cobalt;rhodium',
 'propanal': 'propanal',
 'Ni': 'nickel atom',
 'Cobalt': 'cobalt atom',
 'silica': 'silicon dioxide',
 'La': 'lanthanum atom',
 'rhodium trichloride': 'trichlororhodium',
 'S': 'sulfur atom',
 'Al2O3': 'aluminium oxide',
 'TiO2': 'titanium dioxide',
 'Ti': 'titanium atom',
 'SiO2': 'silicon dioxide',
 'Si': 'silicon atom',
 'CO': 'carbon monoxide',
 'Cu': 'copper atom',
 'ethylene': 'ethene',
 'Rh2O3': 'oxo(oxorhodiooxy)rhodium'}

missing=[]
match_dict={}
chem_list=['Co',
 '1,3-butadiene',
 'oxide',
 'lithium aluminum hydride',
 'olefin',
 'Zn',
 'carbon monoxide',
 'Rh',
 'aluminum',
 'propyl',
 'ethane',
 'Ir',
 'Mn2O3',
 'MCM-41',
 'aldehyde',
 'lithium',
 'Zr',
 'hydride',
 'HZSM-5',
 'methane',
 'methanol',
 'MoO3',
 'Ethylene',
 'cobalt',
 'alkene',
 'Sc2O3',
 'rhodium oxide',
 'propylene',
 'Rh2O3@S-1',
 'propanol',
 'V2O5',
 'Sr',
 'Rh2P',
 'acetic acid',
 'carbon',
 'silicalite-1 ',
 'Al',
 'RhCo',
 'RhCo3(CO)12',
 'zeolite',
 'RhCo3',
 'ZSM-5 ',
 'propanal',
 'ZSM-5',
 'Ni',
 'Cobalt',
 'silica',
 'La',
 'rhodium trichloride',
 'S',
 'propene',
 'Al2O3',
 'rhodium',
 'TiO2',
 'SiO2',
 'CO',
 'Cu',
 'ethylene',
 'Rh2O3',
 'cobalt atom',
 'buta-1,3-diene',
 'oxide',
 'lithium tetrahydroaluminate',
 'lithium atom',
 'aluminium atom',
 'hydride',
 'olefin',
 'zinc atom',
 'carbon monoxide',
 'carbon atom',
 'carbon monoxide',
 'rhodium atom',
 'propyl',
 'ethane',
 'iridium atom',
 'oxo(oxomanganiooxy)manganese',
 'manganese atom',
 'oxygen atom',
 'aldehyde',
 'zirconium atom',
 'methane',
 'methanol',
 'molybdenum trioxide',
 'molybdenum atom',
 'ethene',
 'cobalt atom',
 'alkene',
 'oxo(oxoscandiooxy)scandium',
 'scandium atom',
 'oxorhodium',
 'rhodium atom',
 'propene',
 'propan-1-ol',
 'divanadium pentaoxide',
 'vanadium atom',
 'strontium atom',
 'phosphorus atom',
 'acetic acid',
 'acetic acid',
 'acid',
 'aluminium atom',
 'cobalt;rhodium',
 'carbon atom',
 'zeolite',
 'cobalt;rhodium',
 'propanal',
 'nickel atom',
 'cobalt atom',
 'silicon dioxide',
 'lanthanum atom',
 'trichlororhodium',
 'sulfur atom',
 'aluminium oxide',
 'titanium dioxide',
 'titanium atom',
 'silicon dioxide',
 'silicon atom',
 'carbon monoxide',
 'copper atom',
 'ethene',
 'oxo(oxorhodiooxy)rhodium']
categories={'Rh2P nanoparticle on SiO2 support material': 'Catalyst',
 'hydroformylation': 'Reaction',
 'ethylene': 'Reactant',
 'propylene': 'Reactant',
 'transmission electron microscopy': 'Characterization',
 'infrared analysis of adsorbed CO': 'Characterization',
 'high throughput experimentation': 'Characterization',
 'reduction': 'Treatment',
 'heterogeneous hydroformylation': 'Reaction',
 'RhCo3 supported on MCM-41': 'Catalyst',
 'hydrogenation': 'Reaction',
 'DRIFTS': 'Characterization',
 'DRC': 'Characterization',
 'coimpregnation': 'Treatment',
 'decarbonylation': 'Reaction',
 'atmospheric ethylene': 'Reactant',
 'RhCo3 supported on SiO2': 'Catalyst',
 'binary catalyst': 'Catalyst',
 'monometallic catalyst': 'Catalyst',
 'rhodium': 'Catalyst',
 'cobalt': 'Catalyst',
 '5%Rh supported on Al2O3': 'Catalyst',
 '1%Co supported on Al2O3': 'Catalyst',
 '0.5%Co-0.5%Rh supported on Al2O3': 'Catalyst',
 'ethane': 'Product',
 'propanal': 'Product',
 'propanol': 'Product',
 'Rh catalyst': 'Catalyst',
 'CO': 'Reactant',
 'Ethylene': 'Reactant',
 'carbon monoxide': 'Reactant',
 'methanol': 'Product',
 'Rh supported on SiO2 catalyst': 'Catalyst',
 'dissociation': 'Reaction',
 'MoO3': 'Catalyst',
 'Sc2O3': 'Catalyst',
 'TiO2': 'Catalyst',
 'V2O5': 'Catalyst',
 'Mn2O3': 'Catalyst',
 'organic oxygenate': 'Product',
 'TPR': 'Characterization',
 'XPS': 'Characterization',
 'FTIR': 'Characterization',
 'XRD': 'Characterization',
 'atmospheric hydroformylation': 'Reaction',
 'propene': 'Reactant',
 'linear aldehyde': 'Product',
 'Rh supported on Al ': 'Catalyst',
 'reducing': 'Treatment',
 'rhodium trichloride supported on silica with lithium aluminum hydride': 'Catalyst',
 'vapour phase propene': 'Reactant',
 'X-ray diffraction': 'Characterization',
 'X-ray photoemission spectroscopy': 'Characterization',
 'Fourier  transform-IR spectroscopy': 'Characterization',
 'ZSM-5 zeolite': 'Catalyst',
 'naphtha': 'Reactant',
 'catalytic cracking': 'Reaction',
 'Sr, Zr, La-supported on ZSM-5 zeolite': 'Catalyst',
 'metal-incorporated ZSM-5 zeolite': 'Catalyst',
 'hydride transfer reaction': 'Reaction',
 'alkene': 'Product',
 'light olefin': 'Product',
 'Zr-supported on ZSM-5 zeolite': 'Catalyst',
 'HZSM-5': 'Catalyst',
 'RhCo supported on SiO2 catalyst .': 'Catalyst',
 'heterogeneous rhodium oxide catalyst encapsulated within microporous silicalite-1  (S-1) ': 'Catalyst',
 'Rh2O3@S-1': 'Catalyst',
 'Supported catalyst based on the RhCo': 'Catalyst',
 'vapor phase hydroformylation': 'Reaction',
 'olefin': 'Reactant',
 'RhCo3(CO)12': 'Catalyst',
 'Cobalt complex': 'Catalyst',
 'rhodium based catalyst': 'Catalyst',
 'heterogeneous ethylene': 'Reactant',
 'Rh,Co based catalyst': 'Catalyst',
 'Supported catalyst based on the RhCo couple': 'Catalyst',
 'RhCo based catalyst': 'Catalyst',
 'Rh supported on Al based catalyst': 'Catalyst',
 'propyl specie': 'Product',
 'Rh-based heterogeneous catalyst': 'Catalyst',
 'Rh': 'Catalyst',
 'Rh-based alloy catalyst': 'Catalyst',
 'monometallic Rh supported on MCM-41': 'Catalyst',
 'Rh supported on  MCM-41': 'Catalyst',
 'Rh-based bimetallic catalyst': 'Catalyst',
 'RhM3 supported on MCM-41,M =  M= ,Co Co, Ni,Cu Zn': 'Catalyst',
 'Bimetallic heterogeneous catalyst based on rhodium supported on various oxide': 'Catalyst',
 'Rh, Ir-based atomically dispersed catalyst': 'Catalyst',
 'dimerization': 'Reaction',
 '1,3-butadiene': 'Reactant',
 'methane': 'Reactant',
 'acetic acid': 'Product'}
df_entity, rel_synonym, missing_all, match_dict_all=preprocess_classes(categories, sup_cat, rel_synonym, chem_list, missing, match_dict)
"""
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