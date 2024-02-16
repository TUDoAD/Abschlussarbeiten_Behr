# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 12:42:48 2024

@author: smdicher
"""
import time
from owlready2 import *
import json
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
        ontology = new_world3.get_ontology('http://purl.obolibrary.org/obo/chebi.owl').load()
    except:
        ontology = new_world3.get_ontology('./ontologies/chebi.owl').load()
    onto_class_list = list(ontology.classes())

    set_org_mol= ontology.search_one(label='organic group').descendants()
    for i in set_org_mol:
        if i in onto_class_list:
            onto_class_list.remove(i)
    
    print("--- %.2f seconds ---" % (time.time() - start_time))
    #onto_dict,inchikey = synonym_dicts(onto_class_list)
    try:
        onto1_iris = list([cls.iri for cls in onto_class_list])
    except:
        print("IRIs of ontology " + ontology.name + " not (well) defined and could not be read!")
        onto1_iris=[]
        return None
    iri_dict ={}
    
    for iri in onto1_iris:
       
        try:
            if type(ontology.search_one(iri = iri).label.first()) == locstr: 
                # some ontologies use locstrings to account for different languages
                class_label = ontology.search_one(iri = iri).label.first().split()[0]
            else:
                class_label = ontology.search_one(iri = iri).label.first()
        except:
            #class_label = None
            try: 
                if type(ontology.search_one(iri = iri).prefLabel.first()) == locstr: 
                    # some ontologies use locstrings to account for different languages
                    class_label = ontology.search_one(iri = iri).prefLabel.first().split()[0]
                else:
                    class_label = ontology.search_one(iri = iri).prefLabel.first()
            except:
                #class_prefLabel = None
            
                try:
                    if type(ontology.search_one(iri = iri).altLabel.first()) == locstr:
                        # some ontologies use locstrings to account for different languages
                        class_label = ontology.search_one(iri = iri).altLabel.first().split()[0]
                    else:
                        class_label = ontology.search_one(iri = iri).altLabel.first()
                except:
                    class_label = None
                    print('no label')
                    continue
        '''
        try: 
            if type(ontology.search_one(iri = iri).prefLabel.first()) == locstr: 
                # some ontologies use locstrings to account for different languages
                class_prefLabel = ontology.search_one(iri = iri).prefLabel.first().split()[0]
            else:
                class_prefLabel = ontology.search_one(iri = iri).prefLabel.first()
        except:
            class_prefLabel = None
        
        try:
            if type(ontology.search_one(iri = iri).altLabel.first()) == locstr:
                # some ontologies use locstrings to account for different languages
                class_altLabel = ontology.search_one(iri = iri).altLabel.first().split()[0]
            else:
                class_altLabel = ontology.search_one(iri = iri).altLabel.first()
        except:
            class_altLabel = None
        '''    
        synonyms=[]
        try:
            class_name = ontology.search_one(iri = iri).name
        except:
            class_name = None
        try:
            #if type(ontology.search_one(iri = iri).comment) == locstr:
                # some ontologies use locstrings to account for different languages
            #    class_altLabel = ontology.search_one(iri = iri).comment.split()[0]
            #else:
            synonyms.extend(ontology.search_one(iri = iri).comment)
        except:
            class_comment = None        
        try:
                synonyms.extend(ontology.search_one(iri = iri).hasRelatedSynonym)
        except:
                class_relsyn = None 
        try:
            synonyms.extend(ontology.search_one(iri = iri).hasExactSynonym)
        except:
                class_relsyn = None 
        try:
            synonyms.extend(ontology.search_one(iri = iri).formula)
        except:
                class_relsyn = None 
        if class_label:

            synonyms.append(class_label)
        try:
            inchikey =ontology.search_one(iri = iri).inchikey
        except:
                inchikey = None 
        iri_dict[str(iri)] = {"label": class_label,
                                       #"prefLabel": class_prefLabel,
                                       #"altLabel": class_altLabel,
                                       "synonyms":[*set(synonyms)],
                                       #"name": class_name,
                                       "inchikey": inchikey
                                       }
    with open('iriDictionaryChEBI.json', 'w') as fp:
            json.dump(iri_dict, fp)
            fp.close()
    return iri_dict
