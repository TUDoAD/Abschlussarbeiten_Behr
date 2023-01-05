# load ontology ontochem.owl from local file

import owlready2
from owlready2 import *
import types

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

local_world = owlready2.World()
onto = local_world.get_ontology("./metadata4ing.owl").load()
onto = local_world.get_ontology("./EnzymeML_in_Ontochem_new.owl").load()

# check existing components of the ontology
import ontospy

model = ontospy.Ontospy("./EnzymeML_in_Ontochem_.owl", verbose=True)
model.printClassTree()

print(onto.base_iri)

print("showing classes:")
print( list(onto.classes()) )
print()

print("showing individuals:")
print( list(onto.individuals()) )
print()

print("showing data properties:")
print( list(onto.data_properties()) )
print()

print("showing annotation properties:")
print( list(onto.annotation_properties()) )
print()

print("showing properties:")
print( list(onto.properties()) )
print()

print("disjoint properties:")
print( list(onto.disjoint_properties()) )
print()

print("print disjoints:")
print( list(onto.disjoints()) )
print()

print("showing individuals:")
print( list(onto.individuals()) )

print(list(onto.search(iri="*PhysChemProcessingTask")))

# create classes and subclasses into ontochem.owl
with onto:
    class Agent(Thing): pass
    class Organisation(Agent): pass
    class Group(Agent): pass
    class Person(Agent): pass

    class Project(Thing): pass
    class Documentation(Project): pass
    class EnzymeML_Document(Documentation): pass

    class EnzymaticReaction(Thing): pass

    class Vessels(onto.search_one(iri="*Device")): pass
    class Reactor(Vessels): pass
    class HelicalTubeReactor(Reactor): pass
    class StraightTubeReactor(Reactor): pass

    class BioProcessingModule(onto.search_one(iri="*ProcessingModule")): pass

# create properties 
class has_sheet_ID(Vessels >> Reactor): pass
        
with onto:
    sync_reasoner()

onto.save("OntoPyEnzymeMl.owl")