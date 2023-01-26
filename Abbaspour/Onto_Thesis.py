# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 12:37:54 2023

@author: 49157
"""

from owlready2 import *
import owlready2

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

onto_world = owlready2.World()
onto = onto_world.get_ontology("./Onto_Thesis.owl").load()

# Create classes and subclasses
with onto:
    # Add classes to organize a project
    class Agent(Thing): pass
    class Organisation(Agent): pass    
    class Group(Agent): pass  
    class Person(Agent): pass  
    class Project(Thing): pass
    class Projecttitle(Project): pass
    class Documentation(Project): pass          
    

    # Add classes to organize documentation
    class EnzymeML_Document(Documentation): pass
    class Title(EnzymeML_Document): equivalent_to = [Projecttitle] 
    class Institution(Project): equivalent_to = [Organisation]
   
    
    # Add classes to ontochem 'DEVICE'
    class Vessels(onto.search_one(iri = '*Device')): pass
    class Reactor(onto.search_one(iri = '*Device')): pass
    
   
    # Add enzyme classes to SBO 'ENZYMATIC CATALYST'
    class Oxidoreductases(onto.search_one(iri = '*SBO_0000460')): equivalent_to = [onto.search_one('*SBO_0000200')]
    class Transferases(onto.search_one(iri = '*SBO_0000460')): pass
    class Hydrolases(onto.search_one(iri = '*SBO_0000460')): pass
    class Lyases(onto.search_one(iri = '*SBO_0000460')): pass
    class Isomerases(onto.search_one(iri = '*SBO_0000460')): pass
    class Ligases(onto.search_one(iri = '*SBO_0000460')): pass


# Add individuals
    DepartmentOfBCI = Institution("DepartmentOfBCI")
    TU_Dortmund = Organisation("TU_Dortmund")
    HelicalTubeReactor = Reactor("HelicalTubeReactor")
    StraightTubeReactor = Reactor("StraightTubeReactor")
    Laccase = Oxidoreductases("Laccase")
    Lac_HCR_SCR = Title("Lac_HCR_SCR")
    
    
# Add properties    
    # Data properties class SBO 'ENZYMATIC CATALYST' (to identify given enzyme)
    class has_sheet_ID(onto.search_one(iri = '*SBO_0000460') >> str): pass # conect later with vessel id
    class has_sequence(onto.search_one(iri = '*SBO_0000460') >> str): pass # Primary sequence of your protein; as string
    class has_EC_Number(onto.search_one(iri = '*SBO_0000460') >> int): pass # Enzyme Comission number of the enzyme; depends on catalysed reaction
    class has_UniProt(onto.search_one(iri = '*SBO_0000460') >> int): pass # UniProt identifier
    
    
    #Data properties (to identify given reactants)
    class has_InCHI(onto.search_one(iri = '*SBO_0000010') >> int): pass
    class has_SMILES(onto.search_one(iri = '*SBO_0000010') >> str): pass
    

    # Documentation 
    class has_date_of_creation(EnzymeML_Document >> datetime.date): pass
    

    # Volume of reactor
    # SBO_0000465: spatial measure
    class has_volume_value(onto.search_one(iri = '*Device') >> int): pass
    class has_value_unit(onto.search_one(iri = '*Device') >> str): pass # not only volume value has a unit
    class has_value(onto.search_one(iri = '*SBO_0000465') >> int): pass


    # Wether the concentration of reactant and protein is constant or not
    # CONCENTRATION OF AN ENTITY POOL
    class is_constant(onto.search_one(iri = '*SBO_0000196') >> bool): pass      

    
# Object properties
    class has_eMail(Agent >> Thing, InverseFunctionalProperty): pass
   

# Add annotations
Agent.comment = locstr("An agent (e.g. person, group,software or physical artifact).", lang = "en")
Organisation.comment = locstr("A class of Agents.", lang = "en")
Group.comment = locstr("An organization.", lang = "en")
Person.comment = locstr("A person.",lang = "en")
Project.comment = locstr("An enterprise (potentially individual but typically collaborative), planned to achieve a particular aim.", lang = "en")
Project.label = "Project"
Project.comment = locstr("An enterprise (potentially individual but typically collaborative), planned to achieve a particular aim", lang = "en")
Documentation.comment = locstr("Is the permanent storage of project-related information, the findability and reuse of which is guaranteed in this way.", lang = "en")
EnzymeML_Document.comment = locstr("EnzymeML is a free and open XML-based format for a standardized monitoring and exchange of data on enzyme-catalyzed reactions according to the FAIR principles.", lang = "en")
Lac_HCR_SCR.comment = locstr("Is the title of the current EnzymeML document and experiment.", lang = "en")
is_constant.comment = locstr("Wether or not the concentration of given reactant or protein varies over time.", lang = "en")    
has_SMILES.comment = locstr("Simplified Molecular Inout Line Entry Specification that uniquely identifies the species.", lang = "en")
has_InCHI.comment = locstr("International Chemical Identifier that uniquely identifies the species.", lang = "en")


onto.save("Onto_.owl")