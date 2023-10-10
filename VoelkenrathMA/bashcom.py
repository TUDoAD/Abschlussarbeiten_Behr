# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 10:27:42 2023

@author: mvoel
"""

import os

# URL: link to ontologie
# IRI-file: txt-file with the IRI's
# onto: name of the output-file

URL = "https://raw.githubusercontent.com/nfdi4cat/Ontology-Overview-of-NFDI4Cat/main/ontologies/AFO.ttl"
#URL = "C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/ontologies/HuPSON_v092013_merged.owl"
IRI_file = "ontologies/IRIs.txt"
onto = "ontologies/bsp_zwischengespraech.owl"

# meth: methods can be found here [http://robot.obolibrary.org/extract]
meth = "BOT"

bashCommand = "java -jar C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/robot/robot.jar extract --input-iri {} --method {} --term-file {} --output {} ".format(URL, meth, IRI_file, onto)

#bashCommand = "java -jar C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/robot/robot.jar merge --input ontologies/MV-Onto.owl --input ontologies/Reac4Cat_Folgereaktion.owl --output ontologies/MV-Ontology.owl"


os.system(bashCommand)
