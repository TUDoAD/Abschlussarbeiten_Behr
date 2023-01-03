# load ontochem and add EnzymeML-classes

import owlready2
from owlready2 import *
import types

local_world = owlready2.World()
onto_local = local_world.get_ontology("./metadata4ing.owl").load()
onto_local = local_world.get_ontology("./EnzymeML_in_Ontochem_.owl").load()

onto = onto_local

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

with onto:
    class Vessels(onto.search_one(iri="*Device")): pass
         
onto.save("OntoPyEnzymeMl.owl")