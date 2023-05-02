# -*- coding: utf-8 -*-
"""
Created on Tue May  2 08:56:34 2023

@author: 49157
"""

# Masterthesis Abbaspour
# Erster Schritt des Ontologiedesigns
# Erstellen einer Klassenhierarchie
# Konzepte überlegen, die EnzymeML-Dokumentation und DWSIM Prozesssimulation wiedergeben

# Owlready2 ist ein Paket zur Bearbeitung von OWL 2.0 Ontologien in Python
# Es kann Ontologien laden, modifizieren, speichern und unterstützt Reasoning über HermiT (enthalten)
from owlready2 import *

# neue Ontologie Laden
onto = get_ontology("http://www.semanticweb.org/49157/ontologies/2023/04/Step1Thesis_Klassenhierarchies#")
owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

# Reasoner HermiT ist in Java geschrieben
# Unter Windows muss der Speicherort des Java-Interpreters wie folgt konfiguriert werden

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"  

# Zunächst die Software DWSIM betrachten
# Welche Daten werden für die Ausführung der Simulation benötigt?

with onto:
    # Wichtig ist das Konzept der Substanzen
    # DWSIM stellt einige Stoffe zur Verfügung
    class Substance(Thing): pass
    
    # Chemische Stoffe und biochemische Stoffe als Subklasse von Substanz
    # Chemical Substance existiert in metadata4Ing: http://www.nfdi.org/nfdi4cat/ontochem#ChemicalSubstance
    class Chemical_Substance(Substance): pass
    class Biochemical_Substance(Chemical_Substance): pass
    class Substance_Database(Substance): pass

    # 'Stoffdatenbak beinhaltet Stoff'
    class provides(Substance_Database >> Substance): pass

   # Komponenten: DWSIM stellt 6 Datenbanken zur verfügung (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes)
   # Daraus ergeben sich 1500 verfügbare Komponenten für die Simulation
   # Datenbanken werden der metadata4Ing Klasse 'ChemicalSubstance' subsumiert
    class Default_Database(Substance_Database): pass
    class DWSIM_Compounds(Default_Database): pass
    class ChemSep(Default_Database): pass
    class Biodiesel(Default_Database): pass
    class CoolProp(Default_Database): pass
    class ChEDL(Default_Database): pass
    class Electrolytes(Default_Database): pass

    # DWSIM bietet die Möhlichkeit Komponenten zu importieren über: Online-Quellen, Json- oder XML_Dateien
    # Zusätzlich kann der User über den 'Compound Creator' Stoffe erstellen
    # So entsteht eine von DWSIM 'abweichende Datenbank'
    class Devianting_Database(Substance_Database): pass
    class Online_Source(Devianting_Database): pass
    class User_Defined_Compound(Devianting_Database): pass

    # Um selbst erstellte Komponenten der Simulation verfügbar zu machen, müssen diese in dem spezifischen Ordner 'addcomps' hinterlegt sein
    # Ordner findet sich unter: "C:\Users\49157\AppData\Local\DWSIM8\addcomps"
    class AddCompound_File(User_Defined_Compound): pass      
    class XML_file(AddCompound_File): pass
    class JSON_file(AddCompound_File): pass

    # 'AddComps Ordner muss user definierte Komponente beinhalten'
    class must_include(AddCompound_File >> User_Defined_Compound): pass

# Aus dem EnzymeML Dokument geht hervor, welche Stoffe für die Prozesssimulation benötigt werden
# Diese sind nicht in der DWSIM Datenbank vorgegeben und müssen daher neu erstellt werden
# Stoffe als JSON Datei der Simulation hinzufügen
# Hier als Individuals, später werden Stoffe dynamisch als Klassen in die Ontologie geladen
# So generischer -> Stoffe und Stoffdaten lassen sich über ein Dictionary verändern
Laccase = JSON_file('Laccase')
ABTS_red = JSON_file('ABTS_red')
ABTS_ox = JSON_file('ABTS_ox')
Water = DWSIM_Compounds('Water')
Oxygen = DWSIM_Compounds('Oxygen')


with onto:
    # Auswahl der Property Package in DWSIM
    class Thermodynamic_Model(Thing): pass
    class PropertyPackage(Thermodynamic_Model): pass
    class Activity_Coefficient_Model(PropertyPackage): pass
    class Ideal_Model(PropertyPackage): pass
    class RaoultsLaw(Ideal_Model): pass
    class NRTL(Activity_Coefficient_Model): pass
    class UNIQUAC(Activity_Coefficient_Model): pass
    
    class has_interactionParameter(Activity_Coefficient_Model >> float): pass

    # Abhängig von der Property Package sind unterschiedliche Stoffeigenschaften wichtig
    # Später werden die Stoffeigenschaften über ein Dict dynamisch zugeordnet
    class Substance_Property(Substance): pass
    
    class Physico_chemical_property(Substance_Property): pass
    class Molarmass(Physico_chemical_property): pass
    class MeltingPoint(Physico_chemical_property): pass
    class BoilingPoint(Physico_chemical_property): pass
    class Density(Physico_chemical_property): pass
    class Solubility(Physico_chemical_property): pass
    class Solubility_in_Water(Physico_chemical_property): pass
    class Solubility_in_OrganicSolvent(Physico_chemical_property): pass    
    class Enzymatic_SubstanceProperty(Substance_Property): pass
    class Enzymatic_Substrate_Specificity(Enzymatic_SubstanceProperty): pass
    class pH_Optimum(Enzymatic_SubstanceProperty): pass
    class Temp_Optimum(Enzymatic_SubstanceProperty): pass
    class Catalytic_Efficiency(Enzymatic_SubstanceProperty): pass
    class Kinetic_Parameter(Catalytic_Efficiency):pass
    class Substrate_Affinity(Enzymatic_SubstanceProperty): pass
    class Inhibitor_Sensitivity(Enzymatic_SubstanceProperty): pass    


# Die Nachfolgenden Angaben sind nur ausreichend, wenn ein feststoff vorliegt
# Der ein Feststoff bleibt
    class has_DWSIM_ID(Substance >> int): pass
    class has_CAS_Number(Substance >> str): pass
    class has_SMILES(Substance >> str): pass
    class has_Formula(Substance >> str): pass
    class has_Molecular_Weight(Substance >> float): pass

# Informationen/ Werte zu den Stoffen wurden im Internet recherchiert
Laccase.has_DWSIM_ID.append(00000)
Laccase.has_CAS_Number.append('80498-15-3')
Laccase.has_SMILES.append('CC[C@H](C)[C@@H](C(N1CCC[C@H]1C(=O)O)=O)N=C([C@H](CCC(=N)O)N=C([C@H](CCC(=O)O)N=C([C@H](C)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](C(C)C)N=C([C@H](C)N)O)O)O)O)O)O)O)')
Laccase.has_Formula.append('C66H109N19O25')
# Bestimmung des Molekuargewichtes über einen Sequenzrechner
Laccase.has_Molecular_Weight.append(56000) #g/mol

ABTS_red.has_DWSIM_ID.append(10000)
ABTS_red.has_CAS_Number.append('28752-68-3')
ABTS_red.has_SMILES.append('CCN1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_red.has_Formula.append('C18H18N4O6S4')
ABTS_red.has_Molecular_Weight.append(514.619) #g/mol

ABTS_ox.has_DWSIM_ID.append(20000)
ABTS_ox.has_CAS_Number.append('28752-68-3')
ABTS_ox.has_SMILES.append('CC[N+]1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC')
ABTS_ox.has_Formula.append('C18H17N4O6S4')
ABTS_ox.has_Molecular_Weight.append(513.619) #g/mol

with onto:
# Stoffeigenschaften, die in DWSIM angegeben werden können
# Dafür wurde Stoff Wasser, der in der Datenbank hinterlegt ist als JSON Datei exportiert
# Wasser später als Lösemittel
    class has_Curve_For_VaporPressure(Substance >> float): pass
    class has_Ideal_gas_HeatCapacity(Substance >> float): pass
    class has_Critical_Compressibility(Substance >> float): pass
    class has_Critical_Pressure(Substance >> float): pass
    class has_Critical_Temperature(Substance >> float): pass
    class has_Critical_Volume(Substance >> float): pass
    class has_Normal_Boiling_Point(Substance >> float): pass
    class has_Acentric_Factor(Substance >> float): pass
    class has_Chao_Seader_Acentricity(Substance >> float): pass
    class has_Chao_Seader_Liquid_Molar_Volume(Substance >> float): pass
    class has_Chao_Seader_Solubility_Parameter(Substance >> float): pass
    class has_IG_Enthalpy_of_Formation_25C(Substance >> float): pass
    class has_IG_Entropy_of_Formation_25C(Substance >> float): pass
    class has_IG_Gibbs_Energy_of_Formation_25C(Substance >> float): pass
    class has_InteractionParameter(Substance >> float): pass # Können in DWSIM ausgestellt werden

    class isBlackOil(Substance >> bool): pass
    class is_COOL_PROP_Supported(Substance >> bool): pass
    class is_F_PROPS_Supported(Substance >> bool): pass
    class is_Hydrated_Salt(Substance >> bool): pass
    class is_Ion(Substance >> bool): pass
    class is_Modified(Substance >> bool): pass
    class is_Salt(Substance >> bool): pass
    class is_Solid(Substance >> bool): pass    
    class has_Elements(Substance >> str): pass

Laccase.isBlackOil.append(False)
ABTS_red.isBlackOil.append(False)
ABTS_ox.isBlackOil.append(False)

Laccase.is_COOL_PROP_Supported.append(False)
ABTS_red.is_COOL_PROP_Supported.append(False)
ABTS_ox.is_COOL_PROP_Supported.append(False)

Laccase.is_F_PROPS_Supported.append(False)
ABTS_red.is_F_PROPS_Supported.append(False)
ABTS_ox.is_F_PROPS_Supported.append(False)

Laccase.is_Hydrated_Salt.append(False)
ABTS_red.is_Hydrated_Salt.append(False)
ABTS_ox.is_Hydrated_Salt.append(False)

Laccase.is_Ion.append(False)
ABTS_red.is_Ion.append(False)
ABTS_ox.is_Ion.append(False)

Laccase.is_Modified.append(False)
ABTS_red.is_Modified.append(False)
ABTS_ox.is_Modified.append(False)

Laccase.is_Salt.append(False)
ABTS_red.is_Salt.append(False)
ABTS_ox.is_Salt.append(False)

Laccase.is_Solid.append(False)
ABTS_red.is_Solid.append(False)
ABTS_ox.is_Solid.append(False)

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

    # Disjunktion von Klassen
    # Klassen sind disjunkt, wenn es kein Individuum gibt, das allen Klassen angehört
    # Eine Klassen-Disjointness wird mit der Funktion AllDisjoint() erzeugt, die eine Liste von Klassen als Parameter annimmt
    AllDisjoint([NucleicAcid_Catalysed_Reaction, Protein_Catalysed_Reaction])
    AllDisjoint([Abzymatic_Reaction,Enzymatic_Reaction])

    class Oxidoreductase_Reaction(Enzymatic_Reaction): pass
    class Transferase_Reaction(Enzymatic_Reaction): pass
    class Hydrolyse_Reaction(Enzymatic_Reaction): pass
    class Lyase_Reaction(Enzymatic_Reaction): pass
    class Isomerase_Reaction(Enzymatic_Reaction): pass
    class Ligase_Reaction(Enzymatic_Reaction): pass

    # ABTS-Oxidation ist nur ein Individuum der Klasse Oxidationsreaktion
    AllDisjoint([Oxidoreductase_Reaction, Transferase_Reaction, Hydrolyse_Reaction, Lyase_Reaction, Isomerase_Reaction, Ligase_Reaction])    

    # Substrat, Produkt, Protein -> Klassen existieren bereits in SBO+
    # Product: http://biomodels.net/SBO/SBO_0000011
    # Enzymatic catalyst: http://biomodels.net/SBO/SBO_0000460
    # Substrate: http://biomodels.net/SBO/SBO_0000015
    class Reaction_Participant(Reaction): pass
    class Substrate(Reaction_Participant): pass
    class Product(Reaction_Participant): pass
    class Protein(Reaction_Participant): pass
    
    # Ein Individuum das ein Proetein ist, wird nicht zugleich ein Produkt sein
    AllDisjoint([Substrate, Product, Protein])
    
    class Enzyme(Protein): pass
    # 'Enzym katalysiert eine enzymatische Reaktion'
    class catalyses(Enzyme>> Enzymatic_Reaction): pass

    # Ein Enzym, dass der Klasse Oxidoreduktase angehört, katalysiert nur eine Oxidationsreaktion
    class Oxidoreductase(Enzyme):
        is_a = [catalyses.only(Oxidoreductase_Reaction)]
    # Ein Enzym, dass der Klasse Transferase angehört, katalysiert nur eine Transferasereaktion
    class Transferase(Enzyme):
        is_a = [catalyses.only(Transferase_Reaction)]
    # Ein Enzym, dass der Klasse Hydrolase angehört, katalysiert nur eine Hydrolysereaktion
    class Hydrolyse(Enzyme):
        is_a = [catalyses.only(Hydrolyse_Reaction)]
    # Ein Enzym, dass der Klasse Lyase angehört, katalysiert nur eine Lyasereaktion
    class Lyase(Enzyme):
        is_a = [catalyses.only(Lyase_Reaction)]
    # Ein Enzym, dass der Klasse Isomerase angehört, katalysiert nur eine Isomerasereaktion
    class Isomerase(Enzyme):
        is_a = [catalyses.only(Isomerase_Reaction)]
    # Ein Enzym, dass der Klasse Ligase angehört, katalysiert nur eine Ligasereaktion
    class Ligase(Enzyme):
        is_a = [catalyses.only(Ligase_Reaction)]
        

    AllDisjoint([Oxidoreductase, Transferase, Hydrolyse, Lyase, Isomerase, Ligase])

    # Die Stöchiometrie ist wichtig, um die Reaktion in DWSIM einzugeben
    # Werden als float übergeben
    class has_Stoichometric_Coeff(Reaction_Participant >> float): pass

# ABTS-Oxidation ist die betrachtete Reaktion
# Wird als Individuum der Ontologie übergeben
ABTS_Oxidation = Oxidoreductase_Reaction('ABTS_Oxidation')

# Die Reaktionsteilnehmer
Laccase = Oxidoreductase('Laccase')
ABTS_red = Substrate('ABTS_red')
ABTS_ox = Product('ABTS_ox')
Water = Product('Water')
Oxygen = Substrate('Oxygen')

# Ihre Stöchiometrie
# Überlegung Laccase: Zugabe als wässrige Lösung, daher neg. Vorzeichen
# Proteine gehen unverändert aus einer Katalysereaktion
# Stöchiometrie von Laccase später über DWSIM angelichen lassen, sodass Bilanz stimmt
Laccase.has_Stoichometric_Coeff.append(-1.0)
ABTS_red.has_Stoichometric_Coeff.append(-4.0)
ABTS_ox.has_Stoichometric_Coeff.append(4.0)
Water.has_Stoichometric_Coeff.append(2.0)
Oxygen.has_Stoichometric_Coeff.append(-1.0)

with onto:    
    # in DWSIM dorders = Dictionary[str, float]() and rorders = Dictionary[str, float]()
    class Irreversible_Reaction(Reaction): pass
    class has_Direct_OrderCoeff(Irreversible_Reaction >> float): pass
    class Reversible_Reaction(Reaction): pass
    class has_Reverse_OrderCoeff(Reversible_Reaction >> float): pass


# Ein Basiskomponente muss angegeben werden
# Ein Reaktant, in diesem Fall ABTS-red
Laccase.has_Direct_OrderCoeff.append(0.0)
ABTS_red.has_Direct_OrderCoeff.append(1.0)
ABTS_ox.has_Direct_OrderCoeff.append(0.0)
Water.has_Direct_OrderCoeff.append(0.0)
Oxygen.has_Direct_OrderCoeff.append(0.0)

Laccase.has_Direct_OrderCoeff.append(0.0)
ABTS_red.has_Direct_OrderCoeff.append(0.0)
ABTS_ox.has_Direct_OrderCoeff.append(0.0)
Water.has_Direct_OrderCoeff.append(0.0)
Oxygen.has_Direct_OrderCoeff.append(0.0)

with onto:
# In DWSIM sind vier verschiedene Reaktionstypen vorgegeben
# DWSIM ermöglicht es eigene Reaktionstypen der Software zu übergeben
# Möglich über einen Script Manager
    class ReactionType(Reaction): pass
    class Conversion(ReactionType): pass
    class Equbrilium(ReactionType): pass
    class Arrhenius_Kinetic(ReactionType): pass
    class Heterogeneous_Catalytic(ReactionType): pass

# Kinetik geht aus dem EnzymeML Dokument hervor
# Wichtig ist die Übergabe der Kinetikparameter
# Als Subklasse die Konzepte übergeben
# Anschließend Werte als Data Property übergeben
    class User_Defined_Reaction(ReactionType): pass
    class Michaelis_Menten_Kinetic(User_Defined_Reaction): pass
    class KM(Michaelis_Menten_Kinetic): pass
    class kCAT(Michaelis_Menten_Kinetic): pass

# Werte aus dem EnzymeML Dokument laden
    class has_KM_Value(KM >> float): pass
    class has_KM_Unit(KM >> str): pass
    class has_kCAT_Value(kCAT >> float): pass
    class has_kCAT_Unit(kCAT >> str): pass

# Werte für Km und kcat sind sowohl vonm Enzym als auch vom Substrat abhängig
# Werte hier für ABTS_red als Substrat und Laccase als Enzym
KM_ABTS_ox = KM('KM_ABTS_ox')
kCAT_ABTS_ox = KM('kCAT_ABTS_ox')
KM_ABTS_ox.has_KM_Value.append(0.2)
kCAT_ABTS_ox.has_kCAT_Value.append(1.67)
KM_ABTS_ox.has_KM_Unit.append('mmol/l')
kCAT_ABTS_ox.has_kCAT_Unit.append('1/s')

with onto:
    # EnzymeML bietet die Möglichkeit mehrere Modelle gleichzeitig zu dokumentieren
    # Mit der ID kann der entsprechende Reaktionsteilnehmer identifiziert werden
    # exemplarisch 5 Klassen
    class Modeled_Element(Michaelis_Menten_Kinetic): pass
    class s_0(Modeled_Element): pass
    class s_1(Modeled_Element): pass
    class s_2(Modeled_Element): pass
    class s_3(Modeled_Element): pass
    class s_4(Modeled_Element): pass
    class s_5(Modeled_Element): pass

    class p_0(Modeled_Element): pass
    class p_1(Modeled_Element): pass
    class p_2(Modeled_Element): pass
    class p_3(Modeled_Element): pass
    class p_4(Modeled_Element): pass
    class p_5(Modeled_Element): pass

Laccase = p_0('Laccase')
ABTS_red = s_0('ABTS_red')
ABTS_ox = s_2('ABTS_ox')
# Laut Dokumentation, jedoch s1 = ABTS_red
# Oxygen wird für die Gleichung vernachlässigt
Oxygen = s_1('Oxygen')

with onto:
    # Informationen über das Protein aus dem EnzymeML Dokument
    # Sequenz ist wichtig, um das Molekulargewicht zu ermitteln    
    class has_Sequence(Protein >> str): pass
    class has_Source_Organism(Protein >> str): pass
    class has_EC_Number(Protein >> str): pass
    class has_UniProt_ID(Protein >> str): pass
    class has_Const_Concentration(Protein >> bool or Substrates >> bool or Products >> bool): pass


Laccase.has_Sequence.append('MGLQRFSFFVTLALVARSLAAIGPVASFVVANAPVSPDGFLRDAIVVNGVVPSPLIRAKKGDRFQLNVVDTLTNHSMLKSTSIHWHGFFQAGTNWADGPAFVNQCPIASGHSFLYDFHVPDQAGTFWYHSHLSTQYCDGLRGPFVVYDPKDPHASRYDVDNESTVITLTDWYHTAARLGPRFPLGADATVINGLGRSASTPTAALAVINVQHGKRYRFRLVSISCDPNYTFSIDGHNLTVIEVDGINSQPLLVDSIQIFAAQRYSFVLNANQTVGNYWVRANPNFGTVGFAGGINSAILRYQGAPVAEPTTTQTPSVIPLIETNLHPLARMPVPGTRTPGGVDKALKLAFNFNGTNFFINNASFTPPTVPVLLQILSGAQTAQELLPAGSVYPLPAHSTIEITLPATALAPGAPHPFHLHGHAFAVVRSAGSTTYNYNDPIFRDVVSTGTPAAGDNVTIRFQTDNLGPWFLHCHIDFHLEAGFAIVFAEDVADVKAANPVPKAWSDLCPIYDGLSEADQ')
Laccase.has_Source_Organism.append('Trametes versicolor')
Laccase.has_EC_Number.append('1.10.3.2')
Laccase.has_UniProt_ID.append('D2CSE5')
Laccase.has_Const_Concentration.append(True)

with onto:   
    # Reaktionsbedingungen festlegen
    class Reaction_Conditions(Reaction): pass
    class Temperature(Reaction_Conditions): pass
    class pH(Reaction_Conditions): pass
    class Pressure(Reaction_Conditions): pass
    class Solvent(Reaction_Conditions): pass
    class ReactionRate(Reaction_Conditions): pass

    # Werte als Data property übergeben
    class has_Temperature_Value(Temperature >> float): pass
    class has_pH_Value(pH >> float): pass
    class has_Pressure_Value(Pressure >> float):pass
    class has_Rate_Value(ReactionRate >> float): pass
    class has_Temperature_Unit(Temperature >> str): pass
    class has_Pressure_Unit(Pressure >> str): pass
    class has_Rate_Unit(ReactionRate >> str): pass

Temperature.has_Temperature_Value.append(38.0)
pH.has_pH_Value.append(5.2)
Pressure.has_Pressure_Value.append(1.013)

Temperature.has_Temperature_Unit.append('C')
Pressure.has_Pressure_Unit.append('bar')

with onto:
    # Konzepte, die das Fließbild wiedergeben    
    class ProcessFlowDiagram(Thing): pass
    # Metadata4Ing hat eine Klasse für Input: http://www.nfdi.org/nfdi4cat/ontochem#ChemicalMaterialInput
    # Metadata4Ing hat eine Klasse für Output: http://www.nfdi.org/nfdi4cat/ontochem#ChemicalMaterialOutput
    class MaterialFlow(ProcessFlowDiagram): pass
    class InletFlow(MaterialFlow): pass
    class OutletFlow(MaterialFlow): pass
    class Mixture(MaterialFlow): pass

    # Der Reaktor wird später der existierenden Klasse: http://www.nfdi.org/nfdi4cat/ontochem#Device zugeordnet    
    class Equipment(ProcessFlowDiagram): pass
    class Reactor(Equipment): pass
    class Reactortype(Reactor): pass

    # Volumen und Länge des Reaktors müssen DWSIM übergeben werden
    class has_Volume_Value(Equipment >> float): pass
    class has_Volume_Unit(Equipment >> str): pass

SCR = Reactortype('SCR')
HTR = Reactortype('HTR')

SCR.has_Volume_Value.append(8.0)
SCR.has_Volume_Unit.append('ml')

HTR.has_Volume_Value.append(8.0)
HTR.has_Volume_Unit.append('ml')

with onto:    
    class has_Lenght_Value(Equipment>> float): pass
    class has_Lenght_Unit(Equipment >> str): pass
    class has_Compound_MolarFlow(MaterialFlow >> float): pass

SCR.has_Lenght_Value.append(4.0)
SCR.has_Lenght_Unit.append('m')

HTR.has_Lenght_Value.append(4.0)
HTR.has_Lenght_Unit.append('m')

Inlet_Laccase = InletFlow('Inlet_Laccase')
Inlet_ABTS_ox = InletFlow('Inlet_ABTS_ox')
Inlet_Oxygen = InletFlow('Inlet_Oxygen')

Inlet_Laccase.has_Compound_MolarFlow.append(1.0) # mol/s
Inlet_ABTS_ox.has_Compound_MolarFlow.append(1.0) # mol/s
Inlet_Oxygen.has_Compound_MolarFlow.append(1.0) # mol/s
        
with onto:    
    class UnitOperation(Thing): pass
    class Mixing(UnitOperation): pass

    class Project(Thing): pass
    class Institution(Project): pass
    class Organisation(Institution): pass
    class Agent(Institution): pass         
    class Engineering_Step(Project): pass # Basic Engineering, Detail Engineering
    class Processdesign(Engineering_Step): pass
    class Processsimulation(Processdesign): pass
    class Simulation_for_Automatition(Processsimulation): pass
    class Simulation_Tool(Simulation_for_Automatition): pass
    class Documentation(Project): pass

    class has_Projectstart(Project >> str): pass 
    class ElectronicLabNotebook(Documentation): pass
    class EnzymeML_Documentation(ElectronicLabNotebook): pass

    #class Has_Projectstart(Project >> datetime.date): pass  
    class has_Titel(EnzymeML_Documentation >> str): pass
    class has_Author(EnzymeML_Documentation >> str): pass
    #class Has_Date_of_Creation(EnzymeML_Documentation >> datetime.date): pass
    class has_Date_of_Creation(EnzymeML_Documentation >> str): pass

ABTS_Oxidation_by_Laccase = Project('ABTS_Oxidation_by_Laccase')
TU_Dortmund = Institution('TU_Dortmund')
Chair_of_EquipmentDesign = Organisation('Chair_of_EquipmentDesign')
EnzymeML_Document_1 = EnzymeML_Documentation('EnzymeML_Document_1')

ABTS_Oxidation_by_Laccase.has_Projectstart.append('12.12.2022')

EnzymeML_Document_1.has_Titel.append('Laccase; Helically Coiled Reactor (HCR) & Straight Capillary Reactor (SCR)')
EnzymeML_Document_1.has_Author.append('Katrin Rosenthal')
EnzymeML_Document_1.has_Date_of_Creation.append('18.08.2021')
    
with onto:    
    class Reaction_Optimization(Thing): pass
    class Stabilizer(Reaction_Optimization): pass
    class has_Stabilizer_Concentration(Stabilizer >> float): pass

Tween80 = Stabilizer('Tween80') #(Polysorbat 80)
Tween80.has_Stabilizer_Concentration.append(1.0)

with onto:    
    class Experimental_Data(EnzymeML_Documentation): pass
    class Measurement(Experimental_Data): pass
    # 12 Messungen im EnzymeML Dokument
    class Initial_Concentration(Measurement): pass
    class Reactant_Initial_Conc(Initial_Concentration): pass
    class Protein_Initial_Conc(Initial_Concentration): pass
    class Concentration_Curve(Measurement): pass 
    class Reactant_Conc_Curve(Concentration_Curve): pass
    class Protein_Conc_Curve(Concentration_Curve): pass
    class Absorption(Measurement): pass
    class Time_Measurement(Measurement): pass

Laccase_Conc_Curve = Protein_Conc_Curve('Laccase_Conc_Curve')
ABTS_red_Conc_Curve = Reactant_Conc_Curve('ABTS_red_Conc_Curve')

# Auf Konsistenz prüfen
# Reasoner HermiT
with onto:
    sync_reasoner()
    
onto.save("Step1Thesis_Klassenhierarchie.owl", format="rdfxml") 