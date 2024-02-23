# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:11:28 2024

@author: chern
"""
from txt_extract import get_abstract,  get_metadata
import glob
from owlready2 import *
import json
id=22
onto = get_ontology('./ontologies/afo_dataset_1-m.owl').load()
pub_c = onto.search_one(label='publication')
dois=[]
for p in list(pub_c.instances()):
    dois.append(p.has_doi[0])
path=r'.\import\*.pdf'
for i in glob.iglob(path):
    title,doi,publisher = get_metadata(i)
    if doi==None or doi in dois:
        continue
    print(title+' : '+doi)
    abstract = get_abstract(i, doi, publisher)

    if abstract!=None and abstract:
        
        #txt_pub = cleanup_text(txt_pub)
        full_content={"id":id,"data":{"text":abstract}}
        
        with open('./text_xml/text_json/{}.json'.format(id), 'w', encoding = 'utf-8') as f:
            json.dump(full_content, f, sort_keys=True, indent=4, ensure_ascii=False)
            f.close()
        id+=1
    else:
        print('no abstract found')