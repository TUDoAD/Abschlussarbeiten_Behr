# -*- coding: utf-8 -*-
"""
Created on Fri Dec 31 15:41:14 2021

@author: Alexander Behr
@affiliation: TU Dortmund Fac. BCI - AG AD
"""

# pip install ontospy
# pip install ontospy[FULL]

## full module (use this):
# pip install ontospy[FULL] -U
import ontospy
from ontospy.ontodocs.viz.viz_html_single import *
from ontospy.ontodocs.viz.viz_d3dendogram import *

import vocexcel
from vocexcel import convert

import glob
import os
from pathlib import Path
#import subprocess

import URIgenerator


#convert.excel_to_rdf("eg-withRelated.xlsx")

filenames = glob.glob("./import/*.xlsx")


for name in filenames:
    print("name")
    URIgenerator.URI_generation(name)
    print("URIs generated and saved in {}".format(os.path.basename(name)))
    
    convert.excel_to_rdf(name,output_file_path = "./export/")#,output_format = "xml")
    print("converted import/{} successfully to export/{}.".format(os.path.basename(name),Path(os.path.basename(name)).with_suffix(".ttl")))




# import shutil 
# import os

##
#       SKOS plotting begins
##
model = ontospy.Ontospy("./export/"+str(Path(os.path.basename(name)).with_suffix(".ttl")), verbose = True)

#model = ontospy.Ontospy("ExampleCFDOntology.owl", verbose = True)
docs_model = HTMLVisualizer(model, title="docs")
dendro = Dataviz(model, title = "dendrogram")

docs_model.build(output_path='./export/docs/')
dendro.build(output_path = './export/dendro/')

#dendro.preview()


#docs_model.preview()

#dendro.build()
#dendro.preview()


#ontospy.ontodocs.viz.viz_d3dendogram(model)