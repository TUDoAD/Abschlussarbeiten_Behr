# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 13:58:00 2023

@author: Alexander Behr
@author: Elnaz Abbaspour
"""


####################################################
## Ontology Manipulation
####################################################

from owlready2 import *
import pyenzyme as pe
import json
#from pyenzyme import EnzymeMLDocument, EnzymeReaction, Complex, Reactant, Protein, Creator
#from pyenzyme.enzymeml.models import KineticModel, KineticParameter
import pandas as pd


## 
# To make sure, owlready2 is able to use HermiT for reasoning, configure the path to the java interpreter
# e.g.:
# owlready2.JAVA_EXE = "C://Users//..//Protege-5.5.0-win//Protege-5.5.0//jre//bin//java.exe"
##

def enzymeML_readin(EnzymeML_XLSM_str):
## DEPRECATED FUNCTION
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
    for col, d in eln_sheet.items():
        if col != "Property":
            sub_name = eln_sheet[eln_sheet['Property'].str.contains('Name')][col].iloc[0]
            sub_name = sub_name.strip() if sub_name == str else sub_name 
            if pd.notna(sub_name): ext_eln_data[sub_name] = {}
           # if sub_name in list(ext_eln_data.keys()):
            for index, row in eln_sheet.iterrows():
                if pd.notna(row[col]) and row["Property"] != "Name":
                    ext_eln_data[sub_name][row["Property"]] = row[col]
    
    return ext_eln_data


####
# parsing information from new/additional ELN into dictionary
#
def new_ELN_to_dict(eln_path):
    
    ELN_xlsx = pd.ExcelFile(eln_path)
    eln_sheet = pd.read_excel(ELN_xlsx,'Substances and Reactions')
    
    kin_index = eln_sheet[eln_sheet['Property'].str.contains('Kinetic Parameters', na=False)].index.min()
    eln_sheet_properties = eln_sheet.loc[:kin_index -1].dropna(how='all')
    eln_sheet_kin_params = eln_sheet.loc[kin_index + 1:].dropna(how='all').dropna(axis=1, how='all')
    
    ext_eln_data = {}
    subst_eln_data = {}
    kin_eln_data = {}
    
    # load substances and properties into dictionary
    """
    for col, d in eln_sheet_properties.items():
        if col != "Property":
            sub_name = eln_sheet_properties[eln_sheet_properties['Property'].str.contains('Name')][col].iloc[0].strip()
            subst_eln_data[sub_name] = {}
            for index, row in eln_sheet_properties.iterrows():
                if pd.notna(row[col]) and row["Property"] != "Name":
                    subst_eln_data[sub_name][row["Property"]] = row[col]
     """
    subst_eln_data = eln_subst_data_to_dict(eln_sheet_properties)
    
    ## adding dicts to already existing dict
    for sheet_name in ['Properties for JSON-file', 'Additional Info (Units)']:
        eln_sheet_properties = pd.read_excel(ELN_xlsx,sheet_name)
        add_dict = eln_subst_data_to_dict(eln_sheet_properties)
        subst_eln_data = {key.strip(): {**subst_eln_data.get(key, {}), **add_dict.get(key, {})} for key in set(subst_eln_data) | set(add_dict)}    
    
    ##
    
    # extract kinetic parameters into dictionary
    for col, d in eln_sheet_kin_params.items():
        if col != "Property":
            kin_name = eln_sheet_kin_params[eln_sheet_kin_params['Property'].str.contains('Name')][col].iloc[0].strip()
            kin_eln_data[kin_name] = {}
            for index, row in eln_sheet_kin_params.iterrows():
                if pd.notna(row[col]) and row["Property"] != "kineticName":
                    kin_eln_data[kin_name][row["Property"]] = row[col]
    
    kinetic_eln_data = eln_subst_data_to_dict(eln_sheet_kin_params)
    
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
    ext_eln_data["kinetics"] = kinetic_eln_data
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
   # sbo_onto = onto_world.get_ontology("https://raw.githubusercontent.com/EBI-BioModels/SBO/master/SBO_OWL.owl").load()
    onto = onto_world.get_ontology("./ontologies/"+name_base_ontology+".owl").load()
   # onto.imported_ontologies.append(sbo_onto)
    
    
    # Ohne diese Definition wird die Ontologie für set_relations(test_dict, onto) nicht gefunden
    #BaseOnto = onto

    #SBO has some classes that contain XMLs describing mathematical formulas
    # loading the ontology with owlready2 results in the XML-classes of the formulas
    # being interpreted as ontology classes and annotation properties
    # Thus, deletion of these classes takes place here
    
    """
    SBO_annotation_classes = ["apply","bvar","ci","cn","degree","divide","factorial","floor","lambda","lowlimit","minus","plus","power","product","root","selector","semantics","sum","tanh", "times","uplimit", "ln", "log","MathMLmath"]
    for dep_class in SBO_annotation_classes:
        codestr ="class_list = onto.search(iri = '*{}')\nfor indv in class_list: destroy_entity(indv)".format(dep_class)
        code = compile(codestr, "<string>","exec")
        try: 
            exec(code)
        except:
            print(codestr)
    """        
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

# dynamic creation of substances based on the enzymeML document and the additional eln
def subst_classes_from_dict(enzmldoc, subst_dict, onto):
    #      
    # iterate through each substance from subst_dict and include it in ontology
    
    enzymeML_subst_parameters = ["smiles","inchi"]
    
    for subst in list(subst_dict.keys()):
        
        try: 
            enzml_ID = subst_dict[subst]["hasEnzymeML_ID"]
        except:
            enzml_ID = ''
            
        # include as individual, if label is already present as class
        if onto.search_one(label = subst):
            codestring = """with onto:
                            substance_indv = onto.search_one(label = "{}")('ind_{}')
                            substance_indv.label = 'Sub_{}_{}'
                """.format(subst, subst, subst, enzml_ID)
       
        # include as individual, if part in IRI is already present
        elif onto.search_one(iri = "*{}".format(subst)):
            codestring = """with onto:
                            substance_indv = onto.search_one(iri = "*{}")('ind_{}')
                """.format(subst, subst)
        
        # include as class and individual of class and search in enzymeML doc for
        # the substance
        
        else:   
            try:
                subst_superclass = enzmldoc.getAny(subst_dict[subst]["hasEnzymeML_ID"]).ontology.value.replace(':','_')              
                enzml_name = enzmldoc.getAny(subst_dict[subst]["hasEnzymeML_ID"]).name
            except: 
                subst_superclass = "SBO_0000247" # Simple Chemical
                enzml_name = ''

            
            if enzml_name:
                codestring = """with onto:
                            class {}(onto.search_one(iri = '*{}')):
                                label = '{}'
                                altLabel = '{}' 
                                pass                    
                            substance_indv = {}('ind_{}')
                            substance_indv.label = 'Sub_{}_{}'
                            substance_indv.altLabel = '{}'
                    """.format(subst, subst_superclass, subst, enzml_name, subst, subst,subst, enzml_ID, enzml_name)
            else:
                codestring = """with onto:
                            class {}(onto.search_one(iri = '*{}')):
                                label = '{}'
                                pass                    
                            substance_indv = {}('ind_{}')
                            substance_indv.label = 'Sub_{}_{}'
                    """.format(subst, subst_superclass, subst, subst, subst,subst,enzml_ID)
       
        # compile codestring
        code = compile(codestring, "<string>", "exec")
        # Execute code
        exec(code)
        
        #iterate through enzymeML_subst_parameters and include their properties where suited
        if "hasEnzymeML_ID" in list(subst_dict[subst].keys()):
            for param in enzymeML_subst_parameters:
                try:
                    value = enzmldoc.getAny(subst_dict[subst]["hasEnzymeML_ID"]).dict()[param]
                except:
                    value = None
                
                if value: 
                    codestring = """with onto:
                            onto.search_one(label = '{}').{} = '{}'            
                            """.format(subst, param, value)
                        # compile codestring
                    # print(codestring)
                    code = compile(codestring, "<string>", "exec")
                    # Execute code
                    exec(code)

    return onto

def subst_dataProp_creation(dataProp_dict, onto):
    # Benötigte Relationen bestimmen via set() -> auch bei Mehrfachnennung
    # ist jede Relation aus Dictionary nur max. 1x enthalten in relation_list
    BaseOnto = onto
    relation_set = set()
    #iterate through dataProp_dict keys (all substances in additional eln) and 
    # add all keys as dataProperty
    for i in list(dataProp_dict.keys()):
        relation_set.update(set(dataProp_dict[i].keys()))
    
    
    # Important for adding protein and reactant parameters to ontology that are only contained 
    # in the EnzymeML Excel Sheet
    enzymeML_subst_parameters = ["organism","sequence","ecnumber"]
    relation_set.update(set(enzymeML_subst_parameters))
        
    # only selecting some of the parameters of the EnzymeML substance description
    #relation_set.update(set(enzymeML_subst_parameters))
        
    # Definieren jeder Relation in der Ontologie via codestring und exec:
    for rel in relation_set:
    #for subst in dataProp_dict:
        codestring = """with BaseOnto:
            class {}(DataProperty):
                label = '{}'
                pass
            """.format(rel,rel)
        
        # Code, der im codestring enthalten ist compilieren
        code = compile(codestring, "<string>","exec")
        
        # Code ausführen
        exec(code)
    
    return BaseOnto
    
def subst_set_relations(enzmldoc, subst_dict, onto):
    BaseOnto = onto
    
    # Important for adding protein parameters to ontology that are only contained 
    # in the EnzymeML Excel Sheet
    enzymeML_subst_parameters = ["organism","sequence","ecnumber"]
    prot_dict = enzmldoc.protein_dict
    
    for class_name in list(subst_dict.keys()):
        #iterate through each key of the substance dictionary (each substance)
        # and extend the respective individual with the data properties            
        onto_class = BaseOnto.search_one(iri='*ind_'+class_name)  
        
        if "hasEnzymeML_ID" in subst_dict[class_name].keys():
            if subst_dict[class_name]["hasEnzymeML_ID"] in prot_dict.keys():
                # get the data as dictionary from the respective protein:
                prot_dat = prot_dict[subst_dict[class_name]["hasEnzymeML_ID"]].dict()
    
                for prot_param in enzymeML_subst_parameters:
                    codestring = "{}.{}.append('{}')".format(str(onto_class),prot_param,str(prot_dat[prot_param]))
                    code = compile(codestring, "<string>","exec")
                    exec(code)
                
        for entry in subst_dict[class_name]: 
            data_prop_type = type(subst_dict[class_name][entry])
            
            # Assert value directly, if entry is int or float
            # give the entry as string else
            if (data_prop_type == int) or (data_prop_type == float):
                codestring = "{}.{}.append({})".format(str(onto_class),str(entry), subst_dict[class_name][entry])
            else:
                codestring = "{}.{}.append('{}')".format(str(onto_class),str(entry), str(subst_dict[class_name][entry]))                
            
            # Code, der im codestring enthalten ist compilieren
            code = compile(codestring, "<string>","exec")

            exec(code)       
        
    return BaseOnto

def kin_ind_from_dict(eln_dict, onto):
    
    kin_dict = eln_dict["kinetics"]
    for kin in list(kin_dict.keys()):
        # kin = label of indv
        
        ## adding rateLaw individual
        kin_type = kin_dict[kin]["rateLaw"] # ontology class
        
        #kin_onto_class = onto.search_one(label = kin_type)
        
        ## Enzyme
        # rateLaw -- characteristic of -> Enzyme
        # indv_rateLaw -- http://purl.obolibrary.org/obo/RO_0000052 -> subst_Enzyme
        Enzyme_name = kin_dict[kin]["kineticOfCompound"]             
        subst_id = eln_dict["substances"][Enzyme_name]["hasEnzymeML_ID"]       
        Enz_indv_label = "Sub_" + Enzyme_name + "_" + subst_id
    
        ## Substrate 
        # Might also be more than one substrate, if later there are other kinetics, 
        # this could then be reused
        Substrates = kin_dict[kin]["baseCompound"]
        substrate_indv_label = []
        for i in Substrates.split(","):
            try:
                substrate_indv_label.append("Sub_" + i.strip() + "_" + eln_dict["substances"][i.strip()]["hasEnzymeML_ID"])
            except:
                try:
                    found = eln_dict["substances"][i.strip()]
                    if found:
                        substrate_indv_label.append("Sub_" + i.strip() + "_")
                except:
                    print("baseCompound {} in kinetic of {} not found in elndict. EnzymeML_ID missing or comma in baseCompound-Name?".format(i,kin))
                    pass
        
        #TODO: Product ? 
        #print(substrate_indv_label)
        
        #include kinetic type as individual for further relations
        # RO_0000052 = characteristic of -> used to assign kinetic rate law to enzyme
        # RO_0002233 = has input -> Used for input in kinetics ; Substrates are input of reaction      
        if onto.search_one(label = kin_type):
            codestring = """with onto:
                            kin_indv = onto.search_one(label = "{}")('indv_{}')
                            kin_indv.label = "indv_{}"
                            
                            enzyme_indv = onto.search_one(label = "{}")
                            kin_indv.RO_0000052 = enzyme_indv
                            
                """.format(kin_type, kin, kin, Enz_indv_label)
            
            # adding substrates
            for substrate in substrate_indv_label:
                substr = """\n
                            substrate_indv = onto.search_one(label = "{}")
                            kin_indv.RO_0002233.append(substrate_indv)
                     """.format(substrate)
                codestring = codestring + substr 
                
            
        # include as individual, if part in IRI is already present
        elif onto.search_one(iri = "*{}".format(kin_type)):
            codestring = """with onto:
                            kin_indv = onto.search_one(iri = "*{}")('{}')
                            kin_indv.label = "indv_{}"
                            
                            enzyme_indv = onto.search_one(label = "{}")
                            kin_indv.RO_0000052 = enzyme_indv
                """.format(kin_type, kin, kin, Enz_indv_label)
        else:            
            # if not contained in ontology, the kinetics are introduced as subclass of
            # SBO_0000001 (rate law)
            codestring = """with onto:
                        class {}(onto.search_one(iri = '*SBO_0000001')):
                            label = '{}'
                            pass                    
                        kin_indv = {}('{}')
                        kin_indv.label = 'indv_{}'
                        
                        enzyme_indv = onto.search_one(label = "{}")
                        kin_indv.RO_0000052 = enzyme_indv
                """.format(kin_type,kin_type,kin_type,kin,kin, Enz_indv_label)
        
        #print(codestring)
        code = compile(codestring, "<string>","exec")
        exec(code)
        
        
        
        
        
        if kin_type == "Henri-Michaelis-Menten rate law":
            ## adding Km indv if it is contained
            if "Km" in kin_dict[kin]:
                
                ind_name = "Km_" + kin_dict[kin]["hasEnzymeML_ID"]
                val = kin_dict[kin]["Km"]
                unit = kin_dict[kin]["Km_Unit"]
                
                hasVal = onto.search_one(iri = '*hasValue')
                #hasModel= onto.search_one(iri = '*RO_0002615')
                #kin_indv = onto.search_one(label = kin)
                kin_indv_label =  "indv_"+kin
                
                codestring = """with onto:
                                Km_indv = onto.search_one(iri = "*SBO_0000027")('{}')
                                Km_indv.{}.append('{}')
                                Km_indv.has_unit_string.append('{}')
                                
                                kin_indv = onto.search_one(label = kin_indv_label)
                                Km_indv.RO_0002615.append(kin_indv)
                    """.format(ind_name, hasVal.name, val, unit)
                    
                    
                #print(codestring)
                code = compile(codestring, "<string>","exec")
                exec(code)
            ## adding kcat indv if it is contained
            if "kcat" in kin_dict[kin]:
                
                ind_name = "kcat_" + kin_dict[kin]["hasEnzymeML_ID"]
                val = kin_dict[kin]["kcat"]
                unit = kin_dict[kin]["kcat_Unit"]
                
                kin_indv_label =  "indv_"+kin
                
                codestring = """with onto:
                                kcat_indv = onto.search_one(iri = "*SBO_0000025")('{}')
                                kcat_indv.{}.append('{}')
                                kcat_indv.has_unit_string.append('{}')
                                
                                kin_indv = onto.search_one(label = kin_indv_label)
                                kcat_indv.RO_0002615.append(kin_indv)
                    """.format(ind_name, hasVal.name, val, unit)
                code = compile(codestring, "<string>","exec")
                exec(code)             
            
            
                
                
    return onto

def process_ind_from_dict():
    pass


def substance_knowledge_graph(enzmldoc, supp_eln_dict, onto, onto_str):

    ##
    #SBO Term: enzmldoc.getAny("s0").ontology.value
    
    # insert substances from dictionary in ontology
    BaseOnto = subst_classes_from_dict(enzmldoc, supp_eln_dict["substances"], onto)
    
    # insert data properties to substance individuals from dictionary
    BaseOnto = subst_dataProp_creation(supp_eln_dict["substances"], BaseOnto)

    # insert data properties to substance individuals from dictionary
    BaseOnto = subst_set_relations(enzmldoc, supp_eln_dict["substances"], BaseOnto)
        
    BaseOnto = kin_ind_from_dict(supp_eln_dict,BaseOnto)

    # Ontologie zwischenspeichern
    BaseOnto.save(file="./ontologies/Substances_and_"+ onto_str +".owl", format="rdfxml")

    #####
    # Ontology-Extension der Base Ontology #
    #####
    return BaseOnto, supp_eln_dict

##
#
# in 00_2023_MA_Abaspour_Pythoncode.py nach #ALEX Rev suchen !
#
##


def run():
   # enzymeML_readin("EnzymeML_Template_18-8-2021_KR")
   # onto, test_dict = substance_knowledge_graph("./ELNs/Ergänzendes Laborbuch_Kinetik_1.xlsx", onto, "BaseOnto2")
   
   enzmldoc = pe.EnzymeMLDocument.fromTemplate("./ELNs/EnzymeML_Template_18-8-2021_KR.xlsm")
   
   onto = base_ontology_extension("BaseOnto")
   
   new_eln_dict = new_ELN_to_dict("./ELNs/New-ELN_Kinetik_1.xlsx")
   onto, test_dict = substance_knowledge_graph(enzmldoc, new_eln_dict, onto, "BaseOnto2")
   
   with open('dict_dump.json', 'w') as file:
        json.dump(eln_dict, file)
   
   #return test_dict

eln_str = "./ELNs/New-ELN_Kinetik_1.xlsx"
eln_dict = new_ELN_to_dict(eln_str)

def test():
    enzmldoc = pe.EnzymeMLDocument.fromTemplate("./ELNs/EnzymeML_Template_18-8-2021_KR.xlsm")
    enzdict = enzmldoc.dict()
    eln_str = "./ELNs/New-ELN_Kinetik_1.xlsx"
    eln_dict = new_ELN_to_dict(eln_str)
    
    return enzdict, eln_dict
#enzdict, eln_dict = test()
    
    