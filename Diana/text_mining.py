# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 15:13:36 2023

@author: smdicher
"""

import stanza
#stanza.download('en', package='craft', processors='tokenize')
import spacy
from owlready2 import *
from CatalysisIE.model import *
from CatalysisIE.utils import *
import os
from chemdataextractor import Document
from pubchempy import get_compounds
from preprocess_onto import *

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
     
   
def add_publication(onto_new,onto_old,doi,title,abstract):
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
            if not has_doi:
                class has_doi(DataProperty):
                    range = [str]
                    label = 'has doi'
            new_pub.has_doi = [doi]
            has_title=onto.search_one(label='has title')
            if not has_title:
                class has_title(DataProperty):
                    range = [str]
                    label ='has title'
            new_pub.has_title = [title]
    onto.save('./ontologies/{}.owl'.format(onto_new))
    

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
    #output_tensor_buf = []
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

def CatalysisIE_search(model, test_sents, onto_list, onto_new, onto_old): #change description at the and
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
    nlp = spacy.load('en_core_web_sm')
    chem_list_all = []
    chem_list = []
    sup_cat = {}
    abbreviation = {}
    a=0
    categories={}
    reac_dict={}

    entity_old = (0,None,None)
    output_sents = pred_model_dataset(model, test_sents)
    for sent in output_sents:
        sent_tag = [t['pred'] for t in sent]
        print(assemble_token_text(sent))
        chem_list_all.extend([c.text for c in Document(assemble_token_text(sent)).cems])
        abb_list = Document(assemble_token_text(sent)).abbreviation_definitions
        for i in range(len(abb_list)):
            abbreviation[abb_list[i][0][0]] = abb_list[i][1][0]
        for i, j, l in get_bio_spans(sent_tag):
            print(assemble_token_text(sent[i:j + 1]), l)
            entity = assemble_token_text(sent[i:j + 1])
            
            #add abbreviation if directly after entity an entity in brackets
            if i == a+1 and '({})'.format(entity) in assemble_token_text(sent):
                abbreviation[entity] = entity_old[1]
            
            #match hyphen in chemical entity and remove it  # Rh-Co --> RhCo
            match_hyph = re.findall(r'(([A-Z](?:[a-z])?)[—–-]([A-Z](?:[a-z])?))', entity) 
            if match_hyph:
                for i in range(len(match_hyph)):
                    entity = entity.replace(match_hyph[i][0],match_hyph[i][1]+match_hyph[i][2])
            
            #preprocess the entity with spacy: plural to singular
            doc_list = []
            doc = nlp(entity)
            for i in range(len(doc)):
                if doc[i].tag_ == 'NNS':
                    doc_list.append(str(doc[i].lemma_))
                else:
                    doc_list.append(str(doc[i]))
            entity = " ".join(doc_list)         
            e_split = entity.split()
            entity = doc_token(entity, e_split)
            
            pattern = r'([A-Za-z]+[\s]?[—–-] [a-z]+|[A-Za-z]+ [—–-][\s]?[a-z]+)'
            e_split = re.findall(pattern,entity)
            if e_split:
                print('e_split:{} and entity:{}'.format(e_split, entity)) # check again for examples!
                for i in e_split:
                    i_n = i.replace(' ','')
                    entity = re.sub(i,i_n,entity)
                    missing,_= create_list_IRIs([re.sub(r'[—–-]','',i_n)], onto_list,onto_new,onto_old)
                    if not missing:
                        entity = re.sub(i_n,re.sub(r'[—–-]','',i_n),entity)
            
            #if reactant before reaction: append to reac_dict dictionary {'reaction-type':'reactant'}
            if l == 'Reaction':
                if entity_old[0]+1 == i and entity[2]=='Reactant':
                    if entity not in reac_dict.keys():
                        reac_dict[entity] = [entity_old[1]]
                    elif entity_old[1] not in reac_dict.values():
                        reac_dict[entity].append(entity_old[1])
                
            
            if entity in categories.keys():
                entity_old = (j,entity,l)
                continue
            else:
                mol = re.findall(r'(([\w@—–-]+)(?:[\s]?/[\s]?|[\s]on[\s])+([\w@—–-]+))', entity) # 'RhCo on Al2O3' or 'RhCo/Al2O3'
                if mol:
                    for i in range(len(mol)):
                        if ('supported' or 'Supported') in mol[i][0]:
                            continue
                        elif l == 'Catalyst':
                            if '/' in mol[i][0]:
                                entity = entity.replace('/',' supported on ')
                                sup=True
                            elif 'on' in mol[i][0]:
                                sup= False
                                for c in chem_list_all:
                                    if re.search(mol[i][1],c):
                                        entity = entity.replace('on','supported on')
                                        sup= True
                                        break    
                            if sup==True:    
                                support = mol[i][2]
                                chem_list.append(support)
                                catalyst = mol[i][1]
                                chem_list.append(catalyst)
                                if support in sup_cat.keys():
                                    if catalyst not in sup_cat[support]:
                                        sup_cat[support].append(catalyst)
                                else:
                                        sup_cat[support] = [catalyst]
                        else:
        
                            for k in range(1, len(mol[i])):
                                chem_list.append(mol[i][k])
                                entity = entity.replace('/',',')
                
                pattern = r'^[\d,]+[—–-] [a-z]+$' #1,3- butadiene -> 1,3-butadiene
                if re.search(pattern,entity) or re.search(r'^ [A-Za-z\d—–-]+$',entity):
                    entity=entity.replace(' ','') 
                
                spans = sorted(Document(entity).cems, key = lambda span: span.start)
                chem_list.extend([c.text for c in spans])
                chem_list.extend([c for c in chem_list_all if c in entity and c not in chem_list]) #add chemicals that wasn't recognized with chemdataextractor like()
                
                for c in chem_list: # search if for i.e. ZSM-5 in entity if only ZSM found. replace ZSM with ZSM-5 in chem_list
                    if re.findall(r'{}[—–-][\d]+[\s]'.format(c), entity):
                        chem_list[:] = [re.findall(r'{}[—–-][\d]+[\s]'.format(c), entity)[0] if x == c else x for x in chem_list]
                        
                if 'system' in entity or 'surface' in entity and l=='Catalyst':
                        entity = entity.replace('system','catalyst')
                        entity = entity.replace('surface','catalyst')
                if 'loaded' in entity:#Zr-loaded ZSM-5 zeolites
                    for i in range(len(spans)):
                        if i != 0:
                            e_btwn = entity[spans[i-1].end:spans[i].start]
                            if 'loaded' in e_btwn:    
                                loaded_end =  entity.index('loaded')+len('loaded')+1
                                for c in chem_list:
                                    try:
                                        idx = entity.index(c)
                                    except:
                                        continue
                                    else:
                                        if idx == loaded_end:
                                            if c not in sup_cat.keys():
                                                sup_cat[c] = []
                                            k=0
                                            while k<i:
                                                if spans[k].text not in sup_cat[c]:
                                                    sup_cat[c].append(spans[k].text)
                                                k+=1
                    entity = entity.replace('loaded','supported on')                                           
                #else:
                categories[entity] = l 
            entity_old = (j,entity,l)  
            a = j+1
    chem_list = [*set(chem_list)]
    return categories,chem_list, reac_dict, sup_cat

def doc_token(entity, e_split,  j=0):
    """
    Entity Tokenization Function
    
    This function is used for tokenizing and processing a given entity to remove spaces after .join()-function in CatalystIE_search 
    It is designed to handle specific cases where certain tokens should be combined or modified based on their positions and parts of speech.
    
    Parameters
    ----------
    entity : str
        The input entity within the text.
    
    e_split : list
        A list of splits from the entity.
    
    nlp : object
        A natural language processing (NLP) object used for text processing.
    
    j : int, optional
        The starting index for token processing. Default is 0.
    
    Returns
    -------
    entity : str
        The processed entity after tokenization.

    """
    brackets = False
    doc = nlp(entity) 
    for i,token  in enumerate(doc[j:]):   
        if token == doc[-1]:
            break
        elif token.pos_ in ['CCONJ','PUNCT','SYM','PRON'] and entity[token.idx-1] == ' ' and token.text != "=":
            j=j+i
            if token.pos_ =='CCONJ':
                e_new = ''.join([e_split[j-1],',',e_split[j+1]])
            elif token.pos_=='PRON':
                e_new= ' '.join([e_split[j-1],e_split[j+1]])
                del e_split[j]
            elif token.text =='(' and doc[j+2].text == ')':
                e_new = "".join(e_split[j:j+3])
                brackets = True
                j=j+1
            elif token.text == '(' and brackets == False:
                e_new = "".join([e_split[j],e_split[j+1]])
            elif token.text == ')' and brackets == False:
                e_new = "".join([e_split[j-1],e_split[j]])
            else:
                e_new = "".join(e_split[j-1:j+2])
            if brackets == False:
                e_after = entity[doc[j+1].idx+len(doc[j+1].text)+1:]
            else:
                e_after = entity[doc[j+2].idx+len(doc[j+2].text)+1:]
            if j == 1:
                entity = " ".join([e_new,e_after])
            else:
                e_before = entity[:doc[j-1].idx]
                entity = " ".join([e_before,e_new,e_after])
                   
            entity = doc_token(entity, e_split, j=j+1)
            break
        else:
            continue
    return entity

def chemical_prep(chem_list, onto_list,onto_class_list,onto_new,onto_old):
    global onto_new_dict
    rel_synonym = {}
    comp_dict = {}
    class_list = []        
    onto_new_dict = {}
    synonyms = {}

    onto_dict,inchikey = synonym_dicts(onto_class_list)
    
    for molecule in chem_list:  
        non_chem = False
        if re.search(r'^ [A-Za-z\d—–-]+|^[A-Za-z\d—–-]+ $',molecule): 
            molecule = molecule.replace(' ','')
        
        if molecule in abbreviation.keys():
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
        if non_chem == True or re.search(r'[A-Z]+[—–-][\d]+', molecule):
            onto_new_dict[molecule] = []
            class_list.append(molecule)
            continue        
        molecule_split = molecule.split()
        if len(molecule_split) >= 2 or re.match(r'[A-Za-z]([a-z]){3,}', molecule) or re.match(r'[\d,]+[—–-][a-z]+',molecule):
             comp_dict[molecule] = molecule_split  
        else:
             comp = re.findall(r'([A-Z](?:[a-z])?)',molecule)
             comp_dict[molecule] = comp

    for k,v in comp_dict.items():
        i = 0
        if k not in onto_new_dict.keys():           
            for c in v:
                for k_o, v_o in onto_dict.items():
                    synonyms = fill_synonyms(synonyms,k,v_o,k_o)
                    synonyms = fill_synonyms(synonyms,c,v_o,k_o)
                
                if i == 0:
                    class_list, key ,rel_synonym = compare_synonyms(synonyms, inchikey, class_list, k, rel_synonym,comp = False)
                    onto_new_dict[key] = []
                    i += 1
                if c == k:
                    comp = key
                    
                else:
                    class_list, comp, rel_synonym = compare_synonyms(synonyms, inchikey, class_list, c, rel_synonym,comp = True)                
                onto_new_dict[key].append(comp)
            for i in onto_new_dict[key]:
                if len(i) == 1: #remove components if one of the components (atoms) doesn't exist (ex.ZMS- Z,M don't exist, S-exists)                                   
                    print('deleted key:{}'.format(key))
                    class_list.remove(key)
                    onto_new_dict.pop(key)
                    break
    class_list= [*set(class_list)] #remove duplicates
    class_list.extend(['molecule'])
    missing, match_dict = create_list_IRIs(class_list, onto_list,onto_new,onto_old,IRI_json_filename = 'iriDictionary')

    return missing, match_dict, rel_synonym

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

def compare_synonyms(synonyms, inchikey, class_list, k, rel_synonym, comp):
    if len(synonyms[k]) == 1:
            key= synonyms[k][0]
    else: 
            comp_check, mol= search_inchikey(inchikey, k)
            if k in comp_check:
                if len(synonyms[k]) == 0:
                    if not mol:
                        print('no synonyms and entities for {}, key = k'.format(k))
                        key = k
                        class_list.append(k)

                        return class_list, key, rel_synonym  
                    elif len(mol)==1:
                        key=mol[0].iupac_name #some of the compounds that can be found in pubchem don't have IUPAC names (i.e. "propyl")
                        
                    else:
                        while True:
                            mol_new= [i for i in mol if i.iupac_name]
                            print('choose iupac name for {}:{}'.format(k,[i.iupac_name for i in mol_new]))
                            print('components have following SMILES:')
                            for i in mol_new:
                                print('{}:{}'.format(i.iupac_name, i.isomeric_smiles))
                            idx= input('write number of fitting iupac name or "none"\n')
                            if idx =='none':
                                key = k
                                class_list.append(k)

                                return class_list, key, rel_synonym                   
                            else:
                                try:
                                    idx= int(idx)
                                    key= mol_new[idx-1].iupac_name
                                    break
                                except:
                                    print('error: write a number between 1 and {} or "none"'.format(len(mol_new)))
                                    
                else:
                    while True:
                            print('choose synonyms for {}:{}'.format(k,synonyms[k]))
                            idx= input('write number of fitting synonym or "none"\n')                            
                            if idx =='none':
                                key = k
                                class_list.append(k)
                                return class_list, key, rel_synonym 
                            else:
                                try:
                                    idx= int(idx)
                                    key= synonyms[k][idx-1]
                                    break
                                except:
                                    print('error: write a number between 1 and {} or "none"'.format(len(synonyms[k])))                               
            elif len(comp_check) == 1:
                key= comp_check[0]                  
            else:
                key = None
                for i in comp_check:
                    if i in synonyms[k]:
                        key = i
                if key == None:
                    print('no synonyms but some matches in inchikey for {}:{}'.format(k, comp_check))                 
                    
    if key == None or not key:
        key = k
    rel_synonym[k]=key          
    class_list.append(key)
    return class_list, key, rel_synonym




ckpt_name = 'CatalysisIE/checkpoint/CV_0.ckpt'
bert_name = 'CatalysisIE/pretrained/scibert_domain_adaption'
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
onto_old = 'afo'
onto_new = 'afo'
onto_list ={
            'CHEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            #'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            'CHMO' : 'http://purl.obolibrary.org/obo/chmo.owl',
            'AFO'  : "./ontologies/afo.owl"
            }   
#onto_new= onto_name+'_upd'
test_txt='''
In order to reveal the influences of metal-incorporation and regeneration of ZSM-5 zeolites on naphtha catalytic cracking, the fresh and regenerated Sr, Zr and La-loaded ZSM-5 zeolites have been prepared and evaluated using n-pentane catalytic cracking as a model reaction.
It was found that the metal-incorporated ZSM-5 zeolites promoted hydride transfer reactions, and the Zr-incorporation helped to promote and maintain the catalytic activity while reduced alkenes selectivity;
the regenerated ZSM-5 zeolites promoted C–H bond breaking that increased alkenes selectivity and n-pentane conversion but accelerated catalyst deactivation.
The regenerated metal-incorporated ZSM-5 zeolites combined the feature roles of metal-incorporation and regeneration in modulating reaction pathways, and seemed a promising way to balance the activity, stability and alkenes selectivity, facilitating the optimal production for light olefins.
Within the research scope, the regenerated Zr-loaded ZSM-5 zeolites reached an optimal production (0.97 g) for light olefins in n-pentane catalytic cracking at 550 °C with a weight hourly space velocity of 3.7 h−1 in 3 h, which was 24% higher than that of the parent HZSM-5 (0.78 g).
RhCo/SiO2 catalyst.This work reported the heterogeneous rhodium oxide catalyst encapsulated within microporous silicalite-1 (S-1) zeolite (Rh2O3@S-1) through epitaxial growth of S-1 seeds pre-anchored with rhodium species.
RhCl3 • nH2O, Co(NO3)2 • 6H2O and 
Co2(CO)8 were purchased commercially. 
Supported catalysts based on the Rh-Co couple, mainly derived from the decomposition of 
bimetallic carbonylic clusters, were found particularly active and selective in the vapor phase 
hydroformylation of simple olefins provided that 
the two metals were in intimate contact 
Rh4(CO)12, and RhCo3(CO)12, were synthesized 
according to literature [14,15]. SiO2 was a silica 
‘Aerosil’ supplied by Degussa with a surface 
area of 380 m2/g. Cobalt
complexes had been the main industrial hydroformylation catalysts until the early 1970s, i.e., prior to the commercialization of
rhodium based catalysts. The present work concentrates on heterogeneous ethylene
hydroformylation on a series of Rh and Co based catalysts. Supported catalysts based on the Rh-Co couple, mainly derived from the decomposition of 
bimetallic carbonylic clusters, were found particularly active and selective in the vapor phase 
hydroformylation of simple olefins provided that 
the two metals were in intimate contact. Here we report the preparation, characterization and reactivity studies on propene hydroformylation of Rh-Co based catalysts, with various Rh/Co ratios, obtained by the reduction of 
the metal salts coadsorbed on silica with NaBH, 
in anaerobic conditions. When the Rh/Al based catalysts were subjected to the same 
experimental conditions only the v(C0) absorption at 2015 cm-’ was observed and appears to be involved in the catalytic process. Based on the DRC 
analysis of the reaction orders and apparent activation energies, we propose that the first step of 
propylene hydrogenation to produce propyl species, which is often considered as a kinetically 
non-relevant step, may play a more important role and should draw more attention for future 
improvement of Rh-based heterogeneous catalysts for propylene hydroformylation. However, detailed mechanisms on
the promotion effect of alloying secondary metals with Rh
still remain elusive, which can be of great importance leading
to the rational optimization of Rh-based alloy catalysts for
active and selective heterogeneous hydroformylation. In this communication, systematic studies of catalytic
behaviors from monometallic Rh supported on MCM-41 (Rh/
MCM-41) to Rh-based bimetallic catalysts with the addition of
a secondary 3rd row transition metal M (RhM3/MCM-41, M =
Fe, Co, Ni, Cu, or Zn) for the heterogeneous hydroformylation
of ethylene were reported by combining experiments and
density functional theory (DFT) calculations. Bimetallic heterogeneous catalysts 
based on rhodium supported on various oxides proved to be the more chemo- and regio-selective systems.Recently, it has been shown that tuning the local environment of Rh and Ir-based atomically dispersed catalysts beyond changing the support composition enables interesting
chemistry, such as ethylene dimerization, NO reduction, 1,3-
butadiene hydrogenation, and methane conversion to acetic
acid with high selectivity.'''
onto_class_list=load_classes_chebi()
sents = text_prep(test_txt) 
categories,chem_list, reac_dict, sup_cat= CatalysisIE_search(model, sents, onto_list, onto_new, onto_old)
missing, match_dict, rel_synonym=chemical_prep(chem_list, onto_list,onto_class_list,onto_new,onto_old)