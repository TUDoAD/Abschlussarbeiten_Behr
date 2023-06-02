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
    Agent.comment = locstr("An agent (e.g. person, group,software or physical "
                           "artifact).", lang = "en")
    class Organisation(Agent):
        pass
    Organisation.comment = locstr("A class of Agents.", lang = "en")
    class Group(Agent):
        pass
    Group.comment = locstr("An organization.", lang = "en")
    class Person(Agent):
        pass
    Person.comment = locstr("A person.",lang = "en")
    class Project(Thing):
        pass
    Project.comment = locstr("An enterprise (potentially individual but " 
                             "typically collaborative), planned to achieve a particular aim.",
                             lang = "en")
    class Role(Thing):
        pass
    Role.comment = locstr("A role is the function of an entity or agent with "
                          "respect to an activity, in the context of a usage, "
                          "generation, invalidation, association, start, and end.",
                          lang = "en")
    class Documentation(Project):
        pass
    Documentation.comment = locstr("Is the permanent storage of project-related "
                                   "information, the findability and reuse of which "
                                   "is guaranteed in this way.", lang = "en")
    class EnzymeML_Document(Documentation):
        pass
    EnzymeML_Document.comment = locstr("EnzymeML is a free and open XML-based format "
                                       "for a standardized monitoring and exchange of "
                                       "data on enzyme-catalyzed reactions according to "
                                       "the FAIR principles.", lang = "en")
    class EnzymaticReaction(Thing):
        pass
    EnzymaticReaction.comment = locstr("Is an enzyme catalyzed reaction.", lang ="en")
    AllDisjoint([EnzymaticReaction, onto.search_one(iri='*ChemicalReaction')])
    class Data(EnzymaticReaction):
        pass
    class Measurements(Data):
        pass
    class Vessels(onto.search_one(iri="*Device")):
        pass
    onto.search_one(iri="*Device").comment = locstr("Is a tool, an instrument, a machine "
                                                    "that serves a specific purpose.", 
                                                    lang = "en")
    class Reactor(Vessels):
        pass
    Vessels.comment = locstr("Is an enclosed volume in which a reaction takes place.", 
                             lang = "en")
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


# create individuals
    Sponsor = Role("Sponsor")

# create object properties
    class has_agent(EnzymeML_Document >> Agent):
        pass
    class is_agent_of(Agent >> EnzymeML_Document):
        inverse = has_agent      
    class has_source_organism(Proteins >> Organism):
        pass # Source organism from which the given protein originated from
    class is_source_organism_of(Organism >> Proteins):
        inverse = has_source_organism
   
    
# create data properties
    class has_sheet_ID(Vessels >> int):
        pass
    class has_volume_value(Vessels >> int):
        pass # Numeric value of the vessel volume
    class has_volume_unit(Vessels >> str):
        pass # Unit of the vessel volume
    class is_constant(onto.search_one(iri='*ChemicalSubstance') >> bool):
        pass # Wheter or not the concentration of given substances varies over time; as boolean
    class has_sequence(Proteins >> str):
        pass # Primary sequence of your protein; as string
    class has_temperature_value():
        pass # Numeric value of the temperature the experiment was executed at
    class has_temperature_unit(EnzymaticReaction >> str or onto.search_one(iri='*ChemicalReaction') >> str):
        pass # Unit of the temperature 
    class pH_value():
        pass # pH value at which your reaction was executed
    class is_reversible(onto.search_one(iri='*ChemicalSubstance') >> bool):
        pass # Is the reaction reversible?
    class is_irreversible(onto.search_one(iri='*ChemicalSubstance') >> bool):
        pass

onto.save("OntoPyEnzymeML.owl")

with onto:
    sync_reasoner()