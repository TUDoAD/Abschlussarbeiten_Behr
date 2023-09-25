# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 13:58:00 2023

@author: Alexander Behr
"""


####################################################
## Ontology Manipulation
####################################################

from owlready2 import *
import pyenzyme as pe
from pyenzyme import EnzymeMLDocument, EnzymeReaction, Complex, Reactant, Protein, Creator
from pyenzyme.enzymeml.models import KineticModel, KineticParameter
import pandas as pd


## 
# To make sure, owlready2 is able to use HermiT for reasoning, configure the path to the java interpreter
# e.g.:
# owlready2.JAVA_EXE = "C://Users//..//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"
##


## USER INPUT
# load base ontology
onto_world = owlready2.World()
onto = onto_world.get_ontology("./ontologies/BaseOnto.owl").load()

# Ohne diese Definition wird die Ontologie für set_relations(test_dict, onto) nicht gefunden
BaseOnto = onto

#####
# EnzymeML + erweitert readin #
#####

## USER INPUT
# Load EnzymeML Excel-file
# Make sure, Macros are turned OFF, else the pH-value might not be parsed correctly
enzmldoc = pe.EnzymeMLDocument.fromTemplate("./ELNs/EnzymeML_Template_18-8-2021_KR.xlsm")

"""
# visualize first measurement
fig = enzmldoc.visualize(use_names=True, trendline=True, measurement_ids=["m0"])
"""

# Infos zum Dokument-Autor
for Creator in enzmldoc.creator_dict.values():
    Creator_Name = Creator.given_name # Katrin
    Creator_Familyname = Creator.family_name # Rosenthal
    Creator_Mail = Creator.mail # katrin.rosenthal@tu-dortmund.de

# Infos zum Reaktor
# 
for vessel in enzmldoc.vessel_dict.values():
    Vessel_Name = vessel.name # Straight tube reactor, für die Simualtion wird ein PFR genommen
    Vessel_ID = vessel.id # v1
    # Reaktorvolumen eig 8, aber wurde für die Simulation angepasst (tau=64s)
    Vessel_Volume = vessel.volume # 8
    Vessel_Unit = vessel.unit # ml
    
# Infos zur Reaktion
for reaction in enzmldoc.reaction_dict.values():
    Reaction_Name = reaction.name # ABTS Oxidation
    Reaction_ID = reaction.id # r2
    pH_Value = reaction.ph # 5.2
    Temperature_Value = reaction.temperature # 311.15
    Temperature_Unit = reaction.temperature_unit # K

# Infos zum Protein
for protein in enzmldoc.protein_dict.values():
    Protein_Name = protein.name # Laccase
    Protein_SBO = protein.ontology # SBO_0000252 = Protein
    Protein_Sequence = protein.sequence # wichtig für das Molekulargewicht später
    Protein_EC_Number = protein.ecnumber # 1.10.3.2
    Protein_Organism = protein.organism # Trametes versicolor
    Protein_UniProtID = protein.uniprotid # None, should be 'D2CSE5'



# Excel Datei 'Ergänzendes Laborbuch' laden
# Sheet0 beinhaltet Reaktionsteilnehmer und -koeffizienten
# Sheet1 beinhaltet die Stoffdaten, die für den Compound Creator relevant sind
# Sheet2 beinhaltet zusätzliche Stoffdaten
sheet0 = pd.read_excel("./ELNs/Ergänzendes Laborbuch_Kinetik_1.xlsx", sheet_name=0)
sheet1 = pd.read_excel("./ELNs/Ergänzendes Laborbuch_Kinetik_1.xlsx", sheet_name=1)
sheet2 = pd.read_excel("./ELNs/Ergänzendes Laborbuch_Kinetik_1.xlsx", sheet_name=2)
# Excel 'Ergänzendes Laborbuch' Sheet3 laden für fehlende Parameter
sheet3 = pd.read_excel("./ELNs/Ergänzendes Laborbuch_Kinetik_1.xlsx", sheet_name=3)
   
#####
# EnzymeML + erweitert readin ENDE#
#####



#####
# Ontology-Extension der Base Ontology #
#####
def onto_base_class_extender(onto):
    with onto:
        # Komponenten: DWSIM stellt 6 Datenbanken zur verfügung (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes)
        # Daraus ergeben sich 1500 verfügbare Komponenten für die Simulation
        # Datenbanken werden der metadata4Ing Klasse 'ChemicalSubstance' subsumiert
            class modeledSubstance(onto.search_one(iri = '*ChemicalSubstance')): pass
            class DefaultDatabase(modeledSubstance): pass
            class DWSIMCompound(DefaultDatabase): pass
            #class ChemSep(DefaultDatabase): pass
            #class Biodiesel(DefaultDatabase): pass
            #class CoolProp(DefaultDatabase): pass
            #class ChEDL(DefaultDatabase): pass
            #class Electrolytes(DefaultDatabase): pass
        
            # Object property -> Triplett liest sich: 'Stoffdatenbank liefert chemische Substanz'
            class provides(modeledSubstance >> onto.search_one(iri = '*ChemicalSubstance')): pass

        # DWSIM bietet die Möhlichkeit Komponenten zu importieren über: Online-Quellen, Json- oder XML_Dateien
        # Zusätzlich kann der User über den 'Compound Creator' Stoffe erstellen
        # So entsteht eine von DWSIM 'abweichende Datenbank'
            class DeviatingDatabase(modeledSubstance): pass
            class OnlineSource(DeviatingDatabase): pass
            class UserDefinedCompound(DeviatingDatabase): pass

            # Object property -> Triplett liest sich: 'User-definierte Komponente schafft abweichende Datenbank'
            class creates(UserDefinedCompound >> DeviatingDatabase): pass 
        
        # Um selbst erstellte Komponenten der Simulation verfügbar zu machen, müssen diese in dem spezifischen Ordner 'addcomps' hinterlegt sein
        # Ordner findet sich unter: "C:\Users\49157\AppData\Local\DWSIM8\addcomps"
            class AddCompoundFile(UserDefinedCompound): pass      
            class XMLfile(AddCompoundFile): pass
            class JSONfile(AddCompoundFile): pass
            
            # Object property -> Triplett liest sich: 'AddCompound-Ordner muss user-definierte Komponente enthalten'
            class mustInclude(AddCompoundFile >> UserDefinedCompound): pass


# Code für die dynamische Erstellung von Komponenten/Substanzen als Klassen
# Die Elemente einer Stoffliste werden entweder der Oberklasse JSON-Datei oder DWSIM-Komponente subsumiert

def class_creation(sheet: pd.DataFrame, onto):
    reactantRow = -1
    # Die Zeile ermitteln, in der die Labels der Reaktanten stehen
    for i in range(len(sheet.index)):
        if sheet.iloc[i, 0] == "hasCompoundName":
            reactantRow = i
            break

    # Das sheet durchsuchen nach der Zeile mit 'inDWSIMdatabase', dann die Spalten in dieser Zeile auslesen
    for index, row in sheet.iterrows():
        if row[0] == "inDWSIMdatabase":
            for j in range(1, len(row)):
                # Namen des Reaktanten der aktuellen Spalte auslesen
                substance = sheet.iloc[reactantRow, j]
                if row[j] == "True":
                    # Falls 'inDWSIMdatabase' = "True", Klasse mit 'DWSIMCompound' erzeugen:
                    # codestring aufsetzen, .format(substance,substance) am Ende ersetzt jeden {}-Teil des Strings mit Inhalt der Variablen substance
                    # Neue Komponenten müssen als JSON-file über den AddCompoumd-Ordner hinzugefügt werden
                    # Sind die Komponenten einmal hinzugefügt worden, stehen sie für jede anschließende Simulation zur Verfügung
                    codestring = """with onto:
                                class {}(onto.search_one(iri = '*DWSIMCompound')):
                                    label = '{}'
                                    pass
                                """.format(substance, substance)
                else:
                    # Ansonsten Klasse mit 'JSONfile' erzeugen
                    codestring = """with onto:
                                class {}(onto.search_one(iri = '*JSONfile')): 
                                    label = '{}'
                                    pass
                                """.format(substance, substance)

                # Code, der im codestring enthalten ist compilieren
                code = compile(codestring, "<string>", "exec")

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

# Stoffliste aus dem ergänzenden Laborbuch
# Laccase, ABTS_red, ABTS_ox, Oxygen, Water
test_substances = [sheet0.iloc[2,1], sheet0.iloc[2,2], sheet0.iloc[2,3], sheet0.iloc[2,4], sheet0.iloc[2,5]]

# Wörterbuch mit Stoffeigenschaften erstellen
# Eigenschaften beachten, die relevant sind für die Simulation in DWSIM
# Die relative Dichte und der Normalsiedepunkt, werden gebraucht für 'bulk c7+ pseudocompound creator setting'
# Auf diese Weise können Stoffe direkt über einen Code erstellt werden
# und DWSIM schätzt durch entsprechende Modelle fehlende Stoffeigenschaften ab
# z.B. wird das Molekulargewicht oder die chemische Strukturformel abgeschätzt
# Im vorliegenden Fall weichen die abgeschätzten Werte zu weit von den Literaturwerten ab
# Weshalb Stoffeigenschaften manuell in der JSON-datei korrigiert wurden
# und fehlende Stoffdaten durch die des Lösemittels ersetzt

# Dict, in dem alle Eigenschaften von Laccase hinterlegt sind
data0 = {}
for row in sheet0.iloc[3:7].iterrows():
    data0[row[1][0]] = row[1][1]

for row in sheet1.iloc[3:31].iterrows():
    data0[row[1][0]] = row[1][1]

for row in sheet2.iloc[3:14].iterrows():
    data0[row[1][0]] = row[1][1]

# Dict, in dem alle Eigenschaften von ABTS_red hinterlegt sind
data1 = {}
for row in sheet0.iloc[3:7].iterrows():
    data1[row[1][0]] = row[1][2]
    
for row in sheet1.iloc[3:31].iterrows():
    data1[row[1][0]] = row[1][2]

for row in sheet2.iloc[3:14].iterrows():
    data1[row[1][0]] = row[1][2]

# Dict, in dem alle Eigenschaften von ABTS_ox hinterlegt sind     
data2 = {}
for row in sheet0.iloc[3:7].iterrows():
    data2[row[1][0]] = row[1][3]
    
for row in sheet1.iloc[3:31].iterrows():
    data2[row[1][0]] = row[1][3]

for row in sheet2.iloc[3:14].iterrows():
    data2[row[1][0]] = row[1][3]

# Dict, in dem alle Eigenschaften von Oxygen hinterlegt sind
data3 = {}
for row in sheet0.iloc[3:7].iterrows():
    data3[row[1][0]] = row[1][4]

# Dict, in dem alle Eigenschaften von Wasser hinterlegt sind
data4 = {}
for row in sheet0.iloc[3:7].iterrows():
    data4[row[1][0]] = row[1][5]
    
test_dict = {sheet0.iloc[2,1]: data0, sheet0.iloc[2,2]: data1, sheet0.iloc[2,3]: data2,
             sheet0.iloc[2,4]: data3, sheet0.iloc[2,5]: data4}

# Aufrufen von Funktion class_creation(),um die Reaktanten in Sheet0 durchzugehen
class_creation(sheet0, onto)

dataProp_creation(test_dict, onto)

set_relations(test_dict, onto)

# Ontologie zwischenspeichern
onto.save(file="./ontologies/Zwischenstand_Onto_.owl", format="rdfxml")

#####
# Ontology-Extension der Base Ontology #
#####
