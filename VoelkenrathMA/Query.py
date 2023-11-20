# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 10:07:12 2023

@author: smmcvoel

competency questions:
    - Give me one individual for a specific parameter combination
    - Give me a list of all individuals with some specific parameter
    - Give me the individuals which are the nearest for some given parameters 
        (e.g. Query: T=300 Output: Individuals with T= 273 and T=373)
    - Give me all individuals with a turnover (CO2) bigger than 0.X
    - Give me all individuals which are nearest to the experimental file (dataverse2)
"""
import json
import owlready2
import pandas as pd

from pyDataverse.api import NativeApi, DataAccessApi
from pyDataverse.models import Dataset, Datafile

#print("Loading Ontology...")
onto_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/ontologies/MV-Onto_merged-and-inferred.owl"
#onto_path = "E:/Bibliothek/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/ontologies/MV-Onto_merged-and-inferred.owl"
new_world = owlready2.World()
onto = owlready2.get_ontology(onto_path).load()


def query_1(molefrac_co2, temperature, pressure, velocity, downstream):
    # Query for one specific simulation
    # e.g.: Query.query_1(0.5, 273.0, 100000.0, 0.001, "'Yes'")
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX exp: <http://example.org#>
    """
    
    molefrac_co2 = float(molefrac_co2)
    temperature = float(temperature)
    pressure = float(pressure)
    velocity = float(velocity)
    
    sparql_query = f"""
    SELECT ?individual
    
    WHERE{{
    ?individual afo:hasSimulatedReactionTemperature {temperature}
    ?individual afo:hasSimulatedReactionPressure {pressure}
    ?individual afo:hasSimulatedReactionVelocity {velocity}
    ?individual afo:hasSimulatedDownstream {downstream}
    ?individual afo:hasMolarFractionCarbonDioxide {molefrac_co2}
    }}
    """
    #
    sparqlstr = sparqlstr + sparql_query
    
    try:
        individual_list = list(owlready2.default_world.sparql(sparqlstr))
    except:
        individual_list = []
        print("Some error occured while executing query_1!")
    
    # get urls and format query results
    results = []
    for i in range(len(individual_list)):
        individual = individual_list[i][0]
        comments = individual.comment
        
        for j in range(len(comments)):
            if "DWSIM-file" in comments[j]:
                dwsim_url = comments[j].split("DWSIM-file: ")[1]
            if "LinkML-file" in comments[j]:
                linkml_url = comments[j].split("LinkML-file: ")[1]
        results.append([individual, dwsim_url, linkml_url])
    
    df = pd.DataFrame(results, columns=["Individual", "DWSIM-file", "LinkML-file"])
    path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/query_results/"
    df.to_excel(path + "query_1_results.xlsx")
    
        

def query_2(molefrac_co2=None, temperature=None, pressure=None, velocity=None, downstream=None):
    # Query for some specific parameters
    # e.g.: Query.query_2(molefrac_co2=0.5, temperature=273.0)
    # e.g.: Query.query_2(pressure=10000.0)
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX exp: <http://example.org#>
    """
    
    sparql_query = f"""
    SELECT ?individual
    
    WHERE{{   
    """
    
    if molefrac_co2:
        molefrac_co2 = float(molefrac_co2)
        sparql_query = sparql_query + f"?individual afo:hasMolarFractionCarbonDioxide {molefrac_co2}\n"
    if temperature:
        temperature = float(temperature)
        sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionTemperature {temperature}\n"
    if pressure:
        pressure = float(pressure)
        sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionPressure {pressure}\n"
    if velocity:
        velocity = float(velocity)
        sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionVelocity {velocity}\n"
    if downstream:
        sparql_query = sparql_query + f"?individual afo:hasSimulatedDownstream {downstream}\n"
        
    sparql_query = sparql_query + "}"
    #print(sparql_query)
    
    sparqlstr = sparqlstr + sparql_query
    
    try:
        individual_list = list(owlready2.default_world.sparql(sparqlstr))
    except:
        individual_list = []
        print("Some error occured while executing query_2!")
        
    # get urls and format query results
    results = []
    for i in range(len(individual_list)):
        individual = individual_list[i][0]
        comments = individual.comment
        
        for j in range(len(comments)):
            if "DWSIM-file" in comments[j]:
                dwsim_url = comments[j].split("DWSIM-file: ")[1]
            if "LinkML-file" in comments[j]:
                linkml_url = comments[j].split("LinkML-file: ")[1]
        results.append([individual, dwsim_url, linkml_url])
    
    df = pd.DataFrame(results, columns=["Individual", "DWSIM-file", "LinkML-file"])
    path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/query_results/"
    df.to_excel(path + "query_2_results.xlsx")
    

def query_3(molefrac_co2=None, temperature=None, pressure=None, velocity=None, downstream=None):
    # Query for some unspecific parameter
    # e.g.: Query.query_3(molefrac_co2=0.2, temperature=300.0)
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX exp: <http://example.org#>
    """
    # simulated parameter combinations
    with open("parameter.json") as json_file:
        para = json.load(json_file)
    
    list_mole = [0.04, 0.2, 0.5] # [-]
    list_temp = para["temperature"] # K
    list_pres = para["pressure"] # Pa
    list_velo = para["velocity"] # m/s
    
    sparql_query = f"""
    SELECT ?individual
    
    WHERE{{ 
    """
    
    if molefrac_co2:
        molefrac_co2 = float(molefrac_co2)
        if molefrac_co2 not in list_mole:
            min_frac = max(filter(lambda x: x < molefrac_co2, list_mole), default=None)
            max_frac = min(filter(lambda x: x > molefrac_co2, list_mole), default=None)
            
            if min_frac and not max_frac:
                sparql_query = sparql_query + f"""?individual afo:hasMolarFractionCarbonDioxide ?mole_co2.
                FILTER (?mole_co2={molefrac_co2} || ?mole_co2={min_frac})
                """
            elif not min_frac and max_frac:
                sparql_query = sparql_query + f"""?individual afo:hasMolarFractionCarbonDioxide ?mole_co2.
                FILTER (?mole_co2={molefrac_co2} || ?mole_co2={max_frac})
                """
            elif min_frac and max_frac:
                sparql_query = sparql_query + f"""?individual afo:hasMolarFractionCarbonDioxide ?mole_co2.
                FILTER (?mole_co2={molefrac_co2} || ?mole_co2={min_frac} || ?mole_co2={max_frac})
                """
            else:
                print("Some error occured in query_3 while setting the mole_fraction")
        else:
            molefrac_co2 = float(molefrac_co2)
            sparql_query = sparql_query + f"?individual afo:hasMolarFractionCarbonDioxide {molefrac_co2}\n"
            
    if temperature:
        temperature = float(temperature)
        if temperature not in list_temp:
            min_temp = max(filter(lambda x: x < temperature, list_temp), default=None)
            max_temp = min(filter(lambda x: x > temperature, list_temp), default=None)
            
            if min_temp and not max_temp:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionTemperature ?temp.
                FILTER (?temp={temperature} || ?temp={min_temp})
                """
            elif not min_temp and max_temp:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionTemperature ?temp.
                FILTER (?temp={temperature} || ?temp={max_temp})
                """
            elif min_temp and max_temp:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionTemperature ?temp.
                FILTER (?temp={temperature} || ?temp={min_temp} || ?temp={max_temp})
                """
            else:
                print("Some error occured in query_3 while setting the temperature")
        else:
            temperature = float(temperature)
            sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionTemperature {temperature}\n"
    
    if pressure:
        pressure = float(pressure)
        if pressure not in list_pres:
            min_pres = max(filter(lambda x: x < pressure, list_pres), default=None)
            max_pres = min(filter(lambda x: x > pressure, list_pres), default=None)
            
            if min_pres and not max_pres:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionPressure ?pres.
                FILTER (?pres={pressure} || ?pres={min_pres})
                """
            elif not min_pres and max_pres:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionPressure ?pres.
                FILTER (?pres={pressure} || ?pres={max_pres})
                """
            elif min_pres and max_pres:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionPressure ?pres.
                FILTER (?pres={pressure} || ?pres={min_pres} || ?pres={max_pres})
                """
            else:
                print("Some error occured in query_3 while setting the pressure")
        else:
            temperature = float(temperature)
            sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionPressure {pressure}\n"
    
    if velocity:
        velocity = float(velocity)
        if velocity not in list_velo:
            min_velo = max(filter(lambda x: x < velocity, list_velo), default=None)
            max_velo = min(filter(lambda x: x > velocity, list_velo), default=None)
            
            if min_velo and not max_velo:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionVelocity ?velo.
                FILTER (?velo={velocity} || ?velo={min_velo})
                """
            elif not min_velo and max_velo:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionVelocity ?pres.
                FILTER (?velo={velocity} || ?velo={max_velo})
                """
            elif min_velo and max_velo:
                sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionVelocity ?pres.
                FILTER (?velo={velocity} || ?velo={min_velo} || ?velo={max_velo})
                """
            else:
                print("Some error occured in query_3 while setting the velocity")
        else:
            temperature = float(temperature)
            sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionVelocity {velocity}\n"
            
    if downstream:
        downstream = str(downstream)
        sparql_query = sparql_query + f"""?individual afo:hasSimulatedDownstream {downstream}."""
            
    
    sparql_query = sparql_query + "}"
    #print(sparql_query)
    
    sparqlstr = sparqlstr + sparql_query
    
    try:
        individual_list = list(owlready2.default_world.sparql(sparqlstr))
    except:
        individual_list = []
        print("Some error occured while executing query_3!")
        
    # get urls and format query results
    results = []
    for i in range(len(individual_list)):
        individual = individual_list[i][0]
        comments = individual.comment
        
        for j in range(len(comments)):
            if "DWSIM-file" in comments[j]:
                dwsim_url = comments[j].split("DWSIM-file: ")[1]
            if "LinkML-file" in comments[j]:
                linkml_url = comments[j].split("LinkML-file: ")[1]
        results.append([individual, dwsim_url, linkml_url])
    
    df = pd.DataFrame(results, columns=["Individual", "DWSIM-file", "LinkML-file"])
    path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/query_results/"
    df.to_excel(path + "GUI_Q1_results.xlsx")
    
    return results
    
    
def query_4(x_co2):
    # Query for some unspecific turnover
    # e.g.: Query.query_4(x_co2 = 0.2)
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX exp: <http://example.org#>
    """
    
    sparql_query = f"""
    SELECT ?individual
    
    WHERE{{
        ?individual afo:hasTurnoverCarbonDioxide ?turnover
        FILTER (?turnover > {x_co2})
        }}
    """
    sparqlstr = sparqlstr + sparql_query
    
    try:
        individual_list = list(owlready2.default_world.sparql(sparqlstr))
    except:
        individual_list = []
        print("Some error occured while executing query_4!")
        
    # get urls and format query results
    results = []
    for i in range(len(individual_list)):
        individual = individual_list[i][0]
        comments = individual.comment
        
        for j in range(len(comments)):
            if "DWSIM-file" in comments[j]:
                dwsim_url = comments[j].split("DWSIM-file: ")[1]
            if "LinkML-file" in comments[j]:
                linkml_url = comments[j].split("LinkML-file: ")[1]
        results.append([individual, dwsim_url, linkml_url])
    
    df = pd.DataFrame(results, columns=["Individual", "DWSIM-file", "LinkML-file"])
    path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/query_results/"
    df.to_excel(path + "query_4_results.xlsx")
    
  
def query_5(molefrac_co2=None, temperature=None, pressure=None, velocity=None, downstream=None):
    # Query for a parameter range
    # e.g. Query.query_5(molefrac_co2=0.04, temperature=[200,300], pressure=[100000,2000000], velocity=[0.001,1], downstream="'Yes'")
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX exp: <http://example.org#>
    """
    
    sparql_query = f"""
    SELECT DISTINCT ?individual
    
    WHERE{{ 
    """
    if molefrac_co2:
        sparql_query = sparql_query + f"?individual afo:hasMolarFractionCarbonDioxide {molefrac_co2}\n"
        
    if temperature:
        temperature[0] = float(temperature[0])
        temperature[1] = float(temperature[1])
        
        sparql_query = sparql_query + f"""
        ?individual afo:hasSimulatedReactionTemperature ?temp.
        FILTER(?temp >= {temperature[0]} && ?temp <= {temperature[1]})
        """
    
    if pressure:
        pressure[0] = float(pressure[0])
        pressure[1] = float(pressure[1])
        
        sparql_query = sparql_query + f"""
        ?individual afo:hasSimulatedReactionPressure ?pres.
        FILTER(?pres >= {pressure[0]} && ?pres <= {pressure[1]})
        """
    
    if velocity:
        velocity[0] = float(velocity[0])
        velocity[1] = float(velocity[1])
        
        sparql_query = sparql_query + f"""
        ?individual afo:hasSimulatedReactionVelocity ?velo.
        FILTER(?velo >= {velocity[0]} && ?velo <= {velocity[1]})
        """
        
    if downstream:
        downstream = str(downstream)
        sparql_query = sparql_query + f"""?individual afo:hasSimulatedDownstream {downstream}."""
    
    sparql_query = sparql_query + "}"
    
    sparqlstr = sparqlstr + sparql_query
    
    try:
        individual_list = list(owlready2.default_world.sparql(sparqlstr))
    except:
        individual_list = []
        print("Some error occured while executing query_5!")
        
    # get urls and format query results
    results = []
    for i in range(len(individual_list)):
        individual = individual_list[i][0]
        comments = individual.comment
        turnover = individual.hasTurnoverCarbonDioxide
        temperature = individual.hasSimulatedReactionTemperature
        pressure = individual.hasSimulatedReactionPressure
        velocity = individual.hasSimulatedReactionVelocity
        
        for j in range(len(comments)):
            if "DWSIM-file" in comments[j]:
                dwsim_url = comments[j].split("DWSIM-file: ")[1]
            if "LinkML-file" in comments[j]:
                linkml_url = comments[j].split("LinkML-file: ")[1]
        
        results.append([individual, dwsim_url, linkml_url, temperature[0], pressure[0], velocity[0], turnover])
    
    df = pd.DataFrame(results, columns=["Individual", "DWSIM-file", "LinkML-file", "Temperature [K]", "Pressure [Pa]", "Velocity [m/s]", "Turnover CO2"])
    path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/query_results/"
    df.to_excel(path + "query_5_results.xlsx")
    return results


def query_6():
    # Query for a set of parameter which comes from experimental data (from API)
    # set file name from which u want to use the parameters
    par_file = "Exp15_v0.2.8_eop.xlsx"
    
    # Get parameter from dataverse
    base_url = "https://repo4cat.hlrs.de/"
    api_token = "1e98ec1a-ddf0-4fbd-8348-d5ab86524e70"
    dataverse_alias = "tu-do-ad"
    
    api = NativeApi(base_url, api_token)
    data_api = DataAccessApi(base_url, api_token)

    # DOI of dataset
    DOI = "hdl:21.T11978/repo4cat-proto-1030&version=DRAFT"
    dataset = api.get_dataset(DOI)
    
    file_list = dataset.json()["data"]["latestVersion"]["files"]
    
    for file in file_list:
        filename = file["label"]
        
        if filename == par_file:
            #print(f"{par_file} found in dataset!")
            file_id = file["dataFile"]["id"]
            
            response = data_api.get_datafile(file_id)
            excel = pd.read_excel(filename, sheet_name=[1,2,4])
            user_quest = excel[1]
            experi = excel[2]
            calc = excel[4] 
    
    for i in range(len(user_quest)):
        if user_quest.at[i, "Unnamed: 2"] == "reactor inlet temperature":
            temperature = user_quest.at[i, "Unnamed: 4"] # K
        if user_quest.at[i, "Unnamed: 2"] == "pressure":
            pressure = user_quest.at[i, "Unnamed: 4"] * 100000 # bar -> Pa
    
    for i in range(len(calc)):
        if calc.at[i, "Unnamed: 0"] == "linear velocity":
            velocity = calc.at[i, "Unnamed: 1"]
    
    # sparql query
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX exp: <http://example.org#>
    """
    
    sparql_query = f"""
    SELECT ?individual
    
    WHERE{{ 
    """
    
    with open("parameter.json") as json_file:
        para = json.load(json_file)
        
    list_temp = para["temperature"] # K
    list_pres = para["pressure"] # Pa
    list_velo = para["velocity"] # m/s
    
    temperature = float(temperature)
    if temperature not in list_temp:
        min_temp = max(filter(lambda x: x < temperature, list_temp), default=None)
        max_temp = min(filter(lambda x: x > temperature, list_temp), default=None)
        
        if min_temp and not max_temp:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionTemperature ?temp.
            FILTER (?temp={temperature} || ?temp={min_temp})
            """
        elif not min_temp and max_temp:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionTemperature ?temp.
            FILTER (?temp={temperature} || ?temp={max_temp})
            """
        elif min_temp and max_temp:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionTemperature ?temp.
            FILTER (?temp={temperature} || ?temp={min_temp} || ?temp={max_temp})
            """
        else:
            print("Some error occured in query_3 while setting the temperature")
    else:
        temperature = float(temperature)
        sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionTemperature {temperature}\n"
        
    pressure = float(pressure)
    if pressure not in list_pres:
        min_pres = max(filter(lambda x: x < pressure, list_pres), default=None)
        max_pres = min(filter(lambda x: x > pressure, list_pres), default=None)
        
        if min_pres and not max_pres:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionPressure ?pres.
            FILTER (?pres={pressure} || ?pres={min_pres})
            """
        elif not min_pres and max_pres:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionPressure ?pres.
            FILTER (?pres={pressure} || ?pres={max_pres})
            """
        elif min_pres and max_pres:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionPressure ?pres.
            FILTER (?pres={pressure} || ?pres={min_pres} || ?pres={max_pres})
            """
        else:
            print("Some error occured in query_3 while setting the pressure")
    else:
        temperature = float(temperature)
        sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionPressure {pressure}\n"

    velocity = float(velocity)
    if velocity not in list_velo:
        min_velo = max(filter(lambda x: x < velocity, list_velo), default=None)
        max_velo = min(filter(lambda x: x > velocity, list_velo), default=None)
        
        if min_velo and not max_velo:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionVelocity ?velo.
            FILTER (?velo={velocity} || ?velo={min_velo})
            """
        elif not min_velo and max_velo:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionVelocity ?pres.
            FILTER (?velo={velocity} || ?velo={max_velo})
            """
        elif min_velo and max_velo:
            sparql_query = sparql_query + f"""?individual afo:hasSimulatedReactionVelocity ?pres.
            FILTER (?velo={velocity} || ?velo={min_velo} || ?velo={max_velo})
            """
        else:
            print("Some error occured in query_3 while setting the velocity")
    else:
        temperature = float(temperature)
        sparql_query = sparql_query + f"?individual afo:hasSimulatedReactionVelocity {velocity}\n"

    sparql_query = sparql_query + "}"
    #print(sparql_query)
    
    sparqlstr = sparqlstr + sparql_query
    
    try:
        individual_list = list(owlready2.default_world.sparql(sparqlstr))
    except:
        individual_list = []
        print("Some error occured while executing query_3!")
        
    # get urls and format query results
    results = []
    for i in range(len(individual_list)):
        individual = individual_list[i][0]
        comments = individual.comment
        
        for j in range(len(comments)):
            if "DWSIM-file" in comments[j]:
                dwsim_url = comments[j].split("DWSIM-file: ")[1]
            if "LinkML-file" in comments[j]:
                linkml_url = comments[j].split("LinkML-file: ")[1]
        results.append([individual, dwsim_url, linkml_url])
    
    df = pd.DataFrame(results, columns=["Individual", "DWSIM-file", "LinkML-file"])
    path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/query_results/"
    df.to_excel(path + "query_6_results.xlsx")

























    