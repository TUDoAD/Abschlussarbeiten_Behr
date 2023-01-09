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

print(list(onto.search(iri="*PhysChemProcessingTask")))

# create classes and subclasses into ontochem.owl 
with onto:
    class Agent(Thing):
        pass
    class Organisation(Agent):
        pass
    class Group(Agent):
        pass
    class Person(Agent):
        pass

    class Project(Thing):
        pass
    class Documentation(Project):
        pass
    class EnzymeML_Document(Documentation):
        pass

    class EnzymaticReaction(Thing):
        pass

    class Vessels(onto.search_one(iri="*Device")):
        pass
    class Reactor(Vessels):
        pass
    class HelicalTubeReactor(Reactor):
        pass
    class StraightTubeReactor(Reactor):
        pass

    # Protein and organism as subclass of chemical substance
    # SMILES and InCHI already implied
    # EC Number and UniprotID too?
    class Proteins(onto.search_one(iri='*ChemicalSubstance')):
        pass
    class Organism(onto.search_one(iri='*ChemicalSubstance')):
        pass
    class BioProcessingModule(onto.search_one(iri="*ProcessingModule")):
        pass


# create object properties
    class has_agent(EnzymeML_Document >> Agent):
        pass
    class is_agent_of(Agent >> EnzymeML_Document):
        inverse = has_agent      
    class has_sheet_ID(Vessels >> Reactor):
        pass  
    class has_source_organism(Proteins >> Organism):
        pass # Source organism from which the given protein originated from
   
    
# create data properties
    class has_volume_value(Vessels >> int):
        pass # Numeric value of the vessel volume
    class has_volume_unit(Vessels >> str):
        pass # Unit of the vessel volume
    class is_constant():
        pass # Wheter or not the concentration of given protein varies over time; as boolean
    class has_sequence():
        pass # Primary sequence of your protein; as string
    class has_temperature_value():
        pass # Numeric value of the temperature the experiment was executed at
    class has_temperature_unit():
        pass # Unit of the temperature 
    class pH_value():
        pass # pH value at which your reaction was executed
    class is_reversible(onto.search_one(iri='*ChemicalSubstance') >> bool):
        pass # Is the reaction reversible?

onto.save("OntoPyEnzymeML.owl")

with onto:
    sync_reasoner()