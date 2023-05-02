# -*- coding: utf-8 -*-
"""
Created on Tue May  2 13:51:01 2023

@author: 49157
"""

# Nicht Teil des finalen Codes, da Test
# Intention:
    # Dynamische Erstellung von Klassen, die Stoffe und Stoffdaten wiedergeben
    # Diese Stoffe und Stoffdaten werden verwendet, um die Substanzen automatisiert der DWSIM Datenbank zu übergeben
    # JSON datei in addcomps Ordner
# DWSIM unterstützt Modelle, um fehlende Stoffdaten Abschätzen zu können
# Im User Guide Kapitel: Property Estimation Method
# https://dwsim.org/wiki/index.php?title=IronPython_Script_Snippets#Create_Pseudocompounds_from_Bulk_C7.2B_Assay_Data_.2F_Export_to_JSON_files


# Erst wie im finalen Code: Stoffklassen und Stoffeigenschaften einer Ontologie übergeben
# Im Test: Neue Ontologie öffnen
# Damit die für den finalen Code gespeicherten Substanzen nicht überschrieben werden, hier Testnamen verwenden

from owlready2 import *

def class_creation(substance_list, onto):
    # Durchiterieren durch substance_list, um enthaltene Strings als Klassen 
    # in Ontologie onto einzusetzen
    for substance in test_substances:
        # codestring aufsetzen, .format(substance,substance) am Ende ersetzt 
        # jeden {}-Teil des Strings mit Inhalt der Variablen substance
        codestring = """with onto:
            class {}(Thing):
                label = '{}'
                pass
            """.format(substance,substance)
        
        # ABTSox und ABTSred der Klasse ABTS unterordnen
        if substance == "ABTSoxTest" or substance == "ABTSredTest":
            codestring = """with onto:
            class {}({}):
                label = '{}'
                pass
            """.format(substance,"ABTSTest",substance)
        
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
            
        
# Eine leere Ontologie aufrufen
onto = get_ontology("http://test.org/onto.owl")

# Testsubstanzen nur die Stoffeigenschaften übergeben, die DWSIM für die Abschätzung benötigt
# Zusätzlich angeben welche Rolle die Reaktionsteilnehmer in der Reaktion übernehmen
test_substances = ["LaccaseTest", "ABTSTest", "ABTSoxTest", "ABTSredTest", "Oxygen", "Water"]

test_dict = {"LaccaseTest": {"hasRelativeDensities": 1000.0/1000.0,
                            "has_nbps": 55 + 273.15, 
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
                            "isBaseComponent": False},
             
            "ABTSoxTest":  {"hasRelativeDensities": 1370.0/1000.0,
                            "has_nbps": 100 + 273.15, # in K (Normal Boiling Point von Wasser)
                            "has_nbps_Unit": 'K',
                          
                            "isMainProduct": True,
                          
                            # Sind aus dem Paper: From Coiled Flow Inverter to Stirred Tank Reactor - Bioprocess Development and Ontology Design
                            "hasStoichiometriCoefficient": 4,
                            "hasDirect_OrderCoefficient": 0.0,
                            "hasReverse_OrderCoefficient": 0.0,
  
                            "isBaseComponent": False},
             
            "ABTSredTest": {"hasRelativeDensities": 1372.0/1000.0,
                            "has_nbps": 101 + 273.15, # in K (Normal Boiling Point von Wasser)
                            "has_nbps_Unit": 'K',
                          
                            "isMainSubstrate": True,
                          
                            "hasStoichiometriCoefficient": -4,
                            "hasDirect_OrderCoefficient": 1.0,
                            "hasReverse_OrderCoefficient": 0.0,
  
                            "isBaseComponent": True},
             
             "Oxygen": {"has_stoichiometric_coefficient": -1,
                        "has_direct_order_coefficient": 0.0,
                        "has_reverse_order_coefficient": 0.0},
             
             "Water": {"has_stoichiometric_coefficient": 2,
                       "has_direct_order_coefficient": 0.0,
                       "has_reverse_order_coefficient": 0.0}
             }

# Aufrufen von Funktion class_creation(), um alle Strings aus Liste test_substances
# in Ontologie einzubauen
class_creation(test_substances, onto)

dataProp_creation(test_dict, onto)

set_relations(test_dict, onto)

# Save the ontology
onto.save(file="Komponenten_Test_Abschätzungsmethode.owl", format="rdfxml")

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

interf = Automation3()
sim = interf.CreateFlowsheet()
 
# Name, relative Dichte und Normalsiedepunkt angeben, wenn bekannt
names = [catalysts[0], main_substrates[0], main_products[0]]
relative_densities = [onto.search_one(label = 'LaccaseTest').hasRelativeDensities.first(),
                      onto.search_one(label = 'ABTSredTest').hasRelativeDensities.first(),
                      onto.search_one(label = 'ABTSoxTest').hasRelativeDensities.first()]
                       
nbps = [onto.search_one(label = 'LaccaseTest').has_nbps.first(),
        onto.search_one(label = 'ABTSredTest').has_nbps.first(),
        onto.search_one(label = 'ABTSoxTest').has_nbps.first()]
 
n = 3

# bulk c7+ pseudocompound creator setting
# Abschätzungmethoden für Molekulargewicht, kritische Eigenschaften (Tc und Pc), 
# 'Petroleum Fractions' 
Tccorr = "Riazi-Daubert (1985)"
Pccorr = "Riazi-Daubert (1985)"
AFcorr = "Lee-Kesler (1976)"
MWcorr = "Winn (1956)"
adjustZR = True
adjustAf = True
 
# Anfangswerte für MW, SG und NBP 
mw0 = 65
sg0 = 0.65
nbp0 = 320

# pseudocompound generator 
comps = GenerateCompounds()
 
for i in range(0, n):
    
    # Es wird nur 1 Pseudoverbindung für jeden Eintrag in der Liste der Testdaten erzeugt
    # Normalerweise erzeugen wir 7 bis 10 Pseudoverbindungen für jeden Satz von Testdaten (MW, SG und NBP) (?)
 
    comp_results = comps.GenerateCompounds(names[i], 1, Tccorr, Pccorr, AFcorr, 
                                           MWcorr, adjustAf, adjustZR, None, 
                                           relative_densities[i], nbps[i], None, 
                                           None, None, None, mw0, sg0, nbp0)
 
    comp_values = list(comp_results.Values)
    comp_values[0].Name = names[i]
    comp_values[0].ConstantProperties.Name = names[i]
    comp_values[0].ComponentName = names[i]
    
    # Speichern der Verbindung in einer JSON-Datei, die bei jeder Simulation wieder geladen werden kann
    # WICHTIG: Speichern der JSON-Datei im Ordner "addcomps", um die Verbindung in die Simulation importieren zu können
 
    System.IO.File.WriteAllText("C:\\Users\\49157\\AppData\\Local\\DWSIM8\\addcomps\\"
                                + str(names[i]) + ".json", 
                                JsonConvert.SerializeObject(comp_values[0].ConstantProperties, 
                                                            Formatting.Indented))