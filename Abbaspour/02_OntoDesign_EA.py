# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 13:15:56 2023

@author: 49157
"""

from owlready2 import *
import pyenzyme as pe
from pyenzyme import EnzymeMLDocument, EnzymeReaction, Complex, Reactant, Protein, Creator
from pyenzyme.enzymeml.models import KineticModel, KineticParameter

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

onto_world = owlready2.World()
onto = onto_world.get_ontology("./ONTOLOGY.owl").load()

# load EnzymeML (deactivated macros)
enzmldoc = pe.EnzymeMLDocument.fromTemplate("C://Users//49157//Dropbox//Thesis_ELnaz//05 EnzymeML//EnzymeML_Template_18-8-2021_KR.xlsm")

# print measurements -> Output: Titel, Reactants, Proteins, Complexes and Reactions
#enzmldoc.printDocument(measurements=True)

# Visualize all measurements and add trendline
#fig = enzmldoc.visualize(use_names=True, trendline=True)

for vessel in enzmldoc.vessel_dict.values():
    Vessel_Name = vessel.name
    Vessel_ID = vessel.id
    Vessel_Volume = vessel.volume
    Vessel_Unit = vessel.unit
    Vessel_Constant = vessel.constant
    Vessel_MetaID = vessel.meta_id
    Vessel_Uri = vessel.uri
    Vessel_Creator_ID = vessel.creator_id
    
for reaction in enzmldoc.reaction_dict.values():
    Reaction_Name = reaction.name
    Reaction_ID = reaction.id
    Reaction_SBO = reaction.ontology # SBO_0000176 = Biochemical_Reaction
    Reaction_MetaID = reaction.meta_id
    Reaction_Educts = reaction.educts
    Reaction_Products = reaction.products
    pH_Value = reaction.ph 
    Temperature_Value = reaction.temperature
    Temperature_Unit = reaction.temperature_unit
    Reversible_Reaction = reaction.reversible
    
for Creator in enzmldoc.creator_dict.values():
    Creator_Name = Creator.given_name
    Creator_Familyname = Creator.family_name
    Creator_ID = Creator.id
    Creator_Mail = Creator.mail
    
for reactant in enzmldoc.reactant_dict.values():
    Reactant_Name = reactant.name
    Reactant_MetaID = reactant.meta_id
    Reactant_ID = reactant.id
    Reactant_Vessel = reactant.vessel_id
    Reactant_SBO = reactant.ontology # SBO_0000247 used to be 'SMALL_MOLECULE'? Now -> 'simple chemical'

for protein in enzmldoc.protein_dict.values():
    Protein_Name = protein.name
    Protein_ID = protein.id
    Protein_SBO = protein.ontology # SBO_0000252 = Protein
    Protein_MetaID = protein.meta_id
    Protein_Sequence = protein.sequence
    Protein_EC_Number = protein.ecnumber
    Protein_Organism = protein.organism
    Protein_UniProtID = protein.uniprotid
    Protein_Constant = protein.constant
   

with onto:
    class Biochamical_Substance(onto.search_one(iri = '*ChemicalSubstance')): pass
   
# available components (or compounds): DWSIM comes with six default compound databases (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes), with a total of more than 1500 compounds available for your simulation.
    class Default_Substance_Database(onto.search_one(iri = '*ChemicalSubstance')): pass
    class DWSIM_Compounds(Default_Substance_Database): pass
    class ChemSep(Default_Substance_Database): pass
    class Biodiesel(Default_Substance_Database): pass
    class CoolProp(Default_Substance_Database): pass
    class ChEDL(Default_Substance_Database): pass
    class Electrolytes(Default_Substance_Database): pass

# DWSIM also features full compound data importing from Online Sources or from JSON files or XML files
# additionally a User can create own compounds via Compound Creator
    class Devianting_Database(onto.search_one(iri = '*ChemicalSubstance')): pass
    class Online_Source(Devianting_Database): pass
    class User_Defined_Compounds(Devianting_Database): pass
    
    #class is_part_of():
        #domain = Online_Source
        #range = Devianting_Database
        
    #class is_part_of():
        #domain = User_Defined_Compounds
        #range = Devianting_Database
    
    class XML_file(User_Defined_Compounds): pass
    class JSON_file(User_Defined_Compounds): pass

# too add own compounds, save them in 'addcomps' file as JSON or XML file
    class AddCompound_file(User_Defined_Compounds): pass

    class contains():
        domain = AddCompound_file
        range = User_Defined_Compounds
    
    class contains():
        domain = Default_Substance_Database
        range = onto.search_one(iri = '*ChemicalSubstance')
        
Laccase = User_Defined_Compounds(protein.name)
ABTS_red = User_Defined_Compounds('ABTS_red')
ABTS_ox = User_Defined_Compounds('ABTS_ox')
Water = DWSIM_Compounds('Water')
Oxygen = DWSIM_Compounds('Oxygen')

with onto: 
    class Thermodynamic_Model(Thing): pass
    class PropertyPackage(Thermodynamic_Model): pass
    class Activity_Coefficient_Model(PropertyPackage): pass
    class Ideal_Model(PropertyPackage): pass
    class RaoultsLaw(Ideal_Model): pass
    class NRTL(Activity_Coefficient_Model): pass
    class UNIQUAC(Activity_Coefficient_Model): pass
    class InteractionParameter(Activity_Coefficient_Model): pass

    class is_composed_of_a():
            domain = PropertyPackage
            range = Thermodynamic_Model

# depending on the selected Property Package, different substance properties must be specified 
    class Substance_Property(onto.search_one(iri = '*ChemicalSubstance')): pass
    class Substancename(Substance_Property): pass

# the following properties are only sufficient if a solid is present that remains a solid
    class Has_DWSIM_ID(Substance_Property >> int): pass
    class Has_CAS_Number(Substance_Property >> str): pass
    class Has_SMILES(Substance_Property >> str): pass
    class Has_Formula(Substance_Property >> str): pass
    class Has_Molecular_Weight(Substance_Property >> float): pass

Laccase.Has_DWSIM_ID.append(00000)
Laccase.Has_CAS_Number.append('80498-15-3')
Laccase.Has_SMILES.append('CC[C@H](C)[C@@H](C(N1CCC[C@H]1C(=O)O)=O)N=C([C@H](CCC(=N)O)N=C([C@H](CCC(=O)O)N=C([C@H](C)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](C(C)C)N=C([C@H](C)N)O)O)O)O)O)O)O)')
Laccase.Has_Formula.append('C66H109N19O25')
Laccase.Has_Molecular_Weight.append(1072.08)

ABTS_red.Has_DWSIM_ID.append(10000)
ABTS_red.Has_CAS_Number.append('28752-68-3')
ABTS_red.Has_SMILES.append('CCN1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_red.Has_Formula.append('C18H18N4O6S4')
ABTS_red.Has_Molecular_Weight.append(514.619)

ABTS_ox.Has_DWSIM_ID.append(20000)
ABTS_ox.Has_CAS_Number.append('28752-68-3')
ABTS_ox.Has_SMILES.append('CC[N+]1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_ox.Has_Formula.append('C18H17N4O6S4')
ABTS_ox.Has_Molecular_Weight.append(513.619)

# Substance propoperties in DWSIM
with onto:
    class Has_Curve_For_VaporPressure(Substance_Property >> float): pass
    class Has_Ideal_gas_HeatCapacity(Substance_Property >> float): pass
    class Has_Critical_Compressibility(Substance_Property >> float): pass
    class Has_Critical_Pressure(Substance_Property >> float): pass
    class Has_Critical_Temperature(Substance_Property >> float): pass
    class Has_Critical_Volume(Substance_Property >> float): pass
    class Has_Normal_Boiling_Point(Substance_Property >> float): pass
    class Has_Acentric_Factor(Substance_Property >> float): pass
    class Has_Chao_Seader_Acentricity(Substance_Property >> float): pass
    class Has_Chao_Seader_Liquid_Molar_Volume(Substance_Property >> float): pass
    class Has_Chao_Seader_Solubility_Parameter(Substance_Property >> float): pass
    class Has_IG_Enthalpy_of_Formation_25C(Substance_Property >> float): pass
    class Has_IG_Entropy_of_Formation_25C(Substance_Property >> float): pass
    class Has_IG_Gibbs_Energy_of_Formation_25C(Substance_Property >> float): pass

    class Has_InteractionParameter(NRTL >> float or UNIQUAC >> float): pass #Welche braucht DWSIM?

    class IsBlackOil(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Is_COOL_PROP_Supported(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Is_F_PROPS_Supported(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Is_Hydrated_Salt(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Is_Ion(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Is_Modified(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Is_Salt(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Is_Solid(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class Has_Elements(onto.search_one(iri = '*ChemicalSubstance') >> str): pass

Laccase.IsBlackOil.append(False)
ABTS_red.IsBlackOil.append(False)
ABTS_ox.IsBlackOil.append(False)

Laccase.Is_COOL_PROP_Supported.append(False)
ABTS_red.Is_COOL_PROP_Supported.append(False)
ABTS_ox.Is_COOL_PROP_Supported.append(False)

Laccase.Is_F_PROPS_Supported.append(False)
ABTS_red.Is_F_PROPS_Supported.append(False)
ABTS_ox.Is_F_PROPS_Supported.append(False)

Laccase.Is_Hydrated_Salt.append(False)
ABTS_red.Is_Hydrated_Salt.append(False)
ABTS_ox.Is_Hydrated_Salt.append(False)

Laccase.Is_Ion.append(False)
ABTS_red.Is_Ion.append(False)
ABTS_ox.Is_Ion.append(False)

Laccase.Is_Modified.append(False)
ABTS_red.Is_Modified.append(False)
ABTS_ox.Is_Modified.append(False)

Laccase.Is_Salt.append(False)
ABTS_red.Is_Salt.append(False)
ABTS_ox.Is_Salt.append(False)

Laccase.Is_Solid.append(False)
ABTS_red.Is_Solid.append(False)
ABTS_ox.Is_Solid.append(False)

with onto:
    class Reaction(Thing): pass
    class Chemical_Reaction(Reaction): pass

# SBO_0000176 = biochemical recation    
    class Biochemical_Reaction(Chemical_Reaction): equivalent_to = [(onto.search_one(iri = '*SBO_0000176'))]
    class Bio_Catalysed_Reaction(Biochemical_Reaction): pass
    class Protein_Catalysed_Reaction(Bio_Catalysed_Reaction): pass

    class Has_Reaction_Name(Reaction >> str): pass
    class Has_Reaction_ID(Reaction >> str): pass
    class Has_pH_Value(Reaction >> float): pass
    class Has_Temperature_Value(Reaction >> float): pass
    class Has_Temperature_Unit(Reaction >> str): pass


# SBO_0000208 = acid-base reaction    
    class NucleicAcid_Catalysed_Reaction(Bio_Catalysed_Reaction): equivalent_to = [onto.search_one(iri = '*SBO_0000208')]
    class Abzymatic_Reaction(Protein_Catalysed_Reaction): pass
    class Enzymatic_Reaction(Protein_Catalysed_Reaction): pass

# SBO_0000200 = redox reaction
    class Oxidoreductase_Reaction(Enzymatic_Reaction): equivalent_to = [onto.search_one(iri = '*SBO_0000200')]
    class Transferase_Reaction(Enzymatic_Reaction): pass
    class Hydrolyse_Reaction(Enzymatic_Reaction): pass
    class Lyase_Reaction(Enzymatic_Reaction): pass
    class Isomerase_Reaction(Enzymatic_Reaction): pass
    class Ligase_Reaction(Enzymatic_Reaction): pass

ABTS_Oxidation = Oxidoreductase_Reaction('ABTS_Oxidation')
ABTS_Oxidation.Has_Reaction_ID.append(Reaction_ID)
ABTS_Oxidation.Has_pH_Value.append(pH_Value)
ABTS_Oxidation.Has_Temperature_Value.append(Temperature_Value)
ABTS_Oxidation.Has_Temperature_Unit.append(Temperature_Unit)

with onto: 
# SBO_0000460 = enzymatic catalyst
    class Oxidoreductase(onto.search_one(iri = '*SBO_0000460')): pass
    class Transferase(onto.search_one(iri = '*SBO_0000460')): pass
    class Hydrolyse(onto.search_one(iri = '*SBO_0000460')): pass
    class Lyase(onto.search_one(iri = '*SBO_0000460')): pass
    class Isomerase(onto.search_one(iri = '*SBO_0000460')): pass
    class Ligase(onto.search_one(iri = '*SBO_0000460')): pass

    class catalyses():
        domain = Oxidoreductase
        range = Oxidoreductase_Reaction

    class catalyses():
        domain = Transferase
        range = Transferase_Reaction
    
    class catalyses():
        domain = Hydrolyse
        range = Hydrolyse_Reaction
        
    class catalyses():
        domain = Lyase
        range = Lyase_Reaction

    class catalyses():
        domain = Isomerase
        range = Isomerase_Reaction
        
    class catalyses():
        domain = Ligase
        range = Ligase_Reaction
          
    class Has_Name():
        domain = Reaction
        range = str
        
# SBO_0000003 = participant role
    class Has_Stoichometric_Coeff(onto.search_one(iri = '*SBO_0000003') >> float): pass

Laccase = Oxidoreductase(protein.name)
ABTS_red = (onto.search_one(iri = '*SBO_0000015'))('ABTS_red') # Subtrate = SBO_0000015
ABTS_ox = (onto.search_one(iri = '*SBO_0000011'))('ABTS_ox') # Product = SBO_0000011
Water = (onto.search_one(iri = '*SBO_0000011'))('Water')
Oxygen = (onto.search_one(iri = '*SBO_0000015'))('Oxygen')

Laccase.Has_Stoichometric_Coeff.append(-1.0)
ABTS_red.Has_Stoichometric_Coeff.append(-4.0)
ABTS_ox.Has_Stoichometric_Coeff.append(4.0)
Water.Has_Stoichometric_Coeff.append(2.0)
Oxygen.Has_Stoichometric_Coeff.append(-1.0)

with onto:
# SBO_0000651 = irreversible process    
    class Has_Direct_OrderCoeff(onto.search_one(iri ='*SBO_0000651') >> float): pass

# SBO_0000650 = reversible process
    class Has_Reverse_OrderCoeff(onto.search_one(iri ='*SBO_0000651') >> float): pass

Laccase.Has_Direct_OrderCoeff.append(0.0)
ABTS_red.Has_Direct_OrderCoeff.append(0.0)
ABTS_ox.Has_Direct_OrderCoeff.append(1.0)
Water.Has_Direct_OrderCoeff.append(0.0)
Oxygen.Has_Direct_OrderCoeff.append(0.0)

Laccase.Has_Reverse_OrderCoeff.append(0.0)
ABTS_red.Has_Reverse_OrderCoeff.append(0.0)
ABTS_ox.Has_Reverse_OrderCoeff.append(0.0)
Water.Has_Reverse_OrderCoeff.append(0.0)
Oxygen.Has_Reverse_OrderCoeff.append(0.0)

with onto:
# EnzymeML: Documentation of 19 reactants and 19 proteins
# s0 = ABTS_red, s1 = oxygen, s2 = ABTS_ox, s3 = ABTS_red, s4 = oxygen, s5 = ABTS_ox
# SBO_0000011 = product, SBO_0000015 = substrate
    class s0(onto.search_one(iri ='*SBO_0000015')): pass
    class s1(onto.search_one(iri ='*SBO_0000015')): pass
    class s2(onto.search_one(iri ='*SBO_0000011')): pass
    class s3(onto.search_one(iri ='*SBO_0000015')): pass
    class s4(onto.search_one(iri ='*SBO_0000015')): pass
    class s5(onto.search_one(iri ='*SBO_0000011')): pass

# p0 = Laccase_HTR, p1 = Laccase_SCR
# SBO_0000014 = enzyme (SBO_0000460 = enzymatic catalyst)
    class p0(onto.search_one(iri ='*SBO_0000014')): pass
    class p1(onto.search_one(iri ='*SBO_0000014')): pass

# SBO_0000014 = enzyme (Laccase = Protein = ontology=<SBOTerm.PROTEIN: 'SBO:0000252' -> nicht hinterlegt)
    class Has_Sequence((onto.search_one(iri = '*SBO_0000014')) >> str): pass                  
    class Has_Source_Organism((onto.search_one(iri = '*SBO_0000014')) >> str): pass
    class Has_EC_Number((onto.search_one(iri = '*SBO_0000014')) >> str): pass     
    class Has_UniProt_ID((onto.search_one(iri = '*SBO_0000014')) >> str): pass
    class Has_Const_Concentration((onto.search_one(iri = '*SBO_0000014')) >> bool or (onto.search_one(iri ='*SBO_0000015')) >> bool or (onto.search_one(iri ='*SBO_0000011')) >> bool): pass
        
Laccase.Has_Sequence.append(Protein_Sequence)
Laccase.Has_Source_Organism.append(Protein_Organism)
Laccase.Has_EC_Number.append(Protein_EC_Number)
Laccase.Has_UniProt_ID.append('D2CSE5')
Laccase.Has_Const_Concentration.append(Protein_Constant)        

with onto:
    class ProcessFlowDiagram(Thing): pass
    class MaterialFlow(ProcessFlowDiagram): pass
    class InletFlow(MaterialFlow): pass
    class OutletFlow(MaterialFlow): pass
    class Equipment(ProcessFlowDiagram): pass
    class Reactor(Equipment): pass
    class Reactortype(Reactor): pass
    
    class Has_Volume_Value(Equipment >> float): pass
    class Has_Volume_Unit(Equipment >> str): pass
    
    class Has_Lenght_Value(Equipment>> float): pass
    class Has_Lenght_Unit(Equipment >> str): pass
    class Has_Compound_MolarFlow(MaterialFlow >> float): pass       
        
SCR = Reactortype(Vessel_Name)
HTR = Reactortype('Helical_tube_reactor')

SCR.Has_Volume_Value.append(Vessel_Volume)
SCR.Has_Volume_Unit.append(Vessel_Unit)
HTR.Has_Volume_Value.append(Vessel_Volume)
HTR.Has_Volume_Unit.append(Vessel_Unit)

Inlet_Laccase = InletFlow('Inlet_Laccase')
Inlet_ABTS_ox = InletFlow('Inlet_ABTS_ox')
Inlet_Oxygen = InletFlow('Inlet_Oxygen')

Inlet_Laccase.Has_Compound_MolarFlow.append(1.0) # mol/s
Inlet_ABTS_ox.Has_Compound_MolarFlow.append(1.0) # mol/s
Inlet_Oxygen.Has_Compound_MolarFlow.append(1.0) # mol/s

with onto:
    class Project(Thing): pass
    class Institution(Project): pass
    class Organisation(Institution): pass
    class Agent(Institution): pass         
    class Engineering_Step(Project): pass # Basic Engineering, Detail Engineering
    class Processdesign(Engineering_Step): pass
    class Processsimulation(Processdesign): pass
    class Documentation(Project): pass

    #class has_a(Institution >> Project): pass
    #class is_part_of(Agent >> Institution): pass
    #class is_part_of(Engineering_Step >> Project): pass
    #class is_part_of(Organisation >> Institution): pass
    #class is_a(Processdesign >> Engineering_Step): pass
    #class is_part_of(Processsimulation >> Engineering_Step): pass
    #class is_part_of(Documentation >> Project): pass

    class Has_Projectstart(Project >> str): pass
 
    class ElectronicLabNotebook(Documentation): pass
    class EnzymeML_Documentation(ElectronicLabNotebook): pass

    #class Has_Projectstart(Project >> datetime.date): pass  
    class Has_Titel(EnzymeML_Documentation >> str): pass
    class Has_Creator(EnzymeML_Documentation >> str): pass
    class Has_Creator_Mail(Agent >> str): pass
    #class Has_Date_of_Creation(EnzymeML_Documentation >> datetime.date): pass
    class Has_Date_of_Creation(EnzymeML_Documentation >> str): pass

ABTS_Oxidation_by_Laccase = Project('ABTS_Oxidation_by_Laccase')
TU_Dortmund = Institution('TU_Dortmund')
Chair_of_EquipmentDesign = Organisation('Chair_of_EquipmentDesign')
EnzymeML_Document_1 = EnzymeML_Documentation('EnzymeML_Document_1')
Agent = Agent('Abbaspour')

EnzymeML_Document_1.Has_Titel.append(enzmldoc.name)
EnzymeML_Document_1.Has_Creator.append(Creator_Familyname)
EnzymeML_Document_1.Has_Creator_Mail.append(Creator_Mail)
EnzymeML_Document_1.Has_Date_of_Creation.append(enzmldoc.created)


with onto:
    class Stabilizer(onto.search_one(iri = '*SBO_0000594')): pass
    class Has_Stabilizer_Concentration(onto.search_one(iri = '*SBO_0000594') >> float): pass

    class Experimental_Data(EnzymeML_Documentation): pass
    class Measurement(Experimental_Data): pass
    # 12 Messungen im EnzymeML Dokument
    class Concentration_Curve(Measurement): pass # mit Initialkonzentrationswerten für oxygen laccase und red
    class Reactant_Conc_Curve(Concentration_Curve): pass
    class Protein_Conc_Curve(Concentration_Curve): pass
    class Absorption(Measurement): pass
    class Time_Measurement(Measurement): pass


Laccase_Conc_Curve = Protein_Conc_Curve('Laccase_Conc_Curve')
ABTS_red_Conc_Curve = Reactant_Conc_Curve('ABTS_red_Conc_Curve')

with onto:
    sync_reasoner()
    
    
onto.save("02_OntoChemSBO_myOnto.owl") 