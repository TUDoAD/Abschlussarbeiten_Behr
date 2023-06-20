# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 09:49:10 2023

@author: chern
"""

# load Ontology and search for classes/subclasses/individuals/Description

from owlready2 import *
ontology_name = "chebi"
new_world = owlready2.World()
onto = new_world.get_ontology("http://purl.obolibrary.org/obo/chebi.owl").load()
onto_class_list = list(onto.classes())
print("Loading {} done. Imported {} classes.".format(ontology_name, len(onto_class_list)))

'''def description_dicts(class_list, ontology_name):
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
    print("Extracting formulae...")
    desc_dict = {}
    N_cl = len(class_list)
    temp_class_label = []
    
    def_dict = {'chebi':'formula'}
    try:
        def_id = def_dict[ontology_name]
    except:
        def_id = []
    
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
            if def_id:
                try:
                    desc_dict[temp_class_label] = getattr(temp_class,def_id)
                except:
                    desc_dict[temp_class_label] = temp_class_label
                if not desc_dict[temp_class_label]: # Desc_dict empty
                    desc_dict[temp_class_label] = temp_class_label
            else:
                try: #NCIT
                    desc_dict[temp_class_label] = temp_class.P97
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

def onto_loader(ontology_names):        
    """
    Loading ontologies and storing classes and their descriptions in dictionaries.
    Parameters
    ----------
    ontology_names : TYPE
        DESCRIPTION.

    Returns
    -------
    class_list_dict : TYPE
        DESCRIPTION.
    description_list_dict : TYPE
        DESCRIPTION.

    """
    print("=============================================")
    # Ontologies to load
    # ontology_names = ["chmo","Allotrope_OWL", "chebi", "NCIT", "SBO"]
    class_list_dict = {}
    description_list_dict ={}
        
    for name in ontology_names:
        print("Loading ontology {} ...".format(name))
        class_list_dict[name] = load_ontologies(name)
        description_list_dict[name] = description_dicts(class_list_dict[name],name)
    
    # existing_keys = names of ontologies
    #existing_keys = list(description_list_dict.keys())
        
    print("Ontologies {} loaded. \n PLEASE CHECK if class descriptions are not empty.".format(str(ontology_names)))
    print("=============================================")
    return class_list_dict, description_list_dict'''
