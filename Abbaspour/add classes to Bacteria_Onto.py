# File "bacteria1" laden und Entitäten anzeigen lassen
# Klassen/Subklassen in die bestehende Ontologie einfügen

from owlready2 import *
import types
onto_world = owlready2.World()
onto = onto_world.get_ontology("./bacteria1.owl")
onto = onto.load()

print(onto.base_iri)

import ontospy
model = ontospy.Ontospy("./bacteria1.owl", verbose=True)

model.printClassTree()

print()
print("showing first 10 classes:")
print( list(onto.classes())[:10])
print()

print("showing first 10 individuals:")
print( list(onto.individuals())[:10] )
print()

print("showing data properties:")
print( list(onto.data_properties()) )
print()

# print("showing first 10 annotation properties:")
# print( list(onto.annotation_properties())[:10] )
# print()

print("showing first 10 properties:")
print( list(onto.properties())[:10] )
print()

print("disjoint properties:")
print( list(onto.disjoint_properties()) )
print()

print("print disjoints:")
print( list(onto.disjoints()) )
print()
# print("Get relation instances:")
# print( list(onto.engages.get_relations()))

print("showing individuals:")
print(list(onto.individuals()))

with onto:
    class Plasmid(onto.Bacterium):
        equivalent_to = [ onto.Bacterium
                        & onto.has_shape.only(onto.Round) ]
        
    class NoChain(onto.Grouping):
        pass
    
onto.save("add classes to bacteria1.owl")