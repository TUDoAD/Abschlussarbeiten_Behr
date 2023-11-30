# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:51:27 2023

@author: chern
"""
import stanza
#stanza.download('en', package='craft', processors='tokenize')
import spacy
from owlready2 import *
import pickle
from preprocess_onto import *
import logging
import pandas as pd
#import pytorch_lightning as pl
from CatalysisIE.model import *
from CatalysisIE.utils import *
import requests
import os
from chemdataextractor import Document
from pubchempy import get_compounds
import types
from io import StringIO
from txt_extract import get_metadata, get_abstract

def delete_files_in_directory(directory_path):
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")
     
def add_publication(onto_name,doi,title,abstract):
    new_world=owlready2.World()
    try:
        onto= new_world.get_ontology('./ontologies/{}_upd.owl'.format(onto_name)).load()
    except:
        onto= new_world.get_ontology('./ontologies/{}.owl'.format(onto_name)).load()
    pub_c= onto.search_one(label='publication')
    with onto:
        if not pub_c:
            pub_c = types.new_class('publication', (Thing,))
            pub_c.comment.append('created automatically; collection of processed publications') 
            pub_c.label.append('publication')
        if onto.search_one(comment='DOI: {}'.format(doi)):
            print('Paper with doi: {} already exist in ontology'.format(doi))
            new_pub=onto.search_one(comment='DOI: {}'.format(doi))
            p_id=None
            return p_id
        else:
            p_id= len(list(pub_c.instances()))+1
            new_pub= pub_c('publication{}'.format(p_id))
            new_pub.comment.append('DOI: {}'.format(doi))
            new_pub.comment.append('Abstract:{}'.format(abstract))
            has_doi= onto.search_one(label='has doi')
            if not has_doi:
                class has_doi(DataProperty):
                    range = [str]
                    label='has doi'
            new_pub.has_doi=[doi]
            has_title=onto.search_one(label='has title')
            if not has_title:
                class has_title(DataProperty):
                    range = [str]
                    label='has title'
            new_pub.has_title=[title]
    onto.save('./ontologies/{}_upd.owl'.format(onto_name))
    return p_id
        
def load_ontologies(ontology_name):
    """
    loads an ontology from subfolder ontologies defined by its name 
    outputs list of classes contained in this ontology  

    Parameters
    ----------
    ontology_name : TYPE
        DESCRIPTION.

    Returns
    -------
    onto_class_list : TYPE
        DESCRIPTION.

    """
    onto_class_list = list(onto.classes())


    print("Loading {} done. Imported {} classes.".format(ontology_name, len(onto_class_list)))
    return onto_class_list 

def synonym_dicts(class_list):
    """
    extracts class names and descriptions based on class list (as owlready2 object)
    returns dictionary with general structure of 
    desc_dict = {ontology_class_label : Definition string}
    WARNING: Descriptions often have different identifiers (see try:... except loop)
          Implemented IAO_0000115 and .comment for now. 

    example: [class_dict, desc_dict] = onto_loader(["chmo","Allotrope_OWL", "chebi"])
    execute once to load all ontologies from list    

    Parameters
    ----------
    class_list : TYPE
        DESCRIPTION.


    Raises
    ------
    print
        DESCRIPTION.
    definitionError
        DESCRIPTION.

    Returns
    -------
    desc_dict : TYPE
        DESCRIPTION.

    """
    print("Extracting formulae...")
    desc_dict = {} 
    formula_dict = {}
    inchikey = {}
    temp_class_label = []
    
    def_id = ["hasRelatedSynonym", "hasExactSynonym","inchikey"]
    
    for i in range(len(class_list)):
        temp_class = class_list[i]
        #check, if label and definition are not empty:
        #Definition: IAO_0000115, comment
        try:
            if temp_class.prefLabel:
                # if preferred label is not empty, use it as class label
                temp_class_label = temp_class.prefLabel[0].lower()
                
        except:
            try:
                if temp_class.label:
                    # if label is not empty, use it as class label
                    temp_class_label = temp_class.label[0].lower()
                    
            except:
                temp_class_label = []
                print("Label for class {} not determined!".format(str(temp_class)))
                return()

        if temp_class_label and temp_class_label not in desc_dict.keys():
            
            # if class got a label which is not empty, search for definition                    
            desc_dict[temp_class_label] = getattr(temp_class,def_id[0])
            desc_dict[temp_class_label].extend(getattr(temp_class,def_id[1]))
            if desc_dict[temp_class_label] and temp_class_label not in desc_dict[temp_class_label]: 
                desc_dict[temp_class_label].append(temp_class_label)
            elif not desc_dict[temp_class_label]:    
                desc_dict[temp_class_label] = [temp_class_label]
            #formula_dict[temp_class_label] =getattr(temp_class,def_id[2])
            
            #if temp_class_label in smiles_dict[temp_class_label]:
                #smiles_dict[temp_class_label].remove(temp_class_label)
            inchikey[temp_class_label] = getattr(temp_class,def_id[2])
    print("Done.")
    return desc_dict,  inchikey


#create snip and merge ontologies...
def load_classes_chebi():
    
    new_world3 = owlready2.World()
    onto = new_world3.get_ontology('http://purl.obolibrary.org/obo/chebi.owl').load()
    onto_class_list = list(onto.classes())
    #set_org_mol = onto.search_one(label='organic molecular entity').descendants()#exclude "organic molecular entity problem: ex. aldehyde won't be found
    #set_org_mol= set_org_mol.union(onto.search_one(label='organic group').descendants())
    set_org_mol= onto.search_one(label='organic group').descendants()
    for i in set_org_mol:
        if i in onto_class_list:
            onto_class_list.remove(i)
    return onto_class_list
        
def chemical_prep(chem_list, onto_list,onto_class_list,onto_name): #, chem_list_all
    global abbreviation
    global onto_new_dict
    rel_synonym={}
    comp_dict = {}
    class_list=[]        
    onto_new_dict ={}
    synonyms={}

    onto_dict,inchikey= synonym_dicts(onto_class_list)
    for molecule in chem_list:  
        non_chem = False
        if re.search(r'^ [A-Za-z\d—–-]+|^[A-Za-z\d—–-]+ $',molecule):
            molecule=molecule.replace(' ','')

        if molecule in abbreviation.keys():
            comp_dict[molecule]=[]
            spans=Document(abbreviation[molecule]).cems
            class_list.append(molecule)
            for comp in spans:
                if len(comp.text.split())>1:
                    print('line 211: comp.text={}'.format(comp.text))
                    for c in comp.text.split():
                        comp_dict[molecule].append(c)
                        print('comp_dict:{}'.format(comp_dict))
                else:
                    comp_dict[molecule].append(comp.text)
            continue
        if non_chem ==True or re.search(r'[A-Z]+[—–-][\d]+', molecule):
            onto_new_dict[molecule]=[]
            class_list.append(molecule)
            continue        
        molecule_split= molecule.split()
        if len(molecule_split) >= 2 or re.match(r'[A-Za-z]([a-z]){3,}', molecule) or re.match(r'[\d,]+[—–-][a-z]+',molecule):
             comp_dict[molecule] = molecule_split  
        else:
             comp = re.findall(r'([A-Z](?:[a-z])?)',molecule)
             comp_dict[molecule] = comp
    #print(comp_dict)
    for k,v in comp_dict.items():
        print('{}:{}'.format(k,v))
        i=0
        if k not in onto_new_dict.keys():
           
            for c in v:
                
                #print(c)
                for k_o, v_o in onto_dict.items():
                    synonyms= fill_synonyms(synonyms,k,v_o,k_o)
                    synonyms= fill_synonyms(synonyms,c,v_o,k_o)
                
                if i==0:
                    non_comp,class_list, key ,rel_synonym= compare_synonyms(synonyms,inchikey, class_list, k, rel_synonym,comp= False)
                    #if non_comp = key:
                    #    break
                    onto_new_dict[key]=[]
                    i+=1
                if c == k:
                    comp = key
                    #non_comp = False
                else:
                    non_comp, class_list, comp, rel_synonym = compare_synonyms(synonyms,inchikey, class_list, c, rel_synonym,comp= True) 
                
                #if non_comp == True:
                #    break
                
                onto_new_dict[key].append(comp)
            for i in onto_new_dict[key]:
                if len(i) ==1:#remove components if one of the components (atoms) doesn't exist (ex.ZMS- Z,M don't exist, S-exists) -wrong: mb delete
                    print('deleted key:{}'.format(key))
                    #class_list.remove(i)
                    class_list.remove(key)
                    onto_new_dict.pop(key)
    class_list= [*set(class_list)] #remove duplicates
    print(synonyms)
    class_list.extend(['molecule'])
    missing, match_dict = create_list_IRIs(class_list, onto_list,onto_new,onto_old,IRI_json_filename = 'iriDictionary')

    return onto_new_dict, missing, match_dict, rel_synonym
     
def fill_synonyms(synonyms,c,v,k):
    pattern= r'^{}$'.format(c)
    if c not in synonyms.keys():
                synonyms[c]=[]
    for s in v:
        if re.search(pattern,s): 
            if k not in synonyms[c]:
                synonyms[c].append(k)    
    
    for i in synonyms[c]:
        if re.search(pattern,i):
            synonyms[c]=[i]
                        
    return synonyms

def search_inchikey(inchikey, c):
    
    try:
        mol = get_compounds(c, 'formula')    
    except:
        try:
            mol = get_compounds(c, 'name')       
        except:
            mol = []        
    if not mol:
        mol_out = [c]
    else:
        mol_inch = [k for k, v in inchikey.items() for compound in mol if compound.inchikey in v]
        if mol_inch:
            mol_out= mol_inch
        else:
            mol_out = [c]          
    return mol_out,  mol

def compare_synonyms(synonyms, inchikey, class_list, k, rel_synonym, comp):
    none_comp= False
    if len(synonyms[k]) == 1:
            key= synonyms[k][0]
    else: 
            comp_check, mol= search_inchikey(inchikey, k)
            
            if k in comp_check:
                if len(synonyms[k]) == 0:
                    if not mol:
                        print('no synonyms and entities for {}, key = k'.format(k))
                        key = k
                        class_list.append(k)
                        none_comp =True
                        return none_comp, class_list, key, rel_synonym
                    elif len(mol)==1:
                        key=mol[0].iupac_name
                    else:
                        while True:
                            mol_new= [i for i in mol if i.iupac_name]
                            print('choose iupac name for {}:{}'.format(k,[i.iupac_name for i in mol_new]))
                            print('components have following SMILES:')
                            for i in mol_new:
                                print('{}:{}'.format(i.iupac_name, i.isomeric_smiles))
                            idx= input('write number of fitting iupac name or "none"\n')
                            if idx =='none':
                                key = k
                                if comp==True:
                                    none_comp = True
                                    return none_comp, class_list, key, rel_synonym
                                
                                break
                            else:
                                try:
                                    idx= int(idx)
                                    key= mol_new[idx-1].iupac_name
                                    break
                                except:
                                    print('error: write a number between 1 and {} or "none"'.format(len(mol_new)))
                                    
                else:
                    while True:
                            print('choose synonyms for {}:{}'.format(k,synonyms[k]))
                            idx= input('write number of fitting synonym or "none"\n')
                            
                            if idx =='none':
                                key = k
                                if comp==True:
                                    none_comp =True
                                    return none_comp, class_list, key, rel_synonym
                                break
                            else:
                                try:
                                    idx= int(idx)
                                    key= synonyms[k][idx-1]
                                    break
                                except:
                                    print('error: write a number between 1 and {} or "none"'.format(len(synonyms[k])))
                                
            elif len(comp_check) == 1:
                key= comp_check[0]                  
            else:
                key = None
                for i in comp_check:
                    if i in synonyms[k]:
                        key = i
                if key == None:
                    print('no synonyms but some matches in inchikey for {}:{}'.format(k, comp_check))
                    key = k                  

    rel_synonym[k]=key          
    class_list.append(key)
    return none_comp, class_list, key, rel_synonym
                                  
def pred_model_dataset (model,sent): 
    # CUDA and Pytorch are necessary for execution of function !    
    #use the checkpoint trained on first fold

    
    output_tensor_buf = []
    pred_dataset, pred_dataloader = model.gen_pred_dataloader(sent)
    
    model.setup('test')
    model = model.cuda()
    model.eval()
    with torch.no_grad():
        offset = 0
        for batch in tqdm(pred_dataloader):
            batch = model.batch_cuda(batch)
            model.pred_dataset_step(offset, batch, pred_dataset)
            offset += len(batch[0])
    return pred_dataset.output_pred()

def text_prep(test_txt):
    nlp = stanza.Pipeline('en', package='craft', processors='tokenize', use_gpu=False)
    
    test_sents = []
    idx = 0
    test_txt = cleanup_text(test_txt)
    for sent in nlp(test_txt).sentences:
        sent_token = []
        for token in sent.tokens:
            # it is fine to label all token as O because it is not training
            sent_token.append({
                'text':token.text,
                'label':'O',
                "id":  idx,
                "start": token.start_char,
                "end": token.end_char,
            })
            idx += 1
        test_sents.append((sent.text, sent_token))
    test_sents = stanza_fix(test_sents)
    return test_sents

def CatalysisIE_search(model, test_sents, onto_list,onto_name):
    global categories
    global sup_cat
    global abbreviation
    nlp = spacy.load('en_core_web_sm')
    chem_list_all = []
    chem_list = []
    cat_sup_list=[]
    sup_cat={}
    abbreviation = {}
    a=0
    categories={}
    reac_dict={}
    c_idx=None
    entity_old=(0,None,None)
    '''
    categories = {
        "Catalyst": [],         #Identified as “metal/support” or with keywords like “metal-catalyst”. If details about the catalyst composition are 
                                #provided, then they are included in the catalyst text span (e.g., Ru/CeO2, CeO2-supported metal catalysts, and Pt/H-USY 
                                #(Pt:1 wt %) catalysts).
        "Reaction": [],         #Processes that involve the transformation of a chemical species via interactions with a catalyst (e.g., hydrogenation, 
                                #isomerization, and hydrocracking).
        "Treatment": [],        #Any technique that is used to yield useful information about the catalyst (e.g., gas chromatography mass spectroscopy 
                                #(GC–MS), powder X-ray diffraction (XRD), and infrared spectrometry (IR)).       
        "Reactant": [],         #Species that interact with the catalyst to create a product (e.g., polyethylene, plastics, and PE). Reagents for catalyst 
                                #synthesis are not included in this category.
        "Product": [],          #Species that are produced from a chemical reaction between the reactant and the catalyst (e.g., C1–C4, coke, and liquid 
                                #fuel). Intermediate species that go on to react further are not considered in this category unless there is substantial 
                                #characterization/quantification of those species.
        "Characterization": []  #Any intermediate steps taken to prepare the catalyst (e.g., heating, calcination, and refluxing).
        }
    '''
    output_sents = pred_model_dataset(model, test_sents)
    for sent in output_sents:
        sent_tag = [t['pred'] for t in sent]
        print(assemble_token_text(sent))
        chem_list_all.extend([c.text for c in Document(assemble_token_text(sent)).cems])
        abb_list=Document(assemble_token_text(sent)).abbreviation_definitions
        for i in range(len(abb_list)):
            abbreviation[abb_list[i][0][0]]=abb_list[i][1][0]
        for i, j, l in get_bio_spans(sent_tag):
            print(assemble_token_text(sent[i:j + 1]), l)
            entity = assemble_token_text(sent[i:j + 1])
            
            if entity[-1]=='.':
                entity= entity[:-1]
            #add abbreviation if directly after entity an entity in brackets
            if i == a+1 and '({})'.format(entity) in assemble_token_text(sent):
                    abbreviation[entity]=entity_old[1]
            #match hyphen in chemical entity and remove it  # Rh-Co --> RhCo
            match_hyph=re.findall(r'(([A-Z](?:[a-z])?)[—–-]([A-Z](?:[a-z])?))', entity) 
            if match_hyph:
                for i in range(len(match_hyph)):
                    entity = entity.replace(match_hyph[i][0],match_hyph[i][1]+match_hyph[i][2])
            
            doc_list=[]
            doc = nlp(entity)
            for i in range(len(doc)):
                if doc[i].tag_ == 'NNS':
                    doc_list.append(str(doc[i].lemma_))
                    
                else:
                    doc_list.append(str(doc[i]))
            entity= " ".join(doc_list)         # plural to singular
            e_split= entity.split()
            entity = doc_token(entity, e_split,nlp)
            pattern = r'([A-Za-z]+[\s]?[—–-] [a-z]+|[A-Za-z]+ [—–-][\s]?[a-z]+)'
            e_split= re.findall(pattern,entity)
            if e_split:
                print('e_split:{} and entity:{}'.format(e_split, entity)) # check again for examples!
                for i in e_split:
                    i_n=i.replace(' ','')
                    entity=re.sub(i,i_n,entity)
                    missing,_= create_list_IRIs([re.sub(r'[—–-]','',i_n)], onto_list,onto_name)
                    if not missing:
                        entity= re.sub(i_n,re.sub(r'[—–-]','',i_n),entity)
            
            if l== 'Reaction':
                if sent[j+2:j+4]=='of':
                    for c in Document(assemble_token_text(sent)).cems:
                        if c.start == j+5:
                            c_idx=j+5
                elif entity_old[0]+1 == i and entity[2]=='Reactant':
                    if entity not in reac_dict.keys():
                        reac_dict[entity]=[entity_old[1]]
                        
                    elif entity_old[1] not in reac_dict.values():
                        reac_dict[entity].append(entity_old[1])
                
            
            if entity in categories.keys():
                entity_old=(j,entity,l)
                continue
            else:
                mol = re.findall(r'(([\w@—–-]+)(?:[\s]?/[\s]?|[\s]on[\s])+([\w@—–-]+))', entity) # 'RhCo on Al2O3' or 'RhCo/Al2O3'
                if mol:
                    for i in range(len(mol)):
                        if ('supported' or 'Supported') in mol[i][0]:
                            continue
                        elif l == 'Catalyst':
                            if '/' in mol[i][0]:
                                entity = entity.replace('/',' supported on ')
                                sup=True
                            elif 'on' in mol[i][0]:
                                sup= False
                                for c in chem_list_all:
                                    if re.search(mol[i][1],c):
                                        entity = entity.replace('on','supported on')
                                        sup= True
                                        break    
                            if sup==True:    
                                support = mol[i][2]
                                chem_list.append(support)
                                catalyst = mol[i][1]
                                chem_list.append(catalyst)
                                if support in sup_cat.keys():
                                    if catalyst not in sup_cat[support]:
                                        sup_cat[support].append(catalyst)
                                else:
                                        sup_cat[support] = [catalyst]
                        else:
        
                            for k in range(1, len(mol[i])):
                                chem_list.append(mol[i][k])
                                entity = entity.replace('/',',')
                pattern = r'^[\d,]+[—–-] [a-z]+$' #1,3- butadiene -> 1,3-butadiene
                if re.search(pattern,entity) or re.search(r'^ [A-Za-z\d—–-]+$',entity):

                    entity=entity.replace(' ','') 
                spans = sorted(Document(entity).cems, key=lambda span: span.start)
                chem_list.extend([c.text for c in spans])
                #chem_list.extend([c for c in chem_list_all if c == entity and c not in chem_list]) #add chemicals that wasn't recognized with chemdataextractor like()
                chem_list.extend([c for c in chem_list_all if c in entity and c not in chem_list])
                print('chem_list:{}'.format(chem_list))
                for c in chem_list: # search if for ex. ZSM-5 in entity if only ZSM found. replace ZSM with ZSM-5 in chem_list
                    if re.findall(r'{}[—–-][\d]+[\s]'.format(c), entity):
                        chem_list[:]=[re.findall(r'{}[—–-][\d]+[\s]'.format(c), entity)[0] if x==c else x for x in chem_list]
                        
                if 'system' in entity or 'surface' in entity and l=='Catalyst':
                        entity=entity.replace('system','catalyst')
                        entity=entity.replace('surface','catalyst')
                if 'loaded' in entity:#Zr-loaded ZSM-5 zeolites
                    for i in range(len(spans)):
                        if i != 0:
                            e_btwn = entity[spans[i-1].end:spans[i].start]
                            if 'loaded' in e_btwn:    
                                loaded_end =  entity.index('loaded')+len('loaded')+1
                                for c in chem_list:
                                    try:
                                        idx=entity.index(c)
                                    except:
                                        continue
                                    else:
                                        if idx == loaded_end:
                                            if c not in sup_cat.keys():
                                                sup_cat[c] = []
                                            k=0
                                            while k<i:
                                                if spans[k].text not in sup_cat[c]:
                                                    sup_cat[c].append(spans[k].text)
                                                k+=1
                    entity=entity.replace('loaded','supported on')
                #else:
                categories[entity]=l 
            entity_old=(j,entity,l)  
            a=j+1
            
    chem_list= [*set(chem_list)]
    #chem_list_all=[*set(chem_list_all)]
    return categories,chem_list, reac_dict ,sup_cat#chem_list_all,

    
def preprocess_classes ( rel_synonym,chem_list,missing_all,match_dict_all, onto_list, onto_name ):
    global categories
    global sup_cat
    nlp = spacy.load('en_core_web_sm')
    classes={}
    spans_dict={}
    support=[]
    list_all=[]
    heads=[]
    chem_list.extend([str(i) for i in rel_synonym.values()]) 
    for entity,l in categories.items():
        if entity in classes.keys():
                    continue
        else:
            spans_dict[entity]=[]
            spans_n=[]
        if l =='Catalyst':
                support=[]
                if "based" in entity:
                    
                    e_snip=None
                    based_m = re.search('based',entity)
                    if based_m.start() != 0 or entity[:based_m.start()-1] != 'catalyst': 
                        e_snip = entity[:based_m.start()-1]
                        e_cleaned = e_snip
                        for c in chem_list:
                            pattern='\\b'+c+'\\b'
                            if re.search(pattern,e_snip):
                                e_snip= e_snip[e_snip.index(c)+len(c)+1:]
                                c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                                if c_t not in spans_n:    
                                    spans_n.append(c_t)  
                               
                                if "supported" in e_snip:
                                    e_cleaned = e_snip[re.search('supported',e_snip).end()+1:]
                                    support.append(c_t)
                                    continue

                                if 'catalyst' in e_cleaned:
                                    classes,_= check_in_snip(e_cleaned, classes,nlp, entity,l,chem_list)
                                       
                            if entity[based_m.end()+1:] != 'catalyst':
                                s_on=False
                                if 'on' in e_snip: #based on/ based exclusivelly on
                                    if re.search('supported on', e_snip):
                                        s_on= True
                                        #Rh-Co based system supported on alumina, titania and silica
                                        e_btwn=e_snip[re.search('supported on', e_snip).end():]
                                    else:
                                        based_m = re.search('on',entity)
                                e_snip = entity[based_m.end()+1:]
                                
                                if re.search('supported', e_snip) and s_on==False: 
                                    #based on silica supported bimetallic catalysts
                                    e_btwn=e_snip[:re.search('supported', e_snip).start()-1]
                                    sup_i = True
                                else:
                                    sup_i = False
                                
                                for c in chem_list:
                                    pattern='\\b'+c+'\\b'
                                    if re.search(pattern,e_snip):
                                        c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                                        if sup_i==True and c in e_btwn:
                                                support.append(c_t)                    
                                        if c_t not in spans_n:    
                                            spans_n.append(c_t)  
                                     
                                    #e_cleaned = [re.search(c.text,e_btwn).end()+1:]
                                
                                if 'catalyst' in e_snip:
                                    classes,_= check_in_snip(e_snip, classes,nlp, entity,l,chem_list)
                elif entity not in chem_list or not set(entity.split()).issubset(chem_list):
                    sup_i=False
                    entity_n=entity
                    if re.search('supported on', entity):
                        #Rh-Co based system supported on alumina, titania and silica                                    
                        e_btwn=entity[re.search('supported on ', entity).end():]
                        e_before= entity[:re.search('supported on', entity).start()-1]
                        sup_i=True                            
                    elif re.search('supported', entity): #bimetallic SiO2-supported RhCo3 cluster catalyst
                        if '-' in entity and entity.index('-')==re.search('supported',entity).start()-1:
                            entity_n= entity[:entity.index('-')]+ ' '+entity[entity.index('-')+1:]
                        e_before= None
                        e_btwn=entity[:re.search('supported', entity).start()-1]
                        sup_i = True                 
                    for c in chem_list:
                        pattern='\\b'+c+'\\b'
                        if e_before!=None and set(e_before.split()).issubset(chem_list) or e_before in chem_list:
                            c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                            if c_t not in spans_n:    
                                spans_n.append(c_t)   
                            if sup_i==True:
                                support.append(c_t)                              
                        elif re.search(pattern,entity_n):
                            c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                            if sup_i==True and c in e_btwn:
                                support.append(c_t)                    
                            if c_t not in spans_n:    
                                spans_n.append(c_t)                                  
                    classes,_ = check_in_snip(entity, classes, nlp, entity,l,chem_list)                 
                if support: #überdenken
                    print(support)
                    snaps_n=[c for c in spans_n if c not in support] 
                    for i in support:
                        if i in sup_cat.keys():
                                    sup_cat[i].extend([c for c in snaps_n if c not in sup_cat[i]])
                        else:
                                    sup_cat[i] = snaps_n
        elif l=='Reaction':
            classes,head= check_in_snip(entity, classes, nlp, entity,l,chem_list)
            if head and head not in heads and head != 'reaction':
                heads.append(head)
            for c in chem_list:
                pattern='\\b'+c+'\\b'
                if re.search(pattern,entity):
                    c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                    if c_t not in spans_n:    
                        spans_n.append(c_t) 
        spans_dict[entity].extend(spans_n)                
        if entity in chem_list or set(entity.split()).issubset(chem_list):
            
            if entity in rel_synonym.keys():
                c_list=[rel_synonym[entity]]
            elif entity in rel_synonym.values():
                c_list=[entity]
            else: 
                c_list=[]
                for c in entity.split():
                    c_t = rel_synonym[c] if c in rel_synonym.keys() else c
                    c_list.append(c_t)
            list_all.append([' '.join(c_list),[],[' '.join(c_list)],categories[entity]])    #changed entity! prop-1-ene instead propylene
            #chem_e.append(entity)
            if c_list[0] in sup_cat.keys(): #'ZSM-5' instead of 'ZSM-5 zeolite' (change to second)
                if c_list[0] not in rel_synonym.keys():
                    rel_synonym[c_list[0]]=' '.join(c_list)
                sup_cat[' '.join(c_list)]=sup_cat[c_list[0]] 
                del sup_cat[c_list[0]]
        elif entity.split()[-1] in chem_list and entity not in classes.keys():
            classes,_=check_in_snip(entity, classes, nlp, entity, l,chem_list)
            c_t = rel_synonym[entity.split()[-1]] if entity.split()[-1] in rel_synonym.keys() else entity.split()[-1]
            spans_dict[entity].append(c_t)        
    not_del=[] 
    classes_n={}    
    for k_1,v_1 in classes.items():            
            v_1.sort(key=lambda x: len(x.split()), reverse=False)
            
            classes_n[k_1]=[]
            for k,v in classes.items():
                i = len(v_1)-1
                ele_old=None
                while i >= 0:
                    if k!=k_1 and v_1[i] not in classes_n[k_1]: 
                        if v_1[i] in v:
                            classes_n,ele_old=shortcut_add_class(ele_old, classes_n, not_del, value=v_1, i=i, key=k_1 )
                            
                        elif ele_old:
                            not_del.append(ele_old)
                        i-=1
                    else:                    
                         break 
            #all_values=[v[0] for v in classes_n.values() if v]
            i = len(v_1)-1
            ele_old=None
            while i >= 0:
                if  v_1[i] not in classes_n[k_1]: 
                    classes_n,ele_old=shortcut_add_class(ele_old, classes_n, not_del, value=v_1, i=i, key=k_1 )
                elif ele_old:
                    not_del.append(ele_old)
                i-=1
    v_all=[]
    if heads:
        v_all.extend(heads)
    print(classes_n)    
    for k,v in classes_n.items():
        list_all.append([k,v,spans_dict[k],categories[k]])
        v_all.extend(v)
    missing,match_dict = create_list_IRIs(v_all, onto_list,onto_name, IRI_json_filename = 'iriDictionary',include_main= True) 
    missing_all.extend(missing)   
    match_dict_all.update(match_dict)      
    df_entity= pd.DataFrame(list_all, columns=['entity', 'classes', 'cems', 'category'])        
    return df_entity,missing_all, match_dict_all,rel_synonym

    
                    
                    
def shortcut_add_class(ele_old,classes_n, not_del, value, i, key ):
       
    classes_n[key].append(value[i])
    if ele_old!=None and ele_old not in not_del:
            classes_n[key].remove(ele_old)
    if i!=0:
        if len(value[i].split())>len(value[i-1].split()):
            ele_old=value[i-1]
            print('ele_old:{}'.format(ele_old))
        else:
            ele_old=None
    
    return classes_n,ele_old
         


def check_in_snip(e_snip, classes, nlp, entity, l,chem_list):
    classes[entity]=[]
    doc_snip= nlp(e_snip)
    head=None
    if l=='Catalyst':

        classes[entity] = ['catalyst role']
        if e_snip==entity:
            if 'catalyst' in entity:
                token_new='catalyst role'
                if [t.text for t in [token for token in doc_snip if token.text=='catalyst'][0].children if t.text != "catalyst"]: 
                    token_new='catalyst role'
                    for i in reversed(range(len([t.text for t in [token for token in doc_snip if token.text=='catalyst'][0].children if t.text != "catalyst"]))):
                        if list([token for token in doc_snip if token.text=='catalyst'][0].children)[i].text in chem_list:
                            continue
                        else:
                            token_new=[t.text.lower() for t in [token for token in doc_snip if token.text=='catalyst'][0].children][i] +' ' + token_new
                            classes[entity].append(token_new) # from 'bimetallic SiO2-supported RhCo3 cluster catalyst' only 'cluster catalyst role'
                

#                token_new=doc_snip[-1].text
#                for i in reversed(range(len([t.text for t in doc_snip[-1].children if t.text != doc_snip[-1].text]))):
#                        token_new=[t.text.lower() for t in doc_snip[-1].children][i] +' ' + token_new
#                        classes[entity].append(token_new)
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
#classes={'Rh-based atomically dispersed heterogenous catalyst':['atomically dispersed catalyst role','dispersed catalyst role','heterogenous catalyst role']}
def doc_token(entity, e_split, nlp,j=0):
    
    brackets =False
    doc = nlp(entity) 
    for i,token  in enumerate(doc[j:]):   
        if token == doc[-1]:
            break
        elif token.pos_ in ['CCONJ','PUNCT','SYM','PRON'] and entity[token.idx-1]==' ' and token.text !="=":
            j=j+i
            if token.pos_ =='CCONJ':
                e_new = ''.join([e_split[j-1],',',e_split[j+1]])
            #if doc[j+1].pos_ in ['CCONJ','PRON']:
            #    e_new= ' '.join([e_split[j-1],',',e_split[j+2]])
                
            elif token.pos_=='PRON':
                e_new= ' '.join([e_split[j-1],e_split[j+1]])
                del e_split[j]
            elif token.text=='(' and doc[j+2].text==')':
                e_new = "".join(e_split[j:j+3])
                brackets= True
                j=j+1
            elif token.text=='(' and brackets ==False:
                e_new = "".join([e_split[j],e_split[j+1]])
            elif token.text==')' and brackets ==False:
                e_new = "".join([e_split[j-1],e_split[j]])
            else:
                e_new = "".join(e_split[j-1:j+2])
            if brackets==False:
                e_after = entity[doc[j+1].idx+len(doc[j+1].text)+1:]
                    
            else:
                e_after = entity[doc[j+2].idx+len(doc[j+2].text)+1:]
            if j == 1:
                entity= " ".join([e_new,e_after])
            else:
                e_before = entity[:doc[j-1].idx]
                entity= " ".join([e_before,e_new,e_after])
                   
            entity= doc_token(entity, e_split,nlp, j=j+1)
            break
        else:
            continue
    return entity
      
def create_classes_onto(missing,match_dict, df_entity,reac_dict,p_id,onto_name,rel_synonym,chem_list):
    global sup_cat
    global abbreviation
    
    num=0
    sup_sub_df=pd.DataFrame(columns=['super_class','subclass'])
    new_world= owlready2.World()
    created_classes=[]
    onto= new_world.get_ontology('./ontologies/{}.owl'.format(onto_name)).load()
    pop=[]
    chem_sub={}
    chem_list.extend([str(i) for i in rel_synonym.values()])
    #ind_all= list(onto.individuals())
    for row in df_entity.itertuples():
        classes_parent=[]
        classes= sorted(list(row.classes),reverse=False, key=len)
        #print(classes)
        if row.cems: 
            for c in row.cems:
                if c in sup_cat.keys():
                    for i in sup_cat[c]:
                        if i in row.cems and "based" not in row.entity:
                            sup_sub_df=sup_sub_df.append({'super_class':'chemical substance', 'subclass': row.entity},ignore_index=True)
                            break
                if c in match_dict.values():
                    if c.lower() not in [i.label[0].lower() for i in onto.individuals() if i.label]:
                        cem = onto.search_one(label=c)
                        if not cem:
                            cem = onto.search_one(label=c+' (molecule)')
                            if not cem:
                                cem = onto.search_one(label=c+' (atom)')
                        onto, num,_=add_individum(onto,cem, num,c,p_id=p_id) 
                    
                elif len(c.split())>1:
                    #missing_e=""
                    for i in range(len(c.split())):

                        if c.split()[i] in match_dict.values(): 
                            sup_sub_df= sup_sub_df.append({'super_class':c.split()[i], 'subclass': c},ignore_index=True)  
                        elif i==len(c.split()):
                            sup_sub_df= sup_sub_df.append({'super_class':'molecule', 'subclass': c},ignore_index=True)
                    if c in sup_cat.keys():
                        sup_sub_df= sup_sub_df.append({'super_class':'support material', 'subclass': c},ignore_index=True)
                elif c in sup_cat.keys():
                    sup_sub_df= sup_sub_df.append({'super_class':'support material', 'subclass': c},ignore_index=True)                       
                else:
                    sup_sub_df= sup_sub_df.append({'super_class':'molecule', 'subclass': c},ignore_index=True)
        if row.category =='Catalyst':
            k = 0
            while k<len(row.classes):
                classes_parent.append(classes[k])
                if k != 0:
                    if len(classes[k-1].split())<len(classes[k].split()):
                        sup_sub_df=sup_sub_df.append({'super_class':classes[k-1],'subclass':classes[k]},ignore_index=True)
                        classes_parent.remove(classes[k-1]) 
                    else:                        
                        sup_sub_df=sup_sub_df.append({'super_class':'catalyst role','subclass':classes[k]},ignore_index=True)
                        
                elif row.classes[k]!='catalyst role':
                        sup_sub_df=sup_sub_df.append({'super_class':'catalyst role','subclass':classes[k]},ignore_index=True)
                k+=1  
            
            if row.entity not in list(sup_sub_df['subclass']):    
                for i in classes_parent:
                    sup_sub_df=sup_sub_df.append({'super_class':i, 'subclass':row.entity},ignore_index=True)
            else:
                chem_sub[row.entity]=[]
                for i in classes_parent:
                    chem_sub[entity].append(i)
        elif row.category=='Reaction':
            k=0
            while k<len(row.classes):
                
                classes_parent.append(row.classes[k])
                if k != 0:
                    if len(classes[k-1].split())<len(classes[k].split()):
                        sup_sub_df=sup_sub_df.append({'super_class':classes[k-1],'subclass':classes[k]},ignore_index=True)
                        classes_parent.remove(classes[k-1])                  
                k+=1
            for k in classes_parent:    
                i=len(k.split())-1
                    
                if k in match_dict.values() and k.lower() not in [i.label[0].lower() for i in onto.individuals() if i.label]:
                     onto, num,_=add_individum(onto,onto.search_one(label=k), num,k,p_id=p_id)     

                elif k.split()[i] in match_dict.values():
                    sup_sub_df=sup_sub_df.append({'super_class': k.split()[i], 'subclass':k},ignore_index=True)
                else:
                    sup_sub_df=sup_sub_df.append({'super_class': 'chemical reaction (molecular)', 'subclass':k},ignore_index=True)
                #sup_sub_df=sup_sub_df.append({'super_class':i, 'subclass':row.entity},ignore_index=True) #überdenken
       
                
    with onto:
        
        support_mat= onto.search_one(label='support material')
        if not support_mat:
            support_mat=types.new_class('DC_{:02d}{:02d}'.format(p_id,num), (onto.search_one(label='material'),))
            support_mat.label.append('support material')
            num+=1
        created_classes.append('support material')
        #print(has_role)
        try:
            support_role_i=[i for i in list(onto.search(label='support role')) if i in list(onto.individuals())][0]
        except:
            onto, num,support_role_i=add_individum(onto,onto.search_one(label='support role'),num,'support role',p_id)
        #if 'Reaction' in list(df_entity.category):
            #has_participant= onto.search_one(label='has participant')
        if 'Product' in list(df_entity.category):
            try:
                prod_role_i=[i for i in list(onto.search(label='product role')) if i in list(onto.individuals())][0]
            except:      
                onto, num,prod_role_i=add_individum(onto,onto.search_one(label='product role'), num,'product role',p_id=p_id)        
        if 'Reactant' in list(df_entity.category):
            try:
                reac_role_i=[i for i in list(onto.search(label='reactant role')) if i in list(onto.individuals())][0]
            except:
                onto, num,reac_role_i=add_individum(onto,onto.search_one(label='reactant role'), num,'reactant role',p_id)
        if 'Catalyst' in list(df_entity.category):
            try:
                cat_role_i=[i for i in list(onto.search(label='catalyst role')) if i in list(onto.individuals())][0]
            except:
                onto, num,cat_role_i=add_individum(onto,onto.search_one(label='catalyst role'), num,'catalyst role',p_id)
        indecies=[]
        entities= [i for i in df_entity['entity'] if i]
        print(entities)
        #entities.extend([i for idx,list_c in enumerate(df_entity['cems']) for i in list_c if not df_entity.loc[idx,'entity']])
        for s in sup_sub_df.itertuples():            
            if s.index in indecies:
                continue                                 
            elif s.super_class== 'molecule' or s.super_class== 'support material' or s.super_class=='chemical substance':
                indecies, onto,_,created_classes,num= create_sub_super(num,missing, onto,s.Index, indecies,entities, sup_sub_df,created_classes,chem_list,p_id,s.subclass)
                
                
            else:
                indecies, onto,_,created_classes,num= create_sub_super(num,missing, onto,s.Index, indecies,entities, sup_sub_df,created_classes,chem_list,p_id=p_id)
        
        
        for row in df_entity.itertuples():
            if row.cems:
                e_ind=[i for i in list(onto.search(label=row.entity)) if i in list(onto.individuals())][0]
                print(row.cems)
                if row.category=='Catalyst' and row.entity in chem_sub.keys():
                    ind= onto.search_one(label=row.entity)
                    for c in chem_sub[row.entity]:
                        cat_cl=[i for i in list(onto.search(label=c)) if i in list(onto.classes())][0]
                        ind.RO_0000087.append(cat_cl)
                for c in row.cems:
                    if c!= row.entity and not row.classes:
                        onto, num,ind=add_individum(onto,list(onto.search(label=c))[0], num,row.entity,p_id)
                    else:
                        try:
                            ind=[i for i in list(onto.search(label=c)) if i in list(onto.individuals())][0]
                        except:
                            print('c:{}'.format(c))
                            onto, num,ind=add_individum(onto,list(onto.search(label=c))[0], num,c,p_id)

                        for k in c.split():
                            if k not in sup_cat.keys():
                                k = next((short for short, full in rel_synonym.items() if full == k and short in sup_cat.keys()), None)
                                try:
                                    sup_cat[k]
                                except:
                                    continue
                            ind.RO_0000087.append(support_role_i) #'has role' = RO_0000087
                            ind.support_component_of.append(e_ind)
                            for i in sup_cat[k]:
                                c_t = rel_synonym[i] if i in rel_synonym.keys() else i
                                try:
                                    cat=[i for i in list(onto.search(label=c_t)) if i in list(onto.individuals())][0]
                                except:
                                    onto, num,cat=add_individum(onto,list(onto.search(label=c_t))[0], num,c_t,p_id)
                                    
                                cat.supported_on.append(ind)
                                cat.catalyst_component_of.append(e_ind)
                            pop.append(sup_cat.pop(k)) 
                            
                    if row.category== 'Product':
                        ind.RO_0000087.append(prod_role_i)
                    elif row.category =='Reactant':
                        ind.RO_0000087.append(reac_role_i)
                    elif row.category=='Catalyst':
                        if c==row.entity:
                            ind.RO_0000087.append(cat_role_i) #'has role' = RO_0000087
                        elif e_ind not in ind.support_component_of:                          
                            ind.catalyst_component_of.append(e_ind)
            
            if row.category== 'Reaction':
                if row.entity in reac_dict.keys():
                    ind= [i for i in list(onto.search(label=entity)) if i in list(onto.individuals())][0]                
                    for r in reac_dict[row.entity]:
                       cem_i=[i for i in list(onto.search(label=r)) if i in list(onto.individuals())][0]         
                       ind.RO_0000057.append(cem_i) #'has participant' = RO_0000057
            if row.entity in abbreviation.keys():
                ind.comment.append(abbreviation[row.entity][0])
                     

        for sup,v in sup_cat.items():
            sup = rel_synonym[sup] if sup in rel_synonym.keys() else sup
            try:
                sup=[i for i in list(onto.search(label=sup)) if i in list(onto.individuals())][0]
            except:
                try:
                    onto, num,sup=add_individum(onto,list(onto.search(label=sup))[0], num,sup,p_id)
                except:
                    new_cl = types.new_class(sup, ('support material',))
                    onto, num,sup=add_individum(onto,new_cl, num,sup,p_id)
            sup.RO_0000087.append(support_role_i)
            for cat in v:
                cat=rel_synonym[cat] if cat in rel_synonym.keys() else cat
                try:
                    cat=[i for i in list(onto.search(label=cat)) if i in list(onto.individuals())][0]
                except:
                    try:
                        onto, num,cat=add_individum(onto,list(onto.search(label=cat))[0], num,cat,p_id)
                    except:
                        new_cl = types.new_class(class_name, ('molecule',))
                        onto, num,cat=add_individum(onto,new_cl, num,cat,p_id)
                cat.RO_0000087.append(cat_role_i)    #has role catalyst role
                cat.supported_on.append(sup)
        entities_pub=[]
        entities_pub.extend([c for c in df_entity.entity])
        entities_pub.extend([i for c in df_entity.cems if c for i in c if i not in entities_pub])
        entities_pub= [*set(entities_pub)]
        pub_new=onto.search_one(iri='*publication{}'.format(p_id))
        for entity in entities_pub:
            print('entity:{}'.format(entity))
            ind= [i for i in list(onto.search(label=entity)) if i in list(onto.individuals())][0]
            ind.mentioned_in.append(pub_new)
        for short,entity in rel_synonym.items():
            inds=[i for i in list(onto.search(label=entity))]
            for i in inds:
                i.comment.append(short)
    onto=create_comp_relation(onto,match_dict, rel_synonym,p_id,num)
    #print(list(onto.classes()))                    
    onto.save('./ontologies/{}.owl'.format(onto_name))
    return created_classes, sup_sub_df#,pop         
          
def create_comp_relation(onto,match_dict, rel_synonym,p_id,num):
    global onto_new_dict
    short=[]
    pub_new=onto.search_one(iri='*publication{}'.format(p_id))
    with onto:
        for k,v in onto_new_dict.items():
            print(k)
            if k in match_dict.values() or len(v)==1:
                continue
            else:
                try:
                    mol=[m for m in onto.search(label=k) if m in onto.individuals()][0]
                except:
                    try:
                        onto,num,mol=add_individum(onto,onto.search_one(label=k), num,k,p_id)
                    except:
                        continue
                print('mol:{}'.format(mol))
                for c in v:
                    comp=onto.search(label=c)
                    if not comp:
                        continue
                    elif len(comp)==1:
                        onto,num,c_i=add_individum(onto,comp[0], num,c,p_id)
                    else:
                        c_i=[i for i in comp if i in onto.individuals()][0]
                    short=[i for i in rel_synonym.keys() if rel_synonym[i]==c]
                    if short:
                        for i in short:
                            if i not in list(c_i.comment):
                                c_i.comment.append(i)
                                
                    mol.BFO_0000051.append(c_i) #"has part" realtion between classes or individuals? chosen individuals because of reasoning time
                    c_i.mentioned_in.append(pub_new)
    return onto

    
def create_subclass(onto,subclass,entities,super_class,num,created_classes,chem_list,p_id ):
    new_sub=None  
    created_ind= [i.label[0].lower() for i in onto.individuals() if i.label]
    
    if "based" in subclass or [c for c in chem_list if re.search(r'\b[\d.,%]*{}\b'.format(c),subclass) if c!=subclass]:
        
        if subclass.lower() not in created_ind:
            onto, num, new_i=add_individum(onto,super_class,num,subclass,p_id)
            
        else:
            new_i=onto.search_one(label=subclass)
            new_i.is_a.append(super_class)  
    
    elif subclass==super_class.label[0]:    #to implement for reaction
        onto, num,new_i=add_individum(onto,super_class, num,subclass,p_id)
    elif subclass.lower() not in created_classes:
          class_name= 'DC_{:02d}{:02d}'.format(p_id, num)
          num +=1
          new_sub = types.new_class(class_name,(super_class,))      
          new_sub.label.append(subclass)
          created_classes.append(subclass.lower())
          if subclass in entities:
              if subclass.lower() not in created_ind:
                  onto, num, new_i=add_individum(onto,new_sub, num,subclass,p_id)
              elif subclass.lower() in created_ind:
                  new_i=onto.search_one(label=subclass)
                  new_i.is_a.append(super_class)
    if new_sub:
        new_sub.comment.append('created automatically')    

    return onto, created_classes,  num 

def add_individum(onto,super_class, num,ind,p_id):
    with onto:
        print(super_class)
        new_i=[i for i in onto.search(label=ind) if i in onto.individuals()]
        if new_i:
            new_i=new_i[0]
        else:
            new_i =  super_class('DC_{:02d}{:02d}'.format(p_id,num))
            num+=1
            
            new_i.label.append(ind)
            new_i.comment.append('created automatically')                
    return onto, num, new_i        

def create_sub_super(num,missing, onto, idx, indecies,entities, sup_sub_df,created_classes,chem_list,p_id, subclass=None ):
    super_class_l=sup_sub_df.loc[idx, 'super_class']
    with onto:
        if super_class_l not in missing or super_class_l in created_classes:
            super_class= onto.search_one(label=super_class_l)
            if not super_class:
                super_class= onto.search_one(prefLabel=super_class_l)
            if not subclass:
                onto, created_classes,num=create_subclass(onto,sup_sub_df.loc[idx, 'subclass'],entities,super_class,num,created_classes,chem_list,p_id=p_id)
        elif super_class_l in list(sup_sub_df['subclass']):
            query = sup_sub_df.query('subclass == "{}"'.format(super_class_l))
            idx=query.index[0]
            #print(idx)
            subclass=super_class_l
            #super_class_l=query['super_class'].iloc[0] # only for the list with single super class
            indecies.extend(list(query.index))
            indecies, onto, super_class,created_classes,num= create_sub_super(num,missing, onto, idx, indecies,entities,sup_sub_df,created_classes,chem_list,p_id,subclass=subclass)
            query= sup_sub_df.query('super_class == "{}"'.format(super_class_l))
            if query.empty==False:
                indecies.extend(list(query.index))
                for q in range(len(query)):
                    subclass=query['subclass'].iloc[q]
                    onto, created_classes,num=create_subclass(onto,subclass,entities,super_class,num,created_classes,chem_list,p_id=p_id)
                    subclass=None 
        else: 
            class_name= 'DC_{:02d}{:02d}'.format(p_id, num)
            num+=1
            super_class = types.new_class(class_name, (Thing,))
            super_class.comment.append('created automatically') 
            super_class.label.append(super_class_l)
            created_classes.append(super_class_l.lower())
        if subclass:
            if subclass.lower() not in created_classes:
                class_name= 'DC_{:02d}{:02d}'.format(p_id, num)
                num+=1
                new_sub= types.new_class( class_name,(super_class,))        
                new_sub.comment.append('created automatically') 
                new_sub.label.append(subclass)
                created_classes.append(subclass.lower())
            else:
                new_sub=onto.search_one(label= subclass)
            super_class=new_sub
        if super_class_l.lower() not in created_classes:
            created_classes.append(super_class_l.lower())    

    return  indecies, onto,super_class, created_classes,num
 




def run(abstract,model,onto_list,onto_new,onto_name):#,p_id,onto_class_list
    sents = text_prep(abstract) 
    categories,chem_list, reac_dict, sup_cat= CatalysisIE_search(model, sents, onto_list,onto_new)
    #onto_new_dict, missing, match_dict, rel_synonym= chemical_prep(chem_list, onto_list,onto_class_list,onto_new)
    #df_entity,missing, match_dict,rel_synonym=catalyst_entity(categories, rel_synonym, chem_list,missing,match_dict, onto_list, onto_new )
    #onto_extender(onto_list, onto_name)
    #eq=equality(onto_list,onto_name) #für validierung alle eq1 classen aufnehmen
    #created_classes,sub_sup=create_classes_onto(onto_new_dict,missing, match_dict, df_entity,reac_dict, p_id, onto_new,abbreviation,rel_synonym,chem_list)
    return categories,chem_list, sup_cat#, onto_new_dict#created_classes, eq,df_entity

#onto_class_list=load_classes_chebi()

#onto_new_dict, missing, match_dict, rel_synonym=chemical_prep_2(chem_list, onto_list,onto_class_list)
#create in input ontology 'support material'(subclass of 'material'), 'supported on' property
 
ckpt_name = 'CatalysisIE/checkpoint/CV_0.ckpt'
bert_name = 'CatalysisIE/pretrained/scibert_domain_adaption'
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
onto_name = 'afo'
onto_list ={
            'CHEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            #'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            'CHMO' : 'http://purl.obolibrary.org/obo/chmo.owl',
            'AFO'  : "./ontologies/afo.owl"
            }   
onto_new= onto_name+'_upd'
test_txt='''
In order to reveal the influences of metal-incorporation and regeneration of ZSM-5 zeolites on naphtha catalytic cracking, the fresh and regenerated Sr, Zr and La-loaded ZSM-5 zeolites have been prepared and evaluated using n-pentane catalytic cracking as a model reaction.
It was found that the metal-incorporated ZSM-5 zeolites promoted hydride transfer reactions, and the Zr-incorporation helped to promote and maintain the catalytic activity while reduced alkenes selectivity;
the regenerated ZSM-5 zeolites promoted C–H bond breaking that increased alkenes selectivity and n-pentane conversion but accelerated catalyst deactivation.
The regenerated metal-incorporated ZSM-5 zeolites combined the feature roles of metal-incorporation and regeneration in modulating reaction pathways, and seemed a promising way to balance the activity, stability and alkenes selectivity, facilitating the optimal production for light olefins.
Within the research scope, the regenerated Zr-loaded ZSM-5 zeolites reached an optimal production (0.97 g) for light olefins in n-pentane catalytic cracking at 550 °C with a weight hourly space velocity of 3.7 h−1 in 3 h, which was 24% higher than that of the parent HZSM-5 (0.78 g).
RhCo/SiO2 catalyst.This work reported the heterogeneous rhodium oxide catalyst encapsulated within microporous silicalite-1 (S-1) zeolite (Rh2O3@S-1) through epitaxial growth of S-1 seeds pre-anchored with rhodium species.
RhCl3 • nH2O, Co(NO3)2 • 6H2O and 
Co2(CO)8 were purchased commercially. 
Supported catalysts based on the Rh-Co couple, mainly derived from the decomposition of 
bimetallic carbonylic clusters, were found particularly active and selective in the vapor phase 
hydroformylation of simple olefins provided that 
the two metals were in intimate contact 
Rh4(CO)12, and RhCo3(CO)12, were synthesized 
according to literature [14,15]. SiO2 was a silica 
‘Aerosil’ supplied by Degussa with a surface 
area of 380 m2/g. Cobalt
complexes had been the main industrial hydroformylation catalysts until the early 1970s, i.e., prior to the commercialization of
rhodium based catalysts. The present work concentrates on heterogeneous ethylene
hydroformylation on a series of Rh and Co based catalysts. Supported catalysts based on the Rh-Co couple, mainly derived from the decomposition of 
bimetallic carbonylic clusters, were found particularly active and selective in the vapor phase 
hydroformylation of simple olefins provided that 
the two metals were in intimate contact. Here we report the preparation, characterization and reactivity studies on propene hydroformylation of Rh-Co based catalysts, with various Rh/Co ratios, obtained by the reduction of 
the metal salts coadsorbed on silica with NaBH, 
in anaerobic conditions. When the Rh/Al based catalysts were subjected to the same 
experimental conditions only the v(C0) absorption at 2015 cm-’ was observed and appears to be involved in the catalytic process. Based on the DRC 
analysis of the reaction orders and apparent activation energies, we propose that the first step of 
propylene hydrogenation to produce propyl species, which is often considered as a kinetically 
non-relevant step, may play a more important role and should draw more attention for future 
improvement of Rh-based heterogeneous catalysts for propylene hydroformylation. However, detailed mechanisms on
the promotion effect of alloying secondary metals with Rh
still remain elusive, which can be of great importance leading
to the rational optimization of Rh-based alloy catalysts for
active and selective heterogeneous hydroformylation. In this communication, systematic studies of catalytic
behaviors from monometallic Rh supported on MCM-41 (Rh/
MCM-41) to Rh-based bimetallic catalysts with the addition of
a secondary 3rd row transition metal M (RhM3/MCM-41, M =
Fe, Co, Ni, Cu, or Zn) for the heterogeneous hydroformylation
of ethylene were reported by combining experiments and
density functional theory (DFT) calculations. Bimetallic heterogeneous catalysts 
based on rhodium supported on various oxides proved to be the more chemo- and regio-selective systems.Recently, it has been shown that tuning the local environment of Rh and Ir-based atomically dispersed catalysts beyond changing the support composition enables interesting
chemistry, such as ethylene dimerization, NO reduction, 1,3-
butadiene hydrogenation, and methane conversion to acetic
acid with high selectivity.'''
categories,chem_list, sup_cat=run(test_txt,model,onto_list,'afo','afo')
""" 
"""
#onto_name='afo_upd'
#test_sents = text_prep(test_txt)       

#categories,chem_list,abbreviation, sup_cat, chem_list_all,reac_dict= CatalysisIE_search(model, test_sents, onto_list)    

#onto_new_dict, missing, match_dict, rel_synonym= chemical_prep(chem_list, onto_list,onto_class_list, chem_list_all,abbreviation, onto_name)     
"""

#onto_extender (onto_list)
#eq=equality( onto_list,onto_name='AFO')
#created_classes=create_classes_onto(missing_all, df_entity)


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
sup_cat={'ZSM-5': ['Sr', 'Zr', 'La'],
 'SiO2': ['RhCo'],
 'Al': ['Rh'],
 ' MCM-41': ['Rh'],
 'MCM-41': ['RhM3']} 
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
 'RhM3',
 'Cobalt',
 ' MCM-41',
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
missing=['propyl',
 'prop-1-ene',
 'cobalt(2+);rhodium(3+)',
 'oxorhodium',
 'RhCo3(CO)12',
 'acetic',
 'Rh2O3',
 'MCM-41',
 'ZSM-5']
match_dict={'http://purl.obolibrary.org/obo/CHEBI_33324': 'strontium atom',
 'http://purl.obolibrary.org/obo/CHEBI_29239': 'hydride',
 'http://purl.obolibrary.org/obo/CHEBI_39478': 'buta-1,3-diene',
 'http://purl.obolibrary.org/obo/CHEBI_30563': 'silicon dioxide',
 'http://purl.obolibrary.org/obo/CHEBI_27363': 'zinc atom',
 'http://purl.obolibrary.org/obo/CHEBI_28112': 'nickel atom',
 'http://purl.obolibrary.org/obo/CHEBI_48729': 'zeolite',
 'http://purl.obolibrary.org/obo/CHEBI_33359': 'rhodium atom',
 'http://purl.obolibrary.org/obo/CHEBI_32878': 'alkene',
 'http://purl.obolibrary.org/obo/CHEBI_33342': 'zirconium atom',
 'http://purl.obolibrary.org/obo/CHEBI_28984': 'aluminium atom',
 'http://purl.obolibrary.org/obo/CHEBI_28694': 'copper atom',
 'http://purl.obolibrary.org/obo/CHEBI_25805': 'oxygen atom',
 'http://purl.obolibrary.org/obo/CHEBI_27638': 'cobalt atom',
 'http://purl.obolibrary.org/obo/CHEBI_49666': 'iridium atom',
 'http://purl.obolibrary.org/obo/CHEBI_33641': 'olefin',
 'http://purl.obolibrary.org/obo/CHEBI_27573': 'silicon atom',
 'http://purl.obolibrary.org/obo/CHEBI_27594': 'carbon atom',
 'http://purl.obolibrary.org/obo/CHEBI_25741': 'oxide',
 'http://purl.obolibrary.org/obo/CHEBI_15366': 'acetic acid',
 'http://purl.obolibrary.org/obo/CHEBI_37527': 'acid',
 'http://purl.obolibrary.org/obo/CHEBI_33336': 'lanthanum atom',
 'http://purl.obolibrary.org/obo/CHEBI_25367': 'molecule'}
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
_,_,_, sup_cat, _,reac_dict= CatalysisIE_search(model, test_sents, onto_list) 
""" 

''' 

#

d={'entity':entity,'classes':classes,'cems':cems, 'category':category}
df_entity=pd.DataFrame(data=d)
created_classes=create_classes_onto(missing_all, df_entity)
for c in df_entity.
'''  
'''
	entity	classes	cems	category
0	cobalt;rhodium	[]	['cobalt;rhodium']	Catalyst
1	rhodium atom	[]	['rhodium atom']	Catalyst
2	cobalt atom	[]	['cobalt atom']	Catalyst
3	decarbonylation	['decarbonylation']	[]	Reaction
4	hydroformylation	['hydroformylation']	[]	Reaction
'''
"""  
class expand_onto:
    
    def __init__(self,onto_list, onto_name):
        self.onto_list=onto_list
        new_world= owlready2.World()
        self.onto =new_world.get_ontology("./ontologies/{}_upd.owl".format(onto_name.lower())).load()
        new_world1=owlready2.World()
        self.onto_old=new_world1.get_ontology("./ontologies/{}.owl".format(onto_name.lower())).load()
    
    def write_in_txt(key,value,onto_name):
        path ='class_lists/IRIs_'+ onto_name +'.txt'
        txt = open(path, 'a')
        iri_class = key + '  # ' + value +'\n'
        txt.write(iri_class) 
        txt.close() 
    
    def search_value_in_nested_dict(value, onto_names, onto_dict, match_dict):
        
        for k in onto_names:
            for IRI in onto_dict[k].keys() :
                for key, val in onto_dict[k][IRI].items():
                    if val and value.lower() == val.lower():
                        match_dict[IRI] = val
                    else:
                        continue
                
        return match_dict
    
    def create_list_IRIs(self,class_list,IRI_json_filename = 'iriDictionary'):
        f = open('{}.json'.format(IRI_json_filename))
        onto_dict = json.load(f)
        f.close()
        match_dict={}
        onto_names=list(self.onto_list.keys()) 
        for entity in class_list:
            match_dict = self.search_value_in_nested_dict(entity,onto_names,onto_dict,match_dict)
        print(match_dict)   
        for key,value in match_dict.items():
            x=[]
            for O in onto_names:
                list_IRIs= onto_dict[O].keys()
                try:
                    df= pd.read_excel('./AFO_{}.xlsx'.format(O),sheet_name=0)
                except:
                    print('List with common ontology classes for {} is not provided'.format(O))
                double_afo=df['{}_IRI'.format(O)].to_list()
                if key in double_afo:
                        continue
                if key in list_IRIs and key not in x:
                    self.write_in_txt(key,value,O)
                    x.append(key)
                elif key in x:
                    continue
                else:
                    self.write_in_txt(key, value, 'diverse')
            
      
    def onto_extender (self):
        for o,iri in self.onto_list.items():
            # Der erste Pfad führt zur robot.jar und muss evtl. vom Nutzer angepasst werden.
            # --input: ist die Ontologie in der nach den gewünschten IRI's gesucht werden soll.
            # --method: kann nach Bedarf abgewandelt werden [http://robot.obolibrary.org/extract]
            # --term-file: ist die Textdatei, in der die IRI's abgelegt sind welche gesucht werden sollen
            # --output: selbsterklärend
            os.system('java -jar c://Windows/robot.jar extract --input-iri {} --method BOT --term-file class_lists/IRIs_{}.txt --output ontology_sniplet/{}_classes.owl'.format(iri,o,o))
        for filepath in glob.iglob('ontology_sniplet/*.owl'):
            os.system('robot merge --input {} --input ontologies/afo_upd.owl --output ontologies/afo_upd.owl'.format(filepath))
    
         
    def equality(self):
        labels_old=[]
        for c_1 in self.onto_old.classes():
            if c_1.label:
                labels_old.append(c_1.label[0])
        for o in list(self.onto_list.keys()):
            try:
                new_world2 = owlready2.World()
                onto_snip = new_world2.get_ontology("./ontology_sniplet/{}_classes.owl".format(o)).load()
            except:
                print('no entity from {} ontology found'.format(o))
            for c_2 in list(onto_snip.classes()):
                if c_2.label[0] in labels_old:
                    iri_snip=c_2.iri
                    iri_old=self.onto_old.search_one(label=c_2.label[0]).iri
                    self.onto.search_one(iri=iri_old).equivalent_to.append(self.onto.search_one(iri=iri_snip))
                    self.onto.search_one(iri=iri_old).comment=([
                        'Equivalence with {} added automatically'.format(c_2.iri)])
                    self.onto.search_one(iri=iri_snip).comment=([
                        'Equivalence with {} added automatically'.format(self.onto.search_one(iri=iri_old).iri)]) 
        self.onto.save('./ontologies/{}_upd.owl'.format(onto_name.lower()))           

#create new properties in ontology: support_of and supported_by
"""
#    onto_class = [k_o for k, v in comp_dict.items() for comp in v for k_o, v_o in onto_dict.items() for syn_comp in v_o if comp == syn_comp]
