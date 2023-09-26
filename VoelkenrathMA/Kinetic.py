# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:22:24 2023

@author: smmcvoel
"""
import yaml
from collections import Counter

#with open("E:/Bibliothek/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
with open("C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
    data = yaml.safe_load(file)
    
mechanism = data[2]["ChemicalReaction"][0]
substances = data[0]["Mixture"][0]["substances"]
#kinetics = []

equations = []
for sub in substances:
    eqn = f"d[{sub}]/dt = "
    
    for i in range(len(mechanism)):
        educts = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[0].split("+")
        products = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[1].split("+")
        
        if sub in educts:
            print("educts: " + sub + " " + str(educts) + str(products))
            count = Counter(educts)
            stoichiometry = count[sub]
            stoichiometry_str = f" - k{i}[{educts[0]}"
            
            for educt in educts[1:]:
                stoichiometry_str += f"][{educt}"
            
            stoichiometry_str += "]" if stoichiometry == 1 else f"] ** {stoichiometry}"
            
            print(f"... stoich. coeff. is: {stoichiometry}")
            print(educts[0])
            eqn = eqn + stoichiometry_str
            
        elif sub in products:
            print("product: " + sub + " " + str(educts) + str(products))
            count = Counter(products)
            stoichiometry = count[sub]
            stoichiometry_str = f" + k{i}[{educts[0]}"
            
            for educt in educts[1:]:
                stoichiometry_str += f"][{educt}"
            
            stoichiometry_str += "]" if stoichiometry == 1 else f"] ** {stoichiometry}"
            
            print(f"... stoich. coeff. is: {stoichiometry}")
            print(products[0])
            eqn = eqn + stoichiometry_str
    
    equations.append(eqn)



for i in range(len(equations)):
    print(equations[i])
    print(" ")