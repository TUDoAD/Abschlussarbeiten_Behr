
import json
from owlready2 import *
onto_world = owlready2.World()
onto = onto_world.get_ontology("./KlassenHierarchieDWSIM_AB.owl").load()
Flow = onto.Output({'Water': 1.0})
onto_output = list(onto.Output.direct_instances())[1]
compoundscompoundflow = onto_output.get_name()
destroy_entity(Flow)

#ProcessID = "1"
#Comp_Dict = {'Flow':[{'water':1.0},{'water2':1.0},{'water3':1.0},{'water4':1.0}]}
#onto = onto_world.get_ontology("./rdf.owl").load()
#Flow = onto.Output("Composition"+ProcessID, comment =str(Comp_Dict)) 
#a = list(onto.Output())
#a = onto.Output.get_properties() 
#onto.Output.direct_instances()
#destroy_entity(Flow)

#individual_list = onto.Output.direct_instances()
#names = [x.comment for x in individual_list]
#☻☺☻
#c = json.loads(names[2][0].replace("'","\""))

onto.save("KlassenHierarchieDWSIM_AB.owl")