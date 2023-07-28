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

API_URL = "https://rel.cs.ru.nl/api"

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
    temp_class_label = []
    
    def_id = "hasRelatedSynonym"

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
        
        if temp_class_label:
            # if class got a label which is not empty, search for definition                    
            desc_dict[temp_class_label] = getattr(temp_class,def_id)
            if desc_dict[temp_class_label]: 
                desc_dict[temp_class_label].append(temp_class_label)
            else:
                desc_dict[temp_class_label] = [temp_class_label]
    print("Done.")
    return desc_dict


def chemical_prep(chem_list, onto_list):

    """
    From list with chemicals Differentiation between long and short chemical entities for different preprocessing; 
    separation in components and creation of dictionary:
        comp_dict = {'molecule1': ['comp1', 'comp2'],
                     'molecule2': ['comp3', 'comp1']}
    Search in ontology for classes-synonyms: compare synonyms of ontology-entities with values of comp_dict, save them in dictionary
    
    Parameters
    ----------
    chem_list : list
        DESCRIPTION.
    onto_dict : dict
        DESCRIPTION.

    Returns
    -------
    onto_new_dict : dict
        DESCRIPTION.

    """
    comp_dict = {}
    
    new_world3 = owlready2.World()
    onto = new_world3.get_ontology('http://purl.obolibrary.org/obo/chebi.owl').load()
    
    onto_class_list = list(onto.classes())
    onto_dict = synonym_dicts(onto_class_list)
    
    for molecule in chem_list:
        molecule_split = molecule.split()
        if len(molecule_split) >= 2 or re.match(r'[A-Za-z]([a-z]){3,}', molecule) is not None:
            comp_dict[molecule] = molecule_split  
        else:
            comp = re.findall(r'([A-Z](?:[a-z])?)',molecule)
            comp_dict[molecule] = comp
    class_list=[]        
    onto_new_dict ={}
    for k,v in comp_dict.items():

        for k_o, v_o in onto_dict.items():

            if k not in onto_new_dict.keys():
                onto_new_dict[k]=[]
                if k not in class_list:
                    class_list.append(k)
                done=False
                for c in v:
                    
                    if k_o in onto_new_dict[k]:
                        done = True
                        break
                    elif c in v_o:
                        onto_new_dict[k].append(k_o)
                        if k_o not in class_list:
                            class_list.append(k_o)       
                    else:
                        print(c)
                        onto_new_dict[k].append(c)
                        if c not in class_list:
                            class_list.append(c)
                if done:
                    break
    print(class_list)
    missing, match_dict = create_list_IRIs(class_list, onto_list,IRI_json_filename = 'iriDictionary')


            
    return onto_new_dict, missing, match_dict



#create snip and merge ontologies...

def cem_onto_ext (onto_new_dict, missing):
    """
    check in chebi ontology for synonyms

    Parameters
    ----------
    chem_list : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_world = owlready2.World()
    onto = new_world.get_ontology('./ontologies/afo_upd.owl').load()
    with onto:
        for k in onto_new_dict.keys():
            if k in missing:
               ... 

    onto_class_list = list(onto.classes())
    onto_new_dict = chemical_prep(chem_list, cem_dicts)
    class_list=[]
    for k,v in onto_new_dict.items():
        found_class = onto.search_one(label = k)
        #if found_class:
            
            
        #with onto:
        #NewMolecule = types.new_class(k, tuple(v))


def REL_search (text):
    nlp = spacy.load('en_core_web_sm')
    doc= nlp(text)
    """
    sentences = []
    for sentence in doc.sents:
        sentences.append(str(sentence))
    """
    sentence_n = " ".join([token.lemma_ for token in doc]) 
    doc2 = nlp(sentence_n) 
    for i in range(len(doc2)-1):         
        if (doc2[i].tag_=="NN" and doc2[i+1].tag_ =="NN") or (doc2[i].tag_=="JJ" and doc2[i+1].tag_ =="NN"):         
            ent = doc[i].text + " " + doc[i+1].text         
            print(ent)         
            start_i = doc[i].idx         
            print(start_i)         
            end_i = len(ent)         
            ed_result = requests.post(API_URL, json={
            "text": text,             
            "spans": [(start_i, end_i)]         
            }).json()         
            if ed_result:             
                print("Found Entity: %s \n%.03f\n"%(ed_result[0][3], ed_result[0][4]))     
                #print(doc[i])  
    tags = [word.tag_ for word in doc] 
    tags2 = [word.tag_ for word in doc2] 
    tokens=[i for i in doc]
...    

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
    chem_list = []
    cat_sup={}
    abbreviation = {}
    a=0
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
        "Characterisation": []  #Any intermediate steps taken to prepare the catalyst (e.g., heating, calcination, and refluxing).
        }

    output_sents = pred_model_dataset(model, test_sents)
    for sent in output_sents:
        sent_tag = [t['pred'] for t in sent]
        print(assemble_token_text(sent))
        abb_list=Document(assemble_token_text(sent)).abbreviation_definitions
        for i in range(len(abb_list)):
            abbreviation[abb_list[i][0][0]]=abb_list[i][1][0]
        for i, j, l in get_bio_spans(sent_tag):
            print(assemble_token_text(sent[i:j + 1]), l)
            entity = assemble_token_text(sent[i:j + 1])
            spans=Document(entity).cems
            if i == a+1 and '({})'.format(entity) in assemble_token_text(sent):
                if entity in abbreviation.keys():
                    abbreviation[entity].append(entity_old)
                else:
                    abbreviation[entity]=[]
                    abbreviation[entity].append(entity_old)
            
            if entity in categories[l]:
                continue
            else:
                categories[l].append(entity)
                for c in spans:
                    c=str(c)
                    mol = re.findall(r'/([\w@—–-]+)\b', c)
                    if mol:
                        catalyst= re.search(r'\b([\w@—–-]+)/', c).group(1)
                        chem_list.append(catalyst)
                        if l=='Catalyst':
                            support = mol[0]
                            chem_list.append(support)    
                            if catalyst in cat_sup.keys():
                                    cat_sup[catalyst].append(support)
                            else:
                                    cat_sup[catalyst] = []
                                    cat_sup[catalyst].append(support)
                        else:
                            for i in range(len(mol)):
                                chem_list.append(i)
                    else:
                        chem_list.append(c)
            entity_old=entity
            a=j+1
    return categories,chem_list,abbreviation, cat_sup

def catalyst_support(cat_sup,onto):
    for k,v in cat_sup.items():
        cat=onto.search_one(label=k)
        for i in v:
            ...#carrier_role
    
def catalyst_entity(categories):
    nlp = spacy.load('en_core_web_sm')
    based_cems={}
    for k,v in categories.items():
        if k =='Catalyst':
            for entity in v:
                if "based" in entity:
                     based_m= re.search('based',entity)
                     e_snip= entity[0:based_m.span()[0]-1]
                     spans = Document(e_snip).cems
                     for c in spans:
                         based_cems[c]
                spans = Document(entity).cems
                doc = nlp.entity
                entity_n = " ".join([token.lemma_ for token in doc])

                           
                
                ...
                
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
    
    #process=['source','lemma']
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
            match_dict, missing = search_value_in_nested_dict(entity, onto_names,missing, onto_dict, match_dict)
        print(match_dict)   
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
   

def search_in_nested_dict_val(value, onto_names, missing, onto_dict, match_dict):
    for k in onto_names:
        for IRI in onto_dict[k].keys() :
            for key, val in onto_dict[k][IRI].items():
                if val and value.lower() == val.lower():
                    match_dict[val] = [IRI,k]
                elif value not in missing:
                    missing.append(value)
            
    return match_dict, missing    
def search_value_in_nested_dict(value, onto_names, missing, onto_dict, match_dict):
    for k in onto_names:
        for IRI in onto_dict[k].keys() :
            for key, val in onto_dict[k][IRI].items():
                if val and value.lower() == val.lower():
                    match_dict[IRI] = val
                elif value not in missing:
                    missing.append(value)
            
    return match_dict, missing

def onto_extender (onto_list):
    new_world= owlready2.World()
    onto = new_world.get_ontology("ontologies/afo.owl").load()
    onto.save('./ontologies/afo_upd.owl')
    for o,iri in onto_list.items():
        # Der erste Pfad führt zur robot.jar und muss evtl. vom Nutzer angepasst werden.
        # --input: ist die Ontologie in der nach den gewünschten IRI's gesucht werden soll.
        # --method: kann nach Bedarf abgewandelt werden [http://robot.obolibrary.org/extract]
        # --term-file: ist die Textdatei, in der die IRI's abgelegt sind welche gesucht werden sollen
        # --output: selbsterklärend
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
test_txt='''In order to reveal the influences of metal-incorporation and regeneration of ZSM-5 zeolites on naphtha catalytic cracking, the fresh and regenerated Sr, Zr and La-loaded ZSM-5 zeolites have been prepared and evaluated using n-pentane catalytic cracking as a model reaction.
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
area of 380 m2/g.'''
test_sents = text_prep(test_txt)        
categories,chem_list,abbreviations, cat_sup = CatalysisIE_search(model, test_sents, onto_list)    
new_dict, missing, match_dict= chemical_prep(chem_list, onto_list)      
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
