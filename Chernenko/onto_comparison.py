from owlready2 import *

world1 = owlready2.World()
world2 = owlready2.World()
world3 = owlready2.World()
afo_old = world1.get_ontology("./ontologies/afo.owl").load()
afo_ds1 = world2.get_ontology("./ontologies/afo_dataset-1.owl").load()
afo_ds2 = world3.get_ontology("./ontologies/afo__dataset-2.owl").load()

num_class_diff1 = len(list(afo_ds1.classes()))-len(list(afo_old.classes()))
num_obj_diff1 = len(list(afo_ds1.object_properties()))-len(list(afo_old.object_properties()))
num_dat_diff1 = len(list(afo_ds1.data_properties()))-len(list(afo_old.data_properties()))
num_indv_diff1 = len(list(afo_ds1.individuals()))-len(list(afo_old.individuals()))
num_new_entities = len(afo_ds1.search(iri = "*semanticweb.org*")) - len(afo_old.search(iri = "*semanticweb.org*"))

added_classes_1 = 0
for i in list(afo_ds1.classes()):
    if "semanticweb.org" in i.iri:
        added_classes_1 += 1
        
added_indvs_1 = 0
for i in list(afo_ds1.individuals()):
    if "semanticweb.org" in i.iri:
        added_indvs_1 += 1

added_obj_props_1 = 0
for i in list(afo_ds1.object_properties()):
    if "semanticweb.org" in i.iri:
        added_obj_props_1 += 1

added_dat_props_1 = 0
for i in list(afo_ds1.data_properties()):
    if "semanticweb.org" in i.iri:
        added_dat_props_1 += 1    
    


num_class_diff2 = len(list(afo_ds2.classes()))-len(list(afo_old.classes())) 
num_obj_diff2 = len(list(afo_ds2.object_properties()))-len(list(afo_old.object_properties()))
num_dat_diff2 = len(list(afo_ds2.data_properties()))-len(list(afo_old.data_properties()))
num_indv_diff2 = len(list(afo_ds2.individuals()))-len(list(afo_old.individuals()))
num_new_entities = len(afo_ds2.search(iri = "*semanticweb.org*")) - len(afo_old.search(iri = "*semanticweb.org*"))

added_classes_2 = 0
for i in list(afo_ds2.classes()):
    if "semanticweb.org" in i.iri:
        added_classes_2 += 1
        
added_indvs_2 = 0
for i in list(afo_ds2.individuals()):
    if "semanticweb.org" in i.iri:
        added_indvs_2 += 1

added_obj_props_2 = 0
for i in list(afo_ds2.object_properties()):
    if "semanticweb.org" in i.iri:
        added_obj_props_2 += 1

added_dat_props_2 = 0
for i in list(afo_ds2.data_properties()):
    if "semanticweb.org" in i.iri:
        added_dat_props_2 += 1    
        
        

print("onto_1:\nClasses_diff:" +str(num_class_diff1) + "\n" + "Obj_diff:" + str(num_obj_diff1) + "\n" + "dat_prop_diff:" + str(num_dat_diff1) + "\n" + "individual_diff:" + str(num_indv_diff1) +"\n" + "new_entities:"+ str(num_new_entities) + "\n" + "    custom_classes:"+ str(added_classes_1) + "\n" + "    custom_obj_props:"+ str(added_obj_props_1) + "\n"+ "    custom_dat_props:"+ str(added_dat_props_1) + "\n"+ "    custom_individuals:"+ str(added_indvs_1) + "\n")

print("onto_2:\nClasses_diff:" +str(num_class_diff2) + "\n" + "Obj_diff:" + str(num_obj_diff2) + "\n" + "dat_prop_diff:" + str(num_dat_diff2) + "\n" + "individual_diff:" + str(num_indv_diff2) +"\n" + "new_entities:"+ str(num_new_entities) + "\n" + "    custom_classes:"+ str(added_classes_2) + "\n" + "    custom_obj_props:"+ str(added_obj_props_2) + "\n"+ "    custom_dat_props:"+ str(added_dat_props_2) + "\n"+ "    custom_individuals:"+ str(added_indvs_2) + "\n")

