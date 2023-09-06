# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:51:27 2023

@author: chern
"""
import stanza
stanza.download('en', package='craft', processors='tokenize')
import spacy
from owlready2 import *
import pickle
import json
import logging
import pandas as pd
import pytorch_lightning as pl
from copy import deepcopy
from CatalysisIE.model import *
from CatalysisIE.utils import *
import requests
import json
import os
import glob
from chemdataextractor import Document
from pubchempy import get_compounds
import types
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import StringIO
API_URL = "https://rel.cs.ru.nl/api"
import pandas as pd

def get_pdf_file_content(pdf_file):
    resource_manager = PDFResourceManager(caching=True)
    out_text = StringIO()
    la_params = LAParams()
    text_converter = TextConverter(resource_manager, out_text, laparams=la_params)
    fp = open(pdf_file, mode='rb')
    interpreter = PDFPageInterpreter(resource_manager, text_converter)
    #for page in PDFPage.get_pages(fp, pagenos=set(), maxpages=0, password='', caching=True, check_extractable=True):
    #    interpreter.process_page(page)
    interpreter.process_page(PDFPage.get_pages(fp, pagenos=set(), maxpages=0, password='', caching=True, check_extractable=True)[0])
    text = out_text.getvalue()
    fp.close()
    text_converter.close()
    out_text.close()
    return text
    
def get_globed_content():
    # opens all PDF file, hands it to get_pdf_file_content function and converts it into string
    pdf_globed = glob2.glob('./import/*.pdf')
    pdf_text = []
    for i in range(len(pdf_globed)):
        pdf_text.append(get_pdf_file_content(pdf_globed[i]))
    pdf_text_string = ''.join(pdf_text)
    return pdf_text_string

def text_load(name, mincount):
    name_raw = name + "_raw"
    
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
    new_world = owlready2.World()
    onto = new_world.get_ontology("./ontologies/{}.owl".format(ontology_name)).load()
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
    set_org_mol = onto.search_one(label='organic molecular entity').descendants()#exclude "organic molecular entity
    set_org_mol= set_org_mol.union(onto.search_one(label='organic group').descendants())
    for i in set_org_mol:
        if i in onto_class_list:
            onto_class_list.remove(i)
    return onto_class_list
        
def chemical_prep(chem_list, onto_list,onto_class_list, chem_list_all):
    rel_synonym={}
    comp_dict = {}
    class_list=[]        
    onto_new_dict ={}
    synonyms={}

    onto_dict,inchikey= synonym_dicts(onto_class_list)
    for molecule in chem_list:  
        non_chem = False
        print(molecule)
        pattern= '('+molecule+')[—–-][\d]+' #ex: 'ZSM-5' with m='ZSM'
        for i in chem_list_all:
            match_hyph=re.search(pattern,i)
            if match_hyph:
                non_chem = True
                chem_list=chem_list[:chem_list.index(molecule)]+[i]+chem_list[chem_list.index(molecule)+1:]
                molecule= i
                break
        pattern = '[\d,]+[—–-] [a-z]+'
        if re.search('^ [A-Za-z\d—–-]+',molecule):
            print(molecule)
            molecule=molecule.replace(' ','')
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
    print(comp_dict)
    for k,v in comp_dict.items():
        print('{}:{}'.format(k,v))
        i=0
        if k not in onto_new_dict.keys():
           
            for c in v:
                
                print(c)
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
                    non_comp = False
                else:
                    non_comp, class_list, comp, rel_synonym = compare_synonyms(synonyms,inchikey, class_list, c, rel_synonym,comp= True) 
                
                #if non_comp == True:
                #    break
                
                onto_new_dict[key].append(comp)
            for i in onto_new_dict[key]:
                
                if len(i) ==1:#remove components if one of the components (atoms) doesn't exist (ex.ZMS- Z,M don't exist, S-exists) -wrong: mb delete
                    #print('not all components found {}:{}'.format(key,onto_new_dict[key]))
                    
                    print('deleted key:{}'.format(key))
                    class_list.remove(i)
                    class_list.remove(key)
                    onto_new_dict.pop(key)
    class_list= [*set(class_list)] #remove duplicates
    #print(class_list)
    class_list.extend(['molecule','mineral'])
    missing, match_dict = create_list_IRIs(class_list, onto_list,IRI_json_filename = 'iriDictionary')
    
    return onto_new_dict, missing, match_dict, rel_synonym
     
def fill_synonyms(synonyms,c,v,k):
    pattern= r'^{}$'.format(c)
    for s in v:
        if re.search(pattern,s):
            if c not in synonyms.keys():
                synonyms[c]=[]
                synonyms[c].append(k)
            elif k not in synonyms[c]: 
                synonyms[c].append(k)

    if c not in synonyms.keys():
        synonyms[c]=[]
    
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
                if not key:
                    print('no synonyms but some matches in inchikey for {}:{}'.format(k, comp_check))
                    key = k                  
    
    if not key:  
        key=k
    rel_synonym[k]=key          
    class_list.append(key)
    return none_comp,class_list, key, rel_synonym
                                  
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

def CatalysisIE_search(model, test_sents, onto_list):
    nlp = spacy.load('en_core_web_sm')
    chem_list_all = []
    chem_list = []
    cat_sup_list=[]
    sup_cat={}
    abbreviation = {}
    a=0
    categories={}
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
            
            if i == a+1 and '({})'.format(entity) in assemble_token_text(sent):
                if entity in abbreviation.keys():
                    abbreviation[entity].append(entity_old)
                else:
                    abbreviation[entity]=[entity_old]
            
            doc_list=[]
            match_hyph=re.findall(r'(([A-Z](?:[a-z])?)[—–-]([A-Z](?:[a-z])?))', entity) # Rh-Co --> RhCo
            if match_hyph:
                for i in range(len(match_hyph)):
                    entity = entity.replace(match_hyph[i][0],match_hyph[i][1]+match_hyph[i][2])
                    print(entity)
                
            doc = nlp(entity)
            for i in range(len(doc)):
                if doc[i].tag_ == 'NNS':
                    doc_list.append(str(doc[i].lemma_))
                #elif i!=doc[-1].i and ''.join([doc[i-1,i,i+1]]) in spans_list:
                    
                else:
                    doc_list.append(str(doc[i]))
            entity= " ".join(doc_list)         # plural to singular
            e_split= entity.split()
            entity = doc_token(entity, e_split)
             
            if entity in categories.keys():
                continue
            else:
                
                mol = re.findall(r'([\w@—–-]+[\s]?(?:/[\s]?[\w@—–-]+)+)', entity)
                if mol:
                    for i in range(len(mol)):
                        print(mol)
                        mol_part = [(mol[i],) + tuple(mol[i].split('/'))]
                        cat_sup_list.append(mol[0][0])
                        if l=='Catalyst':
                            support = mol_part[0][2]
                            chem_list.append(support)
                            catalyst= mol_part[0][1]
                            chem_list.append(catalyst)
                            entity = entity.replace('/'+support,'')# remove '/molecule'; already in sup_cat
                            if support in sup_cat.keys():
                                if catalyst not in sup_cat[support]:
                                    sup_cat[support].append(catalyst)
                            else:
                                    sup_cat[support] = [catalyst]
                    
                        else:
                                for k in range(1, len(mol_part[o])):
                                    chem_list.append(mol[i][k])
                                    entity= entity.replace('/',',')
                pattern = '^[\d,]+[—–-] [a-z]+$'
                if re.search(pattern,entity) or re.search('^ [A-Za-z\d—–-]+$',entity):

                    entity=entity.replace(' ','') 
                spans=Document(entity).cems
                chem_list.extend([c.text for c in spans if c.text not in cat_sup_list])
                if 'system' in entity or 'surface' in entity and l=='Catalyst':
                        entity=entity.replace('system','catalyst')
                        entity=entity.replace('surface','catalyst')
                if 'loaded' in entity:
                    for i,c in enumerate(spans):
                         
                        if i != 0:
                            e_btwn = entity[spans[i].end:spans[i-1].start]
                            if e_btwn!= ' ' and 'loaded' in e_btwn:    #Zr-loaded ZSM-5 zeolites
                                loaded_end =  entity.index('loaded')+len('loaded')+1
                                for c in chem_list:
                                        try:
                                            idx=entity.index(c)
                                        except:
                                            continue
                                        else:
                                            if idx == loaded_end:
                                                if c in sup_cat.keys():
                                                    if spans[i].text not in sup_cat[c]:
                                                        sup_cat[c].append(spans[i].text)
                                                else:
                                                    sup_cat[c] = [spans[i].text]
                    entity=entity.replace('loaded','supported on')
                                            
                
                
                #e_split= entity.split()
                #entity = doc_token(entity, e_split)
                categories[entity]=l    
              
            entity_old=entity
            a=j+1
            chem_list= [*set(chem_list)]
            chem_list_all=[*set(chem_list_all)]
    return categories,chem_list,abbreviation, sup_cat, chem_list_all
# supported_on relation getrennt in ursprungsontologie erstellen
def catalyst_support(c,sup_cat,onto):
    carrier_role= onto.search_one(label='carrier role')
    has_role= onto.search_one( label='has role') 
    supported_on= onto.search_one(label='supported on')
    with onto:
        
            sup=onto.search_one(label=c)
            sup.has_role=carrier_role()
            for i in sup_cat[c]:
                cat= onto.search_one(label=i)
                cat.supported_on= sup()
            
#carrier_role
    
def catalyst_entity(categories, rel_synonym, sup_cat,chem_list,missing_all,onto_list ):
    nlp = spacy.load('en_core_web_sm')
    based_cems={}
    classes={}
    spans_dict={}
    support=[]
    list_all=[]
    chem_list.extend([str(i) for i in rel_synonym.values()]) 
    for entity,l in categories.items():
        if l =='Catalyst':

                if entity in classes.keys():
                    continue
                else:
                    spans_dict[entity]=[]
                    spans_n=[]

                    if "based" in entity:
                        support=[]
                        e_snip=None
                        based_m = re.search('based',entity)
                        if based_m.start() != 0 or entity[:based_m.start()-1] != 'catalyst': 
                            e_snip = entity[:based_m.start()-1]
                            #spans = Document(e_snip).cems
                            e_cleaned = e_snip
                            for c in chem_list:
                                pattern='\\b'+c+'\\b'
                                if re.search(pattern,e_snip):
                                    e_btwn= e_snip[e_snip.index(c)+len(c)+1:]
                                    try:
                                        c_t = rel_synonym[c] #search in preprocessed chem entities dict
                                    except:
                                        c_t = c
                                    if c_t in sup_cat.keys():
                                             continue
                                    elif "supported" in e_btwn:
                                             e_cleaned = e_btwn[re.search('supported',e_btwn).end():]
                                             support.append(c_t)
                                             continue
                                    
                                    if c_t not in spans_n:    
                                        spans_n.append(c_t)
                                    
                                    e_snip=e_snip.replace(c,'')
                            
                            if 'catalyst' in e_cleaned:
                                classes= check_in_snip(e_cleaned, classes,nlp, entity)
                                   
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
                            #spans = Document(e_snip).cems
                            #cleaned= e_snip
                            if re.search('supported', e_snip) and s_on==False: 
                                #based on silica supported bimetallic catalysts
                                e_btwn=e_snip[:re.search('supported', e_snip).start()+1]
                            else:
                                sup_i = None
                            for c in chem_list:
                                pattern='\b'+c+'\b'
                                if re.search(pattern,e_snip):
                                    try:
                                        c_t = rel_synonym[c_t]
                                    except:
                                        c_t = c
                                    if sup_i and c in e_btwn:
                                            support.append(c) 

                                                            
                                    if c_t not in spans_n:    
                                        spans_n.append(c_t)  
                                 
                                #e_cleaned = [re.search(c.text,e_btwn).end()+1:]
                            
                            if 'catalyst' in e_snip:
                                classes= check_in_snip(e_snip, classes,nlp, entity)
                        
                    elif entity in chem_list or set(entity.split()).issubset(chem_list):
                        list_all.append([None,[],[entity],categories[entity]])

                    if support:
                        snaps_n=[c for c in spans_n and c not in support]  
                        for i in support:
                            if i in sup_cat.keys():
                                sup_cat[c].extend([c for c in snaps_n and c not in sup_cat[i]])
                            else:
                                sup_cat[i] = snaps_n
                    spans_dict[entity].extend(spans_n)
                   
        elif entity in chem_list or set(entity.split()).issubset(chem_list):
            list_all.append([None,[],[entity],categories[entity]])
            
    not_del=[] 
    classes_n={} 
    for k_1,v_1 in classes.items():
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
            all_values=[v[0] for v in classes_n.values() if v]
            i = len(v_1)-1
            ele_old=None
            while i >= 0:
                if v_1[i] not in all_values and v_1[i] not in classes_n[k_1]:
                    classes_n,ele_old=shortcut_add_class(ele_old, classes_n, not_del, value=v_1, i=i, key=k_1 )
                elif ele_old:
                    not_del.append(ele_old)
                i-=1
    
    print(classes_n)
    for k,v in classes_n.items():
        list_all.append([k,v,spans_dict[k],categories[k]])
        
        missing, _ = create_list_IRIs(v, onto_list,IRI_json_filename = 'iriDictionary',include_main= True) 
        missing_all.extend(missing)         
    df_entity= pd.DataFrame(list_all, columns=['entity','classes', 'cems', 'category'])        
    return sup_cat, df_entity,missing_all
        
def shortcut_add_class(ele_old,classes_n, not_del, value, i, key ):
       
    classes_n[key].append(value[i])
    if ele_old and ele_old not in not_del:
            classes_n[key].remove(ele_old)
    if i!=0:
        if len(value[i])<len(value[i-1]):
            ele_old=value[i]
        else:
            ele_old=None
    
    return classes_n,ele_old
         


def check_in_snip(e_snip, classes, nlp, entity):
    classes[entity]=[]
    doc_snip= nlp(e_snip)
    for token in doc_snip:
        if token.head.text == 'catalyst' or token.pos_=='VERB':
            if 'catalyst role' not in classes[entity]:
                classes[entity] = ['catalyst role']
            if token.text != 'catalyst':
                if not  re.search(r'[Ss]upported',token.text):
                    token_new=token.text.lower()+' catalyst role'
                    classes[entity].append(token_new)
                if token.children:
                    
                    for i in reversed(range(len([t.text for t in token.children if t.text != "catalyst"]))):
                        token_new=[t.text.lower() for t in token.children][i] +' ' + token_new
                        classes[entity].append(token_new) 
        
    classes[entity] = [*set(classes[entity])] 
    if len(classes[entity])>1:
        classes[entity].remove('catalyst role')
    return classes
#classes={'Rh-based atomically dispersed heterogenous catalyst':['atomically dispersed catalyst role','dispersed catalyst role','heterogenous catalyst role']}
def doc_token(entity, e_split, j=0):
    nlp = spacy.load('en_core_web_sm')
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
                   
            entity= doc_token(entity, e_split, j=j+1)
            break
        else:
            continue
    return entity
      
def create_classes_onto(missing, df_entity, onto_name='afo_upd1'):
    num=0
    sup_sub_df=pd.DataFrame(columns=['super_class','subclass'])
    new_world= owlready2.World()
    created_classes=[]
    onto= new_world.get_ontology('./ontologies/{}.owl'.format(onto_name)).load()
    for row in df_entity.itertuples():
        classes_parent=[]
        classes= sorted(list(row.classes),reverse=False, key=len)
        print(classes)
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
                        #super_class = onto.search_one(label='catalyst role')
                elif row.classes[k]!='catalyst role':
                        sup_sub_df=sup_sub_df.append({'super_class':'catalyst role','subclass':classes[k]},ignore_index=True)
                k+=1  
            #if 'based' not in row.entity:
            for i in classes_parent:
                sup_sub_df=sup_sub_df.append({'super_class':i, 'subclass':row.entity},ignore_index=True)
        if row.cems:
            for c in row.cems:
                if c in sup_cat.keys():
                    catalyst_support(c,sup_cat,onto)
                if c not in missing:
                    continue
                elif c in sup_cat.keys():
                    sup_sub_df= sup_sub_df.append({'super_class':'mineral', 'subclass': c},ignore_index=True)    
                else:
                    sup_sub_df= sup_sub_df.append({'super_class':'molecule', 'subclass': c},ignore_index=True)
      
    with onto:
        indecies=[]
        for s in sup_sub_df.itertuples():            
            if s.index in indecies:# or s.super_class.lower() in created_classes:
                continue                                 
            elif s.super_class== 'molecule' or s.super_class== 'material':
                indecies, onto,_,created_classes,num= create_sub_super(num,missing, onto,s.Index, indecies,list(df_entity['entity']), sup_sub_df,created_classes,s.subclass)
                
            else:
                indecies, onto,_,created_classes,num= create_sub_super(num,missing, onto,s.Index, indecies,list(df_entity['entity']), sup_sub_df,created_classes)
        for row in entity_df.itertuples():
            if row.cems:
                for c in row.cems:
                    if c in sup_cat.keys():
                        catalyst_support(c,sup_cat,onto)
            if s.category== 'Product':
                ...
    #print(list(onto.classes()))                    
    onto.save('./ontologies/{}_1.owl'.format(onto_name))
    return created_classes                   
def create_subclass(onto,subclass,entities,super_class,num,created_classes):
      new_sub=None  
      if "based" in subclass:
          return onto, created_classes, num
      elif subclass in entities: #überdenken. "based" nicht includieren
          
          if subclass not in created_classes:
              new_sub =  super_class('DC_{:04d}'.format(num))
              num+=1
              new_sub.label.append(subclass)
              created_classes.append(subclass.lower())
          elif subclass.lower() in created_classes:
              new_sub=onto.search_one(label=subclass)
              new_sub.is_a.append(super_class)
      
      elif subclass.lower() not in created_classes:
          class_name= 'DC_{:04d}'.format(num)
          num +=1
          new_sub = types.new_class(class_name,(super_class,))      
          new_sub.label.append(subclass)
          created_classes.append(subclass.lower())
                
      if new_sub:
          new_sub.comment.append('created automatically')      
          
      return onto, created_classes,num                             
def create_sub_super(num,missing, onto, idx, indecies,entities, sup_sub_df,created_classes,subclass=None ):
    super_class_l=sup_sub_df.loc[idx, 'super_class']
    with onto:
        if super_class_l not in missing or super_class_l in created_classes:
            super_class= onto.search_one(label=super_class_l)
            if not super_class:
                super_class= onto.search_one(prefLabel=super_class_l)
            if not subclass:
                onto, created_classes,num=create_subclass(onto,sup_sub_df.loc[idx, 'subclass'],entities,super_class,num,created_classes)
        elif super_class_l in list(sup_sub_df['subclass']):
            query = sup_sub_df.query('subclass == "{}"'.format(super_class_l))
            idx=query.index[0]
            print(idx)
            subclass=super_class_l
            #super_class_l=query['super_class'].iloc[0] # only for the list with single super class
            indecies.extend(list(query.index))
            indecies, onto, super_class,created_classes,num= create_sub_super(num,missing, onto, idx, indecies,entities,sup_sub_df,created_classes,subclass=subclass)
            query= sup_sub_df.query('super_class == "{}"'.format(super_class_l))
            if query.empty==False:
                indecies.extend(list(query.index))
                for q in range(len(query)):
                    subclass=query['subclass'].iloc[q]
                    onto, created_classes,num=create_subclass(onto,subclass,entities,super_class,num,created_classes)
                    subclass=None 
        else: 
            class_name= 'DC_{:04d}'.format(num)
            num+=1
            super_class = types.new_class(class_name, (Thing,))
            super_class.comment.append('created automatically') 
            super_class.label.append(super_class_l)
            created_classes.append(super_class_l.lower())
        if subclass:
            if subclass.lower() not in created_classes:
                class_name= 'DC_{:04d}'.format(num)
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
 
def search_entity (onto, entity_full, category, onto_list,IRI_json_filename='iriDictionary'):
    f = open('{}.json'.format(IRI_json_filename)) # evtl in class aufnehmen und abrufen
    onto_dict = json.load(f) #
    f.close() #
    match_dict = {} #
    is_a_dict= {}
    #new_world= owlready2.World()
    #for value in onto_list.values():
        #onto= new_world.get_ontology(value).load()
    nlp = spacy.load('en_core_web_sm')
    tags=['NOUN', 'ADJ','PNOUN']
    spans = Document(entity_full).cems
    chemicals=[]
    for c in spans:
        c=str(c).split()
        chemicals.extend(c)
    entity_full = re.sub(r'\[\d+\]', '', entity_full)  #delete all numbers in square brackets
    brackets = re.findall('([\(].*?[\)])[\s,.]', entity_full)  #delete all abbreviations in brackets
    for e in brackets:
        entity_full=entity_full.replace(e,'') 
    doc = nlp(entity_full)
    i=0
    while i < len(doc):
        if i!=len(doc)-1 and doc[i].text=='[' and doc[i+1].text[-1]=='+':
                entity_lemma =entity_lemma + " " + doc[i].text + doc[i+1].text
                i += 1
        elif doc[i].pos_=='NOUN':
            entity_lemma = entity_lemma+" "+doc[i].lemma_
        else:
            entity_lemma = entity_lemma+" "+doc[i].text
        i += 1    
    sub = {}
    super_class = None
    entity_old = ""
    word_list = entity_full.split()
    i = len(word_list) - 1
    is_a_dict[category]=[]
    while i>=0:           
        entity = word_list[i]+' ' + entity_old
        doc = nlp(word_list[i])
        entity_n=re.sub('[—–\-\d]+','',word_list[i])
        i -= 1
        if doc[0].pos_ not in tags:
                print('pass')  
                entity_old=entity
                continue
        elif i == len(word_list) and entity_n in chemicals:
                is_a_dict[category].append(entity)
        elif sub:
                
                for k,v in sub.items() : 
                    if entity.lower() in [i.label[0].lower() for i in v] : #and k == match_dict[entity][1]
                        if i.subclasses():
                            sub[k] = list(i.subclasses())
                        else:
                            write_in_txt(i.iri,entity,k)
                            super_class = i
        else:       
                match_dict,_ = search_in_nested_dict_val(missing = [],value=entity,onto_names= list(onto_list.keys()),onto_dict= onto_dict,match_dict= match_dict)
                if entity in match_dict.keys(): 
                    sub[match_dict[entity][1]]=list(onto.search_one(iri=match_dict[entity][0]).subclasses())
                    write_in_txt(match_dict[entity][0].iri,entity,match_dict[entity][1])
                    print('added entity:', entity)
                    
                else:
                    print('new entity:',entity)
                    if super_class:
                        is_a_dict[super_class]=entity
                        super_class=None
                    elif entity_old=="":
                        is_a_dict[category].append(entity)
                    else:
                        is_a_dict[entity_old]=entity                                       
        entity_old = entity
        
    return is_a_dict
             

def create_list_IRIs(class_list, onto_list,IRI_json_filename = 'iriDictionary', include_main= False):
        f = open('{}.json'.format(IRI_json_filename))
        onto_dict = json.load(f)
        f.close()
        match_dict = {}
        missing=[]
        onto_names = list(onto_list.keys()) 
        if include_main == False:
            onto_names.remove('AFO')
        for entity in class_list:
            match_dict = search_value_in_nested_dict(entity, onto_names, onto_dict, match_dict)
            #if entity not in match_dict.values():
            #   missing.append(entity)
        missing=[e for e in class_list if e not in match_dict.values()]        
        print(missing)   
        for key,value in match_dict.items():
            x=[]
            for O in onto_names:
                list_IRIs = onto_dict[O].keys()
                try:
                    df = pd.read_excel('./AFO_{}.xlsx'.format(O),sheet_name=0)
                except:
                    print('List with common ontology classes for {} is not provided'.format(O))
                double_afo=df['{}_IRI'.format(O)].to_list()
                if key in double_afo or key in x or O == 'AFO':
                        continue
                
                elif key in list_IRIs:
                    write_in_txt(key,value,O)
                    x.append(key)
                else:
                    write_in_txt(key, value, 'diverse')
        return missing, match_dict
        
def write_in_txt(IRI,label,onto_name):
    path = 'class_lists/IRIs_'+ onto_name +'.txt'
    txt = open(path, 'a')
    iri_class = IRI + '  # ' + label +'\n'
    txt.write(iri_class) 
    txt.close() 
   

def search_in_nested_dict_val(value, onto_names, onto_dict, match_dict):
    
    for k in onto_names:
        for IRI in onto_dict[k].keys() :
            for key, val in onto_dict[k][IRI].items():
                if val and value.lower() == val.lower():
                    match_dict[val] = [IRI,k]    
    return match_dict   

def search_value_in_nested_dict(value, onto_names, onto_dict, match_dict):
    for k in onto_names:
        for IRI in onto_dict[k].keys() :
            for key, val in onto_dict[k][IRI].items():
                if val and value.lower() == val.lower():
                    match_dict[IRI] = val            
    return match_dict

def onto_extender (onto_list):
    new_world= owlready2.World()
    onto = new_world.get_ontology("ontologies/afo.owl").load()
    onto.save('./ontologies/afo_upd.owl')
    for o,iri in onto_list.items():
        # Der erste Pfad führt zur robot.jar und muss evtl. vom Nutzer angepasst werden.
        # --input: ist die Ontologie in der nach den gewünschten IRI's gesucht werden soll.
        # --method: kann nach Bedarf abgewandelt werden [http://robot.obolibrary.org/extract]
        # --term-file: ist die Textdatei, in der die IRI's abgelegt sind welche gesucht werden sollen
        os.system('java -jar c://Windows/robot.jar extract --input-iri {} --method BOT --term-file class_lists/IRIs_{}.txt --output ontology_sniplet/{}_classes.owl'.format(iri,o,o))
    for filepath in glob.iglob('ontology_sniplet/*.owl'):
        os.system('robot merge --input {} --input ontologies/afo_upd.owl --output ontologies/afo_upd.owl'.format(filepath))

def equality( onto_list,onto_name='AFO'):
    eq=[]
    labels_old=[]
    new_world= owlready2.World()
    onto =new_world.get_ontology("./ontologies/{}_upd.owl".format(onto_name.lower())).load()
    new_world1=owlready2.World()
    onto_old=new_world1.get_ontology("./ontologies/{}.owl".format(onto_name.lower())).load()
    for c_1 in onto_old.classes():
        if c_1.label:
            labels_old.append(c_1.label[0])
    for o in list(onto_list.keys()):
        try:
            new_world2 = owlready2.World()
            onto_snip = new_world2.get_ontology("./ontology_sniplet/{}_classes.owl".format(o)).load()
        except:
            print('no entity from {} ontology found'.format(o))
        for c_2 in list(onto_snip.classes()):
            if c_2.label[0] in labels_old:
                
                iri_snip=c_2.iri
                iri_old=onto_old.search_one(label=c_2.label[0]).iri
                if str(iri_snip) == str(iri_old):
                    print('continue')
                    continue
                else:
                    eq.append(c_2.label[0])
                    onto.search_one(iri=iri_old).equivalent_to.append(onto.search_one(iri=iri_snip))
                    onto.search_one(iri=iri_old).comment=([
                        'Equivalence with {} added automatically'.format(c_2.iri)])
                    onto.search_one(iri=iri_snip).comment=([
                        'Equivalence with {} added automatically'.format(onto.search_one(iri=iri_old).iri)]) 
    onto.save('./ontologies/{}_upd1.owl'.format(onto_name.lower())) 
    return eq   


"""
ckpt_name = 'CatalysisIE/checkpoint/CV_0.ckpt'
bert_name = 'CatalysisIE/pretrained/scibert_domain_adaption'
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])

onto_list ={
            'ChEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            #'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            'CHMO' : 'http://purl.obolibrary.org/obo/chmo.owl',
            'AFO'  : "./ontologies/afo.owl"
            } 

onto_class_list=load_classes_chebi()

#onto_new_dict, missing, match_dict, rel_synonym=chemical_prep_2(chem_list, onto_list,onto_class_list)


   
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
hydroformylation on a series of Rh and Co based catalysts. Supported catalysts based on the Rh-Co couple, mainly derived from the decomposition of 
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
based on rhodium supported on various oxides proved to be the more chemo- and regio-selective systems.Recently, it has been shown that tuning the localenvironment of Rh and Ir-based atomically dispersed catalysts beyond changing the support composition enables interesting
chemistry, such as ethylene dimerization, NO reduction, 1,3-
butadiene hydrogenation, and methane conversion to acetic
acid with high selectivity.'''

test_sents = text_prep(test_txt)        
categories,chem_list,abbreviation, sup_cat, chem_list_all= CatalysisIE_search(model, test_sents, onto_list)    
onto_new_dict, missing, match_dict, rel_synonym= chemical_prep(chem_list, onto_list,onto_class_list, chem_list_all)     
sup_cat, df_entity,missing_all=catalyst_entity(categories, rel_synonym, sup_cat,chem_list,missing,onto_list)
onto_extender (onto_list)
eq=equality( onto_list,onto_name='AFO')
created_classes=create_classes_onto(missing_all, df_entity)

categories={'ZSM-5 zeolite': 'Catalyst', 'naphtha': 'Reactant', 'catalytic cracking': 'Reaction', 'Sr, Zr, La-supported on ZSM-5 zeolite': 'Catalyst', 'metal-incorporated ZSM-5 zeolite': 'Catalyst', 'hydride transfer reaction': 'Reaction', 'alkene': 'Product', 'light olefin': 'Product', 'Zr-supported on ZSM-5 zeolite': 'Catalyst', 'HZSM-5': 'Catalyst', 'RhCo catalyst': 'Catalyst', 'heterogeneous rhodium oxide catalyst encapsulated within microporous silicalite-1  (S-1) ': 'Catalyst', 'Rh2O3@S-1': 'Catalyst', 'Supported catalyst based on the RhCo': 'Catalyst', 'vapor phase hydroformylation': 'Reaction', 'olefin': 'Reactant', 'RhCo3(CO)12': 'Catalyst', 'Cobalt complex': 'Catalyst', 'rhodium based catalyst': 'Catalyst', 'heterogeneous ethylene': 'Reactant', 'hydroformylation': 'Reaction', 'Rh,Co based catalyst': 'Catalyst', 'Supported catalyst based on the RhCo cou\x02ple': 'Catalyst', 'propene': 'Reactant', 'RhCo based catalyst': 'Catalyst', 'reduction': 'Treatment', 'Rh based catalyst': 'Catalyst', 'DRC': 'Characterization', 'propylene': 'Reactant', 'hydrogenation': 'Reaction', 'propyl specie': 'Product', 'Rh-based heterogeneous catalyst': 'Catalyst', 'Rh': 'Catalyst', 'Rh-based alloy catalyst': 'Catalyst', 'heterogeneous hydroformylation': 'Reaction', 'monometallic Rh supported on MCM-41': 'Catalyst', 'Rh-based bimetallic catalyst': 'Catalyst', 'RhM3,M =  M= ,Co Co, Ni,Cu Zn': 'Catalyst', 'ethylene': 'Reactant', 'Bimetallic heterogeneous catalyst based on rhodium supported on various oxide': 'Catalyst', 'Rh, Ir-based atomically dispersed catalyst': 'Catalyst', 'dimerization': 'Reaction', '1,3- butadiene': 'Reactant', 'methane': 'Reactant', 'acetic acid': 'Product'}
rel_synonym={'Zr': 'zirconium atom', 'Cobalt': 'cobalt atom', 'oxide': 'oxide', 'Ir': 'iridium atom', 'RhCo': 'cobalt(2+);rhodium(3+)', 'Rh': 'rhodium atom', 'Co': 'cobalt atom', 'La': 'lanthanum atom', 'SiO2': 'silicon dioxide', 'Si': 'silicon atom', 'O': 'oxygen atom', 'hydride': 'hydride', 'Zn': 'zinc atom', 'Rh2O3': 'oxygen(2-);rhodium(3+)', 'Sr': 'strontium atom', 'propene': 'prop-1-ene', 'Ni': 'nickel atom', 'propyl': 'propyl', 'Cu': 'copper atom', 'C': 'carbon atom', 'Al': 'aluminium atom', 'propylene': 'prop-1-ene', 'acetic acid': 'acetic acid', 'rhodium': 'rhodium atom', 'zeolite': 'zeolite', 'rhodium oxide': 'oxorhodium'}
sup_cat={'SiO2': ['RhCo'], 'Al': ['Rh'], ' MCM-41': ['Rh'], 'MCM-41': ['RhM3']}
chem_list=['MCM-41', 'Zr', 'Cobalt', 'oxide', 'Ir', 'RhCo', 'Co', 'La', ' MCM-41', 'olefin', 'SiO2', 'hydride', 'alkene', 'Zn', 'Rh2O3', 'Sr', 'ZSM', 'propene', 'Ni', 'propyl', 'Cu', 'RhCo3(CO)12', 'RhM3', 'Al', 'propylene', 'acetic acid', '1,3- butadiene', 'rhodium', 'zeolite', 'rhodium oxide', 'Rh']
missing=[]
"""
#onto_new_dict, missing, match_dict, rel_synonym= chemical_prep(chem_list, onto_list,onto_class_list, chem_list_all)  
#sup_cat, df_entity,_=catalyst_entity(categories, rel_synonym, sup_cat,chem_list,missing)

missing_all=['prop-1-ene',
 'RhCo3(CO)12',
 'MCM-41',
 'cobalt(2+);rhodium(3+)',
 'ZSM-5',
 'acetic',
 'oxorhodium',
 'propyl',
 'oxygen(2-);rhodium(3+)',
 'heterogeneous catalyst role',
 'alloy catalyst role',
 'bimetallic catalyst role',
 'heterogeneous catalyst role',
 'atomically dispersed catalyst role',
 'dispersed catalyst role']
#
entity=[None,
 None,
 None,
 None,
 None,
 None,
 'Supported catalyst based on the RhCo',
 'Supported catalyst based on the RhCo couple',
 'Rh-based heterogeneous catalyst',
 'Rh-based alloy catalyst',
 'Rh-based bimetallic catalyst',
 'Bimetallic heterogeneous catalyst based on rhodium supported on various oxide',
 'Rh, Ir-based atomically dispersed catalyst']
cems=[['alkene'],
 ['olefin'],
 ['propene'],
 ['propylene'],
 ['1,3-butadiene'],
 ['acetic acid'],
 [],
 [],
 ['rhodium atom'],
 ['rhodium atom'],
 ['rhodium atom'],
 [],
 ['rhodium atom', 'iridium atom']]
classes=[[],
 [],
 [],
 [],
 [],
 [],
 ['catalyst role'],
 ['catalyst role'],
 ['heterogeneous catalyst role'],
 ['alloy catalyst role'],
 ['bimetallic catalyst role'],
 ['heterogeneous catalyst role', 'bimetallic catalyst role'],
 ['atomically dispersed catalyst role', 'dispersed catalyst role']]
category=['Product',
 'Reactant',
 'Reactant',
 'Reactant',
 'Reactant',
 'Product',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst',
 'Catalyst']
d={'entity':entity,'classes':classes,'cems':cems, 'category':category}
df_entity=pd.DataFrame(data=d)
created_classes=create_classes_onto(missing_all, df_entity)
''' 
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
