
import json
from owlready2 import *
onto_world = owlready2.World()
onto = onto_world.get_ontology("./rdf-new.owl").load()
compoundscompoundflow =  {"Water" : 0.5, 'Ethanol': 0.5}
Laufvar = 1
    # Ab hier : Speichern des substance Dicts in Ontology Individual als comment 
ProcessID = str(Laufvar)
Flow = onto.outlet_stream("Composition"+ProcessID, comment =str(compoundscompoundflow)) 
## Ab hier: Auslesen des neuesten Dictionaries aus Ontology
# Verweis auf Individuum aus Ontologie suchen
individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
comment_string = individual_searched.comment
compoundscompoundflow = json.loads(comment_string[0].replace("'","\""))
# ontology speichern
onto.save("KlassenHierarchieDWSIM_AB.owl")
Laufvar = Laufvar +1