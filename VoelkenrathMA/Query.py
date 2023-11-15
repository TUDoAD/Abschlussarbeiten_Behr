# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 10:07:12 2023

@author: smmcvoel

competency questions:
    - Give me an individual for a specific parameter combination
    - Give me a list of all individuals with one specific parameter
    - Give me the individuals which are the nearest for some given parameters 
        (e.g. Query: T=300 Output: Individuals with T= 273 and T=373)
    - Give me all individuals with a turnover (CO2) bigger than 0.X

"""

import owlready2

print("Loading Ontology and execute Reasoner...")
onto_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/ontologies/MV-Onto_merged&inferred.owl"
new_world = owlready2.World()
onto = owlready2.get_ontology(onto_path).load()
owlready2.sync_reasoner(onto)
print("...Done!")
#onto_save

def query_1(temperature, pressure, velocity, downstream):
    # Query for a specific parameter combination
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    """
    
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
        }}
    """
    
    sparqlstr = sparqlstr + sparql_query
    
    try:
        individual_list = list(owlready2.default_world.sparql(sparqlstr))
    except:
        individual_list = []
        
    return individual_list
        

def query_2(temperature=None, pressure=None, velocity=None, downstream=None):
    # Query for one specific parameter
    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    """
    