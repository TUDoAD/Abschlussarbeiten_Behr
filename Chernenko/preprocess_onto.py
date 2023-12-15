# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 15:51:32 2023

@author: smdicher
"""
import json
from owlready2 import *
import pandas as pd
import glob
import os

def set_config_key(key, value):
     globals()[key] = value
     
with open("config.json") as json_config:
     for key, value in json.load(json_config).items():
         set_config_key(key, value)
def create_list_IRIs(class_list, IRI_json_filename = 'iriDictionary'):
    """
    Create List of IRIs for Ontology Entities

    This function is responsible for creating a list of IRIs (Internationalized Resource Identifiers) for entities in an ontology.
    It matches entities to existing IRIs and provides a list of missing entities that could not be matched.

    Parameters
    ----------
    class_list : list
        A list of entity class names.

    onto_list : dict
        A dictionary containing information about the ontologies.

    onto_new : str
        The name of the new ontology.

    onto_old : str
        The name of the old ontology.

    IRI_json_filename : str, optional
        The filename for the JSON file containing IRI information. Default is 'iriDictionary'.

    Returns
    -------
    missing : list
        A list of entities that could not be matched to an existing IRI.
    
    match_dict : dict
        A dictionary that maps entities to their matched IRIs.

    """
    f = open('{}.json'.format(IRI_json_filename))
    onto_dict = json.load(f)
    f.close()
    match_dict = {}
    missing=[]
    onto_names = list(onto_list.keys()) 
    new_world=owlready2.World()
    onto= new_world.get_ontology('./ontologies/{}.owl'.format(onto_new)).load()
    entities_all=[c.label[0] for c in onto.classes() if c.label]
    entities_all.extend([c.label[0] for c in onto.individuals() if c.label])
    try:
        onto_names.remove(onto_old.upper())
    except: 
        print('{} not in the list of the given ontologies "onto_list"')
    
    for entity in class_list:
        if entity not in entities_all:
            match_dict = search_value_in_nested_dict(entity, onto_names, onto_dict, match_dict)
        else:

            match_dict['dummy_'+entity]=[entity,entity]
    values=[i[0] for i in match_dict.values()]
            
    missing = [e for e in class_list if e not in values and e not in entities_all] 

    for key,value in match_dict.items():
        x = []
        for O in onto_names:
            if O=='CHEBI':
                O='ChEBI'
            list_IRIs = onto_dict[O].keys()
            if O != onto_old.upper():
                try:
                    df = pd.read_excel('./{}_{}.xlsx'.format(onto_old.upper(),O),sheet_name=0)
                except:
                    print('List with common ontology classes for {}_{} is not provided'.format(onto_old.upper(),O))
            double_afo = df['{}_IRI'.format(O)].to_list()
            if key in double_afo or key in x or O == onto_old.upper() or 'dummy' in key:
                continue
            elif key in list_IRIs:
                write_in_txt(key,value[0],O)
                x.append(key)
            else:
                write_in_txt(key, value[0], 'diverse')
    return missing, match_dict
        
def write_in_txt(IRI,label,onto_name):
    """
    Write IRI and Label to Text File

    This function is used to write an IRI (Internationalized Resource Identifier) and 
    its associated label to a text file for a specific ontology.
    
    Parameters
    ----------
    IRI : str
        The IRI to be written to the text file.
    
    label : str
        The label associated with the IRI.
    
    onto_name : str
        The name of the ontology to which the IRI and label belong to.

    Returns
    -------
    None.

    """
    path = 'class_lists/IRIs_'+ onto_name +'.txt'
    txt = open(path, 'a')
    iri_class = IRI + '  # ' + label +'\n'
    txt.write(iri_class) 
    txt.close() 

    
def search_value_in_nested_dict(value, onto_names, onto_dict, match_dict):
    
    for k in onto_names:
        if k=='CHEBI':
            k='ChEBI'
        for IRI in onto_dict[k].keys() :
            for key, val in onto_dict[k][IRI].items():
                if val and (value.lower() == val.lower() or value.lower()+' (molecule)'==val.lower()):
                    match_dict[IRI] = [value,val]            
    return match_dict

def onto_extender ():
    for o,iri in onto_list.items():
        # The first path leads to robot.jar and may need to be modified by the user.
        # --input: is the ontology in which to search for the desired IRI's.
        # --method: can be modified as needed  [http://robot.obolibrary.org/extract]
        # --term-file: is the text file, in which the IRI's are stored, which are to be searched for.
        os.system('java -jar c://Windows/robot.jar extract --input-iri {} --method BOT --term-file class_lists/IRIs_{}.txt --output ontology_snipet/{}_classes.owl'.format(iri,o,o))
    for filepath in glob.iglob('ontology_snipet/*.owl'):
        os.system('robot merge --input ontologies/{}.owl --input {} --output ontologies/{}.owl'.format(onto_new, filepath,  onto_new))
        #os.system('robot merge --input empty.owl --input {} --output empty.owl'.format(filepath))

def equality():
    """
    Ontology Equality Function

    This function is responsible for establishing equivalence relationships between entities in different ontologies. 
    It identifies entities with the same label in different ontologies and creates equivalence relationships between them.
    
    Parameters
    ----------
    onto_list : dict
        A dictionary containing information about the ontologies to be compared.
    
    onto_old : str
        The name of the old ontology.
    
    onto_new : str
        The name of the new ontology which will be updated.
    Returns
    -------
    eq : list
        A list of entities that have been established as equivalent in different ontologies.


    """
    eq=[]
    labels_old=[]
    new_world4= owlready2.World()
    onto =new_world4.get_ontology("./ontologies/{}.owl".format(onto_new.lower())).load()
    new_world1=owlready2.World()
    onto_old1=new_world1.get_ontology("./ontologies/{}.owl".format(onto_old.lower())).load()
    for c_1 in onto_old1.classes():
        if c_1.label:
            labels_old.append(c_1.label[0])
    for o in list(onto_list.keys()):
        try:
            new_world2 = owlready2.World()
            onto_snip = new_world2.get_ontology("./ontology_snipet/{}_classes.owl".format(o)).load()
        except:
            print('no entity from {} ontology found'.format(o))
        else:
            for c_2 in list(onto_snip.classes()):
                if c_2.label[0] in labels_old:
                    
                    iri_snip=c_2.iri
                    iri_old=onto_old1.search_one(label=c_2.label[0]).iri
                    if str(iri_snip) == str(iri_old):
                        continue
                    else:
                        eq.append(c_2.label[0])
                        onto.search_one(iri=iri_old).equivalent_to.append(onto.search_one(iri=iri_snip))
                        onto.search_one(iri=iri_old).comment = ([
                            'Equivalence with {} added automatically'.format(c_2.iri)])
                        onto.search_one(iri=iri_snip).comment = ([
                            'Equivalence with {} added automatically'.format(onto.search_one(iri=iri_old).iri)]) 

    onto.save('./ontologies/{}.owl'.format(onto_new.lower())) 
    return eq   