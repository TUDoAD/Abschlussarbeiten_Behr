
import json
from owlready2 import *
onto_world = owlready2.World()
onto = onto_world.get_ontology("./rdf-new.owl").load()
#if True == False:
 #   Flow = onto.outlet_stream({'Water': 1.0})
  #  onto_output = list(onto.outlet_stream.direct_instances())[0]
   # compoundscompoundflow = onto_output.get_name()
    #destroy_entity(Flow)

#if True == False:
#ProcessID = "1"
for i in range(2):
    # AB hier : Speichern des substance Dicts in Ontology Individual als comment 
    Laufvar = 1
    ProcessID = str(i)

    Comp_Dict =  {"Water" : 0.5, 'Ethanol': 0.5}
    #Comp_Dict = [{'water':i},{'water2':1.0},{'water3':1.0},{'water4':1.0}]
#onto = onto_world.get_ontology("./rdf-new.owl").load()
    Flow = onto.outlet_stream("Composition"+ProcessID, comment =str(Comp_Dict)) 
#a = list(onto.Output())
#a = onto.Output.get_properties() 
#onto.Output.direct_instances()
#destroy_entity(Flow)
#Laufvar =+ 1
#a = 

#individual_list = onto.outlet_stream.direct_instances()
#names = [x.comment for x in individual_list]
#☻☺☻

## Ab hier: Auslesen des neuesten Dictionaries aus Ontology
# Verweis auf Individuum aus Ontologie suchen
individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
#auslesen des comments = auslesen des Dicts (aber noch als liste, mit einem 
# Eintrag = string des dic)
comment_string = individual_searched.comment
# konvertieren des strings in dict -> type(c) = dict
c = json.loads(comment_string[0].replace("'","\""))

onto.save("KlassenHierarchieDWSIM_AB.owl")