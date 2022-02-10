Code from Alexander Behr @ TUDO University developed for NFDI4Cat

# OntoClassesSearcher.py

## onto_loader(list_of_ontology_names)
Loads ontologies (based on list_of_ontology_names) and outputs a class list and a description/definitions list as dictionary with ontology name as key(s).
Ontology names should be the ones of the .owl-files placed in the ./ontologies subdirectory.

## onto_class_comparison(description_list_dictionary, file_name, new_file_name)
Find same entries of class names in both concept_table and ontologies.
Load Excel-File with name file_name and store list with all concepts, and their definitions (if any) as new_file_name Excel-file.

# Running
Follow commands which are commented at end of OntoClassesSearcher.py (below Example within code)

Execute once to load all ontologies from list 
    
    [class_dict, desc_dict] = onto_loader(["chmo","Allotrope_OWL", "chebi"])

Execute to compare text.xlsx with loaded ontologies, store resulting Dataframe in test_comp.xlsx

    onto_class_comparison(desc_dict, 'test', 'test_comp')
