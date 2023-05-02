# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 17:11:11 2023

@author: 49157
"""

# Masterthesis Abbaspour
# Zusammenfügen des Codes

# Owlready2 ist ein Paket zur Bearbeitung von OWL 2.0 Ontologien in Python
# Es kann Ontologien laden, modifizieren, speichern und unterstützt Reasoning über HermiT (enthalten)

from owlready2 import * 

# Reasoner HermiT ist in Java geschrieben
# Unter Windows muss der Speicherort des Java-Interpreters wie folgt konfiguriert werden

owlready2.JAVA_EXE = "C://Users//49157//Downloads//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"

# Ontologie laden, in der Entitäten der Thesis verabreitet werden sollen
# Diese Ontologie ist ein Zusammenschluss zweier bestehenden Ontologien: metadata4Ing + SBO
# Irrelevante Klassen wurden manuell entfernt, sowie Extraklassen, die durch das Mergen entstanden sind

onto_world = owlready2.World()
onto = onto_world.get_ontology("./BaseOnto.owl").load()

# Ohne diese Definition wird die Ontologie für set_relations(test_dict, onto) nicht gefunden
BaseOnto = onto

# PyEnzyme ist die Schnittstelle zum Datenmodell EnzymeML und bietet eine komfortable Möglichkeit
# zur Dokumentation und Modellierung von Forschungsdaten

import pyenzyme as pe
from pyenzyme import EnzymeMLDocument, EnzymeReaction, Complex, Reactant, Protein, Creator
from pyenzyme.enzymeml.models import KineticModel, KineticParameter

# EnzymeML Dokument laden
# Stelle vorher die Macros aus, da sonst der pH Wert nicht erkannt wird

enzmldoc = pe.EnzymeMLDocument.fromTemplate("./EnzymeML_Template_18-8-2021_KR.xlsm")

# Lade alle relevanten Informationen aus der EnzymeML Dokumentation
# Und zwar relevant für die DWSIM Simulation

# Infos zum Dokument-Autor
for Creator in enzmldoc.creator_dict.values():
    Creator_Name = Creator.given_name # Katrin
    Creator_Familyname = Creator.family_name # Rosenthal
    Creator_Mail = Creator.mail # katrin.rosenthal@tu-dortmund.de

# Infos zum Reaktor
for vessel in enzmldoc.vessel_dict.values():
    Vessel_Name = vessel.name # Straight tube reactor
    Vessel_ID = vessel.id # v1
    Vessel_Volume = vessel.volume # 8.0 
    Vessel_Unit = vessel.unit # ml

# Das Volumen wird in EnzyeML in ml angegeben
# DWSIM benötigt m3 (voreingestellt sind SI Units, manuelle Umstellung möglich)    
    reacV = Vessel_Volume*1e-6
    
# Infos zur Reaktion
for reaction in enzmldoc.reaction_dict.values():
    Reaction_Name = reaction.name # ABTS Oxidation
    Reaction_ID = reaction.id # r2
    Reaction_SBO = reaction.ontology # SBO_0000176 = Biochemical_Reaction
    Reaction_Educts = reaction.educts # Substrate-list
    Reaction_Products = reaction.products # Product-list
    pH_Value = reaction.ph # 5.2
    Temperature_Value = reaction.temperature # 311.15
    Temperature_Unit = reaction.temperature_unit # K
    Reversible_Reaction = reaction.reversible # False
    
# Infos zu Reaktanten
# Ausgabe: Reaktant, der in der letzten Zeile steht, daher nur Infos zu einem Reaktanten
for reactant in enzmldoc.reactant_dict.values():
    Reactant_SBO = reactant.ontology # SBO_0000247 used to be 'SMALL_MOLECULE'? Now -> 'simple chemical'

# Infos zum Protein
for protein in enzmldoc.protein_dict.values():
    Protein_Name = protein.name # Laccase
    Protein_ID = protein.id # p2
    Protein_SBO = protein.ontology # SBO_0000252 = Protein
    Protein_Sequence = protein.sequence # wichtig für das Molekulargewicht später
    Protein_EC_Number = protein.ecnumber # 1.10.3.2
    Protein_Organism = protein.organism # Trametes versicolor
    Protein_UniProtID = protein.uniprotid # None, should be 'D2CSE5'
    Protein_Constant = protein.constant # True
    
# Ontologie Design
# Relevante Entitäten der bestehenden Ontologie hinzufügen
# Um im Anschluss alle erforderlichen Infos für die Simulation in DWSIM aus der Ontologie zu ziehen

with onto:
    # Komponenten: DWSIM stellt 6 Datenbanken zur verfügung (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes)
    # Daraus ergeben sich 1500 verfügbare Komponenten für die Simulation
    # Datenbanken werden der metadata4Ing Klasse 'ChemicalSubstance' subsumiert
        class SubstanceDatabase(onto.search_one(iri = '*ChemicalSubstance')): pass
        class DefaultDatabase(SubstanceDatabase): pass
        class DWSIMCompound(DefaultDatabase): pass
        class ChemSep(DefaultDatabase): pass
        class Biodiesel(DefaultDatabase): pass
        class CoolProp(DefaultDatabase): pass
        class ChEDL(DefaultDatabase): pass
        class Electrolytes(DefaultDatabase): pass
    
        # Object property -> Triplett liest sich: 'Stoffdatenbank liefert chemische Substanz'
        class provides(SubstanceDatabase >> onto.search_one(iri = '*ChemicalSubstance')): pass

    # DWSIM bietet die Möhlichkeit Komponenten zu importieren über: Online-Quellen, Json- oder XML_Dateien
    # Zusätzlich kann der User über den 'Compound Creator' Stoffe erstellen
    # So entsteht eine von DWSIM 'abweichende Datenbank'
        class DeviantingDatabase(SubstanceDatabase): pass
        class OnlineSource(DeviantingDatabase): pass
        class UserDefinedCompound(DeviantingDatabase): pass

        # Object property -> Triplett liest sich: 'User-definierte Komponente schafft abweichende Datenbank'
        class creates(UserDefinedCompound >> DeviantingDatabase): pass 
    
    # Um selbst erstellte Komponenten der Simulation verfügbar zu machen, müssen diese in dem spezifischen Ordner 'addcomps' hinterlegt sein
    # Ordner findet sich unter: "C:\Users\49157\AppData\Local\DWSIM8\addcomps"
        class AddCompoundFile(UserDefinedCompound): pass      
        class XMLfile(AddCompoundFile): pass
        class JSONfile(AddCompoundFile): pass
        
        # Object property -> Triplett liest sich: 'AddCompound-Ordner muss user-definierte Komponente enthalten'
        class mustInclude(AddCompoundFile >> UserDefinedCompound): pass


# Code für die dynamische Erstellung von Komponenten als Klassen
# Die Elemente einer Stoffliste werden entweder der Oberklasse JSON-Datei oder DWSIM-Komponente subsumiert

def class_creation(substance_list, onto):    
    # Durchiterieren durch substance_list, um enthaltene Strings als Klassen in Ontologie 'onto' einzusetzen    
    for substance in test_substances:
        # codestring aufsetzen, .format(substance,substance) am Ende ersetzt jeden {}-Teil des Strings mit Inhalt der Variablen substance               
        # Neue Komponenten müssen als JSON-file über den AddCompoumd-Ordner hinzugefügt werden
        # Sind die Komponenten einmal hinzugefügt worden, stehen sie für jede anschließende Simulation zur Verfügung
        codestring = """with onto:
            class {}(onto.search_one(iri = '*JSONfile')): 
                label = '{}'
                pass
            """.format(substance,substance)
        
        # ABTS_ox und ABTS_red der Klasse ABTS unterordnen
        if substance == "ABTS_ox" or substance == "ABTS_red":
            codestring = """with onto:
            class {}({}):
                label = '{}'
                pass
            """.format(substance,"ABTS",substance)
        
        # Die Komponenten Wasser und Sauerstoff sind bereits in DWSIM hinterlegt
        # Daher der Oberklasse DWSIM-Komponenten zuordnen
        if substance == "Water" or substance == "Oxygen":
            codestring = """with onto:
            class {}(onto.search_one(iri = '*DWSIMCompound')):
                label = '{}'
                pass
            """.format(substance,substance)
        
        # Code, der im codestring enthalten ist compilieren
        code = compile(codestring, "<string>","exec")
        
        # Code ausführen
        exec(code)

def dataProp_creation(dataProp_dict, onto):
    # Benötigte Relationen bestimmen via set() -> auch bei Mehrfachnennung
    # ist jede Relation aus Dictionary nur max. 1x enthalten in relation_list
    relation_set = set()
    for i in list(dataProp_dict.keys()):
        relation_set.update(set(dataProp_dict[i].keys()))
    
    # Definieren jeder Relation in der Ontologie via codestring und exec:
    for rel in relation_set:
        codestring = """with onto:
            class {}(DataProperty):
                label = '{}'
                pass
            """.format(rel,rel)
        
        # Code, der im codestring enthalten ist compilieren
        code = compile(codestring, "<string>","exec")
        
        # Code ausführen
        exec(code)
    
    
def set_relations(dataProp_dict, onto):
    # Wieder aufsetzen des Codestrings, diesmal anhand eines Dictionaries
    
    for class_name in list(dataProp_dict.keys()):
        # Klasse in Ontologie raussuchen, die zum Dictionary-key passt
        onto_class = onto.search_one(label=class_name)
        
        for entry in dataProp_dict[class_name]:
            
            data_prop_type = type(dataProp_dict[class_name][entry])
            if (data_prop_type == int) or (data_prop_type == float):
                codestring = "{}.{} = {}".format(str(onto_class),str(entry), dataProp_dict[class_name][entry])                
                print(dataProp_dict[class_name][entry])
           
            else:
                codestring = "{}.{} = '{}'".format(str(onto_class),str(entry), str(dataProp_dict[class_name][entry]))                
            
            # Code, der im codestring enthalten ist compilieren
            code = compile(codestring, "<string>","exec")
            # Code ausführen
            exec(code)       

# Stoffliste
test_substances = ["Laccase", "ABTS", "ABTS_ox", "ABTS_red", "Oxygen", "Water"]

# Wörterbuch mit Stoffeigenschaften erstellen
# Eigenschaften beachten, die relevant sind für die Simulation in DWSIM
# Die relative Dicht und der Normalsiedepunkt, werden gebraucht für 'bulk c7+ pseudocompound creator setting'
# Auf diese Weise können Stoffe direkt über einen Code erstellt werden
# und DWSIM schätzt durch entsprechende Modelle fehlende Stoffeigenschaften ab
# z.B. wird das Molekulargewicht oder die chemische Strukturformel abgeschätzt
# Im vorliegenden Fall weichen die abgeschätzten Werte zu weit von den Literaturwerten ab
# Weshalb Stoffeigenschaften manuell in der JSON-datei korrigiert wurden
# und fehlende Stoffdaten durch die des Lösemittels ersetzt
test_dict = {"Laccase": { "hasRelativeDensities": None,
                          "has_nbps": 375.15, # in K (Normal Boiling Point von Wasser)
                          "has_nbps_Unit": 'K',
                          
                          # Brauche ich für den DWSIM Code später
                          "isCatalyst": True,
                          
                          # Koeffizienten sind wichtig für die Definition der Reaktion in DWSIM
                          # Stöchiometrie ist für Laccase mit DWSIM abgeschätzt, sodass die 'Balance' passte
                          "hasStoichiometriCoefficient": -7.5219E-05,
                          "hasDirect_OrderCoefficient": 0.0,
                          "hasReverse_OrderCoefficient": 0.0,
                         
                          # DWSIM benötigt eine Basiskomponente, die ein Reaktionspartner sein muss
                          # Diese Basiskomponente wird als Referenz für die Berechnung der Reaktionswärme
                          # In der Regel ein Reaktant
                          "isBaseComponent": False,
                         
                          # Die AS-Sequenz ist aus dem zuvor geladenen EnzymeML-Dokument
                          # Daraus lässt sich das Molekulargewicht ermitteln
                          "hasSequence": Protein_Sequence,

                          # https://nebiocalculator.neb.com/#!/protamt
                          "hasMolecularWeight": 56000, # in kg/kmol
                          "hasMolecularWeight_Unit": 'kg/kmol',
                         
                          # Der Organismus ist aus dem zuvor geladenen EnzymeMl-Dokument
                          "hasSourceOrganism": Protein_Organism,
                         
                          # Die ID wude von DWSIM vergeben
                          "hasDWSIM_ID": -6497,
                          "hasCAS_Number": '80498-15-3',
                          "hasEC_Number": Protein_EC_Number,
                          "hasSMILES": 'CC[C@H](C)[C@@H](C(N1CCC[C@H]1C(=O)O)=O)N=C([C@H](CCC(=N)O)N=C([C@H](CCC(=O)O)N=C([C@H](C)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](CC(=O)O)N=C([C@H](C(C)C)N=C([C@H](C)N)O)O)O)O)O)O)O)',
                          "hasFormula":'C66H109N19O25',
                          "has_pH_Optimum":'4.5-5.0 with ABTS as substrate',
                          "hasTempOptimum":'35-55 °C with ABTS as substrate',

                          # Werte, die vom LöMi (Wasser) übernommen wurden
                          "hasCriticalTemperature": 647.14, # in K
                          "hasCriticalPressure": 2.2064E+07, # in Pa                          
                          "hasCriticalVolume": 0.05595, # in m3/kmol
                          "hascriticalCompressibility": 0.229, # dimensionslos
                          "hasAcentricFactor": 0.344, # dimensionslos
                          "hasIdealGasEnthalpyOfFormation_25Celsius": -13422.7, # in kJ/kg
                          "hasIdealGasGibbsEnergyOfFormation_25Celsius": -12688.7, # in kJ/kg
                          "hasChao_SeaderAcentricFactor": 0.328, # dimensionslos
                          "hasChao_SeaderSolubilityParameter": 0.0114199, # in (cal/mL)^0.5
                          "hasChao_SeaderLiquidMolarVolume": 18.0674, # in mL/mol
                          
                          "hasCriticalTemperature_Unit": 'K',
                          "hasCriticalPressure_Unit": 'Pa',                          
                          "hasCriticalVolume_Unit": 'm3/kmol',
                          "hasIdealGasEnthalpyOfFormation_25Celsius_Unit": 'kJ/kg',
                          "hasIdealGasGibbsEnergyOfFormation_25Celsius_Unit": 'in kJ/kg',
                          "hasChao_SeaderSolubilityParameter_Unit": '(cal/mL)^0.5',
                          "hasChao_SeaderLiquidMolarVolume_Unit": 'mL/mol',
                          
                          "hasRackettCompressibility": 0.2338, # dimensionslos                          
                          "isBlackOil": False,
                          "isCoolPropSupported": False,
                          "isF_PropsSupported": False,
                          "isHydratedSalt": False,
                          "isIon": False,
                          "isModified": False,
                          "isSalt": False,
                          "isSolid": False},
             
             "ABTS_ox": { "hasRelativeDensities": None,
                          "has_nbps": 375.15, # in K (Normal Boiling Point von Wasser)
                          "has_nbps_Unit": 'K',
                          
                          "isMainProduct": True,
                          
                          # Sind aus dem Paper: From Coiled Flow Inverter to Stirred Tank Reactor - Bioprocess Development and Ontology Design
                          "hasStoichiometriCoefficient": 4,
                          "hasDirect_OrderCoefficient": 0.0,
                          "hasReverse_OrderCoefficient": 0.0,

                          "isBaseComponent": False,
                           
                          "hasMolecularWeight": 514.619, # in kg/kmol
                          "hasDWSIM_ID": -4356,
                          "hasCAS_Number": '28752-68-3',
                          #"hasSMILES": 'CCN1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC',
                          "hasFormula":'C18H18N4O6S4',
                           
                          # Werte, die vom LöMi (Wasser) übernommen wurden
                          "hasCriticalTemperature": 647.14, # in K
                          "hasCriticalPressure": 2.2064E+07, # in Pa
                          "hasCriticalVolume": 0.05595, # in m3/kmol
                          "hascriticalCompressibility": 0.229, # dimensionslos
                          "hasAcentricFactor": 0.344, # dimensionslos
                          "hasIdealGasEnthalpyOfFormation_25Celsius": -13422.7, # in kJ/kg
                          "hasIdealGasGibbsEnergyOfFormation_25Celsius": -12688.7, # in kJ/kg
                          "hasChao_SeaderAcentricFactor": 0.328, # dimensionslos
                          "hasChao_SeaderSolubilityParameter": 0.0114199, # in (cal/mL)^0.5
                          "hasChao_SeaderLiquidMolarVolume": 18.0674, # in mL/mol

                          "hasCriticalTemperature_Unit": 'K',
                          "hasCriticalPressure_Unit": 'Pa',                          
                          "hasCriticalVolume_Unit": 'm3/kmol',
                          "hasIdealGasEnthalpyOfFormation_25Celsius_Unit": 'kJ/kg',
                          "hasIdealGasGibbsEnergyOfFormation_25Celsius_Unit": 'in kJ/kg',
                          "hasChao_SeaderSolubilityParameter_Unit": '(cal/mL)^0.5',
                          "hasChao_SeaderLiquidMolarVolume_Unit": 'mL/mol',                          
                                                   
                          "hasRackettCompressibility": 0.2338, # dimensionslos
                          "isBlackOil": False,
                          "isCoolPropSupported": False,
                          "isF_PropsSupported": False,
                          "isHydratedSalt": False,
                          "isIon": False,
                          "isModified": False,
                          "isSalt": False,
                          "isSolid": False},
             
             "ABTS_red": {"hasRelativeDensities": None,
                          "has_nbps": 375.15, # in K (Normal Boiling Point von Wasser)
                          "has_nbps_Unit": 'K',
                          
                          "isMainSubstrate": True,
                          
                          "hasStoichiometriCoefficient": -4,
                          "hasDirect_OrderCoefficient": 1.0,
                          "hasReverse_OrderCoefficient": 0.0,

                          "isBaseComponent": True,
                          "hasMolecularWeight": 513.619, # in kg/kmol
                          
                          "hasDWSIM_ID": -9626,
                          "hasCAS_Number": '28752-68-3',
                          #"hasSMILES": 'CC[N+]1\\C(SC2=C1C=CC(=C2)[S]([O-])(=O)=O)=N\\N=C4/SC3=C(C=CC(=C3)[S]([O-])(=O)=O)N4CC',
                          "hasFormula":'C18H17N4O6S4',
                          "hasWaterSolubilityValue": 50.0, # in g/l
                         
                          # Werte, die vom LöMi (Wasser) übernommen wurden
                          "hasCriticalTemperature": 647.14, # in K
                          "hasCriticalPressure": 2.2064E+07, # in Pa
                          "hasCriticalVolume": 0.05595, # in m3/kmol
                          "hascriticalCompressibility": 0.229, # dimensionslos
                          "hasAcentricFactor": 0.344, # dimensionslos
                          "hasIdealGasEnthalpyOfFormation_25Celsius": -13422.7, # in kJ/kg
                          "hasIdealGasGibbsEnergyOfFormation_25Celsius": -12688.7, # in kJ/kg
                          "hasChao_SeaderAcentricFactor": 0.328, # dimensionslos
                          "hasChao_SeaderSolubilityParameter": 0.0114199, # in (cal/mL)^0.5
                          "hasChao_SeaderLiquidMolarVolume": 18.0674, # in mL/mol
                          
                          "hasCriticalTemperature_Unit": 'K',
                          "hasCriticalPressure_Unit": 'Pa',                          
                          "hasCriticalVolume_Unit": 'm3/kmol',
                          "hasIdealGasEnthalpyOfFormation_25Celsius_Unit": 'kJ/kg',
                          "hasIdealGasGibbsEnergyOfFormation_25Celsius_Unit": 'in kJ/kg',
                          "hasChao_SeaderSolubilityParameter_Unit": '(cal/mL)^0.5',
                          "hasChao_SeaderLiquidMolarVolume_Unit": 'mL/mol',                          
                          
                          "hasRackettCompressibility": 0.2338, # dimensionslos
                          "isBlackOil": False,
                          "isCoolPropSupported": False,
                          "isF_PropsSupported": False,
                          "isHydratedSalt": False,
                          "isIon": False,
                          "isModified": False,
                          "isSalt": False,
                          "isSolid": False},
             
             "Oxygen": {  "isReactant": True,
                          "hasStoichiometriCoefficient": -1,
                          "hasDirect_OrderCoefficient": 0.0,
                          "hasReverse_OrderCoefficient": 0.0},
                       
             "Water": {   "isReactant": True,
                          "hasStoichiometriCoefficient": 2,
                          "hasDirect_OrderCoefficient": 0.0,
                          "hasReverse_OrderCoefficient": 0.0}
             }

# Aufrufen von Funktion class_creation(), um alle Strings aus Liste test_substances
# in Ontologie einzubauen
class_creation(test_substances, onto)

dataProp_creation(test_dict, onto)

set_relations(test_dict, onto)

# Ontologie zwischenspeichern
onto.save(file="Zwischenstand_Onto_.owl", format="rdfxml")


# Erstellen von leeren Listen, um Namen der Substanzen, die Katalysator, Hauptprodukt oder Hauptsustrat sind, zu speichern
catalysts = []
main_products = []
main_substrates = []
reactants = []

# Iterieren durch jede Substanz in test_dict
for substance in test_dict:
    
    # Überprüfen, ob die Substanz als Katalysator markiert ist
    if "isCatalyst" in test_dict[substance] and test_dict[substance]["isCatalyst"] == True:
        
        # Wenn ja, den Namen der Substanz zur Liste der Katalysatoren hinzufügen
        catalysts.append(substance)
        
    # Überprüfen, ob die Substanz als Hauptprodukt markiert ist
    elif "isMainProduct" in test_dict[substance] and test_dict[substance]["isMainProduct"] == True:
        
        # Wenn ja, den Namen der Substanz zur Liste der Hauptprodukte hinzufügen
        main_products.append(substance)
        
    # Überprüfen, ob die Substanz als Hauptsustrat markiert ist
    elif "isMainSubstrate" in test_dict[substance] and test_dict[substance]["isMainSubstrate"] == True:
        
        # Wenn ja, den Namen der Substanz zur Liste der Hauptsustrate hinzufügen
        main_substrates.append(substance)
    
    # Überprüfen, ob die Substanz als Reaktant markiert ist
    elif "isReactant" in test_dict[substance] and test_dict[substance]["isReactant"] == True:
        
        # Wenn ja, den Namen der Substanz zur Liste der Hauptsustrate hinzufügen
        reactants.append(substance)



# Ontologie mit den gespeicherten Stoffen laden
# Um Object properties hinzuzufügen
onto_world = owlready2.World()
onto = onto_world.get_ontology("./Zwischenstand_Onto_.owl").load()

with onto:
        # Object Property -> Triplett liest sich: 'Laacase ist importiert als JSON-Datei'   
        class isImportedAs(onto.search_one(iri = '*Laccase') >> onto.search_one(iri = '*JSONfile')): pass
        # Object Property -> Triplett liest sich: 'ABTS_red ist importiert als JSON-Datei'    
        class isImportedAs(onto.search_one(iri = '*ABTS_red') >> onto.search_one(iri = '*JSONfile')): pass
        # Object Property -> Triplett liest sich: 'ABTS_ox ist importiert als JSON-Datei'
        class isImportedAs(onto.search_one(iri = '*ABTS_ox') >> onto.search_one(iri = '*JSONfile')): pass

        # Object Property -> Triplett liest sich: 'Wasser existiert als DWSIM-Komponente'    
        class existsAs(onto.search_one(iri = '*Water') >> onto.search_one(iri = '*DWSIMCompound')): pass
        # Object Property -> Triplett liest sich: 'Wasser existiert als DWSIM-Komponente' 
        class existsAs(onto.search_one(iri = '*Oxygen') >> onto.search_one(iri = '*DWSIMCompound')): pass

with onto:
    
    # In DWSIM ist die Auswahl verschiedener Property Packages möglich
    # Je nach Property Package sind unterschiedliche Stoffeigenschaften relevant
    # Die vorliegende Simulation wird mit Raoult's Law und NRTL durchgeführt
    # Wobei Raoult's Law als ideales Modell nur der ersten Kontrolle des Codes dient
        class ThermodynamicModel(Thing): pass
        class PropertyPackage(ThermodynamicModel): pass
        class ActivityCoefficientModel(PropertyPackage): pass
        class IdealModel(PropertyPackage): pass
        class RaoultsLaw(IdealModel): pass
        class NRTL(ActivityCoefficientModel): pass
        class UNIQUAC(ActivityCoefficientModel): pass
    
        # Hinweis für später: Die Interaktionsparameter können notfalls in DWSIM ignoriert werden
        class hasInteractionParameter(ActivityCoefficientModel >> float): pass

    # Klasse für die enzymatische Reaktion erstellen
    # Die metadata4Ing Ontologie beinhaltet die Klasse 'chemical reaction'
    # Und die SBO die Klasse SBO_0000176 = 'biochemical recation'
        class BioCatalysedReaction(onto.search_one(iri = '*SBO_0000176')): pass
        # Die meisten Biokatalysatoren sind Proteine
        class ProteinCatalysedReaction(BioCatalysedReaction): pass
        class AbzymaticReaction(ProteinCatalysedReaction): pass
        class EnzymaticReaction(ProteinCatalysedReaction): pass
        
        # Es gibt aber auch Nukleinsäuren die bioreaktionen katalysieren können
        class NucleicAcidCatalysedReaction(BioCatalysedReaction):pass
        
        # Disjunktion von Klassen
        # Klassen sind disjunkt, wenn es kein Individuum gibt, das allen Klassen angehört
        # Eine Klassen-Disjointness wird mit der Funktion AllDisjoint() erzeugt, die eine Liste von Klassen als Parameter annimmt
        # Enzyme in der regel Proteine, RNA und DNA können aber auch katalysieren
        AllDisjoint([ProteinCatalysedReaction, NucleicAcidCatalysedReaction])
        
        # Das EnzymeML vergibt jeder aufgezeichneten Reaktion eine ID
        # Data Property
        class hasReaction_ID(BioCatalysedReaction >> str): pass     

    # SBO_0000200 = 'redox reaction' ist Subklasse von SBO_0000176 = 'biochemical recation'
    # 'redox reaction' als Subklasse von Enzymatic_Reaction(Protein_Catalysed_Reaction) verschieben?
    # Enzymatische Reaktionen lassen sich in 6 verschiedene Reaktionsklassen unterscheiden
        class OxidoreductaseReaction(EnzymaticReaction): pass 
        class TransferaseReaction(EnzymaticReaction): pass
        class HydrolyseReaction(EnzymaticReaction): pass
        class LyaseReaction(EnzymaticReaction): pass
        class IsomeraseReaction(EnzymaticReaction): pass
        class LigaseReaction(EnzymaticReaction): pass

         # ABTS-Oxidation ist nur ein Individuum der Klasse Oxidationsreaktion
        AllDisjoint([OxidoreductaseReaction, TransferaseReaction, HydrolyseReaction, LyaseReaction, IsomeraseReaction, LigaseReaction])
        
# Die betrachtete Reaktion als spezifische Information in der Ontologie hinterlegen
# Dafür Übergabe als Individual 
ABTS_Oxidation = OxidoreductaseReaction(Reaction_Name)

# Dem Individual eine Data Property zuschreiben
ABTS_Oxidation.hasReaction_ID.append(Reaction_ID)

with onto:
    # Enzyme werden entsprechend der Reaktion, die sie katalysieren auch in 6 Klassen eingeteilt 
    # SBO_0000460 = 'enzymatic catalyst'
    # Subklasse von 'catalyst', Subklasse von 'stimulator', Subklasse von 'modifier'
        class Oxidoreductase(onto.search_one(iri = '*SBO_0000460')): pass
        class Transferase(onto.search_one(iri = '*SBO_0000460')): pass
        class Hydrolyse(onto.search_one(iri = '*SBO_0000460')): pass
        class Lyase(onto.search_one(iri = '*SBO_0000460')): pass
        class Isomerase(onto.search_one(iri = '*SBO_0000460')): pass
        class Ligase(onto.search_one(iri = '*SBO_0000460')): pass

        # Object Property auf die Oberklasse beziehen
        # Triplett ließt sich: 'Enzymkatalysator katalysiert einzymatische Reaktion' 
        class catalyses(onto.search_one(iri = '*SBO_0000460') >> EnzymaticReaction): pass

        # Wenn ein Enzym der Klasse Oxidoreduktase angehört, dann nicht mehr der Klasse Transferasen
        AllDisjoint([Oxidoreductase, Transferase, Hydrolyse, Lyase, Isomerase, Ligase])  
        
        # Damit aber nicht jedes Enzym plötzlich jede Reaktion umsetzt die Object Property über SubClass Of zuteilen
        # some? oder only?
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

    # DWSIM stellt 4 verschiedene Reaktonstypen bereit
    # Die Test-Prozesse wurden mit Arrhenius Kinetik durchgeführt
        class ReactionType(onto.search_one(iri = '*ChemicalReaction')): pass
        class Conversion(ReactionType): pass
        class Equbrilium(ReactionType): pass
        class Arrhenius_Kinetic(ReactionType): pass
        class Heterogeneous_Catalytic(ReactionType): pass
    
    # Über einen Script Manager können jedoch User spezifische Reaktionskinetiken definiert und durchgeführt werden   
        class UserDefinedReaction(ReactionType): pass
        class ScriptManager(UserDefinedReaction): pass
    
    # Die ABTS Oxidation folgt der Michaelis Menten Kinetik
    # Kinetischen Parameter sind wichtig für die Definition der Reaktionsrate    
        class MichaelisMentenKinetic(ScriptManager): pass
        class Km(MichaelisMentenKinetic): pass
        class kcat(MichaelisMentenKinetic): pass
    
        class hasKmValue(Km >> float): pass
        class hasKmUnit(Km >> str): pass
        class has_kcatValue(kcat >> float): pass
        class has_kcatUnit(kcat >> str): pass            

# Werte von Km und kcat sind abhängig vom Enzym und vom Substrat
Km_LA = Km('Km_Laccase_ABTS')
kcat_LA = kcat('kcat_Laccase_ABTS')

# Im EnzymeML Dokument in mmol/l
# Für das Reaktionsskript im Skript Manager in mol/m3 angeben
Km_LA.hasKmValue.append(0.2)
Km_LA.hasKmUnit.append('mol/m3')

kcat_LA.has_kcatValue.append(1.67)
kcat_LA.has_kcatUnit.append('1/s')

with onto:
    # EnzymeML: Dokumentation von 19 Reaktanten und 19 Proteinen möglich
    # ID wird für die Aufstellung der Reaktionsrate benötigt und steht für die jeweilige Konzentration
    # r = (p1 * kcat * s1)/(Km + s1) -> wobei s1 = ABTS_red statt Oxygen sein muss!!
    # s0 = ABTS_red, s1 = oxygen, s2 = ABTS_ox, s3 = ABTS_red, s4 = oxygen, s5 = ABTS_ox
    # SBO_0000011 = product, SBO_0000015 = substrate
        class s0(onto.search_one(iri ='*SBO_0000015')): pass
        class s1(onto.search_one(iri ='*SBO_0000015')): pass
        class s2(onto.search_one(iri ='*SBO_0000011')): pass
        class s3(onto.search_one(iri ='*SBO_0000015')): pass
        class s4(onto.search_one(iri ='*SBO_0000015')): pass
        class s5(onto.search_one(iri ='*SBO_0000011')): pass
    
    # p0 = Laccase_HTR, p1 = Laccase_SCR, p2 = Laccase
    # SBO_0000460 = enzymatic catalyst
        class p0(Oxidoreductase): pass
        class p1(Oxidoreductase): pass
        class p2(Oxidoreductase): pass            

    # Reaktionsbedingungen definieren
        class ReactionConditions(onto.search_one(iri = '*ChemicalReaction')): pass
        class Temperature(ReactionConditions): pass
        class pH(ReactionConditions): pass
        class Pressure(ReactionConditions): pass
        
        # Der Druckabfall kann in DWSIM auf einen konstanten wert eingestellt werden
        class PressureDrop(Pressure): pass
        class Solvent(ReactionConditions): pass
        class ReactionRate(ReactionConditions): pass
    
        class hasTemperatureValue(Temperature >> float): pass
        class has_pH_Value(pH >> float): pass
        class hasPressureValue(Pressure >> float):pass
        class hasConstantPressureDropValue(PressureDrop >> float): pass
        
        # fluid rate schon in Ontochem
        class hasRateValue(ReactionRate >> float): pass
        class hasTemperatureUnit(Temperature >> str): pass
        class hasPressureUnit(Pressure >> str): pass
        class hasConstantPressureDropUnit(PressureDrop >> str): pass
        class hasFluidRateUnit(ReactionRate >> str): pass

# Werden teilweise aus dem EnzymeML-Dokument geladen
Temperature.hasTemperatureValue.append(Temperature_Value)
Temperature.hasTemperatureUnit.append(Temperature_Unit)
pH.has_pH_Value.append(pH_Value)

# Druckangabe fehlt im EnzymeML-Dokument
Pressure.hasPressureValue.append(1.01325)
Pressure.hasPressureUnit.append('bar')

with onto:
        class ProcessFlowDiagram(Thing): pass
        
        class Reactor(onto.search_one(iri = '*Device')): pass
        class Reactortype(Reactor): pass
        
        class hasVolumeValue(onto.search_one(iri = '*Device') >> float): pass
        class hasVolumeUnit(onto.search_one(iri = '*Device') >> str): pass
        
        class hasLengthValue(onto.search_one(iri = '*Device')>> float): pass
        class hasLengthUnit(onto.search_one(iri = '*Device') >> str): pass
        class hasCompoundMolarFlow(onto.search_one(iri = '*ChemicalMaterialStaged') >> float): pass       
        
SCR = Reactortype(Vessel_Name)
HTR = Reactortype('HelicalTubeReactor')

# Reaktorvolumen im EzymeMl Dokument in ml
# Für DWSIM in m3 angeben
SCR.hasVolumeValue.append(reacV)
SCR.hasVolumeUnit.append('m³')
HTR.hasVolumeValue.append(reacV)
HTR.hasVolumeUnit.append('m³')

# Die Reaktorlänge fehlt im EnzymeMl Dokument
# Ist laut Paper 4 m -> hier aber in DWSIM: Zu hoher Druckabfall
# Druckabfall kann festgelegt werden (siehe oben)
# 0.004 Wert der Simuliert werden kann und mit Druckabfall von 11 Pa
reacL = 0.004

SCR.hasLengthValue.append(reacL)
SCR.hasLengthUnit.append('m')
HTR.hasLengthValue.append(reacL)
HTR.hasLengthUnit.append('m')

# InletFlow comparable with ontochem class 'ChemicalMaterialInput_Manual'
InletLaccase = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('InletLaccase')
InletABTS_red = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('InletABTS_red')
InletOxygen = (onto.search_one(iri = '*ChemicalMaterialInput_Manual'))('InletOxygen')

# Die Inletströme wurden über die Konzentration und Volumenstrom ermittelt
# In DWSIM kann der Molstrom in mol/s festgelegt werden
InletLaccase.hasCompoundMolarFlow.append(9.66667E-07) # mol/s
InletABTS_red.hasCompoundMolarFlow.append(8.08333E-05) # mol/s
InletOxygen.hasCompoundMolarFlow.append( 1.655E-07) # mol/s

with onto:
    
    # Klassen zu Beschreibung einer Projektorganisiation
        class Project(Thing): pass
        class Institution(Project): pass
        class Agent(Institution): pass         
        class Engineering_Step(Project): pass # Basic Engineering, Detail Engineering
        class Processdesign(Engineering_Step): pass
        class Processsimulation(Processdesign): pass
        class Documentation(Project): pass
    
        # Triplett liest sich: 'Ein Institut erhält ein Projekt'    
        class receives(Institution >> Project): pass
        
        # Triplett liest sich: 'Ein Agent ist angestellt am Institut'
        class isEmployedAt(Agent >> Institution): pass
        
        # Triplett liest sich: 'Ein Agent führt Projekt aus'
        class executes(Agent >> Project): pass
        
        # Triplett liest sich: 'Ein Projekt ist unterteilt in Engineering Step'
        class isDividedInto(Engineering_Step >> Project): pass
        
        # Triplett liest sich: 'Ein Engineering Step ist eine Prozessimulation'
        class is_a(Processsimulation >> Engineering_Step): pass
        
        # Triplett liest sich: ' Eine Dokumentation sichert ein Projekt'
        class saves(Documentation >> Project): pass

        # Data Property: Eigentlich giibt es für ein Datum sowas wie datetime -> aber Error
        # Jedes Projekt hat ein Startdatum
        class hasProjectstart(Project >> str): pass
        #class Has_Projectstart(Project >> datetime.date): pass
    
    # Labordaten können direkt in einem ELN gesichert werden
    # So werden Dokumemte standardisiert gesichert
        class ElectronicLabNotebook(Documentation): pass
        class EnzymeML_Documentation(ElectronicLabNotebook): pass
    
        class hasTitel(EnzymeML_Documentation >> str): pass
        class hasCreator(EnzymeML_Documentation >> str): pass
        class hasCreatorMail(Agent >> str): pass
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


onto.save(file="Finale_Onto_.owl", format="rdfxml")

# Alle Pakete für die Simulation in DWSIM importieren
# Das os-Modul Das os-Modul ist das wichtigste Modul zur Interaktion mit dem Betriebssystem
# und ermöglicht durch abstrakte Methoden ein plattformunabhängiges Programmieren
import os

# Universally Unique Identifier (UUID) ist eine 128-Bit-Zahl, welche zur Identifikation von Informationen in Computersystemen verwendet wird
import uuid

# Die Common Language Runtime, kurz CLR, ist der Name der virtuellen Laufzeitumgebung von klassischen
# .Net-Framework-Anwendungen. Die CLR stellt damit eine konkrete Implementierung der Laufzeitumgebung der Common Language Infrastructure für das .NET Framework dar 
import clr 

# Importiere Python Module
import pythoncom
import System
pythoncom.CoInitialize()

from System.IO import Directory, Path, File
from System import String, Environment
from System.Collections.Generic import Dictionary
 
# Pfad, wo DWSIM-Ordner mit allen Paketen hinterlegt ist
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
clr.AddReference(dwsimpath + "DWSIM.FlowsheetSolver.dll")
clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
clr.AddReference(dwsimpath + "Newtonsoft.Json")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

from enum import Enum
# Paket, um Kalkulationen durchzuführen 
from DWSIM import FlowsheetSolver
# Paket, um ein neues Fließbild zu erstellen und darauf zuzugreifen
from DWSIM import Interfaces
from System import *

from System.Linq import *
from DWSIM import *
from DWSIM import FormPCBulk
from DWSIM.Interfaces import *
from DWSIM.Interfaces.Enums import*

# Paket, um Fließbild zu zeichnen
from DWSIM.Interfaces.Enums.GraphicObjects import *

# Paket, um neu erstellte Komponenten als JSON datei abzuspeichern
from Newtonsoft.Json import JsonConvert, Formatting

from DWSIM.Thermodynamics import*
from DWSIM.Thermodynamics.BaseClasses import *
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import *

# Pakte, um Pseudocompound Creator auszuführen
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization import GenerateCompounds
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization.Methods import *

Directory.SetCurrentDirectory(dwsimpath)

# Automatisierungsmanager erstellen
# Create automatin manager
interf = Automation3()
sim = interf.CreateFlowsheet()

# Komponenten für die Simulation laden
compounds = [catalysts[0], main_substrates[0], main_products[0], reactants[0], reactants[1]]

for comp in compounds:
    sim.AddCompound(comp)

         
# Stoichiometric Koeffizienten den Komponenten zuordnen
# Koeffizienten aus der Ontologie ziehen   
stoich_coeffs = {
    catalysts[0]: onto.search_one(label = 'Laccase').hasStoichiometriCoefficient.first(),
    main_substrates[0]: onto.search_one(label = 'ABTS_red').hasStoichiometriCoefficient.first(),
    main_products[0]: onto.search_one(label = 'ABTS_ox').hasStoichiometriCoefficient.first(),
    reactants[0]: onto.search_one(label = 'Oxygen').hasStoichiometriCoefficient.first(),
    reactants[1]: onto.search_one(label = 'Water').hasStoichiometriCoefficient.first()
    }

# Direct order Koeffizienten den Komponenten zuordnen
# Koeffizienten aus der Ontologie ziehen  
direct_order_coeffs = {
    catalysts[0]: onto.search_one(label = 'Laccase').hasDirect_OrderCoefficient.first(),
    main_substrates[0]: onto.search_one(label = 'ABTS_red').hasDirect_OrderCoefficient.first(),
    main_products[0]: onto.search_one(label = 'ABTS_ox').hasDirect_OrderCoefficient.first(),
    reactants[0]: onto.search_one(label = 'Oxygen').hasDirect_OrderCoefficient.first(),
    reactants[1]: onto.search_one(label = 'Water').hasDirect_OrderCoefficient.first()
    }

# Reverse order Koeffizienten den Komponenten zuordnen
# Koeffizienten aus der Ontologie ziehen  
reverse_order_coeffs = {
    catalysts[0]: onto.search_one(label = 'Laccase').hasReverse_OrderCoefficient.first(),
    main_substrates[0]: onto.search_one(label = 'ABTS_red').hasReverse_OrderCoefficient.first(),
    main_products[0]: onto.search_one(label = 'ABTS_ox').hasReverse_OrderCoefficient.first(),
    reactants[0]: onto.search_one(label = 'Oxygen').hasReverse_OrderCoefficient.first(),
    reactants[1]: onto.search_one(label = 'Water').hasReverse_OrderCoefficient.first()
    }   

# Dictionary festlegen   
comps = Dictionary[str, float]()
dorders = Dictionary[str, float]()
rorders = Dictionary[str, float]()

# Komponenten + Koeffizienten der Simulation hinzufügen
for comp in compounds:
    comps.Add(comp, stoich_coeffs[comp])
    dorders.Add(comp, direct_order_coeffs[comp])
    rorders.Add(comp, reverse_order_coeffs[comp])    

# Arrhenius Kinetik für den Testdurchlauf
# Ideale Kinetik   
kr1 = sim.CreateKineticReaction(Reaction_Name, "ABTS Oxidation using Laccase", 
        comps, dorders, rorders, main_substrates[0], "Mixture", "Molar Concentration", 
        "kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")    
    
# Ströme definiere => Ströme werden als Kanten betrachtet
# Zwei Inletströme mit Reaktant 1 und Reaktant 2
# Aus dem Mixer kommt ein Mix-Strom der in den Reaktor führt
# Aus dem Reaktor kommt ein Outlet-Strom als Produktstrom
# Der Reaktor benötigt einen Energiestrom 
stream_info = [
    {'type': ObjectType.MaterialStream, 'x': 0, 'y': 10, 'name': 'Reactant_1'},
    {'type': ObjectType.MaterialStream, 'x': 0, 'y': 60, 'name': 'Reactant_2'},
    {'type': ObjectType.MaterialStream, 'x': 100, 'y': 50, 'name': 'Mixture'},
    {'type': ObjectType.MaterialStream, 'x': 250, 'y': 50, 'name': 'Product_1'},
    {'type': ObjectType.EnergyStream, 'x': 100, 'y': 90, 'name': 'Heat'}
    ]

streams = []
for s in stream_info:
    stream = sim.AddObject(s['type'], s['x'], s['y'], s['name'])
    # Save streams in variable
    streams.append(stream)
    if s['name'] == 'Reactant_1':
        m1 = stream
    elif s['name'] == 'Reactant_2':
        m2 = stream
    elif s['name'] == 'Mixture':
        m3 = stream
    elif s['name'] == 'Product_1':
        m4 = stream
    elif s['name'] == 'Heat':
        e1 = stream
    
# Geräte definieren => Geräte werden als Knoten bezeichnet   
# Ein Mixer, der die Inletsröme mischt
# Ein PFR, der den CFI simuliert
# Annahme Turbulente Strömung
devices_info = [
    {'type': ObjectType.Mixer, 'x': 50, 'y': 50, 'name': 'Mixer'},
    {'type': ObjectType.RCT_PFR, 'x': 150, 'y': 50, 'name': 'PFR'}
    ]

devices = []
for d in devices_info:
    device = sim.AddObject(d['type'], d['x'], d['y'], d['name'])
    # Save devices in variable 
    devices.append(device)
    if d['name'] == 'PFR':
        pfr = device
    elif d['name'] == 'Mixer':
        MIX1 = device

# Alle Knoten und Kanten müssen als Object der Simulation übergeben werden
m1 = m1.GetAsObject()
m2 = m2.GetAsObject()
m3 = m3.GetAsObject()
m4 = m4.GetAsObject()
e1 = e1.GetAsObject()
MIX1 = MIX1.GetAsObject()
pfr = pfr.GetAsObject()

# Die Knoten werden über Kanten verbunden
# Reaktant 1 un 2 führen in den Mixer
sim.ConnectObjects(m1.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, MIX1.GraphicObject, -1, -1)
# Mixtur führt aus dem Mixer
sim.ConnectObjects(MIX1.GraphicObject, m3.GraphicObject, -1, -1)
# Mixtur führt in den PFR
pfr.ConnectFeedMaterialStream(m3, 0)
# Produktstrom führt aus dem PFR
pfr.ConnectProductMaterialStream(m4, 0)
# Energiestrom führt zum PFR, weil ihm für die Reaktion Wärmezugeführt wird
# Allerdings Reaktion bei Raumtemperatur
# Daher eigentlich keine hohe Wärmezufuhr 
pfr.ConnectFeedEnergyStream(e1, 1)

# PFR Eigenschaften
# Adiabat
pfr.ReactorOperationMode = Reactors.OperationMode.Adiabatic
# Dimensionierung festlegen: Volumen und Länge
# In jedem Fall muss das Volumen festgelegt werden
# Optiional kann zusätzlich die Reaktorlänge ODER Durchmesser angegeben werden
pfr.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length    

# Dimensionierung aus der Ontologie ziehen    
pfr.Volume = reacV; # m3
pfr.Length = reacL; # m

# Für die Thermodynamik ein Property Package festlegen
# Raoult's Law ideal
# Für die vorliegende Simulation NRTL auswählen
# Manuell müssen dafür die fehlenden Interaktionsparameter ausgeschaltet werden
sim.CreateAndAddPropertyPackage("Raoult's Law")
sim.CreateAndAddPropertyPackage("NRTL")

# Die Temperatur jeder Kante festlegen
# Wert in in der Ontologie hinterlegt
materials = {"m1": Temperature.hasTemperatureValue.first(),
             "m2": Temperature.hasTemperatureValue.first(),
             "m3": Temperature.hasTemperatureValue.first(),
             "m4": Temperature.hasTemperatureValue.first()
             }

for material, temperature in materials.items():
    globals()[material].SetTemperature(temperature)


m1.SetMolarFlow(0.0) # will set by compound

# Molstrom der Inletströme wurden über die Anfangskonzentrationen und über den jeweiligen Volumenstrom ermittelt
# Klasse für Anfangskonzentrationen integrieren?
m1.SetOverallCompoundMolarFlow(reactants[0], InletOxygen.hasCompoundMolarFlow.first()) # mol/s
m1.SetOverallCompoundMolarFlow(main_substrates[0], 0.0)  # mol/s
m1.SetOverallCompoundMolarFlow(catalysts[0], 0.0) # mol/s

m2.SetOverallCompoundMolarFlow(reactants[0], 0.0) # mol/s
m2.SetOverallCompoundMolarFlow(main_substrates[0], InletABTS_red.hasCompoundMolarFlow.first())  # mol/s
m2.SetOverallCompoundMolarFlow(catalysts[0], InletLaccase.hasCompoundMolarFlow.first()) # mol/s

# Arrhenius Gleichung hinzufügen
sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", True, 0)    


# Ein Skript definieren, um den Script Manager in DWSIM zu verwenden
# Über den Script Manager eigene Kinetik importieren
# https://sourceforge.net/p/dwsim/discussion/scripting/thread/c530736cdb/?limit=25#1667
def createScript(obj_name):
    #GUID = str(uuid.uuid1())
    GUID = obj_name
    sim.Scripts.Add(GUID, FlowsheetSolver.Script())
    #By not declaring the ID the tabs of each script is not loaded
    #sim.Scripts.TryGetValue(GUID)[1].ID = GUID
    sim.Scripts.TryGetValue(GUID)[1].Linked = True
    sim.Scripts.TryGetValue(GUID)[1].LinkedEventType = Interfaces.Enums.Scripts.EventType.ObjectCalculationStarted
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectName = obj_name
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectType = Interfaces.Enums.Scripts.ObjectType.FlowsheetObject
    sim.Scripts.TryGetValue(GUID)[1].PythonInterpreter = Interfaces.Enums.Scripts.Interpreter.IronPython
    sim.Scripts.TryGetValue(GUID)[1].Title = obj_name
    sim.Scripts.TryGetValue(GUID)[1].ScriptText = str()

# Skript def ausführen
createScript('ABTS_kinetics')

# Auf das geschriebene Skript im Script Manager zugreifen und der Simulation hinzufügen
myreaction = sim.GetReaction('ABTS Oxidation')
myscripttitle = 'ABTS_kinetics'
myscript = sim.Scripts[myscripttitle]
# Skripttext schreiben
myscript.ScriptText = str("import math\n"
"Km = {} # mol/m3\n"
"kcat = {} # 1/s\n"
'\n'
'pfr = Flowsheet.GetFlowsheetSimulationObject("""{}""")\n'
'T = pfr.OutletTemperature\n'
'Flowsheet = pfr.FlowSheet\n'
'\n'
'obj = Flowsheet.GetFlowsheetSimulationObject("""Mixture""")\n'
'\n'
'# Access to compound list\n'
'value = obj.GetOverallComposition()\n'
'\n'
'# Access to compound amound\n'
'z_Laccase = value[0]\n'
'z_ABTS_red = value[2]\n'
'\n'
'n = obj.GetPhase("""Overall""").Properties.molarflow # mol/s\n'
'Q = obj.GetPhase("""Overall""").Properties.volumetric_flow # m3/s\n'
'\n'
'Conc_Laccase = z_Laccase*n/Q # mol/m3\n'
'Conc_ABTS_red = z_ABTS_red*n/Q # mol/m3\n'
'\n'
'r = ((Conc_Laccase * kcat * Conc_ABTS_red)/(Km + Conc_ABTS_red)) # mol/(m3*s)'.format(Km_LA.hasKmValue.first(), kcat_LA.has_kcatValue.first(), 'PFR'))   
    
# Mit dieser Zeile wird in Settings das Skript im Dropdown Feld ausgewählt
myreaction.ScriptTitle = myscripttitle

# Über diese Zeile wird glaube ich das Skript ausgeführt
#myreaction.ReactionKinetics = 1 # script



# Anfrage: Kalkulation des Flowsheets
errors = interf.CalculateFlowsheet4(sim);

print("Reactor Heat Load: {0:.4g} kW".format(pfr.DeltaQ))
for c in pfr.ComponentConversions:
    if (c.Value > 0): print("{0} conversion: {1:.4g}%".format(c.Key, c.Value * 100.0))

if (len(errors) > 0):
    for e in errors:
        print("Error: " + e.ToString())

# Reaktorprofil (temperature, pressure and concentration)
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


# Datei speichern
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), 
                              "Finale_ABTS_Oxidation.dwxmz")
interf.SaveFlowsheet(sim, fileNameToSave, True)

# PDF als Bild speichern und direkt ausgeben
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
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "Finale_ABTS_Oxidation.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image
im = Image.open(imgPath)
im.show()    
