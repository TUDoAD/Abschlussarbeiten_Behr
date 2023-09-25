# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:22:24 2023

@author: smmcvoel
"""
import yaml
from collections import Counter

with open("C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
    data = yaml.safe_load(file)
    
mechanism = data[2]["ChemicalReaction"][0]

substances = data[0]["Mixture"][0]["substances"]
kinetics = []

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
