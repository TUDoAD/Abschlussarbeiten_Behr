# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 09:08:37 2023

@author: smdicher
"""
from text_mining import load_classes_chebi, delete_files_in_directory, run_text_mining, add_publication
from preprocess_onto import *
from onto_extension import preprocess_classes,create_classes_onto
from txt_extract import get_abstract, get_metadata
from CatalysisIE.model import *
from CatalysisIE.utils import *

abstract= """Laccases (EC 1.10.3.2) are multicopper oxidases found in plants, fungi, and bacteria. Laccases oxidize a variety of phenolic substrates, performing one-electron oxidations, leading to crosslinking. For example, laccases play a role in the formation of lignin by promoting the oxidative coupling of monolignols, a family of naturally occurring phenols.[1] Other laccases, such as those produced by the fungus Pleurotus ostreatus, play a role in the degradation of lignin, and can therefore be classed as lignin-modifying enzymes.[2] Other laccases produced by fungi can facilitate the biosynthesis of melanin pigments.[3] Laccases catalyze ring cleavage of aromatic compounds.[4]

Laccase was first studied by Hikorokuro Yoshida in 1883 and then by Gabriel Bertrand[5] in 1894[6] in the sap of the Japanese lacquer tree, where it helps to form lacquer, hence the name laccase.

Active site

The tricopper site found in many laccases; note that each copper center is bound to the imidazole sidechains of histidines (color code: copper is brown, nitrogen is blue).
The active site consists of four copper centers, which adopt structures classified as type I, type II, and type III. A tricopper ensemble contains types II and III copper (see figure). It is this center that binds O2 and reduces it to water. Each Cu(I,II) couple delivers one electron required for this conversion. The type I copper does not bind O2, but functions solely as an electron transfer site. The type I copper center consists of a single copper atom that is ligated to a minimum of two histidine residues and a single cysteine residue, but in some laccases produced by certain plants and bacteria, the type I copper center contains an additional methionine ligand. The type III copper center consists of two copper atoms that each possess three histidine ligands and are linked to one another via a hydroxide bridging ligand. The final copper center is the type II copper center, which has two histidine ligands and a hydroxide ligand. The type II together with the type III copper center forms the tricopper ensemble, which is where dioxygen reduction takes place.[7] The type III copper can be replaced by Hg(II), which causes a decrease in laccase activity.[1] Cyanide removes all copper from the enzyme, and re-embedding with type I and type II copper has been shown to be impossible. Type III copper, however, can be re-embedded back into the enzyme. A variety of other anions inhibit laccase.[8]

Laccases affects the oxygen reduction reaction at low overpotentials. The enzyme has been examined as the cathode in enzymatic biofuel cells.[9] They can be paired with an electron mediator to facilitate electron transfer to a solid electrode wire.[10] Laccases are some of the few oxidoreductases commercialized as industrial catalysts."""
def set_config_key(key, value):
     globals()[key] = value
     
with open("config.json") as json_config:
     for key, value in json.load(json_config).items():
         set_config_key(key, value)
p_id=1         
model = BERTSpan.load_from_checkpoint(ckpt_name, model_name=bert_name, train_dataset=[], val_dataset=[], test_dataset=[])
onto_class_list = load_classes_chebi()
new_world = owlready2.World()
onto = new_world.get_ontology('./ontologies/{}.owl'.format(onto_old)).load()
with onto:
    pub_c = types.new_class('publication', (Thing,))
    new_pub = pub_c('publication{}'.format(p_id))
onto.save('./ontologies/{}.owl'.format(onto_new))

chem_list, categories,onto_new_dict, sup_cat, abbreviation, missing, match_dict, rel_synonym, reac_dict = run_text_mining(abstract,model, onto_class_list)
df_entity, rel_synonym, missing_all, match_dict_all = preprocess_classes(categories, sup_cat, rel_synonym, chem_list, missing, match_dict)
