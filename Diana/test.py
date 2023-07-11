# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 09:49:10 2023

@author: chern
"""

# load Ontology and search for classes/subclasses/individuals/Description

from owlready2 import *
from utils2 import *
import os
#from CatalysisIE.model import *
#from CatalysisIE.utils import * 
"""
ckpt_name = 'checkpoint/CV_0.ckpt'
bert_name = 'pretrained/scibert_domain_adaption'
#model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
ontology_name = "chebi"
new_world = owlready2.World()
#onto = new_world.get_ontology("http://purl.obolibrary.org/obo/chebi.owl").load()

onto2 = new_world.get_ontology("./ontologies/chebi_matom.owl").load()
#onto_class_list = list(onto.classes())
onto_class_list2 = list(onto2.classes())
print("Loading {} done. Imported {} classes.".format(ontology_name, len(onto_class_list2)))



synonyms=utils2.synonym_dicts(onto_class_list2)
chem_list= ['RhCaO', 'Rh2O3@S-1','rhodium', 'BeCa']
"""
#bashCommand = 'java -jar c://Windows/robot.jar extract --input ontologies/chebi.owl --method BOT --term-file CLass_IRIs.txt --output ontologies/rxno.owl'
#os.system(bashCommand)    

onto_list ={
            'CHEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            }  
class_list=['atom', 'ion', 'barium atom','oxidation', 'aldehyde reduction', 'rhodium atom']

#create_list_IRIs(class_list, onto_list,IRI_json_filename = 'iriDictionary')

onto_extender(onto_list)