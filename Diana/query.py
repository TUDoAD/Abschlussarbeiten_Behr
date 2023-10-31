# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 12:40:01 2023

@author: smdicher
"""

#Abfragen 
import re
from owlready2 import *
onto_new= "afo_upd"
new_world = owlready2.World()
onto = get_ontology("./ontologies/{}.owl".format(onto_new)).load()
sync_reasoner(onto) 

def get_reaction(reac=None,doi=None,include_all=False):
    if doi!=None:
        doi= '"{}".}}'.format(doi)

    if reac==None and doi!=None: 
        sparqlstr="""    
            SELECT ?reacLabel
            WHERE{
                ?reaction rdf:type owl:NamedIndividual.
                ?reaction rdf:type ?type.
                ?type rdfs:subClassOf* obo:BFO_0000015.
                ?reaction rdfs:label ?reacLabel
                ?reaction afo:mentioned_in ?mention.
                ?mention afo:has_doi """ +doi
    elif reac==None and doi==None:
        sparqlstr="""    
            SELECT ?reacLabel ?doi
            WHERE{
                ?reaction rdf:type owl:NamedIndividual.
                ?reaction rdf:type ?type.
                ?type rdfs:subClassOf* obo:BFO_0000015.
                ?reaction rdfs:label ?reacLabel
                ?reaction afo:mentioned_in ?mention.
                ?mention afo:has_doi ?doi.}"""

    elif include_all==True:
        sparqlstr="""
            SELECT ?label ?doi
            WHERE{
                ?reaction rdf:type owl:NamedIndividual.
                ?reaction rdf:type ?type.
                ?type rdfs:subClassOf* obo:BFO_0000015.
                ?reaction rdfs:label ?label.
                FILTER regex(STR(?label),"hydroformylation","i").
                ?reaction afo:mentioned_in ?mention.
                ?mention afo:has_doi ?doi}"""
    else: 
        regex_reac='"{}"'.format(reac)
        sparqlstr="""
            SELECT ?doi
            WHERE{
                ?reaction rdf:type owl:NamedIndividual.
                ?reaction rdf:type ?type.
                ?type rdfs:subClassOf* obo:BFO_0000015.
                ?reaction rdfs:label """ +regex_reac+""".
                ?reaction afo:mentioned_in ?mention.
                ?mention afo:has_doi ?doi}""" 
            #BFO_0000015="process ";reactions are individuals of process subclasses
    

    sparqlstr= """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX new:  <http://www.semanticweb.org/chern/ontologies/2023/10/new_onto.owl#>
    """+sparqlstr        
    try:
        reaction_list= list(default_world.sparql(sparqlstr))
    except:
        reaction_list= []
    return reaction_list   

doi= r'10.1016/1381-1169(96)00243-9'
list_reac=get_reaction(reac=None,doi=doi) #get list of all reaction mentioned in given doi (doi needs to be part of ontology)

#get the list of all publications in ontology where same reactions as in input publication were mentioned
same_reac_doi= []
for i in list_reac:
    reac_doi=get_reaction(reac=i[0],doi=None)
    for c in reac_doi:
        if c not in same_reac_doi and c[0]!=doi:
            same_reac_doi.append(c)#output example: [['10.1016/0304-5102(93)87113-m'],['10.1016/1381-1169(96)00243-9']]

#get the list of publications which have "hydroformulation" reaction
reac_doi_list=get_reaction(reac="hydroformylation",doi=None)  #output example: [['10.1016/0304-5102(93)87113-m'],['10.1016/1381-1169(96)00243-9']]

#get list of all publication which have "hydroformulation" and reactions which have "hydroformylation" in label
reac_doi_list=get_reaction(reac="hydroformylation",doi=None, include_all=True)

def cat_list(cat=None,doi=None,restriction=None):
    if doi==None:
        doi= ''
    else: 
        doi='FILTER regex(?doi, "'+doi+'").'
    if restriction!=None:
        restr=''
    
    if cat ==None:
        sparqlstr="""
        WHERE{
        	{
        		?catalyst_e rdf:type owl:NamedIndividual.
		        ?catalyst_e rdf:type ?type.
        		?type rdfs:subClassOf* role:AFRL_0000217.
		?catalyst_e rdfs:label ?catlabel.
          		FILTER NOT EXISTS {
        				FILTER regex(?catlabel, "catalyst role").
        						}
	}	
	UNION
    	{
        		?catalyst_e rdf:type owl:NamedIndividual.
        	 	?catalyst_e rdf:type ?type.
        		?type rdfs:subClassOf* ?chem_substance.
                		?chem_substance rdfs:label ?chemlabel.
               		 FILTER regex(?chemlabel, 'chemical substance').
                ?catalyst afo:catalytic_component_of ?catalyst_e.	
        
        }
    UNION
             {
                 ?catalyst_e rdf:type owl:NamedIndividual.
         	 	?catalyst_e obo:RO_0000087 role:AFRL_0000217.
                 FILTER NOT EXISTS {
  						FILTER regex(?com, "created automatically").
  						?catalyst_chem rdf:type ?type.
                 		?type rdfs:subClassOf* ?chem_substance.
                        ?chem_substance rdfs:label ?chemlabel.
                        FILTER regex(?chemlabel, 'chemical substance').
                        
                          }
                 }
        	OPTIONAL {
        			?catalyst rdfs:comment ?com.
        				FILTER NOT EXISTS {
        						FILTER regex(?com, "created automatically").
        						}
                    BIND(STR(?com) as ?catOtherName)
        			
        		}
        	?catalyst afo:mentioned_in ?mention.
            ?mention afo:has_doi ?doi.
            """+doi+"""
            ?catalyst afo:has_support_component ?support
            
            
            ?support rdf:type owl:NamedIndividual.
            ?support obo:RO_0000087 ?supRole.
            ?catalyst afo:supported_on ?support.
            {?support rdfs:comment ?supcom.
				FILTER NOT EXISTS {
						FILTER regex(?supcom, "created automatically").
						}
            BIND(STR(?supcom) as ?supNames).
            }
            UNION
            {?support rdfs:label ?supNames.}
            FILTER regex(?supNames,'"""+supName+"""').
            }
        """ #search for all catalysts and components of catalyst
    else:

        sparqlstr="""
        WHERE{
        	{
        		?catalyst rdf:type owl:NamedIndividual.
        		?catalyst rdfs:label ?catlabel.
                FILTER regex(?catlabel, '"""+cat+"""')
                
        	}
        	UNION
        	 {
        		?catalyst rdf:type owl:NamedIndividual.
        	 	?catalyst rdfs:comment ?catCom.
                 FILTER regex(?catCom, '"""+cat+"""')
            OPTIONAL {
             			?catalyst rdfs:comment ?com.
             				FILTER NOT EXISTS {
             						FILTER regex(?com, "created automatically")
             						}
                         BIND(STR(?com) as ?catOtherName)
             			
             		}
        	?catalyst afo:mentioned_in ?mention.
            ?mention afo:has_doi ?doi.
            FILTER regex(?doi, "10.1021/acscatal.7b00499.s001").
            }
        """ #search for all catalyst components and alternative names of one catalyst
    sparqlstr="""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX role: <http://purl.allotrope.org/ontologies/role#>
    PREFIX new:  <http://www.semanticweb.org/chern/ontologies/2023/10/new_onto.owl#>
    SELECT ?catalyst_e ?catalyst ?catOtherName ?doi"""+sparqlstr
    catalyst_list=list(default_world.sparql(sparqlstr))
    return catalyst_list

def get_entList(list_type,doi=None): #list_type one of ['reactant','support','product']
    if doi== None:
        doi= '?doi'
    else:
        doi='new:"'+doi+'"'
    sparqlstr='''
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
    PREFIX new:  <http://www.semanticweb.org/chern/ontologies/2023/10/new_onto.owl#>
    SELECT ?ent ?entOtherName
    WHERE{
              ?ent rdf:type owl:NamedIndividual.
              ?entRole rdf:type owl:NamedIndividual.
              ?entRole rdfs:label ?entLabel.
                  FILTER regex(?entLabel, "''' +list_type+''' role")
              ?ent obo:RO_0000087 ?entRole
              ?ent afo:mentioned_in ?mention.
              ?mention afo:has_doi ?doi.
              FILTER regex(?doi, "10.1021/acscatal.7b00499.s001").
              OPTIONAL {
              			?ent rdfs:comment ?com.
          				FILTER NOT EXISTS {
          						FILTER regex(?com, "created automatically")
          						}
                        BIND(STR(?com) as ?entOtherName)   
                          }
            }                                      
        '''

    ent_list=list(default_world.sparql(sparqlstr))
    return ent_list
#sup_list=get_entList('support', None)


def get_new_pub(n,doi=None,cat=None,reaction=None, sup=None, prod=None, reactant=None ):
    #n-number of publication to retrieve

    if doi:
        catalyst_list=cat_list(None,doi)
        reaction_list=get_reaction(None,doi)
        reac_list=get_entList("reactant",doi)        
        prod_list=get_entList("product",doi)    
        support_list=get_entlist("support",doi)
    elif cat=='all':
        catalyst_list=cat_list(None,doi)    
'''
d=list(default_world.sparql("""
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/03/merged-without-qudt-and-inferred#>
                            PREFIX obo: <http://purl.obolibrary.org/obo/>
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
'''                            
#r= ScopusSearch('TITLE-ABS-KEY({}-{}-{}')                            
                            #PREFIX role: <http://purl.allotrope.org/ontologies/role#AFRL_0000360>'''
