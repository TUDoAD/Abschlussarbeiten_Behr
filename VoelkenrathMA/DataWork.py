# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:22:35 2023

@author: smmcvoel
"""
import json
import owlready2
import xmltodict
import subprocess
import regex as re    
import pubchempy as pcp


def ExecDetchemDriver():
    ## Calling DETCHEM Driver and formatting data 
    # define file path
    path = "C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/cli/dist/"
    cli = path + "cli.js"
    dci = path + "input/Methanation_Ni_DETCHEM.txt"
    ckt = path + "input/Methanation_thermdata.txt"
    mol = path + "input/moldata.txt"
    sur = "Ni=2.55e-5" # maybe variable with future "DETCHEM Driver"
    
    command = ["node", cli, "--dci", dci, "--ckt", ckt, "--moldata", mol, "--surface", sur]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.stderr:
        print("ExecDETCHEMDriver Fehlerausgabe", result.stderr)
        
    # convert from bytes to dict
    data_decode = result.stdout.decode("utf8")
    data = json.loads(data_decode)
    
    # the subdict "pbr.inp" is here still in xml format, formatting and converting into dict
    pbr_xml = data["pbr.inp"]
    pbr_main = "<MAIN>" + pbr_xml + "</MAIN>"
    pbr_rep_1 = pbr_main.replace("<STICK>", "<REACTION>")
    pbr_rep_2 = pbr_rep_1.replace("</STICK>", "</REACTION>")
    pbr_rep_3 = pbr_rep_2.replace("mol/m2", "mol_m2")
    
    # replace two pattern: e.g. name=Ni --> name='Ni' & mol_m2=2.5500e-5 --> mol_m2='2.5500e-5'
    pattern_1 = re.compile(r"name=([A-Za-z0-9]+)")
    pattern_2 = re.compile(r"mol_m2=([\d.e+-]+)")
    
    pbr_rep_4 = re.sub(pattern_1, r"name='\1'", pbr_rep_3)
    pbr_rep_5 = re.sub(pattern_2, r"mol_m2='\1'", pbr_rep_4)
    
    pbr_dict = xmltodict.parse(pbr_rep_5)
    data["pbr.inp"] = pbr_dict
    
    return data
    

def AddSubstance(data):
    ## Search Species in Ontolgie and adds them as class and individuum if not found
    # load ontology
    onto = owlready2.get_ontology("ontologies/MV-Onto.owl").load()
    
    # get substances and format (string --> list)
    substance_string = data["pbr.inp"]["MAIN"]["SPECIES"]["GASPHASE"]
    substance_list = substance_string.split("\n")
    
    substances = []
    for sub in substance_list:
        substances.append(sub.replace(" ",""))
    
    # adding catalyst to substance list
    substances.append(data["pbr.inp"]["MAIN"]["SPECIES"]["SURFACE"]["@name"])
    
    # check if substance (individuals) is in onto or not
    substance_not_found = []
    for sub in substances:
        found = False
        substance = "Sub_" + sub
        for individual in onto.individuals():
            if substance.lower() == individual.name.lower():
                print(f"Substance {sub} found in individual: {individual.name}")
                found = True
                break
        if not found:
            substance_not_found.append(sub)
    
    print(" ")
    print("Substances not found:", substance_not_found)
    print("Searching substance in PubChem...")
    
    # extract iupac-names of substances_not_found from Pubchem-API (and format names)
    substance_pubchem = []
    for sub in substance_not_found:
        compounds = pcp.get_compounds(sub, 'formula')
        if compounds:
            compound = compounds[0]
            iupac = compound.iupac_name
            
            if "molecular" in iupac:
                compound_split = iupac.split(" ")
                for i in compound_split:
                    if i != "molecular":
                        compound_name = i.capitalize() + " (molecular)" 
                        substance_pubchem.append([sub, compound_name])
            else:
                substance_pubchem.append([sub, iupac.capitalize()]) 
                
            print(f"{sub} found in PubChem as {compound.iupac_name}")
        else:
            print(f"No Information found for {sub}!")
    #print(substance_pubchem)
    
    # adding substances as class and individuum to ontologie
    print(" ")
    print("Adding Substances to Ontologie...")
    # classes
    classes = onto.classes()
    

def run():
    data = ExecDetchemDriver()
    AddSubstance(data)
    return data