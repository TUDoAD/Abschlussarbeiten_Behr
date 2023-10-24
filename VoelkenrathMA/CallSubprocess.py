# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:33:27 2023

@author: mvoel
"""
import itertools
import subprocess

def call_subprocess():
    temperature = [270, 272.5, 275, 277.5, 280] # K
    pressure = [200000, 225000 ,250000, 275000,300000] # Pa
    velocity = [0.0005, 0.00075, 0.001, 0.00125, 0.0015] # m/s
    
    combinations = list(itertools.product(temperature, pressure, velocity))
    
    for i in range(len(combinations)):
        print(f"Starting simulation number: {i}")
        name = f"Methanation_{combinations[i][0]}K_{combinations[i][1]}Pa_{combinations[i][2]}ms"
        temperature = str(combinations[i][0])
        pressure = str(combinations[i][1])
        velocity = str(combinations[i][2])
        command = ['python', 'SimulateMethanation.py', name, temperature, pressure, velocity]
        
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        process.wait()
    print("Simulated every given parameter combination successfully!")
    
    
call_subprocess()