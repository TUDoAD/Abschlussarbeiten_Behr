# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 14:11:17 2023

@author: smmcvoel
"""
import yaml
import itertools
import SimulateMethanation



with open("C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/new_reaction_2023-10-12_DataSheet.yaml", "r") as file:
    data = yaml.safe_load(file)

# Set parameter for simulation-dice
temperature = [300,350,400,450,500] # K
pressure = [100000, 150000, 200000, 250000, 300000] # Pa
cat_loading = [1, 10, 100, 1000, 100000] # kg/m3

parameter_combinations = list(itertools.product(temperature, pressure, cat_loading))
for combination in parameter_combinations:

    print(f"Simulate system with T={combination[0]} K, p={combination[1]} Pa, Loading={combination[2]} kg/m3")
    name=(f"Methanation_{combination[0]}K_{combination[1]}Pa_{combination[2]}kgm3")
    SimulateMethanation.simulation(name, data, combination)
    print(" ")