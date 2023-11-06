# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 12:40:01 2023

@author: smdicher
"""

#Abfragen 
import re
from owlready2 import *
from pybliometrics.scopus import ScopusSearch
onto_new= "afo_upd"
new_world = owlready2.World()
onto = get_ontology("./ontologies/{}.owl".format(onto_new)).load()
sync_reasoner(onto) 
import pandas as pd

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
"""
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
"""
def cat_list(cat=None,doi=None,restriction=None, include_all=False,add_support=False):
    if doi!=None:
        doi= '"{}".}}'.format(doi) 
        
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
        				FILTER regex(STR(?catlabel), "role").
        						}
	}	
	UNION
    	{
        		?catalyst_full rdf:type owl:NamedIndividual.
        	 	?catalyst_full rdf:type ?type.
        		?type rdfs:subClassOf* ?chem_substance.
                	?chem_substance rdfs:label ?chemlabel.
               		 FILTER regex(?chemlabel, 'chemical substance').
                ?catalyst_e afo:catalytic_component_of ?catalyst_full.	
                ?catalyst_full rdfs:label ?catalyst.
                
        }
    """
    
    if include_all==True and cat ==None:
        
        sparqlstr=sparqlstr+"""
        UNION
             {
                 ?catalyst_e rdf:type owl:NamedIndividual.
         	 	?catalyst_e obo:RO_0000087 role:AFRL_0000217.
                 FILTER NOT EXISTS {
  						
  						?catalyst_chem rdf:type ?type.
                 		?type rdfs:subClassOf* ?chem_substance.
                        ?chem_substance rdfs:label ?chemlabel.
                        FILTER regex(?chemlabel, 'chemical substance').
                          }
                 }
             """
    if add_support!=True:       
         sparqlstr=sparqlstr+"""
             ?catalyst_full afo:has_support_component ?support.
         """ 
    if doi==None:
        sparqlstr=sparqlstr+"""
        	?catalyst_e afo:mentioned_in ?mention.
            ?mention afo:has_doi ?doi.}
            """
    else:
        sparqlstr=sparqlstr+"""
        	?catalyst_e afo:mentioned_in ?mention.
            ?mention afo:has_doi """+doi

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
columns= ['eid',
          'doi',
          'pii',
          'pubmed_id',
          'title',
          'subtype',
          'subtypeDescription',
          'creator',
          'afid',
          'affilname',
          'affiliation_city',
          'affiliation_country',
          'author_count',
          'author_names',
          'author_ids',
          'author_afids',
          'coverDate',
          'coverDisplayDate',
          'publicationName',
          'issn',
          'source_id',
          'eIssn',
          'aggregationType',
          'volume',
          'issueIdentifier',
          'article_number',
          'pageRange',
          'description',
          'authkeywords',
          'citedby_count',
          'openaccess',
          'freetoread',
          'freetoreadLabel',
          'fund_acr',
          'fund_no',
          'fund_sponsor',
          'query']
df_all = pd.DataFrame(columns=columns)
results=[]
reac_list=[['hydroformylation'], ['atmospheric hydroformylation']]
cat_list=[['Co'],['Rh']]
sup_list=[['SiO2']]
for r in reac_list:
    for cat in cat_list:
        for sup in sup_list:
            query = 'TITLE-ABS-KEY("{}"AND"{}"AND"{}")'.format(r[0],cat[0],sup[0])
            result = ScopusSearch(query, view='STANDARD',verbose=True)
            results.append(result)
            df = pd.DataFrame(pd.DataFrame(result.results))
            df['query'] = [query for _ in range(result.get_results_size())]
            df_all = pd.concat([df_all, df], axis=0, ignore_index=True)

distinct_df=df_all.drop_duplicates(['eid']).reset_index(drop=True)

distinct_df['coverDate']=pd.to_datetime(distinct_df['coverDate'])
#filter found publication according the date
start = '2019-01-01'
end = '2023-12-31'
filtered_df = distinct_df[(distinct_df['coverDate'] >= start_date) & (distinct_df['coverDate'] <= end_date)]
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
    # Write the first dataframe to a sheet named 'all'
    df_all.to_excel(writer, sheet_name='all', index=False)

    # Write the second dataframe to a sheet named 'distinct_eid'
    distinct_df.to_excel(writer, sheet_name='distinct_eid', index=False)
    
    #Write the third dataframe to a sheet named 'filtered_distinct'
    filtered_df.to_excel(writer, sheet_name='filtered_distinct', index=False)
    
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
                            WHERE{
                            	{
                            		?catalyst_e rdf:type owl:NamedIndividual.
                    		        ?catalyst_e rdf:type ?type.
                            		?type rdfs:subClassOf* role:AFRL_0000217.
                                    ?catalyst_e rdfs:label ?catalyst.
                              		FILTER NOT EXISTS {
                            				FILTER regex(STR(?catalyst), "role").
                            						}
                    	}	
                    	UNION
                        	{
                            		?catalyst_full rdf:type owl:NamedIndividual.
                            	 	?catalyst_full rdf:type ?type.
                            		?type rdfs:subClassOf* ?chem_substance.
                                    	?chem_substance rdfs:label ?chemlabel.
                                   		 FILTER regex(?chemlabel, 'chemical substance').
                                    ?catalyst_e afo:catalytic_component_of ?catalyst_full.	
                                	{ ?catalyst_e rdfs:comment ?catalyst.
                                        FILTER NOT EXISTS {
                                        FILTER regex(?catalyst, "created automatically").}
                                        }
                                    UNION
                                   	{ ?catalyst_e rdfs:label ?catalyst.}
                                    
                            }
                                        
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
                    ?mention afo:has_doi doi.
                    .
                    }
                """ #search for all catalyst components and alternative names of one catalyst
'''                            
#r= ScopusSearch('TITLE-ABS-KEY({}-{}-{}')                            
                            #PREFIX role: <http://purl.allotrope.org/ontologies/role#AFRL_0000360>'''
