# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 15:13:36 2023
Processing without existence check
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
    categories,chem_list, reac_dict, sup_cat, abbreviation,entities_raw= CatalysisIE_search(model, sents)
    missing, match_dict,chem_list,rel_synonym, onto_new_dict=chemical_prep(chem_list, onto_class_list)
    return chem_list, categories,onto_new_dict, sup_cat, abbreviation, missing, match_dict, rel_synonym, reac_dict,entities_raw
        
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

    class_list = [*set(class_list)] #remove duplicates
    class_list.extend(['molecule'])
    missing, match_dict = create_list_IRIs(class_list,IRI_json_filename = 'iriDictionary')

    return missing, match_dict,chem_list, rel_synonym,onto_new_dict

def synonym_dicts(class_list):
    """
    extracts class names and descriptions based on class list (as owlready2 object)
    returns dictionary with general structure of 
    desc_dict = {ontology_class_label : Definition string}
    WARNING: Descriptions often have different identifiers (see try:... except loop)
          Implemented IAO_0000115 and .comment for now. 


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
                        key = k
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
                            idx = input('write number of fitting synonym or "none"\n')                            
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
test_txt="""Unprecedented bimetallic cobalt–rhodium layered hydrotalcite-type materials (CoRh-HT) were successfully prepared and used as potential catalysts for highly selective hydroformylation of alkenes to aldehydes. This is the first report on hydroformylation studied using a Co–Rh-based heterogeneous catalyst that contains cobalt present in the Co2+ and Co3+ oxidation states and rhodium present as an Rh3+ ion in the framework. Presence of Rh3+ along with Co2+ and Co3+ in the layered framework was confirmed based on various physicochemical studies such as HRTEM, powder X-ray diffraction, and X-ray photoelectron spectroscopy.

1. Introduction
Hydroformylation is one of the most powerful and widely applied industrial processes employed for the synthesis of aldehydes from olefins by using syngas (a mixture of H2 and CO) through an atom-efficient method [1,2]. Active species in homogeneous catalysts are tunable; therefore, homogeneous catalysts afford more efficient systems than heterogeneous catalysts. Nevertheless, heterogeneous catalysts are of considerable interest for use in industrial applications because they can be conveniently recovered and recycled [3].Transition-metal-based catalysts containing metals such as Fe, Co, Ru, Rh, Pd, Pt, and Os have been extensively studied [[4], [5], [6]]. Among these catalysts, Rh-, Co-, and Pt-based catalysts are considered to be powerful tools for achieving selectivity in hydroformylation reactions [[4], [5], [6], [7]].To date, Rh- and Co-based catalysts are most widely used for hydroformylation due to their selectivity toward linear aldehydes and their abundance and affordability [[8], [9], [10], [11], [12]]. Rhodium complexes with phosphorus-based ligands are crucial for homogeneous hydroformylation reactions. Attempts have also been made to stabilize Rh in polymer matrices, porous polymers, ionic liquids, supercritical fluids, etc. [[8], [9], [10], [11], [12]]. However, difficulties associated with the recovery and recycling of these materials restrict their extensive application [13,14]. Therefore, the development of novel catalytic systems that combine the advantages of homogenous and heterogeneous catalysis is still a major aim in modern chemistry. Further, to date, no efficient catalyst has been proposed for hydroformylation that functions under ambient reaction conditions, such as low temperatures, pressures, and durations. Because rhodium- and cobalt-based catalysts are the most efficient catalysts for the hydroformylation of alkenes, the development of heterogeneous catalysts based on Rh and Co systems is essentials. In this regard, it is worth mentioning that hydrotalcite (HT)-like materials are a class of clays containing brucite-like layers, which possess a molar composition of [M2+1-xM3+x(OH)2](An)x/n.mH2O. These clays have a positively charged framework layer and exchangeable interlayer anions and have attracted increasing interest in the field of catalysis [[15], [16], [17]]. Notably, HT-based materials have been used as catalysts or catalytic supports in many organic transformations such as alkylation, isomerization, hydroxylation, trans-esterification, redox reactions, condensation, hydroformylation, and environmentally-friendly reactions [[18], [19], [20]]. In particular, monometallic α-Co(OH)2+x species, which are analogous to layered double hydroxides, have attracted considerable interest as electrochemical, optical, and catalytic materials [21,22].Therefore, the introduction of trivalent metal ions such as Rh3+ into the framework of α-Co(OH)2+x could provide unique materials that are potential hydroformylation catalysts. To the best of our knowledge, there have been no reports on the introduction of trivalent ions, particularly Rh3+, into the framework of cobalt hydrotalcite and on the exploration of the catalytic behavior of such composites. The introduction of rhodium into the less expensive framework of α-Co(OH)2+x may afford a catalyst with the potential for hydroformylation under mild conditions. In this study, for the first time, we prepare rhodium-containing cobalt hydrotalcite (CoRh-HT)-type materials through an in situ sol-gel method. The resultant layered CoRh-HT-type materials were utilized for the hydroformylation of 1-octene and demonstrated to be promising catalysts. The rhodium-containing α-Co(OH)2+x species, which are analogous to layered hydrotalcite, were prepared in the presence of hexamethylenetetramine. The resultant materials were thoroughly characterized by various spectroscopic analytical methods.

2. Experimental
2.1. Chemicals and materials
Following chemicals such as cobalt acetate hydrate [Co(CH3COO)2.4H2O, 99.9%; Spectrochem], Rhodium Chloride hydrate [RhCl3.xH2O, 99.9%; Zeswa Catalyst Pvt. Ltd., India], Hexamethylenetetraamine[(CH2)6N4, 99.0%]and 1-Octene [C8H16, 98.0%; Sigma-Aldrich], 1-Decene [C10H20,96.0%], 1-Heptene [C7H14, 98.0%] and 1-Hexene [C6H12, 98.0%] were purchased from Alfa Aesar. Toluene and Ethanol were procured from Merck, India. Double distilled water was used for all the experiments. H2 and CO gas mixture (1:1) was obtained from Sigma Gas, India. All the chemicals were used as received form without any further purification.

2.2. Synthesis of layered Co-Rh-HT type materials
The synthesis was performed in a round bottom flask under mild reaction condition viz.90 ○C for over-night. In a typical procedure, cobalt acetate (10 mmol) and hexamethylenetetramine (120 mmol) were added to 400 mL of a 9:1 mixture of double distilled water and ethanol. The reaction mixture was stirred at 90 °C for over-night. Then calculated amount of RhCl3.xH2O [in 5 mL water] solution was added drop wise to the reaction mixture at room temperature and allowed to stir for. The precipitate formed was filtered, washed with water and ethanol mixture and dried at room temperature. The sample prepared with 0.02, 0.04 and 0.06 mmol of rhodium salts are represented as CoRhHT-1, CoRhHT-2 and CoRhHT-3 respectively.

2.3. Characterization
The structure and purity of as synthesized Cobalt Rhodium HT were characterized by Powder X-ray diffraction [XRD] patterns recorded on a Brüker D8 diffractometer with Cu-Kα radiation (λ = 1.54184 Å). The diffraction patterns were recorded in the 2θ range 5−70°. The Fourier-transform infrared (FT-IR) analyses were conducted in transmission mode with KBr pallets. It was recorded using a Brüker Tenser 27 FT-IR in the range 400–4000 cm1. The elemental analysis of the HT materials was carried out by ICP-AES techniques on Labtam Plasma Lab 8440 equipment. X-ray photoelectron spectra (XPS) were acquired using Multilab 2000 model obtained from Thermo Scientific, UK having monochromatic Al and standard Mg/Al sources. Further analysis was carried out using 0.9 Fityk version software, which is capable of smoothing, background subtraction and peak deconvolution. The Gaussian-Lorentzian summation function was applied to describe these peaks. The morphology and dimensions of the samples were examined with a (Phillips Technai G2T30) TEM operated at 300 kV.

2.4. Catalytic studies on hydroformylation of olefins
The synthesized catalyst was utilized for hydroformylation of olefins (Scheme 1), namely, 1-octene, 1-hexene, 1-heptene, and 1-decene in a stainless steel autoclave (Amar equipment India Pvt. Ltd.). In a typical procedure, 100 mg of CoRh-HT catalyst in the powder form (particle size: 1 mm), 1-octene (0.0191 M; 3 ml), and the solvent (toluene: 3 ml) were added into the liquid phase reactor under a nitrogen atmosphere. Subsequently, the reaction was conducted at an appropriate temperature in the range of 60‒100 ○C under various syngas [CO and H2 (1:1)] pressures in the range of 20–65 bar with a stirring rate in the range of the rotation speed 100–300 rpm for 6 h. The products were analyzed in a HP-5 capillary column (30 m, HP-5) by using gas chromatography equipped with a flame ionizing detector (Agilent 7890A Series). The recyclability of the catalyst was studied after washing with toluene in the same condition. To identify the leaching of metal ions under the reaction conditions, the product mixture was analyzed by an atomic absorption spectrophotometer (Perkin Elmer; PinAAcle 9004) by using an air-acetylene flame.
3. Results and Discussion
The FT-IR spectra of layered CoRh-HT prepared by using various rhodium concentrations along with α-Co-(OH)2 are displayed in Fig. 1. The spectra exhibited broad absorption bands centered around 3450 and 1640 cm−1. These broad bands can be attributed to the stretching and bending vibrational modes of the OH groups coordinated to the metal ions in the layered brucite-type sheets. The vibrational bands appear at around 2081 cm−1. An additional vibrational band appears at around 2081 cm−1 in thespectra of the rhodium-containing sample. This band can be attributed to the Rh‒C stretching characteristic [[23], [24]] that occurs due to the interaction of Rh3+ ions present in the α-Co(OH)2+x framework with charge balancing carbonate anions. The aforementioned fact clearly demonstrated that the Rh3+ ions are present in the α-Co(OH)2+x framework due to the isomorphous substitution. (In addition, the observed vibrational band below 600 cm−1 corresponds to the M-O stretching and bending mode vibrations.
The powder XRD patterns of α-Co(OH)2 and CoRh-HT prepared with various rhodium concentration are shown in Fig. 2. All the samples exhibited characteristic XRD reflections around 2θ = 7°–9° and 18° corresponding to (003) and (006) of an HT-type layered structure, respectively (Fig. 2) [25,26]. The XRD patterns of the CoRh-HT samples prepared with low rhodium ion loading have an additional peak that can be attributed to the cobalt spinel structures. However, as the concentration of rhodium (Rh3+) ions increases (sample: CoRh-HT-3), Rh3+ ions stabilize the layered HT structure. This stabilization results in the broadening of the X-ray reflection and enables the formation of a layered structure and free from of any impurity phase. The aforementioned fact clearly support that the introduction of trivalent rhodium ions in the lattice of Co-HT facilitated the stabilization of the HT structure. Moreover, the absence of any X-ray reflections corresponding to metallic rhodium indicates that the rhodium ions are highly dispersed in the framework of the layered α-Co(OH)2+x-type structure. The elemental composition of the resultant materials was analyzed using the ICP-AES analysis, and the results are shown in Table 1. The results are in agreement with the molar–gel composition used as the initial gel composition.
The particle size, morphology, and structure of the layered CoRh-HT-type materials were further investigated by high-resolution transmission electron microscopy (HR-TEM), and the corresponding images are shown in Fig. 3. The HR-TEM images of CoRh-HT-1, CoRh-HT-2, and CoRh-HT-3 display uniform plate-like needles, typical correspond to the layered HT-type structures. An observation of the HR-TEM images indicated the absence of a clear dot; this fact implies no rhodium metal nanoparticles were present on the surface of CoRh-HT-type materials. Therefore, rhodium is concluded to be exclusively present in the framework of the α-Co(OH)2+xHT-type materials due to the isomorphous substitution.
To evaluate the oxidation state and environment of rhodium in the layered CoRh-HT-type materials, X-ray photoelectron spectral (XPS) studies were conducted, and the results are displayed in Fig. 4. The cobalt–rhodium hydrotalcite materials prepared with various rhodium concentrations contained Co in the Co+2 and Co+3 oxidation states and Rh in the Rh+3 state, as confirmed by XPS. The Co 2p XPS spectra of all the samples showed the presence of two components due to the spin–orbit coupling of the Co 2p3/2 and Co 2p1/2 states with binding energies of 779.0 and 794.8 eV, respectively [[27], [28], [29]]. The binding energy of cobalt along with the satellite peaks suggest that cobalt is present in mixed oxidation states, that is, Co(II) and Co(III). The Rh 3d5/2 core level was indicated by a peak centered around 309.8 eV, which is a characteristic of the Rh3+ species [[30], [31], [32], [33]] present in the framework of layered CoRh-HT-type materials, and is in agreement with the results of FT-IR, XRD, and HR-TEM [[30], [31], [32], [33]].
3.1. Hydroformylation of olefins over CoRh-HT
The catalytic activity of the layered CoRh-HT-1 material (particle size: approximately 1 mm) in the 1-octene hydroformylation reaction was thoroughly investigated by varying the reaction conditions, such as the pressure (20–65 bar), temperature (60–100 ○C) and time (2–6 h), as shown in Fig. 5, Fig. 6, Fig. 7. In all cases, hydro-formylated products were obtained as the major products along with some minor by-products such as alcohols that are derived by the hydrogenation of post-hydroformylation. In particular, at a low pressure, the catalyst facilitates the formation of a higher amount of olefin-isomerized products than hydro-formylated products, which accounts for the poor hydroformylated product selectivity at low pressures (Fig. 5). Irrespective of the reaction temperature in the range of 60–100 °C, the conversion of olefins remains constant (approximately 98%), as shown in Fig. 6. Moreover, a slight decrease in the aldehyde selectivity was evident at an elevated temperature. However, the use of lower alkenes such as hexane and heptene displayed a superior conversion at 100 °C. The catalytic conversion remains consistent with respect to the stirring conditions (100–300 rpm) and the catalyst particle size (1–3 mm); this fact indicates that there is no diffusion limitation on the catalytic process. The olefin conversion and hydroformylation product formation increased with increases in the reaction time (Fig. 7) and reaches to the maximum conversion at 6 h. Thus, the optimum conditions, corresponding to the maximum olefin conversion (98%) and the highest aldehyde selectivity (96%), were found to be 100 °C using 100 mg of catalyst under a pressure of of syngas [CO and H2 (1:1)] for 6 h. The used catalyst was separated under a nitrogen atmosphere, washed, dried, and subsequently reused for several runs; the results are displayed in Table 2. The catalytic conversion remained almost constant over several runs. However, the selectivity toward the hydroformylated product decreased considerably after several cycles due to the formation of a considerable amount of isomerized olefin and secondary product, namely, alcohol generated by the hydrogenation of hydroformylated products. Moreover, ICP-AES analysis confirmed that there is no leaching of any metal ions (either Co or Rh). The analysis displayed that there is no ppm level of the cobalt and rhodium present in the reaction medium. The aforementioned fact was confirmed by analyzing the elemental composition of used catalysts during each run (Table 2). The results demonstrated that used catalysts are identical to the fresh catalyst. Moreover, the concentration of cobalt and rhodium on the reused catalysts is observed to (Table 2) remain constant after every cycle, supports true heterogeneous catalyst nature of the present catalysts. The catalyst was further utilized in the hydroformylation of several olefins under the optimum reaction conditions, and the results are summarized in Table 3. In all cases, more than 95% olefin conversion was obtained with excellent selectivity toward the aldehyde products. In particular, the lighter olefin yielded formation of a linear aldehyde with more than 70% selectivity. A decrease in the carbon chain length of the substrate in the olefin hydroformylation (C10, C8 and C7, C6) facilitated the formation of a considerable amount of isomerized products. The high branched aldehyde selectivity might be due to the isomerization of linear alkene to branched alkene on the surface of a metal oxide [40,41]. The reaction was also studied using pure cobalt hydrotalcite and HT with various rhodium loadings; the results are shown in Table 4. Clearly, the presence of rhodium ions enhances the catalytic conversion with an exclusive formation of hydroformylation products andwas further confirmed from TOF, which increases with an increase in the rhodium content. In particular, the introduction of a high amount of rhodium ions facilitated the formation of more linear aldehyde selectivity. Moreover, the catalytic activity was compared with that documented in recent literature (Table S1)[5,10,11, [34], [35], [36], [37], [38], [39]]. Clearly, the present heterogeneous catalyst yielded a superior conversion and linear aldehyde selectivity under ambient reaction conditions [temperature (100 ○C), pressure (50 bar) and duration (6 h)] compared to most of the literature studies that deal with heterogenized homogeneous catalysts. The formation of layered hydrotalcite-type materials with exposed trivalent rhodium sites facilitated excellent olefin conversion with a desirable aldehyde selectivity of more than 96%.
4. Conclusions
This is the first report that deals with the synthesis and characterization of Rh3+-containing layered CoRh-HT-type materials. The presence of Rh3+ ions in the framework was proved by XPS. The resultant CoRh-HT exhibited an excellent catalytic activity in the hydroformylation of olefins under ambient reaction conditions. The catalyst retained its activity even after several runs."""
onto_class_list=load_classes_chebi()

model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
chem_list, categories,onto_new_dict, sup_cat, abbreviation, missing, match_dict, rel_synonym, reac_dict,entities_raw = run_text_mining(test_txt,model, onto_class_list)



categories,chem_list, reac_dict, sup_cat, abbreviation= CatalysisIE_search(model, sents)
missing, match_dict, rel_synonym, onto_new_dict=chemical_prep(chem_list, onto_class_list)
38.52 seconds  33.84 
323.99 seconds 351.45
324.65
'''