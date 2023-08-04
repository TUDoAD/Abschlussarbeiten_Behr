# -*- coding: utf-8 -*-
"""
Created on Fri Aug 04 08:38:00 2023

@author: mvoel
"""
import pandas as pd
from owlready2 import *

onto_path = "C:\\Users\smmcvoel\Documents\GitHub\Abschlussarbeiten_Behr\VoelkenrathMA\ontologies\MV-onto.owl"
onto = get_ontology(onto_path).load()


def get_class_info_list():
    classes_info = []
    
    # Get all information needed from Ontology
    for cla in onto.classes():
        class_info = {
            "class": cla.name,
            "label": cla.label.first() if cla.label else None,
            "definition": cla.definition.first() if cla.definition else None,
            "comment": cla.comment.first() if cla.comment else None,                    
            }
        classes_info.append(class_info)
    
    # Store information in Excel-file
    df = pd.DataFrame(classes_info)
    excel_file = "ontologies\ontologie_classes.xlsx"
    df.to_excel(excel_file, index=False)
        
    return classes_info

#get_class_info_list()