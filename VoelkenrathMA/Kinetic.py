# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:22:24 2023

@author: smmcvoel
"""
import yaml
from collections import Counter

with open("E:/Bibliothek/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
#with open("C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
    data = yaml.safe_load(file)
    
mechanism = data[2]["ChemicalReaction"][0]
substances = data[0]["Mixture"][0]["substances"]
kinetics = []
"""
for sub in substances:
    temp = []
    temp.append(sub)
    index = substances.index(sub)
    eqn_kin = ""
    eqn_kin = eqn_kin.join("k=" + str(index))
    for i in range(len(mechanism)):
        if sub in mechanism[i]["reactions"][0]["reaction_equation"]:
            eqn_reac = mechanism[i]["reactions"][0]["reaction_equation"].split(">")
            if sub in eqn_reac[0]:
                eqn_kin = eqn_kin.join("-")
                educts = eqn_reac[0].split("+")
                count = Counter(educts)
                for educt in educts:
                    eqn_kin = eqn_kin.join(f"[{educt}]**{count[educt]}")
            elif sub in eqn_reac[1]:
                eqn_kin = eqn_kin.join("+")
                products = eqn_reac[1].split("+")
                count = Counter(educts)
                for product in products:
                    eqn_kin = eqn_kin.join(f"[{educt}]**{count[educt]}")
    kinetics.append(eqn_kin)
"""
equations = []
for sub in substances:
    eqn = f"eqn: d[{sub}]/dt = "
    for i in range(len(mechanism)):
    
        educts = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[0].split("+")
        products = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[1].split("+")
        if sub in educts:
            print("educts: " + sub + " " + str(educts) + str(products))
            count = Counter(educts)
            print(f"... stoich. coeff. is: -{count[sub]}")
            if len(educts) == 1:
                print(educts[0])
                eqn = eqn + f" - k{i}[{educts[0]}]"
            elif len(educts) == 2 and educts[0] == educts[1]:
                print(educts[0] + " ** 2")
                eqn = eqn + f" - k{i}[{educts[0]}] ** 2"
            else:
                print(educts[0] + educts[1])
                eqn = eqn + f" - k{i}[{educts[0]}][{educts[1]}]"
                        
        elif sub in products:
            print("product: " + sub + " " + str(educts) + str(products))
            count = Counter(products)
            print(f"... stoich. coeff. is: {count[sub]}")
            if len(products) == 1:
                print(products[0])
                eqn = eqn + f" + k{i}[{products[0]}]"
            elif len(products) == 2 and products[0] == products[1]:
                print(products[0] + " ** 2")
                eqn = eqn + f" + k{i}[{products[0]}] ** 2"
            else:
                print(products[0] + products[1])
                eqn = eqn + f" + k{i}[{products[0]}][{products[1]}]"
    
    print("EQUATION: " + eqn)
    print(" ")
    equations.append(eqn)

for i in range(len(equations)):
    print(equations[i])
    print(" ")