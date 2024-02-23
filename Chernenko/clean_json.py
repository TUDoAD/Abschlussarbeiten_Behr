# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 15:44:54 2024

@author: chern
"""
import json
from CatalysisIE.utils import cleanup_text
import glob
import os
from txt_extract import get_absract
def get_content(data, content):
    for k,v in data.items():
        if k=='content':
            if isinstance(v[0], dict):
                for s in v:
                    content= get_content(s, content)

            else:
                for text in v:
                    if isinstance(text, str):
                        content.append(text)
                    else:
                        content= get_content(text, content)
    return content
id=1
path="./text_xml/text_json/*.json"
for json_f in glob.iglob(path):
    with open('{}'.format(json_f), 'r', encoding = 'utf-8') as f:
        name=os.path.basename(json_f).strip('.json')
        data = json.load(f)
        content=[]
    if data['Sections']:
        for s in data['Sections']:
                content= get_content(s,content)
        txt_pub = "\n".join(content)
        txt_pub = cleanup_text(txt_pub)
        full_content={"id":id,"data":{"text":txt_pub}}
        id+=1
        with open('./text_xml/text_json_labeling/{}_labeling_full.json'.format(name), 'w', encoding = 'utf-8') as f:
                        json.dump(full_content,f, sort_keys=True, indent=4, ensure_ascii=False)
                        f.close()
        