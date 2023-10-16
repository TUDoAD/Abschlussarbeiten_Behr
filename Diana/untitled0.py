# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 14:07:50 2023

@author: smdicher
"""
  on=re.search('on')
  for c in chem_list_all:
      if c == re.search(mol[i][1]) or c == re.findall(r'(([\w@—–-]+)(?:[\s]on[\s])+[\w@—–-]+(?:[\s])+([\w@—–-]+))', entity)[2]:
          entity = entity.replace('on','supported on')
          sup = True
          break    
      elif c == re.findall(r'(([\w@—–-]+)(?:[\s]on[\s])+[\w@—–-]+(?:[\s])+([\w@—–-]+))', entity)[2]:
          
          spans = sorted(Document(entity).cems, key = lambda span: span.start)
          list_spans=[i for c in spans for i in c.text.split()]+[c.text for c in spans]
          chem_list.extend([cem for cem in chem_list_all if cem in entity and cem not in chem_list and cem not in list_spans])
from utils2 import *
from txt_extract import get_abstract, get_metadata
path=r'.\import\*.pdf'
ckpt_name = 'CatalysisIE/checkpoint/CV_0.ckpt'
bert_name = 'CatalysisIE/pretrained/scibert_domain_adaption'
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
onto_name = 'afo'
onto_list ={
            'CHEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            #'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            'CHMO' : 'http://purl.obolibrary.org/obo/chmo.owl',
            'AFO'  : "./ontologies/afo.owl"
            } 
onto_class_list=load_classes_chebi()

created_cl=[]
df_all=pd.DataFrame(columns=['entity','classes','cems', 'category'])
onto_new= onto_name+'_upd'

for i in glob.iglob(path):
    abstract=None
    delete_files_in_directory('.\\ontology_sniplet\\')
    delete_files_in_directory('.\\class_lists\\')
    title,doi,publisher,ab = get_metadata(i)
    if doi==None:
        continue
    print(title+' : '+doi)
    abstract = get_abstract(i, doi, publisher,ab)
    if abstract != None:
        p_id= add_publication(onto_name,doi,title,abstract)
        if p_id==None:
            continue
        sents = text_prep(abstract) 
        categories,chem_list,abbreviation, sup_cat, reac_dict= CatalysisIE_search(model, sents, onto_list,onto_new)
        onto_new_dict, missing, match_dict, rel_synonym= chemical_prep(chem_list, onto_list,onto_class_list,nameabbreviation, onto_new)
        sup_cat, df_entity,missing, match_dict,rel_synonym=catalyst_entity(categories, rel_synonym, sup_cat,chem_list,missing,match_dict, onto_list, onto_new )
        df_all=pd.concat([df_all, df_entity], axis=0)
        onto_extender(onto_list, onto_name)
        eq=equality(onto_list,onto_name) #für validierung alle eq1 classen aufnehmen
        created_classes,sub_sup=create_classes_onto(onto_new_dict,missing, match_dict, df_entity,reac_dict, p_id, onto_new,sup_cat,abbreviation,rel_synonym,chem_list)
        created_cl.append(created_classes)

        
JAVA_EXE='C:\Program Files\Java\jdk-11.0.17\bin\java.exe'
onto=get_ontology('./ontologies/{}.owl'.format(onto_new)).load()
with onto:
    sync_reasoner()
onto.save('./ontologies/{}_inf.owl'.format(onto_new))        
"""
problematic entities:
    'bimetallic SiO2-supported RhCo3 cluster catalyst'
    'binary catalyst'  :
        if 'catalyst' in entity and len(entity.split())==2:
            classes[entity]=[entity+' role']
"""    