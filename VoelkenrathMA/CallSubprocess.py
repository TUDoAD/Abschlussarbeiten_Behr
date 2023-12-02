# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:33:27 2023

@author: mvoel

This Code calls the Simulation as Subprocess, otherwise there would be problems with reloaded DWSIM-modules.
You can choose between the simulation with/without downstream by comment one of the command lines!
"""
import os
import yaml
import itertools
import subprocess

def call_subprocess(name, temperature, pressure, res_t, path):    
    # calling the subprocess-simulation
    combinations = list(itertools.product(temperature, pressure, res_t))   
    
    if "_DataSheet" in name:
        nr_sim_sheet = name.split("_")[1]
    else:
        nr_sim_sheet = "01"
    
    data_path = path + name + ".yaml"
    with open(data_path, "r") as file:
        data = yaml.safe_load(file)
    
    for i in range(len(data)):
        if "Mixture" in data[i]:
            for j in range(len(data[i]["Mixture"][0]["mole_fraction"])):
                if "CO2" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                    x_co2 = data[i]["Mixture"][0]["mole_fraction"][j][1]
    
    for i in range(len(data)):
        if "Reaction_Type" in data[i]:
            name_sim = data[i]["Reaction_Type"] + "_" + str(x_co2)
          
    # creating new folder
    if "_DataSheet" in name:
        name_dir = name.split("_DataSheet")[0]
    
    new_dir = path + name_dir + "/"
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    print(new_dir)
    
    for i in range(len(combinations)):
        print(f"Starting simulation number: {i}")
        name_sim_ = name_sim + f"_{combinations[i][0]}K_{combinations[i][1]}Pa_{combinations[i][2]}ms"
        temperature = str(combinations[i][0])
        pressure = str(combinations[i][1])
        res_t = str(combinations[i][2])
        
        """
        Option1: Simulation of Reactor
        Option2: Simulation of Reactor and Downstream
        """
        #command = ['python', 'SimulateMethanation_simkin.py', name_sim_, temperature, pressure, res_t, new_dir, data_path]
        command = ['python', 'SimulateMethanation_Downstream_simkin.py', name_sim_, temperature, pressure, res_t, new_dir, data_path]
        
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        process.wait()
    print("Simulated every given parameter combination!")
    