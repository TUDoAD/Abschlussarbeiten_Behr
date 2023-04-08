# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 13:22:09 2023

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
   
    reacV = Vessel_Volume*1e-7
    
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
    class BiochamicalSubstance(onto.search_one(iri = '*ChemicalSubstance')): pass
   
# available components (or compounds): DWSIM comes with six default compound databases (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes), with a total of more than 1500 compounds available for your simulation.
    class SubstanceDatabase(onto.search_one(iri = '*ChemicalSubstance')): pass
    class DefaultDatabase(SubstanceDatabase): pass
    class DWSIMCompound(DefaultDatabase): pass
    class ChemSep(DefaultDatabase): pass
    class Biodiesel(DefaultDatabase): pass
    class CoolProp(DefaultDatabase): pass
    class ChEDL(DefaultDatabase): pass
    class Electrolytes(DefaultDatabase): pass

    class provides(SubstanceDatabase >> onto.search_one(iri = '*ChemicalSubstance')): pass

# DWSIM also features full compound data importing from Online Sources or from JSON files or XML files
# additionally a User can create own compounds via Compound Creator
    class DeviantingDatabase(SubstanceDatabase): pass
    class OnlineSource(DeviantingDatabase): pass
    class UserDefinedCompound(DeviantingDatabase): pass

    class creates(UserDefinedCompound >> DeviantingDatabase): pass

# to add own compounds, save them in 'addcomps' file as JSON or XML file
    class AddCompoundFile(UserDefinedCompound): pass      
    class XMLfile(AddCompoundFile): pass
    class JSONfile(AddCompoundFile): pass
    
    class mustInclude(AddCompoundFile >> UserDefinedCompound): pass

    class Laccase(JSONfile): pass
    class ABTS_red(JSONfile): pass
    class ABTS_ox(JSONfile): pass

    class isImportedAs(Laccase >> JSONfile): pass
    class isImportedAs(ABTS_red >> JSONfile): pass
    class isImportedAs(ABTS_ox >> JSONfile): pass

    class Water(DWSIMCompound): pass
    class Oxygen(DWSIMCompound): pass

    class existsAs(Water >> DWSIMCompound): pass
    class existsAs(Water >> DWSIMCompound): pass
        
Substrate_Name = 'ABTS_red'
Reactant_Water = 'Water'
Reactant_Oxy = 'Oxygen'

with onto:
    class ThermodynamicModel(Thing): pass
    class PropertyPackage(ThermodynamicModel): pass
    class ActivityCoefficientModel(PropertyPackage): pass
    class IdealModel(PropertyPackage): pass
    class RaoultsLaw(IdealModel): pass
    class NRTL(ActivityCoefficientModel): pass
    class UNIQUAC(ActivityCoefficientModel): pass
    
    class hasInteractionParameter(ActivityCoefficientModel >> float): pass 

# depending on the selected Property Package, different substance properties must be specified 
    class SubstanceProperty(onto.search_one(iri = '*ChemicalSubstance')): pass

# the following properties are only sufficient if a solid is present that remains a solid
    class hasDWSIM_ID(onto.search_one(iri = '*ChemicalSubstance') >> int): pass
    class hasCAS_Number(onto.search_one(iri = '*ChemicalSubstance') >> str): pass
    class hasSMILES(onto.search_one(iri = '*ChemicalSubstance') >> str): pass
    class hasFormula(onto.search_one(iri = '*ChemicalSubstance') >> str): pass
    class hasMolecularWeight(onto.search_one(iri = '*ChemicalSubstance') >> float): pass

# relevante infos, die man für den compound creator braucht
Laccase.hasDWSIM_ID.append(00000)
Laccase.hasCAS_Number.append('80498-15-3')
Laccase.hasSMILES.append('CC[C@H](C)[C@@H](C(N1CCC[C@H]1C(=O)O)=O)N=C([C@H](CCC(=N)O)N=C([C@H](CCC(=O)O)N=C([C@H](C)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](C(C)C)N=C([C@H](C)N)O)O)O)O)O)O)O)')
Laccase.hasFormula.append('C66H109N19O25')
Laccase.hasMolecularWeight.append(53600) #g/mol

ABTS_red.hasDWSIM_ID.append(10000)
ABTS_red.hasCAS_Number.append('28752-68-3')
ABTS_red.hasSMILES.append('CCN1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_red.hasFormula.append('C18H18N4O6S4')
ABTS_red.hasMolecularWeight.append(514.619) #g/mol

ABTS_ox.hasDWSIM_ID.append(20000)
ABTS_ox.hasCAS_Number.append('28752-68-3')
ABTS_ox.hasSMILES.append('CC[N+]1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_ox.hasFormula.append('C18H17N4O6S4')
ABTS_ox.hasMolecularWeight.append(513.619) #g/mol

# Substance propoperties in DWSIM - wichtig, um substanz zu definieren und zu speichern
with onto:
    class hasCurveForVaporPressure(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasIdealGasHeatCapacity(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasCriticalCompressibility(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasCriticalPressure(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasCriticalTemperature(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasCriticalVolume(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasNormalBoilingPoint(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasAcentricFactor(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasChaoSeaderAcentricity(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasChaoSeaderLiquidMolarVolume(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasChaoSeaderSolubilityParameter(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasIG_EnthalpyOfFormation25C(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasIG_EntropyOfFormation25C(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasIG_GibbsEnergyOfFormation25C(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    
    class hasWaterSolubilityValue(onto.search_one(iri = '*ChemicalSubstance') >> float): pass
    class hasWaterSolubilityValueUnit(onto.search_one(iri = '*ChemicalSubstance') >> str): pass

    class isBlackOil(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class isCoolPropSupported(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class isF_PropsSupported(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class isHydratedSalt(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class isIon(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class isModified(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class isSalt(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass
    class isSolid(onto.search_one(iri = '*ChemicalSubstance') >> bool): pass

ABTS_red.hasWaterSolubilityValue.append(50.0)
ABTS_red.hasWaterSolubilityValueUnit.append('g/l')

Laccase.isBlackOil.append(False)
ABTS_red.isBlackOil.append(False)
ABTS_ox.isBlackOil.append(False)

Laccase.isCoolPropSupported.append(False)
ABTS_red.isCoolPropSupported.append(False)
ABTS_ox.isCoolPropSupported.append(False)

Laccase.isF_PropsSupported.append(False)
ABTS_red.isF_PropsSupported.append(False)
ABTS_ox.isF_PropsSupported.append(False)

Laccase.isHydratedSalt.append(False)
ABTS_red.isHydratedSalt.append(False)
ABTS_ox.isHydratedSalt.append(False)

Laccase.isIon.append(False)
ABTS_red.isIon.append(False)
ABTS_ox.isIon.append(False)

Laccase.isModified.append(False)
ABTS_red.isModified.append(False)
ABTS_ox.isModified.append(False)

Laccase.isSalt.append(False)
ABTS_red.isSalt.append(False)
ABTS_ox.isSalt.append(False)

Laccase.isSolid.append(False)
ABTS_red.isSolid.append(False)
ABTS_ox.isSolid.append(False)

with onto:
    # ontochem includes a class chemical reaction
    # SBO_0000176 = biochemical recation
    class BioCatalysedReaction(onto.search_one(iri = '*SBO_0000176')): pass
    class ProteinCatalysedReaction(BioCatalysedReaction): pass
    class AbzymaticReaction(ProteinCatalysedReaction): pass
    class EnzymaticReaction(ProteinCatalysedReaction): pass
    class NucleicAcidCatalysedReaction(BioCatalysedReaction):pass
    
    class hasReaction_ID(BioCatalysedReaction >> str): pass

# SBO_0000200 = redox reaction subclass of SBO_0000176 = biochemical recation
# redox reaction als subclass von Enzymatic_Reaction(Protein_Catalysed_Reaction) verschieben?
    class OxidoreductaseReaction(EnzymaticReaction): pass 
    class TransferaseReaction(EnzymaticReaction): pass
    class HydrolyseReaction(EnzymaticReaction): pass
    class LyaseReaction(EnzymaticReaction): pass
    class IsomeraseReaction(EnzymaticReaction): pass
    class LigaseReaction(EnzymaticReaction): pass

ABTS_Oxidation = OxidoreductaseReaction(Reaction_Name)
ABTS_Oxidation.hasReaction_ID.append(Reaction_ID)

with onto: 
# SBO_0000460 = enzymatic catalyst
# subclass of 'catalyst', subclass of 'stimulator', subclass of 'modifier'
    class Oxidoreductase(onto.search_one(iri = '*SBO_0000460')): pass
    class Transferase(onto.search_one(iri = '*SBO_0000460')): pass
    class Hydrolyse(onto.search_one(iri = '*SBO_0000460')): pass
    class Lyase(onto.search_one(iri = '*SBO_0000460')): pass
    class Isomerase(onto.search_one(iri = '*SBO_0000460')): pass
    class Ligase(onto.search_one(iri = '*SBO_0000460')): pass

    class catalyses(onto.search_one(iri = '*SBO_0000460') >> EnzymaticReaction): pass

    class Oxidoreductase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(OxidoreductaseReaction)]
    class Transferase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(TransferaseReaction)]
    class Hydrolyse(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(HydrolyseReaction)]
    class Lyase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(LyaseReaction)]
    class Isomerase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(IsomeraseReaction)]
    class Ligase(onto.search_one(iri = '*SBO_0000460')):
        is_a = [catalyses.only(LigaseReaction)]
        
# SBO_0000003 = participant role
# subclass of 'occurring entity representation'
# metaclass of 'modifier'
    class hasStoichometricCoeff(onto.search_one(iri = '*SBO_0000003') >> float): pass

# optimum range depends on substrate 
    class has_pH_Optimum(onto.search_one(iri = '*SBO_0000460') >> str): pass
    class hasTempOptimum(onto.search_one(iri = '*SBO_0000460') >> str): pass

#Laccase = Oxidoreductase(protein.name)
# Subtrate = SBO_0000015, subclass of 'participant role'
#ABT_Sred = (onto.search_one(iri = '*SBO_0000015'))('ABTS_red')
# Product = SBO_0000011, subclass of 'participant role'
#ABTS_ox = (onto.search_one(iri = '*SBO_0000011'))('ABTS_ox')
#Water = (onto.search_one(iri = '*SBO_0000011'))('Water')
#Oxygen = (onto.search_one(iri = '*SBO_0000015'))('Oxygen')

Laccase.has_pH_Optimum.append('4.5-5.0 with ABTS as substrate')
Laccase.hasTempOptimum.append('35-55 °C with ABTS as substrate')

Laccase.hasStoichometricCoeff.append(0.000758287)
stoichL = Laccase.hasStoichometricCoeff

ABTS_red.hasStoichometricCoeff.append(-4.0)
stoichAR = ABTS_red.hasStoichometricCoeff

ABTS_ox.hasStoichometricCoeff.append(4.0)
stoichAO = ABTS_ox.hasStoichometricCoeff

Water.hasStoichometricCoeff.append(2.0)
stoichW = Water.hasStoichometricCoeff

Oxygen.hasStoichometricCoeff.append(-1.0)
stoichO = Oxygen.hasStoichometricCoeff

with onto:
# SBO_0000651 = irreversible process, subclass of 'process'   
    class hasDirectOrderCoeff(onto.search_one(iri ='*SBO_0000651') >> float): pass

# SBO_0000650 = reversible process, subclass of 'process' 
    class hasReverseOrderCoeff(onto.search_one(iri ='*SBO_0000651') >> float): pass

Laccase.hasDirectOrderCoeff.append(0.0)
DorderL = Laccase.hasDirectOrderCoeff

ABTS_red.hasDirectOrderCoeff.append(1.0) #basic compound
DorderAR = ABTS_red.hasDirectOrderCoeff

ABTS_ox.hasDirectOrderCoeff.append(0.0)
DorderAO = ABTS_ox.hasDirectOrderCoeff

Water.hasDirectOrderCoeff.append(0.0)
DorderW = Water.hasDirectOrderCoeff

Oxygen.hasDirectOrderCoeff.append(0.0)
DorderO = Oxygen.hasDirectOrderCoeff

Laccase.hasReverseOrderCoeff.append(0.0)
RorderL = Laccase.hasReverseOrderCoeff

ABTS_red.hasReverseOrderCoeff.append(0.0)
RorderAR = ABTS_red.hasReverseOrderCoeff

ABTS_ox.hasReverseOrderCoeff.append(0.0)
RorderAO = ABTS_ox.hasReverseOrderCoeff

Water.hasReverseOrderCoeff.append(0.0)
RorderW = Water.hasReverseOrderCoeff

Oxygen.hasReverseOrderCoeff.append(0.0)
RorderO = Oxygen.hasReverseOrderCoeff

# Reactiontypes, which are supported in DWSIM
with onto:    
    class ReactionType(onto.search_one(iri = '*ChemicalReaction')): pass
    class Conversion(ReactionType): pass
    class Equbrilium(ReactionType): pass
    class Arrhenius_Kinetic(ReactionType): pass
    class Heterogeneous_Catalytic(ReactionType): pass
    class UserDefinedReaction(ReactionType): pass
    class MichaelisMentenKinetic(UserDefinedReaction): pass
    class Km(MichaelisMentenKinetic): pass
    class kcat(MichaelisMentenKinetic): pass

    class hasKmValue(Km >> float): pass
    class hasKmUnit(Km >> str): pass
    class has_kcatValue(kcat >> float): pass
    class has_kcatUnit(kcat >> str): pass

Km_Laccase = Km('Km_Laccase')
kcat_Laccase = kcat('kcat_Laccase')

Km_Laccase.hasKmValue.append(0.2)
Km_Laccase.hasKmUnit.append('mmol/l')

kcat_Laccase.has_kcatValue.append(1.67)
kcat_Laccase.has_kcatUnit.append('1/s')


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
    class p0(Oxidoreductase): pass
    class p1(Oxidoreductase): pass


with onto:
# SBO_0000460 = enzymatic catalyst (Laccase = Protein = ontology=<SBOTerm.PROTEIN: 'SBO:0000252' -> nicht hinterlegt)
    class hasSequence((onto.search_one(iri = '*SBO_0000460')) >> str): pass                  
    class hasSourceOrganism((onto.search_one(iri = '*SBO_0000460')) >> str): pass
    class hasECnumber((onto.search_one(iri = '*SBO_0000460')) >> str): pass     
    class hasUniProt_ID((onto.search_one(iri = '*SBO_0000460')) >> str): pass
    class hasConstConcentration((onto.search_one(iri = '*SBO_0000460')) >> bool or (onto.search_one(iri ='*SBO_0000015')) >> bool or (onto.search_one(iri ='*SBO_0000011')) >> bool): pass
        
Laccase.hasSequence.append(Protein_Sequence)
Laccase.hasSourceOrganism.append(Protein_Organism)
Laccase.hasECnumber.append(Protein_EC_Number)
Laccase.hasUniProt_ID.append('D2CSE5')
Laccase.hasConstConcentration.append(Protein_Constant)        

with onto:
    class ReactionConditions(onto.search_one(iri = '*ChemicalReaction')): pass
    class Temperature(ReactionConditions): pass
    class pH(ReactionConditions): pass
    class Pressure(ReactionConditions): pass
    class Solvent(ReactionConditions): pass
    class ReactionRate(ReactionConditions): pass

    class hasTemperatureValue(Temperature >> float): pass
    class has_pH_Value(pH >> float): pass
    class hasPressureValue(Pressure >> float):pass
    # fluid rate schon in Ontochem
    class hasRateValue(ReactionRate >> float): pass
    class hasTemperatureUnit(Temperature >> str): pass
    class hasPressureUnit(Pressure >> str): pass
    class hasFluidRateUnit(ReactionRate >> str): pass

Temperature.hasTemperatureValue.append(Temperature_Value)
pH.has_pH_Value.append(pH_Value)
Pressure.hasPressureValue.append(1.013)

Temperature.hasTemperatureUnit.append(Temperature_Unit)
Pressure.hasPressureUnit.append('bar')

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
    
    class hasVolumeValue(onto.search_one(iri = '*Device') >> float): pass
    class hasVolumeUnit(onto.search_one(iri = '*Device') >> str): pass
    
    class hasLengthValue(onto.search_one(iri = '*Device')>> float): pass
    class hasLengthUnit(onto.search_one(iri = '*Device') >> str): pass
    class hasCompoundMolarFlow(onto.search_one(iri = '*ChemicalMaterialStaged') >> float): pass       
        
SCR = Reactortype(Vessel_Name)
HTR = Reactortype('HelicalTubeReactor')

SCR.hasVolumeValue.append(reacV)
SCR.hasVolumeUnit.append('m^3')
HTR.hasVolumeValue.append(reacV)
HTR.hasVolumeUnit.append('m^3')

reacL = 0.0001

SCR.hasLengthValue.append(reacL)
SCR.hasLengthUnit.append('m')
HTR.hasLengthValue.append(reacL)
HTR.hasLengthUnit.append('m')

# InletFlow comparable with ontochem class 'ChemicalMaterialInput_Manual'
InletLaccase = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('InletLaccase')
InletABTS_red = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('InletABTS_red')
InletOxygen = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('InletOxygen')

InletLaccase.hasCompoundMolarFlow.append(1.340625e-7) # mol/s
InletABTS_red.hasCompoundMolarFlow.append(0.08083) # mol/s
InletOxygen.hasCompoundMolarFlow.append(9.67e-10) # mol/s

with onto:
    class Project(Thing): pass
    class Institution(Project): pass
    class Agent(Institution): pass         
    class Engineering_Step(Project): pass # Basic Engineering, Detail Engineering
    class Processdesign(Engineering_Step): pass
    class Processsimulation(Processdesign): pass
    class Documentation(Project): pass

    class receives(Institution >> Project): pass
    class isEmployedAt(Agent >> Institution): pass
    class executes(Agent >> Project): pass
    class isDividedInto(Engineering_Step >> Project): pass
    class is_a(Processsimulation >> Engineering_Step): pass
    class saves(Documentation >> Project): pass

    class hasProjectstart(Project >> str): pass
 
    class ElectronicLabNotebook(Documentation): pass
    class EnzymeML_Documentation(ElectronicLabNotebook): pass

    #class Has_Projectstart(Project >> datetime.date): pass  
    class hasTitel(EnzymeML_Documentation >> str): pass
    class hasCreator(EnzymeML_Documentation >> str): pass
    class hasCreatorMail(Agent >> str): pass
    #class Has_Date_of_Creation(EnzymeML_Documentation >> datetime.date): pass
    class hasDateOfCreation(EnzymeML_Documentation >> str): pass

ABTSOxidationbyLaccase = Project('ABTS_OxidationByLaccase')
Chair_of_EquipmentDesign = Institution('TU_Dortmund_ChairOfEquipmentDesign')
EnzymeML_Document1 = EnzymeML_Documentation('EnzymeML_Document1')
Agent1 = Agent('Abbaspour')

EnzymeML_Document1.hasTitel.append(enzmldoc.name)
EnzymeML_Document1.hasCreator.append(Creator_Familyname)
EnzymeML_Document1.hasCreatorMail.append(Creator_Mail)
EnzymeML_Document1.hasDateOfCreation.append(enzmldoc.created)

with onto:
    class Stabilizer(onto.search_one(iri = '*SBO_0000594')): pass
    class hasStabilizerConcentration(onto.search_one(iri = '*SBO_0000594') >> float): pass

    class ExperimentalDataEnzmldoc(onto.search_one(iri = '*DPM_Input')): pass
    class Measurement(ExperimentalDataEnzmldoc): pass
    # 12 measurements in the ducumentation with different initial concentration values 
    class InitialConcentration(Measurement): pass
    class ReactantInitialConc(InitialConcentration): pass
    class ProteinInitialConc(InitialConcentration): pass
   
    class ConcentrationCurve(Measurement): pass
    class ReactantConcCurve(ConcentrationCurve): pass
    class ProteinCon_Curve(ConcentrationCurve): pass
    class Absorption(Measurement): pass
    class TimeMeasurement(Measurement): pass

with onto:
    sync_reasoner()
    
onto.save("05_OntoChemSBO_myOnto.owl", format="rdfxml")

import os

import pythoncom
pythoncom.CoInitialize()
import clr
import System

from System.IO import Directory, Path, File
from System import String, Environment
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\49157\\AppData\\Local\\DWSIM8\\"

clr.AddReference(dwsimpath + "DWSIM")
clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")
clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "System.Buffers.dll")

clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
clr.AddReference(dwsimpath + "Newtonsoft.Json")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

from System import *
from System.Linq import *
from DWSIM import *
from DWSIM import FormPCBulk
 
from DWSIM.Interfaces import *
from DWSIM.Interfaces.Enums import*
from DWSIM.Interfaces.Enums.GraphicObjects import *
from Newtonsoft.Json import JsonConvert, Formatting

from DWSIM.Thermodynamics import*
from DWSIM.Thermodynamics.BaseClasses import *
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import *
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization import GenerateCompounds
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization.Methods import *

Directory.SetCurrentDirectory(dwsimpath)

# Create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

# Add compounds 
sim.AddCompound("Laccase")
sim.AddCompound("ABTS_ox")
sim.AddCompound("ABTS_red")
sim.AddCompound("Water")
sim.AddCompound("Oxygen")

# Stoichiometric coefficients
comps = Dictionary[str, float]()
comps.Add("Laccase", stoichL[0]);
comps.Add("Water", stoichW[0]);
comps.Add("Oxygen", stoichO[0]);
comps.Add("ABTS_ox", stoichAO[0]);
comps.Add("ABTS_red", stoichAR[0]);

# Direct order coefficients
dorders = Dictionary[str, float]()
dorders.Add("Laccase", DorderL[0]);
dorders.Add("Water", DorderW[0]);
dorders.Add("Oxygen", DorderO[0]);
dorders.Add("ABTS_ox", DorderAO[0]);
dorders.Add("ABTS_red", DorderAR[0]);

# Reverse order coefficients
rorders = Dictionary[str, float]()
rorders.Add("Laccase", RorderL[0]);
rorders.Add("Water", RorderW[0]);
rorders.Add("Oxygen", RorderO[0]);
rorders.Add("ABTS_ox", RorderAO[0]);
rorders.Add("ABTS_red",RorderAR[0]);

kr1 = sim.CreateKineticReaction("ABTS Oxidation", "ABTS Oxidation using Laccase", 
        comps, dorders, rorders, "ABTS_red", "Mixture", "Molar Concentration", 
        "kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")

# Add all objects
m1 = sim.AddObject(ObjectType.MaterialStream, 0, 10, "Oxygen")
m2 = sim.AddObject(ObjectType.MaterialStream, 0, 60, "ABTS_red")
m3 = sim.AddObject(ObjectType.MaterialStream, 100, 50, "Mixture")
m4 = sim.AddObject(ObjectType.MaterialStream, 250, 50, "Product")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 90, "Heat")
pfr = sim.AddObject(ObjectType.RCT_PFR, 150, 50, "PFR")
MIX1 = sim.AddObject(ObjectType.Mixer, 50, 50, "Mixer")

m1 = m1.GetAsObject()
m2 = m2.GetAsObject()
m3 = m3.GetAsObject()
m4 = m4.GetAsObject()
e1 = e1.GetAsObject()
MIX1 = MIX1.GetAsObject()
pfr = pfr.GetAsObject()

# Connect the inlet streams
sim.ConnectObjects(m1.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(MIX1.GraphicObject, m3.GraphicObject, -1, -1)

pfr.ConnectFeedMaterialStream(m3, 0)
pfr.ConnectProductMaterialStream(m4, 0)
pfr.ConnectFeedEnergyStream(e1, 1)

# PFR properties (fix pressure drop inside reactor)
pfr.ReactorOperationMode = Reactors.OperationMode.Isothermic
pfr.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length

pfr.Volume = reacV #0.000008m3
pfr.Length = reacL #0.0001m


# Set Property Package
sim.CreateAndAddPropertyPackage("Raoult's Law")

m1.SetTemperature(Temperature_Value) # Kelvin
m2.SetTemperature(Temperature_Value) # Kelvin
m3.SetTemperature(Temperature_Value) # Kelvin
m4.SetTemperature(Temperature_Value) # Kelvin

m1.SetVolumetricFlow(5e-08)# will set by compound
m2.SetVolumetricFlow(8.33333e-08)

m1.SetOverallCompoundMolarFlow("Oxygen", 1.340625e-7) # mol/s
m1.SetOverallCompoundMolarFlow("ABTS_red", 0.0)  # mol/s
m1.SetOverallCompoundMolarFlow("Laccase",0.0)

m2.SetOverallCompoundMolarFlow("Oxygen", 0.0) # mol/s
m2.SetOverallCompoundMolarFlow("ABTS_red", 0.08083) # mol/s
m2.SetOverallCompoundMolarFlow("Laccase",9.67e-10) # mol/s

sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", True, 0)

# request a calculation

errors = interf.CalculateFlowsheet4(sim);

print("Reactor Heat Load: {0:.4g} kW".format(pfr.DeltaQ))
for c in pfr.ComponentConversions:
    if (c.Value > 0): print("{0} conversion: {1:.4g}%".format(c.Key, c.Value * 100.0))

if (len(errors) > 0):
    for e in errors:
        print("Error: " + e.ToString())

# reactor profiles (temperature, pressure and concentration)
coordinates = [] # volume coordinate in m3
names = [] # compound names
values = [] # concentrations in mol/m3 (0 to j, j = number of compounds - 1), temperature in K (j+1), pressure in Pa (j+2)

for p in pfr.points:
    coordinates.append(p[0])

for j in range(1, pfr.ComponentConversions.Count + 3):
    list1 = []
    for p in pfr.points:
        list1.append(p[j])
    values.append(list1)

for k in pfr.ComponentConversions.Keys:
    names.append(k)

# save file
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), 
                              "09_ABTS Oxidation plus Onto.dwxmz")
interf.SaveFlowsheet(sim, fileNameToSave, True)

# save the pfd to an image and display it
clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

PFDSurface = sim.GetSurface()
bmp = SKBitmap(1000, 600)
canvas = SKCanvas(bmp)
canvas.Scale(0.5)
PFDSurface.ZoomAll(bmp.Width, bmp.Height)
PFDSurface.UpdateCanvas(canvas)
d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
str = MemoryStream()
d.SaveTo(str)
image = Image.FromStream(str)
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "09_ABTS Oxidation.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image
im = Image.open(imgPath)
im.show()