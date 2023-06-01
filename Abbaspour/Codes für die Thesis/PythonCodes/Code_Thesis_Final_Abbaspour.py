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

# Die erste Messung visualisieren lassen
fig = enzmldoc.visualize(use_names=True, trendline=True, measurement_ids=["m0"])

# Lade alle relevanten Informationen aus der EnzymeML Dokumentation
# Relevant für die DWSIM Simulation

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

# Da das EnzymeML Dokument nicht alle notwendigen Informationen beinhaltet,
# soll ein weiteres Excel Sheet ausgefüllt werden (im Labor)
import pandas as pd

# Excel Datei 'Ergänzendes Laborbuch' laden
# Sheet0 beinhaltet Reaktionsteilnehmer und -koeffizienten
# Sheet1 beinhaltet die Stoffdaten, die für den Compound Creator relevant sind
# Sheet2 beinhaltet zusätzliche Stoffdaten
sheet0 = pd.read_excel("./Ergänzendes Laborbuch.xlsx", sheet_name=0)
sheet1 = pd.read_excel("./Ergänzendes Laborbuch.xlsx", sheet_name=1)
sheet2 = pd.read_excel("./Ergänzendes Laborbuch.xlsx", sheet_name=2)
    
# Ontologie Design
# Relevante Entitäten der bestehenden Ontologie hinzufügen
# (Klassen, Individuen und Relationen definieren)
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
                    # Falls 'inDWSIMdatabase' = "True"/"true", Klasse mit 'DWSIMCompound' erzeugen:
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
onto.save(file="Zwischenstand_Onto_.owl", format="rdfxml")

# Erstellen von leeren Listen, um Reaktionsteilnehmer in Abhängigkeit ihrer Funktion zu sichern
catalysts = []
main_substrates = []
main_products = []
reactants = []

for index, row in sheet0.iterrows():
    if row[0] == "hasRole":
        for i in range(1, len(row)):
            if row[i] == "Catalyst":
                catalysts.append(sheet0.iloc[2, i])                
            elif row[i] == "MainSubstrate":
                main_substrates.append(sheet0.iloc[2, i])                
            elif row[i] == "MainProduct":               
                main_products.append(sheet0.iloc[2, i])                
            elif row[i] == "Reactant":
                reactants.append(sheet0.iloc[2,i])
        print(catalysts)
        print(main_substrates)
        print(main_products)
        print(reactants)

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
        class EquationOfState(PropertyPackage): pass
        class IdealModel(PropertyPackage): pass
        class RaoultsLaw(IdealModel): pass

    
        # Hinweis für später: Die Interaktionsparameter können notfalls in DWSIM ignoriert werden
        class hasBinaryInteractionParameter(ActivityCoefficientModel >> float): pass

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
        # Enzyme in der Regel Proteine, RNA und DNA können aber auch katalysieren
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
        # Ein Enzym, dass der Klasse Oxidoreduktase angehört, katalysiert nur eine Oxidationsreaktion
        class Oxidoreductase(onto.search_one(iri = '*SBO_0000460')):
            is_a = [catalyses.only(OxidoreductaseReaction)]      
        # Ein Enzym, dass der Klasse Transferase angehört, katalysiert nur eine Transferasereaktion
        class Transferase(onto.search_one(iri = '*SBO_0000460')):
            is_a = [catalyses.only(TransferaseReaction)]      
        # Ein Enzym, dass der Klasse Hydrolase angehört, katalysiert nur eine Hydrolysereaktion
        class Hydrolyse(onto.search_one(iri = '*SBO_0000460')):
            is_a = [catalyses.only(HydrolyseReaction)]
        # Ein Enzym, dass der Klasse Lyase angehört, katalysiert nur eine Lyasereaktion
        class Lyase(onto.search_one(iri = '*SBO_0000460')):
            is_a = [catalyses.only(LyaseReaction)]
        # Ein Enzym, dass der Klasse Isomerase angehört, katalysiert nur eine Isomerasereaktion        
        class Isomerase(onto.search_one(iri = '*SBO_0000460')):
            is_a = [catalyses.only(IsomeraseReaction)]
        # Ein Enzym, dass der Klasse Ligase angehört, katalysiert nur eine Ligasereaktion
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

# Werden teilweise aus dem EnzymeML-Dokument geladen
Temperature.hasTemperatureValue.append(Temperature_Value)
Temperature.hasTemperatureUnit.append(Temperature_Unit)
pH.has_pH_Value.append(pH_Value)

# Excel 'Ergänzendes Laborbuch' Sheet3 laden für fehlende Parameter
sheet3 = pd.read_excel("./Ergänzendes Laborbuch.xlsx", sheet_name=3)

# Druckangaben fehlen im EnzymeML-Dokument
Pressure.hasPressureValue.append(sheet3.iloc[1,1])
Pressure.hasPressureUnit.append(sheet3.iloc[2,1])

with onto:
        class ProcessFlowDiagram(Thing): pass
        
        class Reactor(onto.search_one(iri = '*Device')): pass
        class Reactortype(Reactor): pass
        
        class hasVolumeValue(onto.search_one(iri = '*Device') >> float): pass
        class hasVolumeUnit(onto.search_one(iri = '*Device') >> str): pass
        
        class hasLengthValue(onto.search_one(iri = '*Device')>> float): pass
        class hasLengthUnit(onto.search_one(iri = '*Device') >> str): pass
    
        class hasDiameter(onto.search_one(iri = '*Device')>> float): pass
        class hasDiameterUnit(onto.search_one(iri = '*Device') >> str): pass
    
        class hasResidenceTime(onto.search_one(iri = '*Device')>> float): pass
        class hasResidenceTimeUnit(onto.search_one(iri = '*Device') >> str): pass
    
        class hasDeltaP(onto.search_one(iri = '*Device')>> float): pass
        class hasDeltaP_Unit(onto.search_one(iri = '*Device') >> str): pass
    
        class hasTypeOf_OperationMode(onto.search_one(iri = '*Device') >> int): pass
    
        class hasCompoundMolarFlow(onto.search_one(iri = '*ChemicalMaterialStaged') >> float): pass       
        class hasCompoundMolarFlowUnit(onto.search_one(iri = '*ChemicalMaterialStaged') >> str): pass
        class hasVolumetricFlow(onto.search_one(iri = '*ChemicalMaterialStaged') >> float): pass
        class hasVolumetricFlowUnit(onto.search_one(iri = '*ChemicalMaterialStaged') >> str): pass
    
    
SCR = Reactortype('StraightTubeReactor')
HTR = Reactortype('HelicalTubeReactor')
Reactor = Reactortype(sheet3.iloc[11,1])

# Reaktorvolumen im EzymeMl Dokument in ml
# Für DWSIM in m3 angeben
Reactor.hasVolumeValue.append(sheet3.iloc[12,1])
Reactor.hasVolumeUnit.append(sheet3.iloc[13,1])

# Die Reaktorlänge fehlt im EnzymeMl Dokument
# SCR und HTR 4 m -> hier aber in DWSIM: Zu hoher Druckabfall
# neue Länge für die Simulation bestimmt
Reactor.hasLengthValue.append(sheet3.iloc[7,1])
Reactor.hasLengthUnit.append(sheet3.iloc[8,1])

# Reaktordurchmesser fehlt im EnzymeML Dokument
# SCR und HTR 1.6 mm Innendurchmesser
Reactor.hasDiameter.append(sheet3.iloc[9,1])
Reactor.hasDiameterUnit.append(sheet3.iloc[10,1])
Reactor.hasResidenceTime.append(sheet3.iloc[5,1])
Reactor.hasResidenceTimeUnit.append(sheet3.iloc[6,1])
Reactor.hasDeltaP.append(sheet3.iloc[3,1])
Reactor.hasDeltaP_Unit.append(sheet3.iloc[4,1])
Reactor.hasTypeOf_OperationMode.append(sheet3.iloc[14,1])

# InletFlow comparable with ontochem class 'ChemicalMaterialInput_Manual'
InletLaccase = (onto.search_one(iri = '*ChemicalMaterialInput_CF'))('InletLaccase')
InletABTS_red = (onto.search_one(iri = '*ChemicalMaterialInput_CF'))('InletABTS_red')
InletOxygen = (onto.search_one(iri = '*ChemicalMaterialInput_CF'))('InletOxygen')
InletWater = (onto.search_one(iri = '*ChemicalMaterialInput_CF'))('InletWater') # LöMi

OutletWater = (onto.search_one(iri = '*ChemicalMaterialOutput_CF'))('OutletWater')
OutletABTS_ox = (onto.search_one(iri = '*ChemicalMaterialOutput_CF'))('OutletABTS_ox')


# Die Inletströme wurden über die Konzentration und Volumenstrom ermittelt
# In DWSIM kann der Molstrom in mol/s festgelegt werden
# Aus der Excel 'Ergänzendes Laborbuch' importieren -> Sheet0
InletLaccase.hasCompoundMolarFlow.append(sheet0.iloc[8,1])
InletLaccase.hasCompoundMolarFlowUnit.append(sheet0.iloc[9,1]) # mol/s

InletABTS_red.hasCompoundMolarFlow.append(sheet0.iloc[8,2])
InletABTS_red.hasCompoundMolarFlowUnit.append(sheet0.iloc[9,2]) # mol/s 

InletOxygen.hasCompoundMolarFlow.append(sheet0.iloc[8,4])
InletOxygen.hasCompoundMolarFlowUnit.append(sheet0.iloc[9,4]) # mol/s

InletWater.hasCompoundMolarFlow.append(sheet0.iloc[8,5])
InletWater.hasCompoundMolarFlowUnit.append(sheet0.iloc[9,5]) # LöMi

# Volumenstrom
InletABTS_red.hasVolumetricFlow.append(sheet0.iloc[10,2])
InletABTS_red.hasVolumetricFlowUnit.append(sheet0.iloc[11,2]) # m3/s 

InletOxygen.hasVolumetricFlow.append(sheet0.iloc[10,4])
InletOxygen.hasVolumetricFlowUnit.append(sheet0.iloc[11,4]) # m3/s 

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
Chair_of_EquipmentDesign = Institution('TU_Dortmund_LaboratoryOfEquipmentDesign')
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

# Die Konsistenz der Ontologie überprüfen
# Reasoner: HermiT
        sync_reasoner()

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
         
# Zugriff auf die Koeffizienten
# Komponentenliste kann beliebig lang sein
stoich_coeffs = {}  
direct_order_coeffs = {}  
reverse_order_coeffs = {}   

for comp in compounds:
    stoich_coeffs[comp] = onto.search_one(label=comp).hasStoichiometriCoefficient.first()
    direct_order_coeffs[comp] = onto.search_one(label=comp).hasDirect_OrderCoefficient.first()
    reverse_order_coeffs[comp] = onto.search_one(label=comp).hasReverse_OrderCoefficient.first()

# Dictionary, um Komponentennamen und Koeff zu sichern
# Mit der zweiten Zeile können die jeweiligen Koeff geupdatet werden
comps = {}
comps.update(stoich_coeffs)

dorders = {}
dorders.update(direct_order_coeffs)

rorders = {}
rorders.update(reverse_order_coeffs)

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
RCT_Type = ObjectType.RCT_PFR
devices_info = [
    {'type': ObjectType.Mixer, 'x': 50, 'y': 50, 'name': 'Mixer'},
    {'type': RCT_Type, 'x': 150, 'y': 50, 'name': sheet3.iloc[11,1]}
    ]

devices = []
for d in devices_info:
    device = sim.AddObject(d['type'], d['x'], d['y'], d['name'])
    # Save devices in variable 
    devices.append(device)
    if d['name'] == sheet3.iloc[11,1]:
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
# Reaktant 1 und 2 führen in den Mixer
sim.ConnectObjects(m1.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, MIX1.GraphicObject, -1, -1)
# Mixtur führt aus dem Mixer
sim.ConnectObjects(MIX1.GraphicObject, m3.GraphicObject, -1, -1)
# Mixtur führt in den PFR
pfr.ConnectFeedMaterialStream(m3, 0)
# Produktstrom führt aus dem PFR
pfr.ConnectProductMaterialStream(m4, 0)
# Energiestrom führt zum PFR, weil ihm für die Reaktion Wärme zugeführt wird
# Allerdings Reaktion bei Raumtemperatur
# Daher ~0 
pfr.ConnectFeedEnergyStream(e1, 1)

# Für die Operation Mode wird das ergänzende ELN durchsucht nach 
# 'hasTypeOf_ThermodynamicProcess'
# DWSIM braucht Integer als input, daher: 1 == Adiabatic, 0 == Isothermic
pfr.ReactorOperationMode = Reactors.OperationMode(Reactor.hasTypeOf_OperationMode.first())
# Dimensionierung festlegen: Volumen und Länge
# In jedem Fall muss das Volumen festgelegt werden
# Optiional kann zusätzlich die Reaktorlänge oder Durchmesser angegeben werden
pfr.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length    

# Dimensionierung aus der Ontologie ziehen
pfr.Volume = Reactor.hasVolumeValue.first(); # m3
pfr.Length = Reactor.hasLengthValue.first();

# DeltaP im Reaktor einstellen
# das Feld 'Constant Linear Pressure Drop' anklicken
pfr.UseUserDefinedPressureDrop = True;
# Wert für DeltaP aus dem ergänzenden Laborbuch importieren
pfr.UserDefinedPressureDrop = Reactor.hasDeltaP.first(); 


# Für die Thermodynamik ein Property Package festlegen
# Raoult's Law ideal
# Für die vorliegende Simulation NRTL auswählen
# Manuell müssen dafür die fehlenden Interaktionsparameter ausgeschaltet werden
sim.CreateAndAddPropertyPackage("Raoult's Law")
#sim.CreateAndAddPropertyPackage("NRTL")

# Die Temperatur jeder Kante festlegen
# Wert in in der Ontologie hinterlegt
materials = {"m1": Temperature.hasTemperatureValue.first(),
             "m2": Temperature.hasTemperatureValue.first(),
             "m3": Temperature.hasTemperatureValue.first(),
             "m4": Temperature.hasTemperatureValue.first()
             }

for material, temperature in materials.items():
    globals()[material].SetTemperature(temperature)

#m1.SetMolarFlow(0.0) # will set by compound

# Molstrom der Inletströme wurden über die Anfangskonzentrationen und über den jeweiligen Volumenstrom ermittelt
# Klasse für Anfangskonzentrationen integrieren?
m1.SetOverallCompoundMolarFlow(reactants[0], InletOxygen.hasCompoundMolarFlow.first()) # mol/s
m1.SetOverallCompoundMolarFlow(main_substrates[0], 0.0)  # mol/s
m1.SetOverallCompoundMolarFlow(catalysts[0], 0.0) # mol/s

m2.SetOverallCompoundMolarFlow(reactants[0], 0.0) # mol/s
m2.SetOverallCompoundMolarFlow(main_substrates[0], InletABTS_red.hasCompoundMolarFlow.first())  # mol/s
m2.SetOverallCompoundMolarFlow(catalysts[0], InletLaccase.hasCompoundMolarFlow.first()) # mol/s
m2.SetOverallCompoundMolarFlow(reactants[1], InletWater.hasCompoundMolarFlow.first())

m1.SetVolumetricFlow(InletOxygen.hasVolumetricFlow.first())
m2.SetVolumetricFlow(InletABTS_red.hasVolumetricFlow.first())

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

myreaction = sim.GetReaction('ABTS Oxidation')
myscripttitle = 'ABTS_kinetics'
myscript = sim.Scripts[myscripttitle]

myscript.ScriptText = str("import math\n"
"Km = {} # mol/m3\n"
"kcat = {} # 1/s\n"
'\n'
'reactor = Flowsheet.GetFlowsheetSimulationObject("""{}""")\n'
'T = reactor.OutletTemperature\n'
'Flowsheet = reactor.FlowSheet\n'
'\n'
'obj = Flowsheet.GetFlowsheetSimulationObject("""Mixture""")\n'
'\n'
'# Access to compound list\n'
'value = obj.GetOverallComposition()\n'
'\n'
'# Access to compound amount\n'
'z_Protein = value[{}]\n'
'z_Substrate = value[{}]\n'
'\n'
'n = obj.GetPhase("""Overall""").Properties.molarflow # mol/s\n'
'Q = obj.GetPhase("""Overall""").Properties.volumetric_flow # m3/s\n'
'\n'
'Conc_Protein = z_Protein*n/Q # mol/m3\n'
'Conc_Substrate = z_Substrate*n/Q # mol/m3\n'
'\n'
'r = ((Conc_Protein * kcat * Conc_Substrate)/(Km + Conc_Substrate)) # mol/(m3*s)'.format(
    Km_LA.hasKmValue.first(), kcat_LA.has_kcatValue.first(), sheet3.iloc[11,1], 0, 1))  
    
myreaction.ReactionKinetics = ReactionKinetics(1)
myreaction.ScriptTitle = myscripttitle

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
                              "ABTS_Oxidation.dwxmz")
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
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "ABTS_Oxidation.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image
im = Image.open(imgPath)
im.show()    