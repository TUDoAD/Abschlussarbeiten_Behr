# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 15:13:36 2023

@author: smdicher
"""
import time
import stanza
#stanza.download('en', package='craft', processors='tokenize')
import spacy
from owlready2 import *
from CatalysisIE.model import *
from CatalysisIE.utils import *
import os
import json
from chemdataextractor import Document
from pubchempy import get_compounds
from preprocess_onto import *
import pickle
def set_config_key(key, value):
     globals()[key] = value
def run_text_mining(abstract,model, onto_class_list):
    with open("config.json") as json_config:
         for key, value in json.load(json_config).items():
             set_config_key(key, value)
    sents = text_prep(abstract) 
    categories,chem_list, reac_dict, sup_cat, abbreviation,raw_entities= CatalysisIE_search(model, sents)
    missing, match_dict,chem_list,rel_synonym, onto_new_dict=chemical_prep(chem_list, onto_class_list)
    return chem_list, categories,onto_new_dict, sup_cat, abbreviation, missing, match_dict, rel_synonym, reac_dict,raw_entities
        
def load_classes_chebi():
    """
    Load Classes from ChEBI Ontology

    This function loads classes from the ChEBI (Chemical Entities of Biological Interest) ontology and returns a list of these classes.
    It excludes classes that are descendants of 'organic group'.


    Returns
    -------
    onto_class_list : list
    A list of classes from the ChEBI ontology after excluding descendants of 'organic group'.

    """
    print('extracting ChEBI classes...')
    start_time=time.time()
    new_world3 = owlready2.World()
    try:
        onto = new_world3.get_ontology('http://purl.obolibrary.org/obo/chebi.owl').load()
    except:
        onto = new_world3.get_ontology('./ontologies/chebi.owl').load()
    onto_class_list = list(onto.classes())
    set_org_mol= onto.search_one(label='organic group').descendants()
    for i in set_org_mol:
        if i in onto_class_list:
            onto_class_list.remove(i)
    print("--- %.2f seconds ---" % (time.time() - start_time))
    #onto_dict,inchikey = synonym_dicts(onto_class_list)
    
    return onto_class_list

def delete_files_in_directory(directory_path):
   """
    delete all files in the specified directory

    Parameters
    ----------
    directory_path : raw-str
        Path to directory.

    Returns
    -------
    None.

   """
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")
     
   
def add_publication(doi,title,abstract):
    """
    Add Publication to Ontology

    This function adds a publication to an ontology, creating a 'publication' class in the ontology if it doesn't exist. 
    It also associates the publication with a DOI, title, and abstract. 
    It assigns data properties (“has doi”, “has title”) with corresponding values and saves DOI and Title in 

    Parameters
    ----------
    onto_name : str
        The name of the parent ontology (i.e. 'afo').
    doi : str
        The DOI (Digital Object Identifier) of the publication.
    title : str
        The title of the publication.
    abstract : str
        The abstract of the publication.

    Returns
    -------
    p_id : int or None
        If the publication is added successfully, it returns the unique publication ID (an integer). 
        If the publication already exists in the ontology, it returns None.

    """
    print('processing input publication...')
    global p_id
    new_world = owlready2.World()
    try:
        onto = new_world.get_ontology('./ontologies/{}.owl'.format(onto_new)).load()
    except:
        onto = new_world.get_ontology('./ontologies/{}.owl'.format(onto_old)).load()       
        with onto:    
            class has_doi(DataProperty):
                    range = [str]
                    label = 'has doi'
            class has_title(DataProperty):
                    range = [str]
                    label ='has title'
        onto.set_base_iri('http://www.semanticweb.org/ontologies/2023/11/new_onto.owl#',rename_entities=False)
    pub_c = onto.search_one(label='publication')
    with onto:
        if not pub_c:
            pub_c = types.new_class('publication', (Thing,))
            pub_c.comment.append('created automatically; collection of processed publications') 
            pub_c.label.append('publication')
        if onto.search_one(comment='DOI: {}'.format(doi)):
            print('Paper with doi: {} already exist in ontology'.format(doi))
            new_pub = onto.search_one(comment='DOI: {}'.format(doi))
            p_id = None
            return p_id
        else:
            p_id = len(list(pub_c.instances()))+1
            new_pub = pub_c('publication{}'.format(p_id))
            new_pub.label.append('publication{}'.format(p_id))
            new_pub.comment.append('DOI: {}'.format(doi))
            new_pub.comment.append('Abstract:{}'.format(abstract))
            has_doi = onto.search_one(label='has doi')
            new_pub.has_doi = [doi]
            has_title = onto.search_one(label='has title')
            new_pub.has_title = [title]
    onto.save('./ontologies/{}.owl'.format(onto_new))
    return p_id

def pred_model_dataset (model,sent): 
    """
    Predict Using a Model on a Dataset

    This function takes a trained model and a dataset of sentences and predicts the outcomes for the sentences using the model. 

    Parameters
    ----------
    model : object
        The trained model to be used for prediction.

    sent : list
        A list of sentences for which predictions will be made.

    Returns
    -------
    pred_dataset.output_pred(): list
        A list containing the predicted outcomes for the given sentences.
    
    Notes
    -----
    - The function assumes that CUDA and PyTorch are necessary for its execution.
    - It uses the checkpoint trained on the first fold.
    - The function utilizes a trained model to predict outcomes for sentences, and the predictions are stored in pred_dataset.output_pred().

    """
    pred_dataset, pred_dataloader = model.gen_pred_dataloader(sent)
    
    model.setup('test')
    model = model.cuda()
    model.eval()
    with torch.no_grad():
        offset = 0
        for batch in tqdm(pred_dataloader):
            batch = model.batch_cuda(batch)
            model.pred_dataset_step(offset, batch, pred_dataset)
            offset += len(batch[0])
    return pred_dataset.output_pred()

def text_prep(test_txt):
    """
    Text Preprocessing Function

    This function is used for preprocessing text. It takes unprocessed text, tokenizes it, 
    and prepares it for further natural language processing tasks. The function uses the Stanza library for tokenization.

    Parameters
    ----------
    test_txt : str
        The input text that needs to be preprocessed.

    Returns
    -------
    test_sents : list
        A list containing preprocessed sentences and their corresponding tokens.

    Notes
    -----
    - The function utilizes the Stanza library for tokenization.
    - It tokenizes the input text, labels all tokens as 'O' (not training data), and provides token information such as text, 
    label, ID, start character, and end character.
    - The 'test_sents' list contains preprocessed sentences and their associated tokens.

    """
    nlp_s = stanza.Pipeline('en', package='craft', processors='tokenize', use_gpu=False)

    test_sents = []
    idx = 0
    test_txt = cleanup_text(test_txt)
    for sent in nlp_s(test_txt).sentences:
        sent_token = []
        for token in sent.tokens:
            # it is fine to label all token as O because it is not training
            sent_token.append({
                'text':token.text,
                'label':'O',
                "id":  idx,
                "start": token.start_char,
                "end": token.end_char,
            })
            idx += 1
        test_sents.append((sent.text, sent_token))
    test_sents = stanza_fix(test_sents)
    return test_sents

def CatalysisIE_search(model, test_sents): #change description at the and
    """
    Catalysis Information Extraction and Search

    This function performs information extraction and search related to catalysis. 
    It takes a model, a list of test sentences, a dictionary with ontologies and its IRIs, and the name of the ontology as input. 
    It processes the sentences, extracts chemical entities, and returns information related to catalysis, chemicals, and reactions.


    Parameters
    ----------
    model : object
        The model for information extraction.

    test_sents : list
        A list of test sentences for information extraction.
    
    onto_list : dict
        A dictionary of ontologies for search of existing classes.
    
    onto_name : str
        The name of the ontology to use.

    Returns
    -------
    categories : dict
        A dictionary of categories for the entities extracted from the text.
    
    chem_list : list
        A list of chemical entities.
    
    abbreviation : dict
        A dictionary of abbreviations and their expansions.
    
    sup_cat : dict
        A dictionary of catalysts and their support materials.
    
    chem_list_all : list
        A list of all possible chemical entities in sentences.
    
    reac_dict : dict
        A dictionary of reactions and their types.

    Notes
    -----
    - The function uses a pretrained CatalysisIE model to predict information from the test sentences.
    - It extracts chemical entities, abbreviations, supports for catalysts, and reactions.
    - The output includes dictionaries and lists related to categories, chemical entities, abbreviations, supported catalysts, and reactions.
    """
    global abbreviation
    global nlp
    global sup_cat
    nlp = spacy.load('en_core_web_sm')
    chem_list_all = []
    chem_list = []
    sup_cat = {}
    abbreviation = {}
    a = 0
    categories = {}
    reac_dict = {}   
    entity_old = (0,None,None)
    output_sents = pred_model_dataset(model, test_sents)
    raw_entities= {}
    for sent in output_sents:
        c_idx=None
        sent_tag = [t['pred'] for t in sent]
        print(assemble_token_text(sent))
        chem_list_all.extend([c.text for c in Document(assemble_token_text(sent)).cems])
        abb_list = Document(assemble_token_text(sent)).abbreviation_definitions
        for i in range(len(abb_list)):
            abbreviation[abb_list[i][0][0]] = abb_list[i][1][0]
        for k, j, l in get_bio_spans(sent_tag):
            print(assemble_token_text(sent[k:j + 1]), l)
            entity = assemble_token_text(sent[k:j + 1])
            entity_raw=entity
            #add abbreviation if directly after entity an entity in brackets
            if k == a+1 and '({})'.format(entity) in assemble_token_text(sent):
                abbreviation[entity] = entity_old[1]
            
            doc = nlp(entity)
            for i in range(len(doc)):
                if entity not in (abbreviation.keys() or abbreviation.values()):
                    if doc[i].tag_ == 'NNS' and doc[i].text not in (abbreviation.keys() or abbreviation.values()):
                        entity=re.sub(str(doc[i].text),str(doc[i].lemma_),entity )
                        entity_raw=entity
            #match hyphen in chemical entity and remove it  # Rh-Co --> RhCo
            abbr=False
            match_hyph = re.findall(r'(([A-Z](?:[a-z])?)[—–-]([A-Z](?:[a-z])?))', entity) 
            for v in abbreviation.keys():
                if v in entity:
                    abbr=True
            if match_hyph and abbr==False:
                for i in range(len(match_hyph)):
                    entity = entity.replace(match_hyph[i][0],match_hyph[i][1]+match_hyph[i][2])
            
    
            if re.search(r'[A-Za-z]*(\([\s]?[\d]+[\s]?\))',entity): #Rh(111 )
                i = re.findall(r'[A-Za-z]*(\([\s]?[\d]+[\s]?\))',entity)[0].replace(' ','')
                entity = entity.replace(re.findall(r'[A-Za-z]*(\([\s]?[\d]+[\s]?\))',entity)[0],i)
            pattern = r'([A-Za-z]+[\s]?[—–-] [a-z]+|[A-Za-z]+ [—–-][\s]?[a-z]+)' #e_split:['hydro- formylation'] and entity:heterogeneous hydro- formylation or X - ray diffraction
            e_split = re.findall(pattern,entity)
            if e_split:
                for i in e_split:
                    i_n = i.replace(' ','')
                    entity = re.sub(i,i_n,entity)
                    missing,_= create_list_IRIs([re.sub(r'[—–-]','',i_n)])
                    if not missing:
                        entity = re.sub(i_n,re.sub(r'[—–-]','',i_n),entity)
            
            #if reactant before reaction: append to reac_dict dictionary {'reaction-type':'reactant'}
            if l == 'Reaction':
                if assemble_token_text(sent[j+1:j+2])=='of':
                    for c in Document(assemble_token_text(sent)).cems:
                        if c.start == re.search(assemble_token_text(sent[k:j+1])+' of',assemble_token_text(sent)).end()+1:
                            c_idx=j+2
                if entity_old[0]+1 == k and entity_old[2]=='Reactant':
                    if entity not in reac_dict.keys():
                        reac_dict[entity] = [entity_old[1]]
                    elif entity_old[1] not in reac_dict[entity]:
                        reac_dict[entity].append(entity_old[1])
                
            
                    
            if entity in categories.keys():
                entity_old = (j,entity,l)
                continue
            else:
                
                spans = sorted(Document(entity).cems, key = lambda span: span.start)
                chem_entity=[c.text for c in spans]
                list_spans=[i for c in spans for i in c.text.split()]+[c.text for c in spans]
                chem_entity.extend([cem for cem in chem_list_all if cem in entity and cem not in chem_entity and cem not in list_spans])
                
                for c in chem_entity: # search spans
                #if for i.e. ZSM-5 in entity if only ZSM found. replace ZSM with ZSM-5 in chem_list
                    pattern = r'\b({}[—–-]\d+[-]?\d*[A-Z]*)\b'.format(c)
                    matches = re.findall(pattern, entity)
                    if matches:
                        if not re.findall(r'{}[—–-]\d+\.'.format(c), entity):
                            list_spans.append(c)
                            chem_list.append(matches[0])
                    pattern = r'\b({}[—–-][A-Z]+(?:-\d+)?)\b'.format(c)
                    matches = re.findall(pattern, entity)
                    if matches:
                            list_spans.append(c)
                            chem_list.append(matches[0])
                pattern = r'^[\d,]+[—–-] [a-z]+$' #1,3- butadiene -> 1,3-butadiene
                if re.search(pattern,entity) or re.search(r'^ [A-Za-z\d—–-]+$|^[A-Za-z\d—–-]+ $',entity):
                    entity=entity.replace(' ','') 
                        
                mol = re.findall(r'(([\w—–-]+)(?:[\s]?/[\s]?|[\s]?@[\s]?|[\s]on[\s])+([\w—–-]+))', entity) # 'RhCo on Al2O3' or 'RhCo/Al2O3' or 'RhCo@Al2O3'r'((?:([\w@—–-]+)[\s])?([\w@—–-]+)(?:[\s]?/[\s]?|[\s]on[\s])+([\w@—–-]+))', entity
                if mol:
                    for i in range(len(mol)):
                        if ('supported' or 'Supported') in mol[i][0]:
                            continue
                        elif l == 'Catalyst':
                            cem=[]
                            if '/' in mol[i][0]:
                                entity = entity.replace('/',' supported on ')
                                support = mol[i][2]
                                chem_list.append(support)
                                catalyst = mol[i][1]
                                chem_list.append(catalyst)
                                sup = True
                            if '@' in mol[i][0]:
                                    #if entity not in abbreviation.keys():
                                    entity = entity.replace('@',' supported on ')
                                    support = mol[i][2]
                                    if re.findall(r'([A-Za-z]+)[—–-]\d+[—–-]?\d*[A-Z]*', support):
                                        print(re.findall(r'(([A-Za-z]+)[—–-]\d+[—–-]?\d*[A-Z]*)', support))
                                        list_spans.append(re.findall(r'([A-Za-z]+)[—–-]\d+[—–-]?\d*[A-Z]*', support)[0])
                                    chem_list.append(support)
                                    catalyst = mol[i][1]
                                    chem_list.append(catalyst)
                                    sup = True
                            elif 'on' in mol[i][0]:
                                
                                sup = False
                                if 'based' not in entity[:re.search(r'[\s]on[\s]',entity).start()]:
                                    for c in chem_entity:
                                        if mol[i][1] in chem_list_all:
                                            sup = True
                                            cem.append(mol[i][1])
                                            if mol[i][1] not in chem_list:
                                                print('{} added to chem_list'.format(mol[i][1]))
                                                chem_list.append(mol[i][1])
                                        elif c in entity[:re.search(r'[\s]on[\s]',entity).start()]:
                                            cem.append(c)
                                    for c in chem_entity:    
                                        if c in entity[re.search(r'[\s]on[\s]',entity).end():]:
                                            support = c     
                                            sup =True
                                            break
                                        else:
                                            sup=False
                                    if sup==True:
                                        entity = entity.replace('on','supported on')                                        
                            if sup==True:    
                                if support in sup_cat.keys():
                                    if cem:
                                        sup_cat[support].extend([c for c in cem if c not in sup_cat[support]])
                                    elif catalyst not in sup_cat[support]:
                                        sup_cat[support].append(catalyst)
                                else:
                                    if cem:
                                        cem=[*set(cem)]
                                        sup_cat[support] = cem
                                    else:
                                        sup_cat[support] = [catalyst]
                        else:
                            for n in range(1, len(mol[i])):
                                chem_list.append(mol[i][n])
                                entity = entity.replace('/',',')
                                     
                if 'system' in entity or 'surface' in entity and l=='Catalyst':
                        entity = entity.replace('system','catalyst')
                        entity = entity.replace('surface','catalyst')
                if 'loaded' in entity:#Zr-loaded ZSM-5 zeolites
                    for i in range(len(spans)):
                        if i != 0:
                            e_btwn = entity[spans[i-1].end:spans[i].start]
                            if 'loaded' in e_btwn:    
                                loaded_end =  entity.index('loaded')+len('loaded')+1
                    entity = entity.replace('loaded','supported on')
                if k==c_idx and entity_old[2]=='Reaction':
                    if entity_old[1] not in reac_dict.keys():
                        reac_dict[entity_old[1]] = [entity]
                    elif entity not in reac_dict[entity_old[1]]:
                        reac_dict[entity_old[1]].append(entity)
                    c_idx=None
                if (l=="Reactant" or l=="Product") and entity_old[2]=="Reaction":
                    if assemble_token_text(sent[k-1:k])=='of':
                        if entity_old[1] not in reac_dict.keys():
                            reac_dict[entity_old[1]] = [entity]
                        elif entity not in reac_dict[entity_old[1]]:
                            reac_dict[entity_old[1]].append(entity)
                if l not in ['Characterization','Treatment']:
                    spans_new = sorted(Document(entity).cems, key = lambda span: span.start)
                    for c in spans_new:
                        if len(c.text.split())==2 and set(c.text.split()).issubset([i.text for i in spans]):
                            chem_list.extend(c.text.split())
                        else:
                            chem_list.append(c.text)
                    chem_list.extend([cem for cem in chem_list_all if cem in entity and cem not in chem_list and cem not in list_spans])
                                         
                #else:
                
                categories[entity] = l 
            entity_old = (j,entity,l)  
            a = j+1
            if entity in raw_entities.keys():
                raw_entities[entity].append(entity_raw)
                raw_entities[entity]=[*set(raw_entities[entity])]
            else:
                raw_entities[entity]=[entity_raw]
    chem_list = [*set(chem_list)]
    return categories,chem_list, reac_dict, sup_cat, abbreviation,raw_entities


def chemical_prep(chem_list, onto_class_list):
    global onto_new_dict
    rel_synonym = {}
    comp_dict = {}
    class_list = []        
    onto_new_dict = {}
    synonyms = {}
    onto_dict,inchikey = synonym_dicts(onto_class_list)
    
    for molecule in chem_list:  
        if re.search(r'^ [A-Za-z\d—–-]+|^[A-Za-z\d—–-]+ $',molecule): 
            molecule = molecule.replace(' ','')
        if molecule in abbreviation.keys(): #check if nessesary
            comp_dict[molecule] = []
            spans = Document(abbreviation[molecule]).cems
            class_list.append(molecule)
            for comp in spans:
                if len(comp.text.split()) > 1:
                    for c in comp.text.split():
                        comp_dict[molecule].append(c)
                else:
                    comp_dict[molecule].append(comp.text)
            continue
        if re.search(r'[A-Z]+[—–-][\d]+', molecule):
            onto_new_dict[molecule] = []
            class_list.append(molecule)
            continue        
        match_material=re.findall(r'((?:[A-Z](?:[a-wyz]?[\d]*))+)[—–-]((?:[A-Z](?:[a-wyz]?[\d]*))+)',molecule) #TiO2-SiO2 from Ni-W/TiO2-SiO2
        if match_material and molecule in sup_cat.keys():
            comp_dict[molecule] = [match_material[0][0],match_material[0][1]]
        molecule_split = molecule.split()        
        if len(molecule_split) >= 2 or re.match(r'[A-Za-z]([a-z]+){3,}', molecule) or re.match(r'[\d,]+[—–-][A-Z]?[a-z]+',molecule):
            comp_dict[molecule] = molecule_split  
        else:
             comp = re.findall(r'([A-Z](?:[a-wyz]+)?)',molecule)
             comp_dict[molecule] = comp
    for k,v in comp_dict.items():
        i = 0
        key=False
        if k not in onto_new_dict.keys():           
            for c in v:
                for k_o, v_o in onto_dict.items():
                    synonyms = fill_synonyms(synonyms,k,v_o,k_o)
                    synonyms = fill_synonyms(synonyms,c,v_o,k_o)
                
                if i == 0:
                    class_list, key ,rel_synonym = compare_synonyms(synonyms, inchikey, class_list, k, rel_synonym) #,comp = False

                    if key==False:
                        chem_list.remove(k)
                        break

                    onto_new_dict[key] = []
                    i += 1
                if c == k:
                    comp = key
                    
                else:
                    class_list, comp, rel_synonym = compare_synonyms(synonyms, inchikey, class_list, c, rel_synonym) #,comp = True                
                onto_new_dict[key].append(comp)
            """
            if key:
                for i in onto_new_dict[key]:
                    if len(i) == 1: #remove components if one of the components (atoms) doesn't exist (ex.ZMS- Z,M don't exist, S-exists)                                   
                        print('deleted key:{}'.format(key))
                        chem_list.remove(key)
                        class_list.remove(key)
                        onto_new_dict.pop(key)
                        break
              """  
    class_list = [*set(class_list)] #remove duplicates
    class_list.extend(['molecule'])
    missing, match_dict = create_list_IRIs(class_list,IRI_json_filename = 'iriDictionary')

    return missing, match_dict,chem_list, rel_synonym,onto_new_dict

def synonym_dicts(class_list):
    """
    extracts class names and descriptions based on class list (the owlready2 object)
    returns dictionary with general structure of 
    desc_dict = {ontology_class_label : Definition string}
    WARNING: Descriptions often have different identifiers (see try:... except loop)
           


    """
    print("Extracting formulae...")
    desc_dict = {} 
    inchikey = {}
    temp_class_label = []
    """
    new_world4 = owlready2.World()
    onto = new_world4.get_ontology('ontologies/{}.owl'.format(onto_new)).load()
    """
    def_id = ["hasRelatedSynonym", "hasExactSynonym","inchikey"]
    
    for i in range(len(class_list)):
        temp_class = class_list[i]
        #check, if label and definition are not empty:
        try:
            if temp_class.prefLabel:
                # if preferred label is not empty, use it as class label
                temp_class_label = temp_class.prefLabel[0].lower()
                
        except:
            try:
                if temp_class.label:
                    # if label is not empty, use it as class label
                    temp_class_label = temp_class.label[0].lower()
                    
            except:
                temp_class_label = []
                print("Label for class {} not determined!".format(str(temp_class)))
                return()

        if temp_class_label and temp_class_label not in desc_dict.keys():
            
            # if class got a label which is not empty, search for Related and Exact synonyms                    
            desc_dict[temp_class_label] = getattr(temp_class,def_id[0])
            desc_dict[temp_class_label].extend(getattr(temp_class,def_id[1]))
            
            if desc_dict[temp_class_label] and temp_class_label not in desc_dict[temp_class_label]: 
                desc_dict[temp_class_label].append(temp_class_label)
            elif not desc_dict[temp_class_label]:    
                desc_dict[temp_class_label] = [temp_class_label]
            # get inchikeys of chemical components
            inchikey[temp_class_label] = getattr(temp_class,def_id[2])
    print("Done.")
    return desc_dict,  inchikey

def fill_synonyms(synonyms,c,v,k):
    pattern = r'^{}$'.format(c)
    if c not in synonyms.keys():
                synonyms[c] = []
    for s in v:
        if re.search(pattern,s): 
            if k not in synonyms[c]:
                synonyms[c].append(k)    
    
    for i in synonyms[c]:
        if re.search(pattern,i):
            synonyms[c] = [i]
                        
    return synonyms

def search_inchikey(inchikey, c):    
    try:
        mol = get_compounds(c, 'formula')    
    except:
        try:
            mol = get_compounds(c, 'name')       
        except:
            mol = []        
    if not mol:
        mol_out = [c]
    else:
        mol_inch = [k for k, v in inchikey.items() for compound in mol if compound.inchikey in v]
        if mol_inch:
            mol_out = mol_inch
        else:
            mol_out = [c]          
    return mol_out,  mol

def compare_synonyms(synonyms, inchikey, class_list, k, rel_synonym):
    numinbrackets = None
    if len(synonyms[k]) == 1:
            key = synonyms[k][0]
            print('found {} in ChEBI as {}'.format(k,key))
    else:   
            print(k)
            if re.search(r'^[A-Za-z]+\(\d+\)$',k):
                numinbrackets = k
                k = re.findall(r'^([A-Za-z]+)\(\d+\)$',k)[0]
            comp_check, mol= search_inchikey(inchikey, k)
            if k in comp_check:
                if len(synonyms[k]) == 0:
                    if not mol:
                        print('no synonyms and entities for {}, key = k'.format(k))
                        ans= input('Is {} an existing compound?\n'.format(k))
                        if ans=='no':
                            key=False   
                            print('\n{} is skipped'.format(k))
                        else:    
                            key = k
                            print('new chemical compound added\n')
                            class_list.append(k)
                        return class_list, key, rel_synonym  
                    elif len(mol) == 1:
                        key=mol[0].iupac_name #some of the compounds that can be found in pubchem don't have IUPAC names (i.e. "propyl")
                        print('found {} in PubChem as {}'.format(k,key))
                    else:
                        while True:
                            mol_new = [i for i in mol if i.iupac_name]
                            print('choose IUPAC name for {}\n'.format(k))
                            print('components have following SMILES:')
                            n=1
                            for i in mol_new:
                                print('{}. {}:{}'.format(n,i.iupac_name, i.isomeric_smiles))
                                n+=1
                            idx = input('\nwrite number of fitting IUPAC name or "none"\n')
                            if idx =='none':
                                key = k
                                class_list.append(k)

                                return class_list, key, rel_synonym                   
                            else:
                                try:
                                    idx = int(idx)
                                    key = mol_new[idx-1].iupac_name
                                    break
                                except:
                                    print('\nerror: write a number between 1 and {} or "none"\n'.format(len(mol_new)))
                                    
                else:
                    while True:
                            print('choose synonyms for {}'.format(k))
                            n=1
                            for i in synonyms[k]:
                                print('{}. {}'.format(n,i))
                                n+=1
                            idx = input('\nwrite number of fitting synonym or "none"\n')                            
                            if idx =='none':
                                key = k
                                class_list.append(k)
                                return class_list, key, rel_synonym 
                            else:
                                try:
                                    idx = int(idx)
                                    key = synonyms[k][idx-1]
                                    break
                                except:
                                    print('\nerror: write a number between 1 and {} or "none"\n'.format(len(synonyms[k])))                               
            elif len(comp_check) == 1:
                key = comp_check[0]                  
            else:
                print('no synonyms but some matches in InChiKeys for {}:'.format(k))                 
                n=1
                for i in comp_check:
                    print('{}. {}'.format(n,i))
                    n+=1
                while True:
                    idx = input('\nwrite number of fitting synonym or "none"\n')                            
                    if idx =='none':
                        key = k
                        class_list.append(k)
                        return class_list, key, rel_synonym 
                    else:
                        try:
                            idx = int(idx)
                            key = comp_check[idx-1]
                            break
                        except:
                            print('\nerror: write a number between 1 and {} or "none"\n'.format(len(comp_check)))                  
                    
    if key == None or not key:
        key = k 
    if numinbrackets != None:
        rel_synonym[numinbrackets] = key  
    else:
        rel_synonym[k] = key          
    class_list.append(key)
    return class_list, key, rel_synonym
'''
#onto_new= onto_name+'_upd'
test_txt="""A method for the synthesis of highly crystalline Rh2P nanoparticles on SiO2 support materials and their use as truly heterogeneous
 single-site catalysts for the hydroformylation of ethylene and propylene is presented. The supported Rh2P nanoparticles were investigated 
 by transmission electron microscopy and by infrared analysis of adsorbed CO. The inﬂuence of feed gas composition and reaction temperature 
 on the activity and selectivity in the hydroformylation reaction was evaluated by using high throughput experimentation as an enabling 
 element; core ﬁndings were that beneﬁcial eﬀects on the selectivity were observed at high CO partial pressures and after addition of water
 to the feed gas. The analytical and performance data of the materials gave evidence that high temperature reduction leading to highly 
 crystalline Rh2P nanoparticles is key to achieving active, selective, and long- term stable catalysts. KEYWORDS: hydroformylation, 
 heterogeneous, rhodium, phosphide, nanoparticles, ethylene The reaction mechanisms of heterogeneous hydro- formylation of ethylene and 
 propylene were compared at 413−453 K using RhCo3/MCM-41 as catalysts. The reaction rates of propylene for both hydroformylation and the 
 undesired side reaction of hydrogenation were found to be about one order of magnitude lower than those for ethylene in ﬂow reactor studies.
 The diﬀerence in the kinetic behavior between ethylene and propylene was investigated by measuring the reaction orders and apparent 
 activation energies, and these macrokinetic observables were analyzed using the degree of rate control (DRC) method. In situ diﬀuse 
 reﬂectance infrared Fourier transform spectroscopy (DRIFTS) experiments were performed to characterize the surface intermediates formed
 during the reactions. When the reactant was changed from ethylene to propylene, the IR peak corresponding to adsorbed CO exhibited a 
 signiﬁcant increase, while the IR peaks of the alkyl group decreased in magnitude. Combined with the DRIFTS results, DRC analysis indicates
 that the ﬁrst step of oleﬁn hydroformylation, the formation of an alkyl group on the catalyst surface, plays a key role in the diﬀerence
 between ethylene and propylene. This step is kinetically nonrelevant when ethylene is the reactant, but it is one of the rate-controlling 
 steps for propylene. The low concentration of the adsorbed propyl group, which is a common intermediate shared by both hydroformylation and 
 hydrogenation of propylene, decreases the rates of both reaction pathways as compared to ethylene. KEYWORDS: hydroformylation, ethylene, 
 propylene, kinetics, degree of rate controlA bimetallic SiO2-supported RhCo3 cluster catalyst derived from Rh4(CO)12 and Co2(CO)8 by 
 coimpregnation followed by decarbonylation under H2 at 623 K has been probed by atmospheric ethylene hydroformylation at 423 K. 
 The catalytic behavior is consistent with that of RhCo3/SiO2 derived from RhCo3(CO)12. At the same time, the corresponding binary 
 catalysts prepared from inorganic rhodium and cobalt salts exhibit much lower activities than RhCo3/SiO2 and significantly enhanced 
 activities compared to monometallic catalysts. The results suggest that the increase in catalytic activity by combination of rhodium and 
 cobalt is attributed to the bimetallic catalysis by RhCo3 clusters regardless of the synergistic catalysis by monometallic rhodium and 
 cobalt sites.Intrinsic hydroformylation kinetics have been measured in a high-throughput kinetic test setup at temperatures varying from 
 448 to 498 K, with the total pressure ranging from 1 to 3 MPa. A gaseous feed containing CO, C 2H4 and H2 was used with space times varying
 from 2.7 kgcat s/molC2H4,in to 149 kgcat s/molC2H4,in. Three catalysts have been investigated, i.e., 5%Rh on Al2O3, 1%Co on 
 Al2O3 and 0.5%Co-0.5%Rh on Al2O3. The main products observed were ethane, propanal and propanol. The Rh catalyst showed the highest 
 hydroformylation and hydrogenation site time conversions in the investigated range of operating conditions. Moreover it was found on 
 all investigated catalysts that the hydrogenation activation energy was about 15-20 kJ mol-1 higher than that for hydroformylation. On the
 Rh catalyst, higher ethylene feed concentrations have a more pronounced effect on CO conversion and production of propanal and propanol 
 compared with an increase in the inlet concentration of the other reactants.© 2013 Elsevier B.V. All rights reserved.
 Ethylene hydroformylation and carbon monoxide hydrogenation (leading to methanol and C2-oxygenates) over Rh/SiO2 catalysts share several 
 important common mechanistic features, namely, CO insertion and metal-carbon (acyl or alkyl) bond hydrogenation. However, these processes 
 are differentiated in that the CO hydrogenation also requires an initial CO dissociation before catalysis can proceed. In this study, the 
 catalytic response to changes in particle size and to the addition of metal additives was studied to elucidate the differences in the two 
 processes. In the hydroformylation process, both hydroformylation and hydrogenation of ethylene occurred concurrently. The desirable 
 hydroformylation was enhanced over fine Rh particles with maximum activity observed at a particle diameter of 3.5 nm and hydrogenation was 
 favored over large particles. CO hydrogenation was favored by larger particles. These results suggest that hydroformylation occurs at the 
 edge and corner Rh sites, but that the key step in CO hydrogenation is different from that in hydroformylation and occurs on the surface.
 The addition of group II-VIII metal oxides, such as MoO3, Sc2O3, TiO2, V2O5, and Mn2O3, which are expected to enhance CO dissociation,
 leads to increased rates in CO hydrogenation, but only served to slow the hydroformylation process slightly without any effect on the 
 selectivity. Similar comparisons using basic metals, such as the alkali and alkaline earths, which should enhance selectivity for insertion
 of CO over hydrogenation, increased the selectivity for the hydroformylation over hydrogenation as expected, although catalytic activity
 was reduced. Similarly, the selectivity toward organic oxygenates (a reflection of the degree of CO insertion) in CO hydrogenation was also
 increased.The reduction of cobalt and rhodium salts coadsorbed on silica by aqueous NaBH4 at 273 K in Ar allows the synthesis of catalytic 
 systems formed by very small rhodium crystallites (< 4 nm) and cobalt oxide/hydroxide. The presence of an unreduced cobalt species is well 
 documented by TPR and XPS. The cobalt oxide is probably deposited on the rhodium surface, obscuring a large amount of the active metal 
 centers. As can be judged by FT-IR and XRD data the morphology of the system is not modified by thermal treatments in CO and H2.
 The system resulted inactive for the atmospheric hydroformylation of propene, but actively catalyzed the reaction when a slight pressure (506 kPa) was 
 applied. The high values of chemoselectivity towards hydroformylation (R = 0.75) and regioselectivity to linear aldehydes (S(L) = 96) can 
 be due to the electronic and steric effects of the cobalt oxide layer.A Rh/Al system with rhodium nanocrystals was prepared by reducing 
 rhodium trichloride supported on silica with lithium aluminum hydride at low temperature in THF. After pretreatment in Ar and in CO/H2 the 
 system was found to be an active catalyst of vapour phase propene hydroformylation at atmospheric pressure. The nature and composition of 
 the active surface was studied by X-ray diffraction, X-ray photoemission spectroscopy (XPS) and Fourier transform-IR spectroscopy. 
 Regioselectivity and chemoselectivity data are correlated to the proposed nature and morphology of the active sites of the catalyst derived 
 from spectroscopic data. The Rh/Al system is compared with the Rh/B system we described in preceding papers."""
onto_class_list=load_classes_chebi()
sents = text_prep(test_txt) 
categories,chem_list, reac_dict, sup_cat, abbreviation= CatalysisIE_search(model, sents)
missing, match_dict, rel_synonym, onto_new_dict=chemical_prep(chem_list, onto_class_list)

'''