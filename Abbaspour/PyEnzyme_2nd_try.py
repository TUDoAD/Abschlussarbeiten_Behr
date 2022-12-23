# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 16:51:03 2022

@author: 49157
"""

import pyenzyme as pe

# EnzymeMLDocument is the container object that stores all experiment
# information based on sub classes

# Initialize the EnzymeML document 
enzmldoc = pe.EnzymeMLDocument(name="enzymkatalysierte Reaktion")

# Creator carries the metadata about an author
# addCreator adds a Creator object to the EnzymeMLdocument

# Add authors to the document
author = pe.Creator(given_name="Elnaz", family_name="Abbaspour",
                    mail="elnaz.abbaspour@tu-dortmund.de")
author_id = enzmldoc.addCreator(author)

# Vessel carries the metadata for vessels that are used
# addVessel adds a Vessel object to the document and returns the ID

vessel = pe.Vessel(name="STR", volume=40.0, unit="ml")
vessel_id = enzmldoc.addVessel(vessel)

# Protein carries the metadata for proteins that are part of the experiment
# addProtein adds a Protein object to the document and returns the ID

enzyme = pe.Protein(name="Laccase", vessel_id=vessel_id,
                    sequence="MAVKLT", constant=False)
enzyme_id = enzmldoc.addProtein(enzyme)

# Reactant carries the metadata for reactants that are part of the experiment
# addReactant adds a Reactant object to the document and returns the ID

substrate = pe.Reactant(name="ABTS_red", vessel_id=vessel_id)
substrate_id = enzmldoc.addReactant(substrate)

product = pe.Reactant(name="ABTS_ox", vessel_id=vessel_id)
product_id = enzmldoc.addReactant(product)

# Add enzyme-substrate- and enzyme-product-complexes
es_complex_id = enzmldoc.addComplex(
    name="ES",
    vessel_id=vessel_id,
    participants=[enzyme_id, substrate_id])

ep_complex_id = enzmldoc.addComplex(
    name="EP",
    vessel_id=vessel_id,
    participants=[enzyme_id, product_id])

# Creating reactions from equations
# Setting up by equation or add-methods

reaction_1 = pe.EnzymeReaction.fromEquation("ABTS_red + Laccase = ES",
                                            "reaction-1", enzmldoc)
reaction_2 = pe.EnzymeReaction.fromEquation("ES = EP", "reaction-2", enzmldoc)
reaction_3 = pe.EnzymeReaction.fromEquation("EP = ABTS_ox", "reaction-3", 
                                            enzmldoc)

# Finally, add al reactions to the document
reaction_ids = enzmldoc.addReactions([reaction_1, reaction_2, reaction_3])
reaction_ids = {'reaction-1': 'r0', 'reaction-2': 'r1', 'reaction-3': 'r2'}

# Finally, save the document to an OMEX archive
enzmldoc.toFile(".", name="Experiment ohne Reaktionen")