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

path=".\text_xml\*.xml"
for xml in glob.iglob(path):
    with open('{}.xml'.format(xml), 'r', encoding='utf-8') as file:
        xml_str = file.read()
        data = ECSSoup.parse(xml_str) 
        with open('file_test.json', 'w', encoding = 'utf-8') as f:
            json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)

