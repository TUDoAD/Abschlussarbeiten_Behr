"""
@author: 49157
"""
import owlready2 as owl
from owlready2 import *
import types
import pathlib
import os

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

local_world = owlready2.World()
onto1 = local_world.get_ontology("./SBO.owl").load()
onto2 = local_world.get_ontology("./metadata4ing.owl").load()
onto2 = local_world.get_ontology("./EnzymeML_in_Ontochem_new.owl").load()

importPath = pathlib.Path("onto1")
exportPath = pathlib.Path("onto2")

if os.path.exists(os.path.join(importPath.parent, 'imports')):
    owl.onto_path.append(os.path.join(importPath.parent, 'imports'))
else:
    raise Exception

if importPath.exists():
    owl.onto_path.append(str(importPath.parent.resolve()))
    tpoImport = owl.get_ontology(str(importPath.resolve())).load(only_local=True)
else:
    raise FileNotFoundError

world = owl.default_world

graph = world.as_rdflib_graph()

graph.serialize(destination=str(exportPath.resolve()), format="xml")