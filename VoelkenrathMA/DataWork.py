# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:22:35 2023

@author: smmcvoel
"""
import json
import types
import owlready2
import xmltodict
import subprocess
import regex as re    
import pubchempy as pcp

from collections import Counter


def ExecDetchemDriver():
    ## Calling DETCHEM driver and formatting data 
    # define file path
    path = "C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/cli/dist/"
    cli = path + "cli.js"
    dci = path + "input/Methanation_Ni_DETCHEM.txt"
    ckt = path + "input/Methanation_thermdata.txt"
    mol = path + "input/moldata.txt"
    sur = "Ni=2.55e-5" # ATTENTION: maybe variable with future "DETCHEM Driver"
    
    command = ["node", cli, "--dci", dci, "--ckt", ckt, "--moldata", mol, "--surface", sur]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.stderr:
        print("ExecDETCHEMDriver Fehlerausgabe", result.stderr)
        
    # convert from bytes to dict
    data_decode = result.stdout.decode("utf8")
    data = json.loads(data_decode)
    
    # the subdict "pbr.inp" is here still in xml format, formatting and converting into dict
    pbr_xml = data["pbr.inp"]
    
    pbr_rep = ("<MAIN>" + pbr_xml + "</MAIN>").replace("<STICK>", "<REACTION>").replace("</STICK>", "</REACTION>").replace("mol/m2", "mol_m2")
    
    # replace two pattern: e.g. name=Ni --> name='Ni' & mol_m2=2.5500e-5 --> mol_m2='2.5500e-5'
    pattern_1 = re.compile(r"name=([A-Za-z0-9]+)")
    pattern_2 = re.compile(r"mol_m2=([\d.e+-]+)")
    
    pbr_sub_1 = re.sub(pattern_1, r"name='\1'", pbr_rep)
    pbr_sub_2 = re.sub(pattern_2, r"mol_m2='\1'", pbr_sub_1)
    
    pbr_dict = xmltodict.parse(pbr_sub_2)
    data["pbr.inp"] = pbr_dict
    
    return data


def GetSubstances(data):
    ## Extract every (ontology relevant) substance and format them
    # get substances and format (string --> list)
    substance_string = data["pbr.inp"]["MAIN"]["SPECIES"]["GASPHASE"]
    substance_list = substance_string.split("\n")
    
    substances = []
    for sub in substance_list:
        substances.append(sub.replace(" ",""))
    
    # adding catalyst to substance list
    substances.append(data["pbr.inp"]["MAIN"]["SPECIES"]["SURFACE"]["@name"])
    
    return substances


def GetEductAndProduct(data):
    ## Extract educts and products as seperate lists
    # getting every educt and product
    reactions = []
    for index, reaction in enumerate(data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"]):
        if type(reaction) == str:
            reac_eqn = reaction.splitlines()[0]
            reactions.append(reac_eqn)
        elif type(reaction) == dict:
            reac_dict = reac_dict =  data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"][index]
            reac_eqn = reac_dict["#text"].splitlines()[0]
            reactions.append(reac_eqn)
    
    # create list with educts and product
    educt_eqn = []
    product_eqn = []
    for reaction in reactions:
        equation_split = reaction.split(">")
        educt_eqn.append(equation_split[0])
        product_eqn.append(equation_split[1])
    
    educt_all = [] # list with all possible educts
    for reaction in educt_eqn:
        re = reaction.replace(" ", "")
        educts = re.split("+")
        for i in educts:
            if "-" not in i:
                educt_all.append(i)
    print(educt_all)
    product_all = [] # list with all possible products
    for reaction in product_eqn:
        re = reaction.replace(" ", "")
        products = re.split("+")
        for i in products:
            if "-" not in i:
                product_all.append(i)
    print(product_all)            
    counter_educt = Counter(educt_all)
    counter_product = Counter(product_all)
        
    educt = []
    product = []
    
    # compare lists 
    for element, count in counter_educt.items():
        if element in counter_product:
            min_count = min(count, counter_product[element])
            educt.extend([element] * (count - min_count))
            product.extend([element] * (counter_product[element] - min_count))
    
    print(educt)
    print(product)    
    "Siehe Kommentar am Funtkionsaufruf am Ende vom Skript"

    
def AddSubstanceToOWL(substances):
    ## Search species in ontolgie and adds them as class and individuum if not found
    # load ontology
    onto = owlready2.get_ontology("ontologies/MV-Onto.owl").load()
    
    # check if substance (individual) is in onto or not
    substance_not_found = []
    for sub in substances:
        found = False
        substance = "Sub_" + sub
        for individual in onto.individuals():
            if substance.lower() == individual.name.lower():
                print(f"Substance {sub} found as individual: {individual.name}")
                found = True
                break
        if not found:
            substance_not_found.append(sub)
    
    if len(substance_not_found) > 0:
        print(" ")
        print("Substances not found:", substance_not_found)
        print("Searching substance in PubChem...")
    
    # extract iupac-names of substances_not_found from Pubchem-API (and format names)
    substance_pubchem = []
    for sub in substance_not_found:
        compounds = pcp.get_compounds(sub, 'formula')
        if compounds:
            compound = compounds[0] # 
            iupac = compound.iupac_name
            substance_pubchem.append([sub, iupac.title()])
            print(f"{sub} found in PubChem as {compound.iupac_name}")
        else:
            print(f"No Information found for {sub}!")
    #print(substance_pubchem)
    
    # adding substances as class and individuum to ontologie
    with onto:
        # set iri for class "molecule", cause its the superclass for all added molecules
        if len(substance_pubchem) > 0:
            super_class = onto.search(iri="*molecule")[0] 
            print(" ")
            print("Adding missing Substances to Ontologie...")
            for formula, iupac in substance_pubchem:
                # create the substance class
                class_name = iupac.replace(" ", "_")
                class_iri = "example.org#" + class_name

                molecule_class = types.new_class(class_name, (super_class,))
                
                molecule_class.comment.append("Substance-Class is created automatically")
                
                # create the substance individual and connect it to its class
                individual_name = "Sub_" + formula
                individual = molecule_class(individual_name)
                
                print(f"Class {class_name} created with its individuum {individual_name}")
                
                onto.save("ontologies/MV-Onto.owl")
                

def AddReactionToOWL(educts, products, cat):
    ## Checks if the given reactionsystem is allready in the ontology and creates them if not
    # getting every educt and product
    print("")
    

def run():
    ## run complete script
    # Execute KIT's DETHCHEM driver
    data = ExecDetchemDriver()
    
    # Extract Substances and add them to ontology
    substances = GetSubstances(data)
    AddSubstanceToOWL(substances)
    
    # Extract educts and products and add reaction (individual) to ontology
    """
    In Detchem Daten sind zu jeder Reaktion Hin- sowie Rückreaktion gegeben, d.h. Vergleich linke/rechte Seite zum Erhalt von Edukte und Produkten liefert leere Listen.
    Falls bis dahin keine eigene Idee, Alex fragen ob er ne Idee zum auslesen hat und falls nicht könnte man hier den ersten User Input einbauen.
    Für weitere Entwicklung des Codes werden Edukte und Produkte zunächst in den folgenden Zeilen Hardcoded.
    educts, products, cat = GetEductAndProduct(data)
    
    """
    educts = ["CO", "CO2", "H2"]
    products = ["CH4", "H2O"]
    cat = ["Ni"]
    #AddReactionToOWL(educts, products, cat)
    
    