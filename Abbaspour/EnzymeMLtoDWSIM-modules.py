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

def enzymeML_readin(EnzymeML_XLSM_str):

    ## USER INPUT
    # Load EnzymeML Excel-file
    # Make sure, Macros are turned OFF, else the pH-value might not be parsed correctly
    enzmldoc = pe.EnzymeMLDocument.fromTemplate("./ELNs/"+EnzymeML_XLSM_str+".xlsm")
    """
    # visualize first measurement
    fig = enzmldoc.visualize(use_names=True, trendline=True, measurement_ids=["m0"])
    """

    Creator_Names = [i.given_name+ i.family_name for i in enzmldoc.creator_dict.values()]
    Creator_Names = ", ".join(Creator_Names)

        
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

####


def eln_subst_data_to_dict(eln_sheet):
    ext_eln_data = {}
    for col, d in eln_sheet.iteritems():
        if col != "Property":
            sub_name = eln_sheet[eln_sheet['Property'].str.contains('hasCompoundName')][col].iloc[0]
            sub_name = sub_name.strip() if sub_name == str else sub_name 
            if pd.notna(sub_name): ext_eln_data[sub_name] = {}
           # if sub_name in list(ext_eln_data.keys()):
            for index, row in eln_sheet.iterrows():
                if pd.notna(row[col]) and row["Property"] != "hasCompoundName":
                    ext_eln_data[sub_name][row["Property"]] = row[col]
    
    return ext_eln_data


####

def new_ELN_to_dict(eln_path):
    
    ELN_xlsx = pd.ExcelFile(eln_path)
    eln_sheet = pd.read_excel(ELN_xlsx,'Substances and Reactions')
    
    ext_eln_data = {}
    subst_eln_data = {}
    
    # load substances and properties into dictionary
    for col, d in eln_sheet.iteritems():
        if col != "Property":
            sub_name = eln_sheet[eln_sheet['Property'].str.contains('hasCompoundName')][col].iloc[0].strip()
            subst_eln_data[sub_name] = {}
            for index, row in eln_sheet.iterrows():
                if pd.notna(row[col]) and row["Property"] != "hasCompoundName":
                    subst_eln_data[sub_name][row["Property"]] = row[col]
    
    subst_eln_data = eln_subst_data_to_dict(eln_sheet)
    
    ## adding dicts to already existing dict
    for sheet_name in ['Properties for JSON-file', 'Additional Info (Units)']:
        eln_sheet = pd.read_excel(ELN_xlsx,sheet_name)
        add_dict = eln_subst_data_to_dict(eln_sheet)
        subst_eln_data = {key.strip(): {**subst_eln_data.get(key, {}), **add_dict.get(key, {})} for key in set(subst_eln_data) | set(add_dict)}    
    
    ##
    
    # load PFD data
    # Sheet PFD
    eln_sheet = pd.read_excel(ELN_xlsx,"PFD")
    pfd_eln_data = {}
    for index, row in eln_sheet.iterrows():
        pfd_eln_data[row["object"].strip()] = {'DWSIM-object type':row["DWSIM-object type"].strip(),
                                       'DWSIM-object argument':int(row["DWSIM-object argument"]) if pd.notna(row["DWSIM-object argument"]) else None, 
                                       'connection':row["output connected to"].strip() if pd.notna(row["output connected to"]) else None,
                                       }
    
    # Sheet Material Streams
    eln_sheet = pd.read_excel(ELN_xlsx,"Material Streams")
    matstream_dict = eln_subst_data_to_dict(eln_sheet)    
    for subst in matstream_dict: 
        if "EntersAtObject" in matstream_dict[subst]:
            pfd_eln_data[matstream_dict[subst]["EntersAtObject"]].update({subst:matstream_dict[subst]})
    
    # Sheet Reactor Specification
    eln_sheet = pd.read_excel(ELN_xlsx,"Reactor Specification")    
    react_dict = {}
    
    for index, row in eln_sheet.iterrows():
        react_dict[row["Property"]] = row["Value"]
    
    try: 
        pfd_eln_data[react_dict["isDWSIMObject"]].update(react_dict)   
    except:
        print('Warning: Sheet Reactor Specification in ELN misses proper DWSIM Object!')
    
    ##
    # join substances related data and PFD-related data    
    ext_eln_data["substances"] = subst_eln_data   
    ext_eln_data["PFD"] = pfd_eln_data 
    # 
    
    return ext_eln_data

####


#####
# Ontology-Extension der Base Ontology #
#####
def base_ontology_extension(name_base_ontology):
    # Only supports owl-ontologies
    # load base ontology
    onto_world = owlready2.World()
    onto = onto_world.get_ontology("./ontologies/"+name_base_ontology+".owl").load()
    # Ohne diese Definition wird die Ontologie für set_relations(test_dict, onto) nicht gefunden
    BaseOnto = onto

    with onto:
        # Komponenten: DWSIM stellt 6 Datenbanken zur verfügung (DWSIM, ChemSep, Biodiesel, CoolProp, ChEDL and Electrolytes)
        # Daraus ergeben sich 1500 verfügbare Komponenten für die Simulation
        # Datenbanken werden der metadata4Ing Klasse 'ChemicalSubstance' subsumiert
        
        # Bool to state whether the substance is already contained in DWSIM Database
        class hasDWSIMdatabaseEntry(DataProperty):
            label = 'hasDWSIMdatabaseEntry'
            range = [bool]
            pass
        
        class isImportedAs(DataProperty):
            label = 'isImportedAs'
            range = [str]
            pass
        
    return onto

# Code für die dynamische Erstellung von Komponenten/Substanzen als Klassen
# Die Elemente einer Stoffliste werden entweder der Oberklasse JSON-Datei oder DWSIM-Komponente subsumiert

def subst_classes_from_dict(eln_dict, onto): #sheet: pd.DataFrame, onto):
    #TODO: Lookup, ob es die Substanz schon als Ontologie-Klasse gibt !
    #      
    for subst in list(eln_dict["substances"].keys()):
        # include as individual, if label is already present
        if onto.search_one(label = subst) != None:
            codestring = """with onto:
                            substance_indv = onto.search_one(label = "{}")('ind_{}')
                """.format(subst, subst)
       
        # include as individual, if part in IRI is already present
        elif onto.search_one(iri = "*{}".format(subst)) != None:
            codestring = """with onto:
                            substance_indv = onto.search_one(iri = "*{}")('ind_{}')
                """.format(subst, subst)
        
        # include as class and individual of class
        else:
            codestring = """with onto:
                        class {}(onto.search_one(iri = '*ChemicalSubstance')):
                            label = '{}'
                            pass                    
                        substance_indv = {}('ind_{}')
                
                """.format(subst, subst, subst, subst)
        #
        # compile codestring
        code = compile(codestring, "<string>", "exec")
        # Execute code
        exec(code)

    
    return onto

def dataProp_creation(dataProp_dict, onto):
    # Benötigte Relationen bestimmen via set() -> auch bei Mehrfachnennung
    # ist jede Relation aus Dictionary nur max. 1x enthalten in relation_list
    BaseOnto = onto
    relation_set = set()
    for i in list(dataProp_dict.keys()):
        relation_set.update(set(dataProp_dict[i].keys()))
    # Definieren jeder Relation in der Ontologie via codestring und exec:
    for rel in relation_set:
    #for subst in dataProp_dict:
        codestring = """with onto:
            class {}(DataProperty):
                label = '{}'
                pass
            """.format(rel,rel)
        
        # Code, der im codestring enthalten ist compilieren
        code = compile(codestring, "<string>","exec")
        
        # Code ausführen
        exec(code)
    
    return BaseOnto
    
def set_relations(dataProp_dict, onto):
    # Wieder aufsetzen des Codestrings, diesmal anhand eines Dictionaries
    BaseOnto = onto
    for class_name in list(dataProp_dict.keys()):
        # Klasse in Ontologie raussuchen, die zum Dictionary-key passt
        #onto_class = BaseOnto.search_one(label=class_name)
        onto_class = BaseOnto.search_one(iri='*ind_'+class_name)  
        for entry in dataProp_dict[class_name]:           
            data_prop_type = type(dataProp_dict[class_name][entry])
            
            # Assert value directly, if entry is int or float
            # give the entry as string else
            if (data_prop_type == int) or (data_prop_type == float):
                codestring = "{}.{}.append({})".format(str(onto_class),str(entry), dataProp_dict[class_name][entry])
           
            else:
                codestring = "{}.{}.append('{}')".format(str(onto_class),str(entry), str(dataProp_dict[class_name][entry]))                
            
            # Code, der im codestring enthalten ist compilieren
            code = compile(codestring, "<string>","exec")
            # Code ausführen
            try: 
                exec(code)
            except:
                print(codestring)
                
    return BaseOnto

def substance_knowledge_graph(support_ELN_str, onto, onto_str):
    # Stoffliste aus dem ergänzenden Laborbuch
    # Laccase, ABTS_red, ABTS_ox, Oxygen, Water
    # test_substances = [sheet0.iloc[2,1], sheet0.iloc[2,2], sheet0.iloc[2,3], sheet0.iloc[2,4], sheet0.iloc[2,5]]

    # Wörterbuch mit Stoffeigenschaften erstellen
    # Eigenschaften beachten, die relevant sind für die Simulation in DWSIM
    # Die relative Dichte und der Normalsiedepunkt, werden gebraucht für 'bulk c7+ pseudocompound creator setting'
    # Auf diese Weise können Stoffe direkt über einen Code erstellt werden
    # und DWSIM schätzt durch entsprechende Modelle fehlende Stoffeigenschaften ab
    # z.B. wird das Molekulargewicht oder die chemische Strukturformel abgeschätzt
    # Im vorliegenden Fall weichen die abgeschätzten Werte zu weit von den Literaturwerten ab
    # Weshalb Stoffeigenschaften manuell in der JSON-datei korrigiert wurden
    # und fehlende Stoffdaten durch die des Lösemittels ersetzt

    ##
    eln_dict = new_ELN_to_dict(support_ELN_str)
    
    BaseOnto = subst_classes_from_dict(eln_dict, onto)
    
    BaseOnto = dataProp_creation(eln_dict["substances"], BaseOnto)

    BaseOnto= set_relations(eln_dict["substances"], BaseOnto)
    # Ontologie zwischenspeichern
    BaseOnto.save(file="./ontologies/Substances_and_"+ onto_str +".owl", format="rdfxml")

    #####
    # Ontology-Extension der Base Ontology #
    #####
    return onto, eln_dict

##
#
# in 00_2023_MA_Abaspour_Pythoncode.py nach #ALEX Rev suchen !
#
##





def run():
   # enzymeML_readin("EnzymeML_Template_18-8-2021_KR")
   enzmldoc = pe.EnzymeMLDocument.fromTemplate("./ELNs/EnzymeML_Template_18-8-2021_KR.xlsm")
   onto = base_ontology_extension("BaseOnto")
  # onto, test_dict = substance_knowledge_graph("./ELNs/Ergänzendes Laborbuch_Kinetik_1.xlsx", onto, "BaseOnto2")
   onto, test_dict = substance_knowledge_graph("./ELNs/New-ELN_Kinetik_1.xlsx", onto, "BaseOnto2")
   
   #return test_dict

#eln_str = "./ELNs/New-ELN_Kinetik_1.xlsx"
#eln_dict = new_ELN_to_dict(eln_str)

    
"""
eln_sheet = pd.read_excel(ELN_xlsx, sheet_name)
for col, d in eln_sheet.iteritems():
    if col != "Property":
        sub_name = eln_sheet[eln_sheet['Property'].str.contains('hasCompoundName')][col].iloc[0]
        #ext_eln_data[sub_name] = {}
        if sub_name in list(ext_eln_data.keys()):
            for index, row in eln_sheet.iterrows():
                if pd.notna(row[col]) and row["Property"] != "hasCompoundName":
                    ext_eln_data[sub_name][row["Property"]] = row[col]
"""

    

"""
subst_row_sheet2 = sheet2[sheet2['Property'].str.contains('hasCompoundName')]
for col in sheet2: 
    for subst in ext_eln_data:    
        if ext_eln_data[subst]["inDWSIMdatabase"] 
        
"""        
    
    #index_EnzymeML_ID = sheet1[sheet1['Property'].str.contains('hasCompoundName')]
    
    
    
    
