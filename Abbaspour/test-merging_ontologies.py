"""
@author: 49157
"""
import owlready2
import types
from owlready2 import *

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

local_world = owlready2.World()
onto = local_world.get_ontology("./SBO_rohfassung.owl").load()
onto = local_world.get_ontology("./Ontochem_modifiziert_rohfassung.owl").load()

local_world.save("py-merge-ontos.owl")
