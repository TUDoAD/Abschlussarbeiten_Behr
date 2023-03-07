# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:12:33 2023

@author: 49157
"""

# File create_onto.py
from owlready2 import *
 
onto = get_ontology("http://www.semanticweb.org/49157/ontologies/2023/02/Class_Hierarchy#")
owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

with onto:
    class Substance(Thing): pass
    class Chemical_Substance(Substance): pass
    class Biological_Substance(Substance): pass

    class is_a(Chemical_Substance >> Substance): pass
    class is_a(Biological_Substance >> Substance): pass
    
# available components (or compounds): DWSIM comes with six default compound databases (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes), with a total of more than 1500 compounds available for your simulation.
    class Default_Substance_Database(Substance): pass
    class DWSIM_Compounds(Default_Substance_Database): pass
    class ChemSep(Default_Substance_Database): pass
    class Biodiesel(Default_Substance_Database): pass
    class CoolProp(Default_Substance_Database): pass
    class ChEDL(Default_Substance_Database): pass
    class Electrolytes(Default_Substance_Database): pass

    class is_a(DWSIM_Compounds >> Default_Substance_Database): pass
    class is_a(ChemSep >> Default_Substance_Database): pass
    class is_a(Biodiesel >> Default_Substance_Database): pass
    class is_a(CoolProp >> Default_Substance_Database): pass
    class is_a(ChEDL >> Default_Substance_Database): pass
    class is_a(Electrolytes >> Default_Substance_Database): pass


# DWSIM also features full compound data importing from Online Sources or from JSON files or XML files
# additionally a User can create own compounds via Compound Creator
    class Devianting_Database(Substance): pass
    class Online_Source(Devianting_Database): pass
    class User_Defined_Compounds(Devianting_Database): pass
    
    class is_part_of(Online_Source >> Devianting_Database): pass
    class is_part_of(User_Defined_Compounds >> Devianting_Database): pass
    
    class XML_file(User_Defined_Compounds): pass
    class JSON_file(User_Defined_Compounds): pass
    
    class is_a(XML_file >> User_Defined_Compounds): pass
    class is_a(JSON_file >> User_Defined_Compounds): pass

# too add own compounds, save them in 'addcomps' file as JSON or XML file
    class AddCompound_file(User_Defined_Compounds): pass
    class contains(AddCompound_file >> User_Defined_Compounds): pass
    
    class contains(Default_Substance_Database >> Substance): pass
    class contains(Devianting_Database >> Substance): pass

Laccase = User_Defined_Compounds('Laccase') #später über EnzymeML Dokument reinladen
ABTS_red = User_Defined_Compounds('ABTS_red')
ABTS_ox = User_Defined_Compounds('ABTS_ox')
Water = DWSIM_Compounds('Water')
Oxygen = DWSIM_Compounds('Oxygen')

#with onto:
#    sync_reasoner()

with onto:
    class Thermodynamic_Model(Thing): pass
    class PropertyPackage(Thermodynamic_Model): pass
    class Activity_Coefficient_Model(PropertyPackage): pass
    class Ideal_Model(PropertyPackage): pass
    class RaoultsLaw(Ideal_Model): pass
    class NRTL(Activity_Coefficient_Model): pass
    class UNIQUAC(Activity_Coefficient_Model): pass
    
    class is_composed_of_a(PropertyPackage >> Thermodynamic_Model): pass
    class is_a(RaoultsLaw >> Ideal_Model): pass
    class is_a(NRTL >> Activity_Coefficient_Model) : pass
    class is_a(UNIQUAC >> Activity_Coefficient_Model) : pass

    class InteractionParameter(Activity_Coefficient_Model): pass #Wieviele Interactionsparameter und welche braicht DWSIM?

# depending on the selected Property Package, different substance properties must be specified 
    class Substance_Property(Substance): pass
    class Substancename(Substance_Property): pass

    class is_a(Substancename >> Substance_Property): pass

# the following properties are only sufficient if a solid is present that remains a solid
    class Has_ID(Substance_Property >> int): pass
    class Has_CAS_Number(Substance_Property >> str): pass
    class Has_SMILES(Substance_Property >> str): pass
    class Has_Formula(Substance_Property >> str): pass
    class Has_Molecular_Weight(Substance_Property >> float): pass

Laccase.Has_ID.append(00000)
Laccase.Has_CAS_Number.append('80498-15-3')
Laccase.Has_SMILES.append('CC[C@H](C)[C@@H](C(N1CCC[C@H]1C(=O)O)=O)N=C([C@H](CCC(=N)O)N=C([C@H](CCC(=O)O)N=C([C@H](C)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](C(C)C)N=C([C@H](C)N)O)O)O)O)O)O)O)')
Laccase.Has_Formula.append('C66H109N19O25')
Laccase.Has_Molecular_Weight.append(1072.08)

ABTS_red.Has_ID.append(10000)
ABTS_red.Has_CAS_Number.append('28752-68-3')
ABTS_red.Has_SMILES.append('CCN1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_red.Has_Formula.append('C18H18N4O6S4')
ABTS_red.Has_Molecular_Weight.append(514.619)

ABTS_ox.Has_ID.append(20000)
ABTS_ox.Has_CAS_Number.append('28752-68-3')
ABTS_ox.Has_SMILES.append('CC[N+]1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_ox.Has_Formula.append('C18H17N4O6S4')
ABTS_ox.Has_Molecular_Weight.append(513.619)

with onto:
    
# important properties    
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

    class IsBlackOil(Substance >> bool): pass
    class Is_COOL_PROP_Supported(Substance >> bool): pass
    class Is_F_PROPS_Supported(Substance >> bool): pass
    class Is_Hydrated_Salt(Substance >> bool): pass
    class Is_Ion(Substance >> bool): pass
    class Is_Modified(Substance >> bool): pass
    class Is_Salt(Substance >> bool): pass
    class Is_Solid(Substance >> bool): pass
    
    class Has_Elements(Substance >> str): pass # vlt lieber als Klasse und dann Elemente zuordnen?

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
    class Biochemical_Reaction(Chemical_Reaction): pass
    class Bio_Catalysed_Reaction(Biochemical_Reaction): pass
   
    #https://www.ebi.ac.uk/ols/ontologies/rex/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FREX_0000071&lang=en&viewMode=All&siblings=true
    class Protein_Catalysed_Reaction(Bio_Catalysed_Reaction): pass
    class NucleicAcid_Catalysed_Reaction(Bio_Catalysed_Reaction): pass
    class Abzymatic_Reaction(Protein_Catalysed_Reaction): pass
    class Enzymatic_Reaction(Protein_Catalysed_Reaction): pass

    AllDisjoint([NucleicAcid_Catalysed_Reaction, Protein_Catalysed_Reaction])
    AllDisjoint([Abzymatic_Reaction,Enzymatic_Reaction])

    class is_a(Chemical_Reaction >> Reaction): pass
    class is_a(Biochemical_Reaction >> Chemical_Reaction): pass
    class is_a(Bio_Catalysed_Reaction >> Biochemical_Reaction): pass
    class is_a(NucleicAcid_Catalysed_Reaction >> Bio_Catalysed_Reaction): pass
    class is_a(Protein_Catalysed_Reaction >> Bio_Catalysed_Reaction): pass
    class is_a(Abzymatic_Reaction >> Protein_Catalysed_Reaction): pass
    class is_a(Enzymatic_Reaction >> Protein_Catalysed_Reaction): pass

    class Oxidorecductase_Reaction(Enzymatic_Reaction): pass
    class Transferase_Reaction(Enzymatic_Reaction): pass
    class Hydrolyse_Reaction(Enzymatic_Reaction): pass
    class Lyase_Reaction(Enzymatic_Reaction): pass
    class Isomerase_Reaction(Enzymatic_Reaction): pass
    class Ligase_Reaction(Enzymatic_Reaction): pass

    AllDisjoint([Oxidorecductase_Reaction, Transferase_Reaction, Hydrolyse_Reaction, Lyase_Reaction, Isomerase_Reaction, Ligase_Reaction])    
    AllDifferent([Oxidorecductase_Reaction, Transferase_Reaction, Hydrolyse_Reaction, Lyase_Reaction, Isomerase_Reaction, Ligase_Reaction])
    
    class Reaction_Participant(Reaction): pass
    class Substrate(Reaction_Participant): pass
    class Product(Reaction_Participant): pass
    class Protein(Reaction_Participant): pass
    
    AllDisjoint([Substrate, Product, Protein])
    
    class is_part_of(Reaction_Participant >> Reaction): pass
    class is_a(Substrate >> Reaction_Participant): pass
    class is_a(Product >> Reaction_Participant): pass
    class is_a(Protein >> Reaction_Participant): pass
    
    class Enzyme(Protein): pass
    class Oxidoreductase(Enzyme): pass
    class Transferase(Enzyme): pass
    class Hydrolyse(Enzyme): pass
    class Lyase(Enzyme): pass
    class Isomerase(Enzyme): pass
    class Ligase(Enzyme): pass

    AllDisjoint([Oxidoreductase, Transferase, Hydrolyse, Lyase, Isomerase, Ligase])
    AllDifferent([Oxidoreductase, Transferase, Hydrolyse, Lyase, Isomerase, Ligase])

    class catalyses(Oxidoreductase >> Oxidorecductase_Reaction): pass
    class catalyses(Transferase >> Transferase_Reaction): pass
    #class catalyses(Hydrolyse >> Hydrolyse_Reaction): pass
    #class catalyses(Lyase >> Lyase_Reaction): pass
    #class catalyses(Isomerase >> Isomerase_Reaction): pass
    #class catalyses(Ligase >> Ligase_Reaction): pass
    
    AllDisjoint([catalyses, is_a, is_part_of])

    class Has_Name(Reaction >> str): pass
    class Has_Stoichometric_Coeff(Reaction_Participant >> float): pass

ABTS_Oxidation = Oxidorecductase_Reaction('ABTS_Oxidation')
Laccase = Oxidoreductase('Laccase')
ABTS_red = Substrate('ABTS_red')
ABTS_ox = Product('ABTS_ox')
Water = Product('Water')
Oxygen = Substrate('Oxygen')

Laccase.Has_Stoichometric_Coeff.append(-1.0)
ABTS_red.Has_Stoichometric_Coeff.append(-4.0)
ABTS_ox.Has_Stoichometric_Coeff.append(4.0)
Water.Has_Stoichometric_Coeff.append(2.0)
Oxygen.Has_Stoichometric_Coeff.append(-1.0)

with onto:
    
    # in DWSIM dorders = Dictionary[str, float]() and rorders = Dictionary[str, float]()
    class Irreversible_Reaction(Reaction): pass
    class Has_Direct_OrderCoeff(Irreversible_Reaction >> float): pass
    class Reversible_Reaction(Reaction): pass
    class Has_Reverse_OrderCoeff(Irreversible_Reaction >> float): pass

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
   
    #System of Unit (User Guide)
    
with onto:
    
    class ReactionType(Reaction): pass
    class Conversion(ReactionType): pass
    class Equbrilium(ReactionType): pass
    class Kinetic(ReactionType): pass
    class Heterogeneous(ReactionType): pass
    class User_Defined_Reaction(ReactionType): pass
    class Michaelis_Menten_Kinetic(User_Defined_Reaction): pass
    class KM(Michaelis_Menten_Kinetic): pass
    class kCAT(Michaelis_Menten_Kinetic): pass

    class is_a(Conversion >> Reaction): pass
    class is_a(Equbrilium >> Reaction): pass
    class is_a(Kinetic >> Reaction): pass
    class is_a(Heterogeneous >> Reaction): pass
    class is_a(User_Defined_Reaction >> Reaction): pass
    class is_a(Michaelis_Menten_Kinetic >> User_Defined_Reaction): pass 
    class is_parameter_of(KM >> Michaelis_Menten_Kinetic): pass
    class is_parameter_of(kCAT >> Michaelis_Menten_Kinetic): pass

    class Has_Value(KM >> float or kCAT >> float): pass
    class Has_Value_Unit(KM >> str or kCAT >> str): pass

KM_ABTS_ox = KM('KM_ABTS_ox')
kCAT_ABTS_ox = KM('kCAT_ABTS_ox')
KM_ABTS_ox.Has_Value.append(0.2)
kCAT_ABTS_ox.Has_Value.append(1.67)
KM_ABTS_ox.Has_Value_Unit.append('mmol/l')
kCAT_ABTS_ox.Has_Value_Unit.append('1/s')

with onto:

    # EnzymeML: Documentation of 19 reactants and 19 proteins
    class Modeled_Element(Michaelis_Menten_Kinetic): pass
    class s_0(Modeled_Element): pass
    class s_1(Modeled_Element): pass
    class s_2(Modeled_Element): pass
    class s_3(Modeled_Element): pass
    class s_4(Modeled_Element): pass
    class s_5(Modeled_Element): pass
    class s_6(Modeled_Element): pass
    class s_7(Modeled_Element): pass
    class s_8(Modeled_Element): pass
    class s_9(Modeled_Element): pass
    class s_10(Modeled_Element): pass
    class s_11(Modeled_Element): pass
    class s_12(Modeled_Element): pass
    class s_13(Modeled_Element): pass
    class s_14(Modeled_Element): pass
    class s_15(Modeled_Element): pass
    class s_16(Modeled_Element): pass
    class s_17(Modeled_Element): pass
    class s_18(Modeled_Element): pass
    class s_19(Modeled_Element): pass

    class p_0(Modeled_Element): pass
    class p_1(Modeled_Element): pass
    class p_2(Modeled_Element): pass
    class p_3(Modeled_Element): pass
    class p_4(Modeled_Element): pass
    class p_5(Modeled_Element): pass
    class p_6(Modeled_Element): pass
    class p_7(Modeled_Element): pass
    class p_8(Modeled_Element): pass
    class p_9(Modeled_Element): pass
    class p_10(Modeled_Element): pass
    class p_11(Modeled_Element): pass
    class p_12(Modeled_Element): pass
    class p_13(Modeled_Element): pass
    class p_14(Modeled_Element): pass
    class p_15(Modeled_Element): pass
    class p_16(Modeled_Element): pass
    class p_17(Modeled_Element): pass
    class p_18(Modeled_Element): pass
    class p_19(Modeled_Element): pass

    class is_a(s_0 >> Modeled_Element): pass
    class is_a(s_1 >> Modeled_Element): pass
    class is_a(s_2 >> Modeled_Element): pass
    class is_a(s_3 >> Modeled_Element): pass
    class is_a(s_4 >> Modeled_Element): pass
    class is_a(s_5 >> Modeled_Element): pass
    class is_a(s_6 >> Modeled_Element): pass
    class is_a(s_7 >> Modeled_Element): pass
    class is_a(s_8 >> Modeled_Element): pass
    class is_a(s_9 >> Modeled_Element): pass
    class is_a(s_10 >> Modeled_Element): pass
    class is_a(s_11 >> Modeled_Element): pass
    class is_a(s_12 >> Modeled_Element): pass
    class is_a(s_13 >> Modeled_Element): pass
    class is_a(s_14 >> Modeled_Element): pass
    class is_a(s_15 >> Modeled_Element): pass
    class is_a(s_16 >> Modeled_Element): pass
    class is_a(s_17 >> Modeled_Element): pass
    class is_a(s_18 >> Modeled_Element): pass
    class is_a(s_19 >> Modeled_Element): pass
    class is_a(p_0 >> Modeled_Element): pass
    class is_a(p_1 >> Modeled_Element): pass
    class is_a(p_2 >> Modeled_Element): pass
    class is_a(p_3 >> Modeled_Element): pass
    class is_a(p_4 >> Modeled_Element): pass
    class is_a(p_5 >> Modeled_Element): pass
    class is_a(p_6 >> Modeled_Element): pass
    class is_a(p_7 >> Modeled_Element): pass
    class is_a(p_8 >> Modeled_Element): pass
    class is_a(p_9 >> Modeled_Element): pass
    class is_a(p_10 >> Modeled_Element): pass
    class is_a(p_11 >> Modeled_Element): pass
    class is_a(p_12 >> Modeled_Element): pass
    class is_a(p_13 >> Modeled_Element): pass
    class is_a(p_14 >> Modeled_Element): pass
    class is_a(p_15 >> Modeled_Element): pass
    class is_a(p_16 >> Modeled_Element): pass
    class is_a(p_17 >> Modeled_Element): pass
    class is_a(p_18 >> Modeled_Element): pass
    class is_a(p_19 >> Modeled_Element): pass

Laccase = p_0('Laccase')
ABTS_red = s_0('ABTS_red')
ABTS_ox = s_2('ABTS_ox')
Oxygen = s_1('Oxygen')

# MM-Kinetic: (p_0*kCAT*s_1)/(KM+s_1)

with onto:
    
    class Has_Sequence(Protein >> str): pass
    class Has_Source_Organism(Protein >> str): pass
    class Has_EC_Number(Protein >> str): pass
    class Has_UniProt_ID(Protein >> str): pass
    class Has_Const_Concentration(Protein >> bool or Substrates >> bool or Products >> bool): pass

Laccase.Has_Sequence.append('MGLQRFSFFVTLALVARSLAAIGPVASFVVANAPVSPDGFLRDAIVVNGVVPSPLIRAKKGDRFQLNVVDTLTNHSMLKSTSIHWHGFFQAGTNWADGPAFVNQCPIASGHSFLYDFHVPDQAGTFWYHSHLSTQYCDGLRGPFVVYDPKDPHASRYDVDNESTVITLTDWYHTAARLGPRFPLGADATVINGLGRSASTPTAALAVINVQHGKRYRFRLVSISCDPNYTFSIDGHNLTVIEVDGINSQPLLVDSIQIFAAQRYSFVLNANQTVGNYWVRANPNFGTVGFAGGINSAILRYQGAPVAEPTTTQTPSVIPLIETNLHPLARMPVPGTRTPGGVDKALKLAFNFNGTNFFINNASFTPPTVPVLLQILSGAQTAQELLPAGSVYPLPAHSTIEITLPATALAPGAPHPFHLHGHAFAVVRSAGSTTYNYNDPIFRDVVSTGTPAAGDNVTIRFQTDNLGPWFLHCHIDFHLEAGFAIVFAEDVADVKAANPVPKAWSDLCPIYDGLSEADQ')
Laccase.Has_Source_Organism.append('Trametes versicolor')
Laccase.Has_EC_Number.append('1.10.3.2')
Laccase.Has_UniProt_ID.append('D2CSE5')
Laccase.Has_Const_Concentration.append(True)

with onto:
    
    class Reaction_Property(Reaction): pass
    class Temperature(Reaction_Property): pass
    class pH(Reaction_Property): pass
    class Pressure(Reaction_Property): pass
    class ReactionRate(Reaction): pass

    class is_a(Temperature >> Reaction_Property): pass
    class is_a(pH >> Reaction_Property): pass
    class is_a(Pressure >> Reaction_Property): pass

    class Has_Value(Temperature >> float or pH >> float or Pressure >> float or ReactionRate >> float): pass
    class Has_Value_Unit(Temperature >> str or Pressure >> str or ReactionRate >> str): pass

Temperature.Has_Value.append(38.0)
pH.Has_Value.append(5.2)
Pressure.Has_Value.append(1.013)

Temperature.Has_Value_Unit.append('C')
Pressure.Has_Value_Unit.append('bar')

with onto:
    
    class ProcessFlowDiagram(Thing): pass
    class MaterialFlow(ProcessFlowDiagram): pass
    class InletFlow(MaterialFlow): pass
    class OutletFlow(MaterialFlow): pass
    class Mixture(MaterialFlow): pass
    
    class is_part_of(MaterialFlow >> ProcessFlowDiagram): pass
    class is_a(InletFlow >> MaterialFlow): pass
    class is_a(OutletFlow >> MaterialFlow): pass
    class is_a(Mixture >> MaterialFlow): pass

    class Equipment(ProcessFlowDiagram): pass
    class Reactor(Equipment): pass
    class Reactortype(Reactor): pass

    class is_part_of(Equipment >> ProcessFlowDiagram): pass
    class is_a(Reactor >> Equipment): pass
    class is_a(Reactortype >> Reactor): pass
    
    class Has_Volume_Value(Equipment >> float): pass
    class Has_Volume_Unit(Equipment >> str): pass

SCR = Reactortype('SCR')
HTR = Reactortype('HTR')

SCR.Has_Volume_Value.append(8.0)
SCR.Has_Volume_Unit.append('ml')

HTR.Has_Volume_Value.append(8.0)
HTR.Has_Volume_Unit.append('ml')

with onto:
    
    class Has_Lenght_Value(Equipment>> float): pass
    class Has_Lenght_Unit(Equipment >> str): pass
    class Has_Compound_MolarFlow(MaterialFlow >> float): pass

Inlet_Laccase = InletFlow('Inlet_Laccase')
Inlet_ABTS_ox = InletFlow('Inlet_ABTS_ox')
Inlet_Oxygen = InletFlow('Inlet_Oxygen')

Inlet_Laccase.Has_Compound_MolarFlow.append(1.0) # mol/s
Inlet_ABTS_ox.Has_Compound_MolarFlow.append(1.0) # mol/s
Inlet_Oxygen.Has_Compound_MolarFlow.append(1.0) # mol/s
        
with onto:
    
    class UnitOperation(Thing): pass
    class Mixing(UnitOperation): pass

    class is_a(Mixing >> UnitOperation): pass

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
    class is_a(Processdesign >> Engineering_Step): pass
    class is_part_of(Processsimulation >> Engineering_Step): pass
    class is_part_of(Documentation >> Project): pass

    class Has_Projectstart(Project >> str): pass
 
    class ElectronicLabNotebook(Documentation): pass
    class EnzymeML_Documentation(ElectronicLabNotebook): pass

    class is_a(ElectronicLabNotebook >> Documentation): pass
    class is_a(EnzymeML_Documentation >> ElectronicLabNotebook): pass

    #class Has_Projectstart(Project >> datetime.date): pass  
    class Has_Titel(EnzymeML_Documentation >> str): pass
    class Has_Author(EnzymeML_Documentation >> str): pass
    #class Has_Date_of_Creation(EnzymeML_Documentation >> datetime.date): pass
    class Has_Date_of_Creation(EnzymeML_Documentation >> str): pass

ABTS_Oxidation_by_Laccase = Project('ABTS_Oxidation_by_Laccase')
TU_Dortmund = Institution('TU_Dortmund')
Chair_of_EquipmentDesign = Organisation('Chair_of_EquipmentDesign')
EnzymeML_Document_1 = EnzymeML_Documentation('EnzymeML_Document_1')

ABTS_Oxidation_by_Laccase.Has_Projectstart.append('12.12.2022')

EnzymeML_Document_1.Has_Titel.append('Laccase; Helically Coiled Reactor (HCR) & Straight Capillary Reactor (SCR)')
EnzymeML_Document_1.Has_Author.append('Katrin Rosenthal')
EnzymeML_Document_1.Has_Date_of_Creation.append('18.08.2021')
    
with onto:
    
    class Reaction_Optimization(Thing): pass
    class Stabilizer(Reaction_Optimization): pass
    class Has_Stabilizer_Concentration(Stabilizer >> float): pass

Tween80 = Stabilizer('Tween80') #(Polysorbat 80)
Tween80.Has_Stabilizer_Concentration.append(1.0)

with onto:
    
    class Experimental_Data(EnzymeML_Documentation): pass
    class Measurement(Experimental_Data): pass
    # 12 Messungen im EnzymeML Dokument
    class Concentration_Curve(Measurement): pass # mit Initialkonzentrationswerten für oxygen laccase und red
    class Reactant_Conc_Curve(Concentration_Curve): pass
    class Protein_Conc_Curve(Concentration_Curve): pass
    class Absorption(Measurement): pass
    class Time_Measurement(Measurement): pass

    class is_part_of(Experimental_Data >> EnzymeML_Documentation): pass
    class is_part_of(Measurement >> EnzymeML_Documentation): pass
    class is_a(Concentration_Curve >> Measurement): pass
    class is_a(Reactant_Conc_Curve >> Concentration_Curve): pass
    class is_a(Protein_Conc_Curve >> Concentration_Curve): pass
    class is_a(Absorption >> Measurement): pass
    class is_a(Time_Measurement >> Measurement): pass

Laccase_Conc_Curve = Protein_Conc_Curve('Laccase_Conc_Curve')
ABTS_red_Conc_Curve = Reactant_Conc_Curve('ABTS_red_Conc_Curve')

with onto:
    sync_reasoner()
    
onto.save("Class Hierarchy.owl")    