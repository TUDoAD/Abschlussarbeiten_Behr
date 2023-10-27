# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:33:27 2023

@author: mvoel
"""
"""
This Code calls the Simulation as Subprocess, otherwise there would be problems with reloaded DWSSIM-modules.
You can choose between the simulation with/without downstream by comment one of the command lines!
"""
import os
import itertools
import subprocess

def call_subprocess(name, temperature, pressure, velocity, path):    
    # calling the subprocess-simulation
    combinations = list(itertools.product(temperature, pressure, velocity))
    
    data_path = path + name + ".yaml"
    
    if "_DataSheet" in name:
        name_sim = name.split("_DataSheet")[0]
        
    # creating new folder
    new_dir = path + name_sim + "/"
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    print(new_dir)
    
    for i in range(len(combinations)):
        print(f"Starting simulation number: {i}")
        name_sim_ = name_sim + f"_{combinations[i][0]}K_{combinations[i][1]}Pa_{combinations[i][2]}ms"
        temperature = str(combinations[i][0])
        pressure = str(combinations[i][1])
        velocity = str(combinations[i][2])
        
        command = ['python', 'SimulateMethanation.py', name_sim_, temperature, pressure, velocity, new_dir, data_path]
        #command = ['python', 'SimulateMethanation_Downstream.py', name_sim_, temperature, pressure, velocity, new_dir, data_path]
        
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        process.wait()
    print("Simulated every given parameter combination!")
    