# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:33:27 2023

@author: mvoel
"""
import itertools
import subprocess

def call_subprocess():
    temperature = [300, 350, 400, 450, 500] # K
    pressure = [100000, 150000, 200000, 250000, 300000] # Pa
    cat_loading = [1, 10, 100, 1000, 100000] # kg/m3
    
    combinations = list(itertools.product(temperature, pressure, cat_loading))
    
    for i in range(len(combinations)):
        name = f"Methanation_{combinations[i][0]}K_{combinations[i][1]}Pa_{combinations[i][2]}kgm3"
        temperature = str(combinations[i][0])
        pressure = str(combinations[i][1])
        loading = str(combinations[i][2])
        command = ['python', 'SimulateMethanation.py', name, temperature, pressure, loading]
        
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        process.wait()
    print("Subprocess called successfull every single simulation!")
    
    
call_subprocess()