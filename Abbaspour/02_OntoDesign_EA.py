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
onto = onto_world.get_ontology("./00_ONTOLOGY.owl").load()

# load EnzymeML (deactivated macros)
enzmldoc = pe.EnzymeMLDocument.fromTemplate("C://Users//49157//Dropbox//Thesis_ELnaz//05 EnzymeML//EnzymeML_Template_18-8-2021_KR.xlsm")

# print measurements -> Output: Titel, Reactants, Proteins, Complexes and Reactions
#enzmldoc.printDocument(measurements=True)

# Visualize all measurements and add trendline
#fig = enzmldoc.visualize(use_names=True, trendline=True)

for vessel in enzmldoc.vessel_dict.values():
    Vessel_Name = vessel.name #'Straight tube reactor'
    Vessel_ID = vessel.id #'v1'
    Vessel_Volume = vessel.volume #'8.0
    Vessel_Unit = vessel.unit #'ml'
    Vessel_Constant = vessel.constant #True
    Vessel_MetaID = vessel.meta_id #'METAID_V1'
    Vessel_Uri = vessel.uri #None
    Vessel_Creator_ID = vessel.creator_id #None
    
for reaction in enzmldoc.reaction_dict.values():
    Reaction_Name = reaction.name #'ABTS oxidation, SCR'
    Reaction_ID = reaction.id #'r1'
    Reaction_SBO = reaction.ontology #'SBO_0000176 = Biochemical_Reaction'
    Reaction_MetaID = reaction.meta_id #'METAID_R1'
    Reaction_Educts = reaction.educts #Substrate-list
    Reaction_Products = reaction.products #Product-list
    pH_Value = reaction.ph #5.2
    Temperature_Value = reaction.temperature #311.15
    Temperature_Unit = reaction.temperature_unit #K
    Reversible_Reaction = reaction.reversible #False
    
for Creator in enzmldoc.creator_dict.values():
    Creator_Name = Creator.given_name #'Katrin '
    Creator_Familyname = Creator.family_name #'Rosenthal'
    Creator_ID = Creator.id #'a0'
    Creator_Mail = Creator.mail #'katrin.rosenthal@tu-dortmund.de'
    
for reactant in enzmldoc.reactant_dict.values():
    Reactant_Name = reactant.name #'ABTS oxidized'
    Reactant_MetaID = reactant.meta_id #'METAID_S5'
    Reactant_ID = reactant.id #'s5'
    Reactant_Vessel = reactant.vessel_id #'v0'
    Reactant_SBO = reactant.ontology # SBO_0000247 used to be 'SMALL_MOLECULE'? Now -> 'simple chemical'

for protein in enzmldoc.protein_dict.values():
    Protein_Name = protein.name #'Laccase, SCR'
    Protein_ID = protein.id #'p1'
    Protein_SBO = protein.ontology # SBO_0000252 = Protein
    Protein_MetaID = protein.meta_id #'METAID_P1'
    Protein_Sequence = protein.sequence
    Protein_EC_Number = protein.ecnumber #'1.10.3.2'
    Protein_Organism = protein.organism # 'Trametes versicolor'
    Protein_UniProtID = protein.uniprotid #None, should be 'D2CSE5'
    Protein_Constant = protein.constant #True
   

with onto:
    class Biochamical_Substance(onto.search_one(iri = '*ChemicalSubstance')): pass
   
# available components (or compounds): DWSIM comes with six default compound databases (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes), with a total of more than 1500 compounds available for your simulation.
    class Substance_Database(onto.search_one(iri = '*ChemicalSubstance')): pass
    class Default_Database(Substance_Database): pass
    class DWSIM_Compounds(Default_Database): pass
    class ChemSep(Default_Database): pass
    class Biodiesel(Default_Database): pass
    class CoolProp(Default_Database): pass
    class ChEDL(Default_Database): pass
    class Electrolytes(Default_Database): pass

# DWSIM also features full compound data importing from Online Sources or from JSON files or XML files
# additionally a User can create own compounds via Compound Creator
    class Devianting_Database(Substance_Database): pass
    class Online_Source(Devianting_Database): pass
    class User_Defined_Compound(Devianting_Database): pass

# too add own compounds, save them in 'addcomps' file as JSON or XML file
    class AddCompound_File(User_Defined_Compound): pass      
    class XML_file(AddCompound_File): pass
    class JSON_file(AddCompound_File): pass

    class must_include(AddCompound_File >> User_Defined_Compound): pass
        
Laccase = JSON_file(protein.name)
ABTS_red = JSON_file('ABTS_red')
ABTS_ox = JSON_file(Reactant_Name)
Water = DWSIM_Compounds('Water')
Oxygen = DWSIM_Compounds('Oxygen')

with onto:
    class Thermodynamic(Thing): pass
    class PropertyPackage(Thermodynamic): pass
    class Activity_Coefficient_Model(PropertyPackage): pass
    class Ideal_Model(PropertyPackage): pass
    class RaoultsLaw(Ideal_Model): pass
    class NRTL(Activity_Coefficient_Model): pass
    class UNIQUAC(Activity_Coefficient_Model): pass
    class InteractionParameter(Activity_Coefficient_Model): pass #Wieviele Interactionsparameter und welche braicht DWSIM?

# depending on the selected Property Package, different substance properties must be specified 
    class Substance_Property(onto.search_one(iri = '*ChemicalSubstance')): pass
    class Physico_chemical_propertiy(Substance_Property): pass
    class Molarmass(Physico_chemical_propertiy): pass
    class MeltingPoint(Physico_chemical_propertiy): pass
    class BoilingPoint(Physico_chemical_propertiy): pass
    class Density(Physico_chemical_propertiy): pass
    class Solubility(Physico_chemical_propertiy): pass
    class Solubility_in_Water(Physico_chemical_propertiy): pass
    class Solubility_in_OrganicSolvent(Physico_chemical_propertiy): pass    
    class Enzymatic_SubstanceProperty(Substance_Property): pass
    class Enzymatic_Substrate_Specificity(Enzymatic_SubstanceProperty): pass
    class pH_Optimum(Enzymatic_SubstanceProperty): pass
    class Temp_Optimum(Enzymatic_SubstanceProperty): pass
    class Catalytic_Efficiency(Enzymatic_SubstanceProperty): pass
    class Kinetic_Parameter(Catalytic_Efficiency):pass
    class Substrate_Affinity(Enzymatic_SubstanceProperty): pass
    class Inhibitor_Sensitivity(Enzymatic_SubstanceProperty): pass

# the following properties are only sufficient if a solid is present that remains a solid
    class Has_DWSIM_ID(onto.search_one(iri = '*ChemicalSubstance') >> int): pass
    class Has_CAS_Number(onto.search_one(iri = '*ChemicalSubstance') >> str): pass
    class Has_SMILES(onto.search_one(iri = '*ChemicalSubstance') >> str): pass
    class Has_Formula(onto.search_one(iri = '*ChemicalSubstance') >> str): pass
    class Has_Molecular_Weight(onto.search_one(iri = '*ChemicalSubstance') >> float): pass

# relevante infos, die man für den compound creator braucht
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

# Substance propoperties in DWSIM - wichtig, um substanz zu definieren und zu speichern
with onto:
    class Has_Curve_For_VaporPressure(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Ideal_gas_HeatCapacity(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Critical_Compressibility(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Critical_Pressure(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Critical_Temperature(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Critical_Volume(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Normal_Boiling_Point(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Acentric_Factor(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Chao_Seader_Acentricity(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Chao_Seader_Liquid_Molar_Volume(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_Chao_Seader_Solubility_Parameter(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_IG_Enthalpy_of_Formation_25C(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_IG_Entropy_of_Formation_25C(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class Has_IG_Gibbs_Energy_of_Formation_25C(onto.search_one(iri = '*ChemicalSubstance') >> float): pass

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
    # ontochem includes a class chemical reaction
    # SBO_0000176 = biochemical recation
    class Bio_Catalysed_Reaction(onto.search_one(iri = '*SBO_0000176')): pass
    class Protein_Catalysed_Reaction(Bio_Catalysed_Reaction): pass
    class Abzymatic_Reaction(Protein_Catalysed_Reaction): pass
    class Enzymatic_Reaction(Protein_Catalysed_Reaction): pass
    class NucleicAcid_Catalysed_Reaction(Bio_Catalysed_Reaction):pass
    
    class Has_Reaction_ID(Bio_Catalysed_Reaction >> str): pass

# SBO_0000200 = redox reaction subclass of SBO_0000176 = biochemical recation
# redox reaction als subclass von Enzymatic_Reaction(Protein_Catalysed_Reaction) verschieben?
    class Oxidoreductase_Reaction(Enzymatic_Reaction): pass 
    class Transferase_Reaction(Enzymatic_Reaction): pass
    class Hydrolyse_Reaction(Enzymatic_Reaction): pass
    class Lyase_Reaction(Enzymatic_Reaction): pass
    class Isomerase_Reaction(Enzymatic_Reaction): pass
    class Ligase_Reaction(Enzymatic_Reaction): pass

ABTS_Oxidation = Oxidoreductase_Reaction(Reaction_Name)
ABTS_Oxidation.Has_Reaction_ID.append(Reaction_ID)

with onto: 
# SBO_0000460 = enzymatic catalyst
# subclass of 'catalyst', subclass of 'stimulator', subclass of 'modifier'
    class Oxidoreductase(onto.search_one(iri = '*SBO_0000460')): pass
    class Transferase(onto.search_one(iri = '*SBO_0000460')): pass
    class Hydrolyse(onto.search_one(iri = '*SBO_0000460')): pass
    class Lyase(onto.search_one(iri = '*SBO_0000460')): pass
    class Isomerase(onto.search_one(iri = '*SBO_0000460')): pass
    class Ligase(onto.search_one(iri = '*SBO_0000460')): pass

    class catalyses(onto.search_one(iri = '*SBO_0000460') >> Enzymatic_Reaction): pass

    class Oxidoreductase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(Oxidoreductase_Reaction)]
    class Transferase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(Transferase_Reaction)]
    class Hydrolyse(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(Hydrolyse_Reaction)]
    class Lyase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(Lyase_Reaction)]
    class Isomerase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(Isomerase_Reaction)]
    class Ligase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(Ligase_Reaction)]
        
# SBO_0000003 = participant role
# subclass of 'occurring entity representation'
# metaclass of 'modifier'
    class Has_Stoichometric_Coeff(onto.search_one(iri = '*SBO_0000003') >> float): pass

Laccase = Oxidoreductase(protein.name)
# Subtrate = SBO_0000015, subclass of 'participant role'
ABTS_red = (onto.search_one(iri = '*SBO_0000015'))('ABTS_red')
# Product = SBO_0000011, subclass of 'participant role'
ABTS_ox = (onto.search_one(iri = '*SBO_0000011'))('ABTS_ox')
Water = (onto.search_one(iri = '*SBO_0000011'))('Water')
Oxygen = (onto.search_one(iri = '*SBO_0000015'))('Oxygen')

Laccase.Has_Stoichometric_Coeff.append(-1.0)
ABTS_red.Has_Stoichometric_Coeff.append(-4.0)
ABTS_ox.Has_Stoichometric_Coeff.append(4.0)
Water.Has_Stoichometric_Coeff.append(2.0)
Oxygen.Has_Stoichometric_Coeff.append(-1.0)

with onto:
# SBO_0000651 = irreversible process, subclass of 'process'   
    class Has_Direct_OrderCoeff(onto.search_one(iri ='*SBO_0000651') >> float): pass

# SBO_0000650 = reversible process, subclass of 'process' 
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

# Reactiontypes, which are supported in DWSIM
with onto:    
    class ReactionType(onto.search_one(iri = '*ChemicalReaction')): pass
    class Conversion(ReactionType): pass
    class Equbrilium(ReactionType): pass
    class Arrhenius_Kinetic(ReactionType): pass
    class Heterogeneous_Catalytic(ReactionType): pass
    class User_Defined_Reaction(ReactionType): pass
    class Michaelis_Menten_Kinetic(User_Defined_Reaction): pass
    class KM(Michaelis_Menten_Kinetic): pass
    class kCAT(Michaelis_Menten_Kinetic): pass

    class has_KM_Value(KM >> float): pass
    class has_KM_Unit(KM >> str): pass
    class has_kCAT_Value(kCAT >> float): pass
    class has_kCAT_Unit(kCAT >> str): pass

KM_ABTS_ox = KM('KM_ABTS_ox')
kCAT_ABTS_ox = kCAT('kCAT_ABTS_ox')
KM_ABTS_ox.has_KM_Value.append(0.2)
kCAT_ABTS_ox.has_kCAT_Value.append(1.67)
KM_ABTS_ox.has_KM_Unit.append('mmol/l')
kCAT_ABTS_ox.has_kCAT_Unit.append('1/s')


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
# SBO_0000460 = enzymatic catalyst
    class p0(onto.search_one(iri ='*SBO_0000460')): pass
    class p1(onto.search_one(iri ='*SBO_0000460')): pass

# ABTS oxidation in SCR
Laccase = p1('Laccase')
ABTS_red = s3('ABTS_red')
ABTS_ox = s5('ABTS_ox')
Oxygen = s4('Oxygen')

with onto:
# SBO_0000460 = enzymatic catalyst (Laccase = Protein = ontology=<SBOTerm.PROTEIN: 'SBO:0000252' -> nicht hinterlegt)
    class Has_Sequence((onto.search_one(iri = '*SBO_0000460')) >> str): pass                  
    class Has_Source_Organism((onto.search_one(iri = '*SBO_0000460')) >> str): pass
    class Has_EC_Number((onto.search_one(iri = '*SBO_0000460')) >> str): pass     
    class Has_UniProt_ID((onto.search_one(iri = '*SBO_0000460')) >> str): pass
    class Has_Const_Concentration((onto.search_one(iri = '*SBO_0000460')) >> bool or (onto.search_one(iri ='*SBO_0000015')) >> bool or (onto.search_one(iri ='*SBO_0000011')) >> bool): pass
        
Laccase.Has_Sequence.append(Protein_Sequence)
Laccase.Has_Source_Organism.append(Protein_Organism)
Laccase.Has_EC_Number.append(Protein_EC_Number)
Laccase.Has_UniProt_ID.append('D2CSE5')
Laccase.Has_Const_Concentration.append(Protein_Constant)        

with onto:
    class Reaction_Conditions(onto.search_one(iri = '*ChemicalReaction')): pass
    class Temperature(Reaction_Conditions): pass
    class pH(Reaction_Conditions): pass
    class Pressure(Reaction_Conditions): pass
    class Solvent(Reaction_Conditions): pass
    class ReactionRate(Reaction_Conditions): pass

    class has_Temperature_Value(Temperature >> float): pass
    class has_pH_Value(pH >> float): pass
    class has_Pressure_Value(Pressure >> float):pass
    # fluid rate schon in Ontochem
    class has_Rate_Value(ReactionRate >> float): pass
    class has_Temperature_Unit(Temperature >> str): pass
    class has_Pressure_Unit(Pressure >> str): pass
    class has_Fluid_Rate_Unit(ReactionRate >> str): pass

Temperature.has_Temperature_Value.append(Temperature_Value)
pH.has_pH_Value.append(pH_Value)
Pressure.has_Pressure_Value.append(1.013)

Temperature.has_Temperature_Unit.append(Temperature_Unit)
Pressure.has_Pressure_Unit.append('bar')

with onto:
    class ProcessFlowDiagram(Thing): pass
# ontochem class 'chemical material staged' includes input and output flow
    #class MaterialFlow(ProcessFlowDiagram): pass
    #class InletFlow(MaterialFlow): pass
    #class OutletFlow(MaterialFlow): pass
# ontochem class 'Device'
    #class Equipment(ProcessFlowDiagram): pass
    class Reactor(onto.search_one(iri = '*Device')): pass
    class Reactortype(Reactor): pass
    
    class Has_Volume_Value(onto.search_one(iri = '*Device') >> float): pass
    class Has_Volume_Unit(onto.search_one(iri = '*Device') >> str): pass
    
    class Has_Lenght_Value(onto.search_one(iri = '*Device')>> float): pass
    class Has_Lenght_Unit(onto.search_one(iri = '*Device') >> str): pass
    class Has_Compound_MolarFlow(onto.search_one(iri = '*ChemicalMaterialStaged') >> float): pass       
        
SCR = Reactortype(Vessel_Name)
HTR = Reactortype('Helical_tube_reactor')

SCR.Has_Volume_Value.append(Vessel_Volume)
SCR.Has_Volume_Unit.append(Vessel_Unit)
HTR.Has_Volume_Value.append(Vessel_Volume)
HTR.Has_Volume_Unit.append(Vessel_Unit)

# InletFlow comparable with ontochem class 'ChemicalMaterialInput_Manual'
Inlet_Laccase = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('Inlet_Laccase')
Inlet_ABTS_ox = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('Inlet_ABTS_ox')
Inlet_Oxygen = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('Inlet_Oxygen')

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

    class has_a(Institution >> Project): pass
    class is_part_of(Agent >> Institution): pass
    class is_part_of(Engineering_Step >> Project): pass
    class is_part_of(Organisation >> Institution): pass
    class is_part_of(Processsimulation >> Engineering_Step): pass
    class is_part_of(Documentation >> Project): pass

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

    class Experimental_Data_enzmldoc(onto.search_one(iri = '*DPM_Input')): pass
    class Measurement(Experimental_Data_enzmldoc): pass
    # 12 measurements in the ducumentation with different initial concentration values 
    class Initial_Concentration(Measurement): pass
    class Reactant_Initial_Conc(Initial_Concentration): pass
    class Protein_Initial_Conc(Initial_Concentration): pass
   
    class Concentration_Curve(Measurement): pass
    class Reactant_Conc_Curve(Concentration_Curve): pass
    class Protein_Conc_Curve(Concentration_Curve): pass
    class Absorption(Measurement): pass
    class Time_Measurement(Measurement): pass

with onto:
    sync_reasoner()
    
    
onto.save("02_OntoChemSBO_myOnto.owl") 