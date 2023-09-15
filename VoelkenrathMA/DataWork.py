# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:22:35 2023

@author: smmcvoel
"""
import json
import math
import yaml
import types
import owlready2
import xmltodict
import subprocess
import regex as re    
import pubchempy as pcp

from collections import Counter, OrderedDict
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.yamlutils import as_dict
from linkml_runtime.linkml_model import SchemaDefinition


def ExecDetchemDriver():
    ## Calling DETCHEM driver and formatting data 
    # define file path
    path = "C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/cli/dist/"
    cli = path + "cli.js"
    dci = path + "input/Methanation_Ni_DETCHEM.txt"
    ckt = path + "input/Methanation_thermdata.txt"
    mol = path + "input/moldata.txt"
    sur = "Ni=2.55e-5" # ACHTUNG: maybe variable with future "DETCHEM Driver"
    
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
            print(f"No information found for {sub}!")
    #print(substance_pubchem)
    
    # adding substances as class and individuum to ontologie
    with onto:
        # set iri for class "molecule", cause its the superclass for all added molecules
        if len(substance_pubchem) > 0:
            super_class = onto.search(iri="*molecule")[0] 
            print(" ")
            print("Adding missing substances to ontologie...")
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
                

def AddReactionToOWL(name, educts, products, cat):
    ## Checks if the given reactionsystem is allready in the ontology and creates them if not
    # load ontology
    onto = owlready2.get_ontology("ontologies/MV-Onto.owl").load()
    
    mixture_class = onto.search(iri="https://nfdi4cat.org/ontologies/reac4cat#Mixture")[0]
    reaction_class = onto.search(iri="http://example.org#ChemicalReaction")[0]
    #prop = onto.search(iri="*hasComponent")[0]
    
    print(" ")
    print("Adding reaction to ontologie...")
    
    # create feed/product mixture individuum
    with onto:
        # create individuum Mix_...
        mix_feed = mixture_class("MV_Mix_Feed_" + name)
        mix_product = mixture_class("MV_Mix_Product_" + name)
        
        print("Generate feed composition as individuum...")
        # combine educt-individuums with mix-feed individuum
        for educt in educts:
            ind_iri = "*Sub_" + educt
            ind = onto.search(iri=ind_iri)[0]
            
            mix_feed.hasComponent.append(ind)
        
        # combine cat-individuum with mix-feed individuum
        for c in cat:
            ind_iri = "*Sub_" + c
            ind = onto.search(iri=ind_iri)[0]
            
            mix_feed.hasComponent.append(ind)
        
        print("Generate product composition as individuum...")
        # combine product-individuum with mix-product individuum
        for product in products:
            ind_iri = "*Sub_" + product
            ind = onto.search(iri=ind_iri)[0]
            
            mix_product.hasComponent.append(ind)
        
        print("Generate reaction as individuum...")
        # create reaction individuum
        reaction = reaction_class("MV_Reac_" + name)
        reaction.hasInitialMixture.append(mix_feed)
        reaction.hasProduct.append(mix_product)
        
    # execute reasoner
    print(" ")
    print("Execute reasoner...")
    owlready2.sync_reasoner(onto)
    onto.save("ontologies/MV-Onto.owl")
    
    
def CreateDataSheet(name, data):
    ## Extracting all simulation parameter from data and creates a yaml-file with the scheme
    # Achtung: prüfe nochmal wie Edukte und Produkte ins LinkML-Data-file übertragen werden
    # --> Individuals auslesen
    onto = owlready2.get_ontology("ontologies/MV-Onto.owl").load()
    
    # get reaction-type
    individual_name = "MV_Reac_" + name
    individual = onto[individual_name]
    individual_classes = individual.is_a
    if len(individual_classes) > 0:
        reaction_class = str(individual_classes[1])
        reaction_type = reaction_class.split(".")[1]
        print(" ")
        print(f"The implemented reaction is a {reaction_type}")
    else:
        print("Reasoner not found a reaction-type for the implemented reaction. Check if reaction is in ontology and define it if not")
        return False

    # load reactor scheme
    scheme_name = "linkml/PFR_Scheme.yaml"
    with open(scheme_name, 'r') as scheme_file:
        scheme_data = scheme_file.read()
    scheme = yaml_loader.load(scheme_data, target_class=SchemaDefinition)
    
    # get feed parameter
    TPV = data["pbr.inp"]["MAIN"]["PBR"]["INITIAL"]["#text"]
    inlet_temperature = float(TPV.split("\n")[0].split("=")[1].replace(" ", "")) # K
    inlet_pressure = float(TPV.split("\n")[1].split("=")[1].replace(" ", "")) # Pa
    inlet_velocity = float(TPV.split("\n")[2].split("=")[1].replace(" ", "")) # m/s
    
    mole_frac = data["pbr.inp"]["MAIN"]["PBR"]["INITIAL"]["MOLEFRAC"].split("\n")
    for i in range(len(mole_frac)):
        mole_frac[i] = mole_frac[i].replace(" ", "").split("=")
        mole_frac[i][1] = float(mole_frac[i][1])
        
    gasphase = data["pbr.inp"]["MAIN"]["SPECIES"]["GASPHASE"].replace(" ","").split("\n")
    surface = data["pbr.inp"]["MAIN"]["SPECIES"]["SURFACE"]["#text"].replace(" ","").split("\n")
    components = gasphase + surface
    
    print(" ")
    print("Creating LinkML datasheet...")
    # get reactor parameter (reactive volume is calculated with tube length and diameter)
    process = data["pbr.inp"]["MAIN"]["PBR"]["PROCESS"].split("\n")
    for i in process:
        if "= y" in i:
            calculation_mode = i.replace(" ", "").split("=")[0]
    
    tube_length = float(data["pbr.inp"]["MAIN"]["PBR"]["GEOMETRY"]["SECTION"].replace(" ", "").split("\n")[0].split("=")[1]) # m
    tube_radius = float(data["pbr.inp"]["MAIN"]["PBR"]["GEOMETRY"]["#text"].replace(" ", "").split("\n")[1].split("=")[1]) # m
    tube_diameter = tube_radius * 2
    
    reactive_volume = math.pi * tube_radius ** 2 * tube_length
    
    
    "EVTL. IN EINER SPÄTEREN VERSION DES DRIVERS VORHANDEN"
    num_tubes = 1 # not given in detchem-data
    catalyst_loading = 1 # not given in detchem-data
    
    catalyst_diameter = float(data["pbr.inp"]["MAIN"]["PBR"]["GEOMETRY"]["SECTION"].replace(" ", "").split("\n")[2].split("=")[1]) # m
    catalyst_porosity = float(data["pbr.inp"]["MAIN"]["PBR"]["GEOMETRY"]["SECTION"].replace(" ", "").split("\n")[9].split("=")[1]) # m3/m3
    
    # get reaction mechanism (1. create a list with ids, parameters as strings ; 2. format list for datapoints)
    mechanism_list = []
    
    for i in range(len(data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"])):
        if type(data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"][i]) == str:
            mecha = data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"][i]
            mechanism_list.append(mecha)
        elif type(data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"][i]) == dict:
            mecha_1 = data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"][i]["#text"]
            mecha_2 = data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"][i]["COV"]
            mecha = mecha_1 + "\n" + mecha_2
            mechanism_list.append(mecha)
        else:
            (f"Fehler bei Index {i}")
    
    for i in range(len(mechanism_list)):
        mechanism_list[i] = mechanism_list[i].replace(" ", "").split("\n")
        
    mechanism_data_points = []
    
    for i in range(len(mechanism_list)):
        S0 = None
        A_cm = None
        epsilon = None
        mu = None
        
        reaction_id = i
        reaction_equation = mechanism_list[i][0]
        beta = float(mechanism_list[i][2].split("=")[1])
        EA = float(mechanism_list[i][3].split("=")[1].split("[")[0])
        
        if "S0=" in mechanism_list[i][1]:
            S0 = float(mechanism_list[i][1].split("=")[1])
        
        elif "A/cm_units=" in mechanism_list[i][1]:
            A_cm = float(mechanism_list[i][1].split("=")[1])
        else:
            print("An unexpected error accured during the parameter-extraction for the mechanism")
            
        if len(mechanism_list[i]) > 4:
            epsilon = float(mechanism_list[i][5].split("=")[1])
            mu = float(mechanism_list[i][6].split("=")[1])
        
            
        if S0 and len(mechanism_list[i]) > 4:
            mech_data_point = {'id': i, 
                               'reactions': [{'reaction_equation': reaction_equation,
                                             'S0': S0,
                                             'beta': beta,
                                             'EA': EA,
                                             'epsilon': epsilon,
                                             'mu': mu}]}
            mechanism_data_points.append(mech_data_point)
            
        elif A_cm and len(mechanism_list[i]) > 4:
            mech_data_point = {'id': i, 
                               'reactions': [{'reaction_equation': reaction_equation,
                                             'A_cm_units': A_cm,
                                             'beta': beta,
                                             'EA': EA,
                                             'epsilon': epsilon,
                                             'mu': mu}]}
            mechanism_data_points.append(mech_data_point)
            
        elif S0 and len(mechanism_list[i]) == 4:
            mech_data_point = {'id': i, 
                               'reactions': [{'reaction_equation': reaction_equation,
                                             'S0': S0,
                                             'beta': beta,
                                             'EA': EA}]}
            mechanism_data_points.append(mech_data_point)
            
        elif A_cm and len(mechanism_list[i]) == 4:
            mech_data_point = {'id': i, 
                               'reactions': [{'reaction_equation': reaction_equation,
                                             'A_cm_units': A_cm,
                                             'beta': beta,
                                             'EA': EA}]}
            mechanism_data_points.append(mech_data_point)

        else:
            print("An unexpected error accured during the datapoint creation for reaction mechanism")            
    
    mechanism = [{'ChemicalReaction': [mechanism_data_points]}]
    
    # creating data points
    mixture_class = onto.search(iri="https://nfdi4cat.org/ontologies/reac4cat#Mixture")[0]
    reactor_class = onto.search(iri="http://purl.allotrope.org/ontologies/equipment#AFE_0000153")[0]
    
    data_points = [
        {'Mixture':[{'type': mixture_class, 'temperature': inlet_temperature, 'pressure': inlet_pressure, 'velocity': inlet_velocity, 'mole_fraction': mole_frac, 'substances': components}]},
        {'Reactor':[{'type': reactor_class, 'calculation_mode': calculation_mode, 'reactive_volume': reactive_volume, 'tube_length': tube_length, 'tube_diameter': tube_diameter,
         'num_tubes': num_tubes, 'catalyst_loading': catalyst_loading, 'catalyst_particle_diameter': catalyst_diameter, 'catalyst_void_fraction':  catalyst_porosity}]}
        ]
    
    data_points_all = data_points + mechanism
    
    # creating data-sheet in yaml-format
    data_sheet = []
    for data_point in data_points_all:
        data_sheet.append(as_dict(data_point))
    
    sheet_name = "linkml/" + name + "_DataSheet.yaml"
    with open(sheet_name, "w") as output_file:
        yaml.dump(data_sheet, output_file)
    
    
def run(name):
    ## run complete script
    # Execute KIT's DETHCHEM driver
    data = ExecDetchemDriver()
    
    # Extract Substances and add them to ontology
    substances = GetSubstances(data)
    AddSubstanceToOWL(substances)

    # Adding reaction as individual to ontology and start reasoner
    # ACHTUNG: auslesen von Edukt, Produkt und Kat. muss noch automatisiert werden!
    # Frage Alex ob er eine Idee dazu hat!
    educts = ["CO", "CO2", "H2"]
    products = ["CH4", "H2O"]
    cat = ["Ni"]
    
    #educts, products = GetInputOutput()
    
    AddReactionToOWL(name, educts, products, cat)
    
    # Creating LinkML-datasheet for simulation
    CreateDataSheet(name, data)
    
    