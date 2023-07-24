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
IRI_file = "ontologies/robot_bot_iri.txt"
onto = "ontologies/top.owl"

# meth: methods can be found here [http://robot.obolibrary.org/extract]
meth = "BOT"

bashCommand = "java -jar c://Windows/robot.jar extract --input-iri {} --method {} --term-file {} --output {} ".format(URL, meth, IRI_file, onto)

"""
bashCommand = "java -jar c://Windows/robot.jar merge --input ontologies/bot.owl --input ontologies/top.owl --output ontologies/MV-Ontology.owl"
"""

os.system(bashCommand)
