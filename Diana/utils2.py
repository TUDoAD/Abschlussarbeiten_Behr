# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:51:27 2023

@author: chern
"""
from owlready2 import *
import pickle

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
    onto_class_list = list(new_world.classes())
    print("Loading {} done. Imported {} classes.".format(ontology_name, len(onto_class_list)))
    return onto_class_list 

def description_dicts(class_list, ontology_name):
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
    ontology_name : TYPE
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
    print("Extracting class descriptions...")
    formula = {}
    synonyms = {}
    N_cl = len(class_list)
    temp_class_label = []
    
    def_dict = {'chebi':'has_related_synonym'}
    def_id = "has_related_synonym"
    
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
            try:
                    desc_dict[temp_class_label] = getattr(temp_class,def_id)
            except:
                    desc_dict[temp_class_label] = temp_class_label
            if not desc_dict[temp_class_label]: # Desc_dict empty
                    desc_dict[temp_class_label] = temp_class_label
                
                except:
                    try: #temp_class.IAO_0000115
                        desc_dict[temp_class_label] = temp_class.IAO_0000115    
                    except:
                        try:
                            desc_dict[temp_class_label] = temp_class.definition
                            if not desc_dict[temp_class_label]: 
                                # .definition is empty    
                                try: #temp_class.comment
                                    desc_dict[temp_class_label] = temp_class.comment
                                except:
                                    raise print("in description_dicts - class definitions were not recognized properly.")
                                    return()
                        except:
                            raise definitionError("in description_dicts - class definitions were not recognized properly.")
                            return()
    print("Done.")
    return desc_dict