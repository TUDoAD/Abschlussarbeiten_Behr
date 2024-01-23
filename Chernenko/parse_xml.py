# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 05:05:29 2024

@author: chern
"""
import glob
import json
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

path="./text_xml/*.xml"
for xml in glob.iglob(path):
    with open('{}'.format(xml), 'r', encoding='utf-8') as file:
        xml_str = file.read()
        name=xml.strip('.xml')
        try:
            data = ElsevierSoup.parse(xml_str) 
            with open('./text_xml/text_json/{name}.json', 'w', encoding = 'utf-8') as f:
                json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
        except:
            try:
                data = ACSSoup.parse(xml_str) 
                with open('./text_xml/text_json/{name}.json', 'w', encoding = 'utf-8') as f:
                    json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
            except:
                try:
                    data = RSCSoup.parse(xml_str) 
                    with open('./text_xml/text_json/{name}.json', 'w', encoding = 'utf-8') as f:
                        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
                except:    
                    try:
                        data = SpringerSoup.parse(xml_str) 
                        with open('./text_xml/text_json/{name}.json', 'w', encoding = 'utf-8') as f:
                            json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
                    except:    
                        try:
                            data = WileySoup.parse(xml_str) 
                            with open('./text_xml/text_json/{name}.json', 'w', encoding = 'utf-8') as f:
                                json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
                        except:
                            print('file: {} could not be parsed. check the publisher'.format(xml))
                            