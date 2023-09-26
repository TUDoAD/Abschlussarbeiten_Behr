# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 14:07:50 2023

@author: smdicher
"""

from utils2 import *
from txt_extract import get_abstract, get_metadata
path=r'.\import\*.pdf'
ckpt_name = 'CatalysisIE/checkpoint/CV_0.ckpt'
bert_name = 'CatalysisIE/pretrained/scibert_domain_adaption'
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
onto_name = 'afo'
onto_list ={
            'ChEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            #'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            'CHMO' : 'http://purl.obolibrary.org/obo/chmo.owl',
            'AFO'  : "./ontologies/afo.owl"
            } 
onto_class_list=load_classes_chebi()
'''
def process_multiple(path):
    for i in glob.iglob(path):
        title,doi,publisher= get_metadata(i)      
        
        print('-------------------', '\n')
        return abstract,
'''    
created_cl=[]
df_all=pd.DataFrame(columns=['entity','classes','cems', 'category'])
onto_new= onto_name+'_upd'

for i in glob.iglob(path):
    abstract=None
    delete_files_in_directory('.\\ontology_sniplet\\')
    delete_files_in_directory('.\\class_lists\\')
    title,doi,publisher = get_metadata(i)
    print(title+' : '+doi)
    abstract = get_abstract(i, doi, publisher)
    if abstract != None:
        p_id= add_publication(onto_name,doi,title)
        if p_id==None:
            continue
        sents = text_prep(abstract) 
        categories,chem_list,abbreviation, sup_cat, chem_list_all,reac_dict= CatalysisIE_search(model, sents, onto_list)
        onto_new_dict, missing, match_dict, rel_synonym= chemical_prep(chem_list, onto_list,onto_class_list, chem_list_all,abbreviation, onto_new)
        sup_cat, df_entity,missing, match_dict,rel_synonym=catalyst_entity(categories, rel_synonym, sup_cat,chem_list,missing,match_dict, onto_list, onto_new )
        df_all=pd.concat([df_all, df_entity], axis=0)
        onto_extender(onto_list, onto_name)
        _=equality(onto_list,onto_name) #für validierung alle eq classen aufnehmen
        created_classes,sub_sup=create_classes_onto(missing,match_dict, df_entity,reac_dict, p_id, onto_new,sup_cat,abbreviation)
        created_cl.append(created_classes)
        
        
"""
problematic entities:
    'bimetallic SiO2-supported RhCo3 cluster catalyst'
    'binary catalyst'  :
        if 'catalyst' in entity and len(entity.split())==2:
            classes[entity]=[entity+' role']
"""    