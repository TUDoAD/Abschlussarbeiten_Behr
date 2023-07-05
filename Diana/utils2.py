# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:51:27 2023

@author: chern
"""
import spacy
from owlready2 import *
import pickle
import json
import logging
import pandas as pd
#import pytorch_lightning as pl
from copy import deepcopy
#from CatalysisIE.model import *
#from CatalysisIE.utils import *
import requests
import json

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
    N_cl = len(class_list)
    temp_class_label = []
    
    def_id = "hasRelatedSynonym"

    for i in range(N_cl):
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

def chemical_prep(chem_list, onto_dict):

    """
    From list with chemicals Differentiation between long and short chemical entities for different preprocessing; 
    separation in components and creation of dictionary:
        comp_dict = {'molecule1': ['comp1', 'comp2'],
                     'molecule2': ['comp3', 'comp1']}
    Serch in ontology for classes-synonyms: compare synonyms of ontology-entities with values of comp_dict, save them in dictionary
    
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
    for entity in chem_list:
        entity_split = entity.split()
        if len(entity_split) >= 2 or re.match(r'[A-Za-z]([a-z]){3,}', entity) is not None:
            comp_dict[entity] = entity_split  
        else:
            comp = re.findall(r'([A-Z](?:[a-z])?)',entity)
            comp_dict[entity] = comp
   
    onto_new_dict ={}
    for k,v in comp_dict.items():
        onto_super=[]
        for comp in v:
            for k_o, v_o in onto_dict.items():
                for syn_comp in v_o: 
                    if comp == syn_comp:
                        onto_super.append(k_o)
        onto_new_dict[k] = onto_super
    return onto_new_dict


def cem_onto_ext (chem_list, ontology_name='chebi_matom', new_onto_name ='chebi_new' ):
    new_world = owlready2.World()
    onto = new_world.get_ontology("./ontologies/{}.owl".format(ontology_name)).load()
    onto_class_list = list(onto.classes())
    cem_dicts = synonym_dicts(onto_class_list)
    onto_new_dict = chemical_prep(chem_list, cem_dicts)
    for k,v in onto_new_dict.items():
        class_name = k
        SuperClasses = v
        with onto:
            NewMolecule = types.new_class(class_name, tuple(SuperClasses))
...

def REL_search (text):
    nlp = spacy.load('en_core_web_sm')
    doc= nlp.text
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


def CatalysisIE_search (model, test_sents):
    catalysts  = []         #Identified as “metal/support” or with keywords like “metal-catalyst”. If details about the catalyst composition are 
                            #provided, then they are included in the catalyst text span (e.g., Ru/CeO2, CeO2-supported metal catalysts, and Pt/H-USY 
                            #(Pt:1 wt %) catalysts).
    reactions  = []         #Processes that involve the transformation of a chemical species via interactions with a catalyst (e.g., hydrogenation, 
                            #isomerization, and hydrocracking).
    treatments = []         #Any technique that is used to yield useful information about the catalyst (e.g., gas chromatography mass spectroscopy 
                            #(GC–MS), powder X-ray diffraction (XRD), and infrared spectrometry (IR)).
    reactants  = []         #Species that interact with the catalyst to create a product (e.g., polyethylene, plastics, and PE). Reagents for catalyst 
                            #synthesis are not included in this category.
    products   = []         #Species that are produced from a chemical reaction between the reactant and the catalyst (e.g., C1–C4, coke, and liquid 
                            #fuel). Intermediate species that go on to react further are not considered in this category unless there is substantial 
                            #characterization/quantification of those species.
    characterisations = []  #Any intermediate steps taken to prepare the catalyst (e.g., heating, calcination, and refluxing).

    output_sents = pred_model_dataset(model, test_sents)
    for sent in output_sents:
        sent_tag = [t['pred'] for t in sent]
        print(assemble_token_text(sent))
        pattern = r'/([\w]+)\b'
        for i,j,l in get_bio_spans(sent_tag):
            print(assemble_token_text(sent[i:j+1]), l)
            if l == "Catalyst":
                support_match = re.search(pattern,sent[i:j+1])
                support = support_match.group(1)
                catalysts.append(l)
            elif l == "Reactant":
                reactants.append(l)
            elif l == "Treatment":
                treatments.append(l)
            elif l == "Reaction":
                reactions.append(l)
            elif l == "Product":
                products.append(l)
            else:
                characterisations.append(l)
        print('\n\n')

...

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

    for k in onto_dict.keys():
        for IRI in onto_dict[k].keys() :
            for key, val in onto_dict[k][IRI].items():
                if value == val:
                    match_dict[IRI]=val
                else:
                    continue
            
    return match_dict

            

#    onto_class = [k_o for k, v in comp_dict.items() for comp in v for k_o, v_o in onto_dict.items() for syn_comp in v_o if comp == syn_comp]
