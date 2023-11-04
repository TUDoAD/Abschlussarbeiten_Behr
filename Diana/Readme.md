The tool consists following modules: preprocess_onto.py, txt_extract.py, text_mining.py, onto_extension.py also there are jupyter notebook with SPARQL queries examples and functions for querying the ontology depending on the information of interest. 
Before starting the code, some preparations must be done:
-	Folder structure must have the following structure:

main_folder
  
  |__import
  |__ontologies
  |__ontology_snipet
  |__class_lists
 	
-	The ontology to be extended must be stored in the “ontologies” folder;
-	main_folder can also have a different name important is that all Python modules together with config.json are placed inside it;
-	Global variables listed in config.json must be adjusted for the process.
