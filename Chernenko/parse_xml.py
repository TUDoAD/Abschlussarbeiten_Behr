# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 05:05:29 2024

@author: chern
"""
import glob
import json
import os
#from CatalysisIE.utils import cleanup_text
from LimeSoup import (
    ACSSoup, 
    AIPSoup,
    APSSoup, 
    ECSSoup, 
    ElsevierSoup, 
    IOPSoup, 
    NatureSoup, 
    RSCSoup, 
    SpringerSoup, 
    WileySoup,
)

def get_content(data, content):
    for k,v in data.items():
        if k=='content':
            if isinstance(v[0], dict):
                for s in v:
                    content= get_content(s, content)
                
            else:
                for text in v:
                    content.append(text)
    return content
#id=1
path="./text_xml/*.xml"
for xml in glob.iglob(path):
    with open('{}'.format(xml), 'r', encoding='utf-8') as file:
        xml_str = file.read()
        name=os.path.basename(xml).strip('.xml')
        print(name)
        try:
            data = ElsevierSoup.parse(xml_str) 
        except:
            try:
                data = ACSSoup.parse(xml_str) 
            except:
                try:
                    data = RSCSoup.parse(xml_str) 
                except:    
                    try:
                        data = SpringerSoup.parse(xml_str) 
                    except:    
                        try:
                            data = WileySoup.parse(xml_str) 
                        except:
                            print('file: {} could not be parsed. check the publisher'.format(xml))
                            data=None
    if data != None:
        
        content=[]
        for s in data['Sections']:
            content= get_content(s,content)
        '''
        txt_pub = " ".join(content)
        #txt_pub = cleanup_text(txt_pub)
        full_content={"id":id,"data":{"text":txt_pub}}
        id+=1
        '''
        with open('./text_xml/text_json/{}.json'.format(name), 'w', encoding = 'utf-8') as f:
            json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
            f.close()
        '''
        with open('./text_xml/text_json_labeling/{name}_labeling.json', 'w', encoding = 'utf-8') as f:
            json.dump(full_content,f, sort_keys=True, indent=4, ensure_ascii=False)
            f.close()'''