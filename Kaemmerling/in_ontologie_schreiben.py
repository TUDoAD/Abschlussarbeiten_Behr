

from owlready2 import *
onto_world = owlready2.World()
onto = onto_world.get_ontology("./KlassenHierarchieDWSIM_AB.owl").load()
Flow = onto.Output({'Flow':{'water':1.0}}) 
#a= list(onto.Output())
#a = onto.Flow.get_properties() 
#destroy_entity(Flow)
onto.save("KlassenHierarchieDWSIM_AB.owl")