# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 14:07:50 2023
 (author: smdicher"""
from text_mining import load_classes_chebi, delete_files_in_directory, run_text_mining, add_publication
from preprocess_onto import *
from onto_extension_new import preprocess_classes,create_classes_onto 
from txt_extract import get_abstract, get_metadata
from CatalysisIE.model import *
from CatalysisIE.utils import *
from pubchempy import get_compounds
def set_config_key(key, value):
     globals()[key] = value
     
with open("config.json") as json_config:
     for key, value in json.load(json_config).items():
         set_config_key(key, value)
get_compounds("SiO2","formula")         
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])

#onto_class_list = load_classes_chebi()
df_all = pd.DataFrame(columns=['entity','classes','cems', 'category'])
created_cl=[]
match_d_all={}
eq1=[]
for i in glob.iglob(path):
    abstract=None
    delete_files_in_directory(path_snipet)
    delete_files_in_directory(path_class_list)
    title,doi,publisher = get_metadata(i)
    if doi == None:
        continue 
    print(title+' : '+doi)
    abstract = get_abstract(i, doi, publisher)
    if abstract != None:
        p_id = add_publication(doi,title,abstract)
        if p_id == None:
            print('p_id = None')
            continue
        chem_list, categories,onto_new_dict, sup_cat, abbreviation, missing, match_dict, rel_synonym, reac_dict,entities_raw = run_text_mining(abstract,model) #, onto_class_list
        df_entity, rel_synonym, missing_all, match_dict_all = preprocess_classes(categories, abbreviation, onto_new_dict, sup_cat, rel_synonym, chem_list, missing, match_dict,entities_raw)
        df_all = pd.concat([df_all, df_entity], axis=0)
        onto_extender()

        eq = equality()#für validierung alle eq1 classen aufnehmen
        created_classes,sup_sub_df = create_classes_onto(abbreviation, sup_cat, missing_all, match_dict_all, df_entity,reac_dict,p_id,rel_synonym,chem_list,onto_new_dict)
        created_cl.extend(created_classes)
        eq1.extend(eq)
        match_d_all.update(match_dict_all)

