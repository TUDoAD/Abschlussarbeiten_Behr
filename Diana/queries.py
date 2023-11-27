# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 10:50:24 2023

@author: chern
"""
from owlready2 import *
import pandas as pd
from bs4 import BeautifulSoup 
import itertools
from pybliometrics.scopus import ScopusSearch
#query function for reaction retrieval
def get_reaction(reac=None,doi=None,include_all=False):
    df_reac=None
    if doi != None:
        doi = '"{}".}}'.format(doi)

    if reac == None and doi != None: 
        sparqlstr = """    
            SELECT ?reacLabel
            WHERE{
                ?reaction rdf:type owl:NamedIndividual.
                ?reaction rdf:type ?type.
                ?type rdfs:subClassOf* obo:BFO_0000015.
                ?reaction rdfs:label ?reacLabel
                ?reaction afo:mentioned_in ?mention.
                ?mention afo:has_doi """ +doi
    elif reac == None and doi == None:
        sparqlstr = """    
            SELECT ?reacLabel ?doi
            WHERE{
                ?reaction rdf:type owl:NamedIndividual.
                ?reaction rdf:type ?type.
                ?type rdfs:subClassOf* obo:BFO_0000015.
                ?reaction rdfs:label ?reacLabel
                ?reaction afo:mentioned_in ?mention.
                ?mention afo:has_doi ?doi.}"""

    elif include_all == True:
        sparqlstr = """
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
        regex_reac = '"{}"'.format(reac)
        sparqlstr = """
            SELECT ?doi
            WHERE{
                ?reaction rdf:type owl:NamedIndividual.
                ?reaction rdf:type ?type.
                ?type rdfs:subClassOf* obo:BFO_0000015.
                ?reaction rdfs:label """ +regex_reac+""".
                ?reaction afo:mentioned_in ?mention.
                ?mention afo:has_doi ?doi}""" 
            #BFO_0000015="process ";reactions are individuals of process subclasses
        

    sparqlstr = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>
    PREFIX new:  <http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#> 
    """ + sparqlstr        
    try:
        reaction_list = list(default_world.sparql(sparqlstr))
    except:
        reaction_list = []
    if reaction_list and len(reaction_list[0])==2:
        reactions=[]
        dois=[]
        for i in reaction_list:
            reactions.append(i[0])
            dois.append(i[1])
        df_reac=pd.DataFrame(data={'DOI':dois,'Title':reactions})
        
    return reaction_list,df_reac   

def get_catalyst_full(doi = None):
    if doi != None:
        doi = '"{}".}}'.format(doi) 
    sparqlstr = """
    WHERE{
        		?catalyst_full rdf:type owl:NamedIndividual.
        	 	?catalyst_full rdf:type ?type1.
        		?type1 rdfs:subClassOf* ?chem_substance.
                ?chem_substance rdfs:label 'chemical substance'.
                ?catalyst_full obo:RO_0000087 ?cat_role.
                ?cat_role rdfs:label "catalyst role".
                ?catalyst_full rdfs:label ?catalyst_name.
    """
    if doi == None:
        select = """SELECT ?catalyst_full ?catalyst_name ?doi"""
        sparqlstr = sparqlstr+"""
        	?catalyst_full afo:mentioned_in ?mention.
            ?mention afo:has_doi ?doi}
            """
    else:
        select = """SELECT ?catalyst_full ?catalyst_name """
        sparqlstr = sparqlstr+"""
            	?catalyst_full afo:mentioned_in ?mention.
            ?mention afo:has_doi """+doi
    sparqlstr = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX role: <http://purl.allotrope.org/ontologies/role#>
        PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>
        PREFIX new:  <http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#>
        """ + select + sparqlstr
    catalyst_list = list(default_world.sparql(sparqlstr))
    new_k = []
    for elem in catalyst_list:
        if elem not in new_k:
            new_k.append(elem)
    catalyst_list = new_k
    return catalyst_list
#query function for catalyst retrieval
def get_catalyst(cat = None,doi = None,include_all = False):
    if doi != None:
        doi = '"{}".}}'.format(doi) 
    
    if cat == None:
        sparqlstr = """
    WHERE{
        {
        		?catalyst_e rdf:type owl:NamedIndividual.
		        ?catalyst_e rdf:type ?type.
        		?type rdfs:subClassOf* role:AFRL_0000217.
                ?catalyst_e rdfs:label ?catalyst.
        }
        UNION
    	{
        		?catalyst_full rdf:type owl:NamedIndividual.
        	 	?catalyst_full rdf:type ?type.
        		?type rdfs:subClassOf* ?chem_substance.
                ?chem_substance rdfs:label 'chemical substance'.
                ?catalyst_e afo:catalytic_component_of ?catalyst_full.	
                ?catalyst_e rdfs:label ?catalyst.
        }
    """
    
        if include_all == True: 
        
            sparqlstr = sparqlstr + """
            UNION
                 {
                    ?catalyst_e rdf:type owl:NamedIndividual.
                    ?catalyst_e obo:RO_0000087 ?cat_role.
                    ?cat_role rdfs:label "catalyst role".
                    ?catalyst_e rdfs:label ?catalyst.
                    FILTER NOT EXISTS {?catalyst_e rdf:type ?type.
                                       ?type rdfs:subClassOf* ?chem_sub.
                                       ?chem_sub rdfs:label 'chemical substance'.}
                     }
                 """

    if doi == None:
        select = """SELECT ?catalyst_e ?catalyst ?doi"""
        end="""
        	?catalyst_e afo:mentioned_in ?mention.
            ?mention afo:has_doi ?doi}
            """
        
    else:
        select = """SELECT ?catalyst_e ?catalyst """
        end="""
        	?catalyst_e afo:mentioned_in ?mention.
            ?mention afo:has_doi """+doi
    
        
    prefix = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX role: <http://purl.allotrope.org/ontologies/role#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>
    PREFIX new:  <http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#>
    
    """ 
    sparqlstr1=prefix+ select + sparqlstr +end
    #print(sparqlstr)
    catalyst_list = list(default_world.sparql(sparqlstr1))
    """
    if not catalyst_list:
        sparqlstr1=prefix+ select + sparqlstr +'''
        	?catalyst_e afo:mentioned_in ?mention.
            ?mention afo:has_doi '''+doi+'''^^<http://www.w3.org/2001/XMLSchema#string> }'''
           
                
        catalyst_list = list(default_world.sparql(sparqlstr1))
        """
    new_k = []
    for elem in catalyst_list:
        if elem not in new_k:
            new_k.append(elem)
    catalyst_list = new_k
    return catalyst_list

def get_support(sup = None,doi = None,only_doi=True):
    if doi != None:
        doi = '"{}".}}'.format(doi)
    if sup == None:
        
        sparqlstr = """
        WHERE{
                        {
                            ?catalyst_full rdf:type ?type.
                            ?type rdfs:subClassOf* ?chem_substance.
                            ?chem_substance rdfs:label 'chemical substance'.
                            ?catalyst_full rdfs:label ?catalyst.
                            ?support_e afo:support_component_of ?catalyst_full.
                            ?support_e rdfs:label ?support.
                        }
                        UNION
                        {
                            ?support_e rdf:type owl:NamedIndividual.
                            ?support_e rdf:type ?type.
                    		?type rdfs:subClassOf* ?support_material.
                            ?support_material rdfs:label "support material".
                            ?support_e rdfs:label ?support.
                            ?catalyst_full afo:supported_on ?support_e.
                            ?catalyst_full rdfs:label ?catalyst.
                            }
                            """
    if doi==None:
        select= """SELECT ?support_e ?support ?catalyst ?doi"""
        sparqlstr=sparqlstr+"""
        	?support_e afo:mentioned_in ?mention.
            ?mention afo:has_doi ?doi}
            """
    else:
        select= """SELECT ?support_e ?support ?catalyst"""
        if only_doi== False:
            sparqlstr=sparqlstr+"""
            	?support_e afo:mentioned_in ?mention.
                ?mention afo:has_doi """+doi
        else:
            sparqlstr=sparqlstr+"""
                ?support_e afo:mentioned_in ?mention.
                ?catalyst_full afo:mentioned_in ?mention.
                ?mention afo:has_doi """+doi
    
    sparqlstr="""    
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX role: <http://purl.allotrope.org/ontologies/role#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>
    PREFIX new:  <http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#>
    """+select+sparqlstr
    support_list=list(default_world.sparql(sparqlstr))
    #print(sparqlstr)
    new_k = []
    for elem in support_list:
        if elem not in new_k:
            new_k.append(elem)
    support_list = new_k    
    return support_list
def get_abstr(doi):
    sparqlstr='''
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>

    SELECT ?abstract
        WHERE{
                ?publication rdf:type owl:NamedIndividual.
                ?publication afo:has_doi "'''+doi+'''".
                ?publication rdfs:comment ?abstract.
                FILTER regex(?abstract, "Abstract","i").
                }
    '''
    #print(sparqlstr)
    abstract=list(default_world.sparql(sparqlstr))[0][0]    
    print(abstract)
    return abstract
def get_entList(list_type,entity= None,doi=None): #list_type one of ['reactant','product','all']
    if doi!=None:
        doi= '"{}".}}'.format(doi)
    if list_type=='all':
        sparqlstr='''
        WHERE{
                ?ent_e rdf:type owl:NamedIndividual.
                ?ent_e rdfs:label ?ent.
                '''
    else:
        if entity== None:
            sparqlstr='''
            WHERE{
                    ?ent_e rdf:type owl:NamedIndividual.
                    ?entRole rdf:type owl:NamedIndividual.
                    ?entRole rdfs:label "''' +list_type+''' role".
                    ?ent_e obo:RO_0000087 ?entRole.
                    ?ent_e rdfs:label ?ent.
                '''

    if doi==None:
        select= '''SELECT ?ent_e ?ent ?doi'''
        sparqlstr= sparqlstr+'''?ent_e afo:mentioned_in ?mention.
            ?mention afo:has_doi ?doi}'''
            
    else:
        select=''' SELECT ?ent_e ?ent''' 
        sparqlstr= sparqlstr + '''?ent_e afo:mentioned_in ?mention.
            ?mention afo:has_doi''' +doi
    sparqlstr="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>
    PREFIX new:  <http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#>
    """+select+sparqlstr
    #print(sparqlstr)
    ent_list=list(default_world.sparql(sparqlstr))
    return ent_list

def get_synonyms(ent_list): #,is_cat=False
    ent_dict={}
    entity_all= [] 
    class_list= []
    for i in range(len(ent_list)):
            super_class=ent_list[i][0].is_a
            ancestors= [i.label for i in super_class[0].ancestors()]
            if super_class[0].label=='chemical substance': #super_class[0].label=='catalyst role' or
                class_list.append(ent_list[i][0])
            elif 'catalyst role' in ancestors:
                ent_dict[ent_list[i][1]]=[ent_list[i][1]]
            else:
                if super_class[0] not in class_list:
                    class_list.extend(super_class)
                class_list.append(ent_list[i][0])
    def_id = ["hasRelatedSynonym", "hasExactSynonym","comment"]
    temp_class_label=[]
    for i in range(len(class_list)):
            temp_class = class_list[i]
            #check, if label and definition are not empty:
            if temp_class.prefLabel:
                    # if preferred label is not empty, use it as class label
                    temp_class_label = temp_class.prefLabel[0]                
            elif temp_class.label:
                        # if label is not empty, use it as class label
                        temp_class_label = temp_class.label[0]
            else:
                temp_class_label=[]


            if temp_class_label and temp_class_label not in ent_dict.keys() and temp_class_label!='chemical substance':
                # if class got a label which is not empty, search for Related and Exact synonyms                    
                ent_dict[temp_class_label] = getattr(temp_class,def_id[0])
                ent_dict[temp_class_label].extend(getattr(temp_class,def_id[1]))
                ent_dict[temp_class_label].extend([i for i in getattr(temp_class,def_id[2]) if i != 'created automatically'])
                ent_dict[temp_class_label]=[*set(ent_dict[temp_class_label])]
                if ent_dict[temp_class_label] and temp_class_label not in ent_dict[temp_class_label]: 
                    ent_dict[temp_class_label].append(temp_class_label)
                elif not ent_dict[temp_class_label]:    
                    ent_dict[temp_class_label] = [temp_class_label]
                  
    for v in ent_dict.values():
        for value in v:
            if value not in entity_all:
                entity_all.append(value)
    return entity_all,ent_dict

def get_entities(doi):
    sup_list=get_support(sup=None,doi=doi)
    _,sup_all=get_synonyms(sup_list)

    cat_list=get_catalyst(cat=None,doi=doi,include_all=True)
    _,cat_all=get_synonyms(cat_list)

    reactant_list=get_entList('reactant',entity= None,doi=doi)
    reactant_all,_=get_synonyms(reactant_list)

    product_list=get_entList('product',entity= None,doi=doi)
    product_all,_=get_synonyms(product_list)
    
    cat_list_full=get_catalyst_full(doi = doi)
    _,cat_full_all=get_synonyms(cat_list_full)
    return sup_all, cat_all, reactant_all, product_all, cat_full_all

def scopus_seach_process(doi, onto_pub_list ):
    queries=[]
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
    if doi!=None:
        sup_all, cat_all, reactant_all, product_all, cat_full_all= get_entities(doi)
        list_reac_doi,_ = get_reaction(reac=None,doi=doi) 
        df_all,_=ScopusSearchQueries(reac_all, sup_all, cat_all,cat_full_all, reactant_all, product_all,queries)
        
    else:
        for p in onto_pub_list:
            sup_all, cat_all, reactant_all, product_all,cat_full_all = get_entities(p[0])
            list_reac_doi,_ = get_reaction(reac=None,doi=p[0]) 
            reac_all = [*set([i[0].lower() for i in list_reac_doi])]
            df,queries = ScopusSearchQueries(reac_all, sup_all, cat_all,cat_full_all, reactant_all, product_all,queries)
            df_all = pd.concat([df_all, df], axis=0, ignore_index=True)
    return df_all
    
def ScopusSearchQueries(reac_all, sup_all, cat_all, cat_full_all,reactant_all, product_all,queries):
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
    
    if not reac_all:
        reac_all.append(' ')
    if not reactant_all:
        reactant_all.append(' ')
    if not product_all:
        product_all.append(' ')
    if not sup_all:
        sup_all['sup']=[" "]
    if not cat_all:
        cat_all["cat"]=["catalysis"]
    for r in reac_all:
            for react in reactant_all:
                for prod in product_all:
                    if cat_full_all:
                        for v_cat_all in cat_full_all.values():
                            for c in v_cat_all:
                                query = 'TITLE-ABS-KEY("{}"AND"{}"AND"{}"AND"{}")'.format(r,c,react,prod)
                                if query not in queries:
                                    print('Downloading results for query ' + query)
                                    result = ScopusSearch(query, view='STANDARD',verbose=False, subscriber=True, refresh=100)
                                    results.append(result)
                                    queries.append(query) 
                                    df = pd.DataFrame(pd.DataFrame(result.results))
                                    df['query'] = [query for _ in range(result.get_results_size())]
                                    df_all = pd.concat([df_all, df], axis=0, ignore_index=True)
                    for k_cat,v_cat in cat_all.items():
                        for k_sup,v_sup in sup_all.items():
                            if k_sup == k_cat:
                                continue
                            else:
                                for cat in v_cat:
                                    for sup in v_sup:
                                        query = 'TITLE-ABS-KEY("{}"AND"{}"AND"{}"AND"{}"AND"{}")'.format(r,cat,sup,react,prod)
                                        if query not in queries:
                                            print('Downloading results for query ' + query)
                                            result = ScopusSearch(query, view='STANDARD',verbose=False, subscriber=True, refresh=100)
                                            results.append(result)
                                            queries.append(query) 
                                            df = pd.DataFrame(pd.DataFrame(result.results))
                                            df['query'] = [query for _ in range(result.get_results_size())]
                                            df_all = pd.concat([df_all, df], axis=0, ignore_index=True)
    return df_all,queries

def reasoning_dois_onto(onto_name):
    new_world = owlready2.World()
    onto = get_ontology("./ontologies/{}.owl".format(onto_name)).load()
    
    sync_reasoner(onto) 
    doi_list=[]
    title_list=[]
    onto_pub_list=list(default_world.sparql('''
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>
    PREFIX new:  <http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#>
    SELECT ?doi ?title
    WHERE{
              ?publication rdf:type owl:NamedIndividual.
              ?publication rdf:type ?type.
              ?type rdfs:subClassOf* new:publication.
              ?publication afo:has_doi ?doi
              ?publication afo:has_title ?title
            }'''))
    for i in onto_pub_list:
        doi_list.append(i[0])
        title_list.append(i[1])
    df=pd.DataFrame(data={'DOI':doi_list,'Title':title_list})
    print('The {} ontology consists of following publications:'.format(onto_name))

    return onto_pub_list,onto,df

def filter_date(start_date,end_date, df_all,onto_pub_list):
    distinct_df=df_all.drop_duplicates(['eid']).reset_index(drop=True)
    
    distinct_df['coverDate']=pd.to_datetime(distinct_df['coverDate'])
    if start_date!= None:
        filtered_df = distinct_df[(distinct_df['coverDate'] >= start_date) & (distinct_df['coverDate'] <= end_date)]
    else:
        filtered_df = distinct_df  
    idx_none=[]
    for row in filtered_df.itertuples():
        if row.doi == None:
            idx_none.append(row.Index)
    filtered_df_doi= filtered_df.drop(index=idx_none)
    
    query_doi_list=list(filtered_df['doi'])
    idx_copy=[]
    for d in onto_pub_list:
        if d[0] in query_doi_list:
            idx_copy.extend(list(filtered_df_doi.query('doi == "{}"'.format(d[0])).index))
    filtered_df_doi_new = filtered_df.drop(index=idx_copy)
    return distinct_df, filtered_df, filtered_df_doi, filtered_df_doi_new

def save_in_excel(output_path, df_all, distinct_df, filtered_df, filtered_df_doi, filtered_df_doi_new ):
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer: #install xlsxwriter with pip
        # Write the first dataframe to a sheet named 'all'
        df_all.to_excel(writer, sheet_name='all', index=False)
    
        # Write the second dataframe to a sheet named 'distinct_eid'
        distinct_df.to_excel(writer, sheet_name='distinct_eid', index=False)
        
        #Write the third dataframe to a sheet named 'filtered_distinct'
        filtered_df.to_excel(writer, sheet_name='filtered_distinct', index=False)
        
        #Write the fourth dataframe to a sheet named 'filtered_with doi'
        filtered_df_doi.to_excel(writer, sheet_name='filtered_with_doi', index=False)
        
        #Write the fourth dataframe to a sheet named 'filtered_new_doi'
        filtered_df_doi_new.to_excel(writer, sheet_name='filtered_new_doi', index=False)
        
        """
        FILTER NOT EXISTS {

       ?catalyst_chem rdf:type ?type3.
       ?type3 rdfs:subClassOf* ?chem_substance.
       ?chem_substance rdfs:label 'chemical substance'.
       ?catalyst_e rdf:type ?chem_substance    
         }    
        """
        doi='10.1016/0304-5102(93)87113-m'
        sparqlstr = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX afo: <http://purl.allotrope.org/voc/afo/merged/REC/2023/09/merged-without-qudt-and-inferred#>
        PREFIX new:  <http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#>
        SELECT ?mention
        WHERE{
            ?entities rdf:type owl:NamedIndividual.
            ?entities afo:mentioned_in ?publication.
            ?publication afo:has_doi "'''+doi+'''".
            ?entities rdfs:label ?mention.}'''