# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 12:40:01 2023

@author: smdicher
"""

#Abfragen 
from owlready2 import *
onto_name='afo_upd'

new_world = owlready2.World()
onto = get_ontology("./ontologies/{}.owl".format(onto_name)).load()
sync_reasoner(onto) 
def
reaction_list= list(default_world.sparql("""
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX obo: <http://purl.obolibrary.org/obo/>
                            PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
                            SELECT ?reaction ?doi
                            WHERE{
                                ?reaction rdf:type owl:NamedIndividual.
                                ?reaction rdf:type ?type.
                                ?reaction afo:mentioned_in ?mention.
                                ?type rdfs:subClassOf* obo:BFO_0000015.
                                ?mention afo:has_doi ?doi.}"""))#BFO_0000015=process ;reactions are individuals of process subclasses

catalyst_list=list(default_world.sparql("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
PREFIX role: <http://purl.allotrope.org/ontologies/role#>
SELECT ?catalyst ?catOtherName ?doi
WHERE{
	{
		?catalyst rdf:type owl:NamedIndividual.
		?catalyst rdfs:subClassOf+ role:AFRL_0000217.
	}
	UNION
	 {
		?catalyst_e rdf:type owl:NamedIndividual.
	 	?catalyst_e rdf:type ?type.
		?type rdfs:subClassOf* role:AFRL_0000217.
		?supRole rdf:type owl:NamedIndividual.
		?supRole rdfs:label ?supLabel.
			FILTER regex(?supLabel, "support role")
		?catalyst_e obo:BFO_0000051 ?catalyst. FILTER NOT EXISTS {?catalyst obo:RO_0000087 ?supRole}.

	 }
	OPTIONAL {
			?catalyst rdfs:comment ?com.
				FILTER NOT EXISTS {
						FILTER regex(?com, "created automatically")
						}
            BIND(STR(?com) as ?catOtherName)
			
		}
	?catalyst afo:mentioned_in ?mention.
    ?mention afo:has_doi ?doi.
    }
""")) #search for catalysts and components of catalyst

def get_entList(list_type,doi=None): #list_type one of ['reactant','support','product']
    if doi:
        sparqlstr='''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        SELECT ?ent ?supOtherName
        WHERE{
              ?ent rdf:type owl:NamedIndividual.
              ?entRole rdf:type owl:NamedIndividual.
              ?entRole rdfs:label ?entLabel.
                  FILTER regex(?entLabel, "''' +list_type+''' role")
              ?ent obo:RO_0000087 ?entRole
              ?ent afo:mentioned_in ?mention.
              ?mention afo:has_doi '''+doi+'''.
              OPTIONAL {
              			?ent rdfs:comment ?com.
          				FILTER NOT EXISTS {
          						FILTER regex(?com, "created automatically")
          						}
                        BIND(STR(?com) as ?entOtherName)   
                          }
            }                                      
        '''
    sparqlstr='''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    SELECT ?ent ?supOtherName ?doi
    WHERE{
          ?ent rdf:type owl:NamedIndividual.
          ?entRole rdf:type owl:NamedIndividual.
          ?entRole rdfs:label ?entLabel.
              FILTER regex(?entLabel, "''' +list_type+''' role")
          ?ent obo:RO_0000087 ?supRole
          OPTIONAL {
          			?ent rdfs:comment ?com.
      				FILTER NOT EXISTS {
      						FILTER regex(?com, "created automatically")
      						}
                    BIND(STR(?com) as ?entOtherName)   
                      }
          ?ent afo:mentioned_in ?mention.
          ?mention afo:has_doi ?doi.
        }                                      
    '''
    ent_list=list(default_world.sparql(sparqlstr))
    return ent_list

def get_new_pub(n,sim_doi=None,cat=None,reacion=None, sup=None, prod=None, reactant=None ):
    #n-number of publication to retrieve
    if sim_doi:
        reaction_list=
        
                            
'''
d=list(default_world.sparql("""
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
                            PREFIX obo: <http://purl.obolibrary.org/obo/BFO_0000050>
                            PREFIX new: <http://www.semanticweb.org/chern/ontologies/2023/10/new_onto.owl#>
                            
                            SELECT ?support ?catalyst ?pubTitle ?pubDOI
                            WHERE{
                                ?support rdf:type owl:NamedIndividual.
                            	?support rdfs:comment ?supportComment.
                            	?catalyst afo:supported_on ?support.
                            	?catalyst afo:mentioned_in ?publication.
                            	?publication afo:has_doi ?pubDOI.
                            	?publication afo:has_title ?pubTitle.
                            	FILTER regex(?supportComment, "Al2O3").
                                ?reaction rdf:type owl:NamedIndividual.
                                
                                }
                            """))
                            
r= ScopusSearch('TITLE-ABS-KEY({}')                            
                            #PREFIX role: <http://purl.allotrope.org/ontologies/role#AFRL_0000360>'''
onto.individuals()