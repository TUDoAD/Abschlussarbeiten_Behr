# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 09:49:10 2023

@author: chern
"""

# load Ontology and search for classes/subclasses/individuals/Description

from owlready2 import *
from utils2 import *
import os
from CatalysisIE.model import *
from CatalysisIE.utils import * 

ckpt_name = 'CatalysisIE/checkpoint/CV_0.ckpt'
bert_name = 'CatalysisIE/pretrained/scibert_domain_adaption'
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
"""
ontology_name = "chebi"
new_world = owlready2.World()
#onto = new_world.get_ontology("http://purl.obolibrary.org/obo/chebi.owl").load()

onto2 = new_world.get_ontology("./ontologies/chebi_matom.owl").load()
#onto_class_list = list(onto.classes())
onto_class_list2 = list(onto2.classes())
print("Loading {} done. Imported {} classes.".format(ontology_name, len(onto_class_list2)))



synonyms=utils2.synonym_dicts(onto_class_list2)
chem_list= ['RhCaO', 'Rh2O3@S-1','rhodium', 'BeCa']
"""
#bashCommand = 'java -jar c://Windows/robot.jar extract --input ontologies/chebi.owl --method BOT --term-file CLass_IRIs.txt --output ontologies/rxno.owl'
#os.system(bashCommand)    

onto_list ={
            'ChEBI': 'http://purl.obolibrary.org/obo/chebi.owl',
            #'BFO'  : 'http://purl.obolibrary.org/obo/bfo/2.0/bfo.owl',
            'RXNO' : 'http://purl.obolibrary.org/obo/rxno.owl',
            'CHMO' : 'http://purl.obolibrary.org/obo/chmo.owl',
            'AFO'  : "./ontologies/afo.owl"
            }  
#class_list=['atom', 'ion', 'barium atom','oxidation', 'aldehyde reduction', 'rhodium atom','enolisability','Pictet-Spengler reaction']

#match =create_list_IRIs(class_list, onto_list,IRI_json_filename = 'iriDictionary')

#onto_extender(onto_list)
#eq=equality( onto_list,onto_name='AFO')

#c= expand_onto(onto_list, onto_name)

test_txt='''Intrinsic hydroformylation kinetics have been measured in a high-throughput kinetic test setup at
temperatures varying from 448 to 498K, with the total pressure ranging from 1 to 3 MPa. A gaseous
feed containing CO, C2H4 and H2 was used with space times varying from 2.7 kgcat s/molC2H4,in to
149 kgcat s/molC2H4,in. Three catalysts have been investigated, i.e., 5%Rh on Al2O3, 1%Co on Al2O3 and
0.5%Co–0.5%Rh on Al2O3. The main products observed were ethane, propanal and propanol. The Rh catalyst showed the highest hydroformylation and hydrogenation site time conversions in the investigated
range of operating conditions. Moreover it was found on all investigated catalysts that the hydrogenation
activation energy was about 15–20 kJ mol−1 higher than that for hydroformylation. On the Rh catalyst,
higher ethylene feed concentrations have a more pronounced effect on CO conversion and production of
propanal and propanol compared with an increase in the inlet concentration of the other reactants.'''

'''
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
area of 380 m2/g. n-hexane used as the solvent 
was distilled over P205 and stored under Ar 
over activated 5 A molecular sieves. The gases 
H2, CO, C2H4 and Ar had a purity of 99.99%. 
Before introduction into a sample vessel and a 
reactor, they were further purified by passage 
through traps of activated 5 A molecular sieves 
and Mn/MnO. 
The carbonyl clusters Rh4(CO)12, Co2(CO)8 
and RhCo3(CO)12 were employed to prepare a 
series of catalysts such as Rh6(CO)16/SiO2 [16], 
Co4(CO)12/SiO2 [17], [Rh,(C0)16 + 
Co4(CO)12]/SiO2 and RhCo3(CO)12/SiO2. 
SiO2 (60-80 mesh granule) was predehydroxylated under vacuum at 673 K for 5 h and impregnated or coimpregnated with the carbonyl clusters in dry n-hexane under Ar. The impregnated 
systems were subjected to 2 h of stirring. The 
solvent was removed by evacuation and the 
resulting solid samples were dried under vacuum at 1.3 X 10d3 kPa for 1 h. For preparing a 
binary SiO2-supported catalyst from RhCl3 and 
Co2(CO)8, SiO2 was first impregnated with an 
aqueous solution of RhCl3 . nH2O followed by 
drying and calcination in air at 673 K for 5 h. 
Then the resulting sample was impregnated with 
a n-hexane solution of Co2(CO)8 followed by 
stirring and removal of the solvent. 
Rh2P nanoparticles (NPs) have been identified as suitable mimics
of [RhI(Ph3P)3]+, the benchmark of homogeneous catalysts in liquid-phase
hydroformylation. For this reason, a fitted synthetic strategy is required to develop
catalysts based exclusively on Rh2P NPs.'''

test_sents = text_prep(test_txt)


#new_world= owlready2.World()
#for k,value in onto_list.items():
#    onto= new_world.get_ontology(value).load()
#    print('{} loaded'.format(k))
categories,chem_list,abbreviations, cat_sup = CatalysisIE_search(model, test_sents, onto_list)
#entity= 'heterogeneous rhodium oxide catalyst encapsulated within microporous silicalite-1 (S-1) zeolite'
#is_s_dict=search_entity(onto=onto, entity_full= entity, category= 'Catalyst', onto_list=onto_list,IRI_json_filename='iriDictionary')
new_dict, missing, match_dict= chemical_prep(chem_list, onto_list, onto)