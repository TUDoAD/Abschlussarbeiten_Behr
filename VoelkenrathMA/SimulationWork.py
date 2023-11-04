# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 09:32:55 2023

@author: smmcvoel
"""

import CallSubprocess
import EvaluateMethanation

"""
Script calls the simulation and the evaluation of the simulated parameter combinations.

USER-INPUT:
    - Set the name of the yaml-file which shall be used for simulation (without ending: .yaml)
    - Set the path to your directory with the yaml files
ATTENTION:
    If you want to switch between simulation with and without downstream look at: CallSubprocess.py
"""

# set path for the data-sheet
"!!USER-INPUT!!"
name = "NewReaction_02_DataSheet"
path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/"

# specify the simulated temperature, pressure and velocity
temperature = [273, 373]#, 473, 573, 673, 773, 873] # K
pressure = [100000]#, 500000, 1000000, 2000000, 3000000] # Pa
velocity = [0.0001]#, 0.001, 0.01, 0.1, 1] # m/s

# execute the script which calls the simulation as subprocess
CallSubprocess.call_subprocess(name, temperature, pressure, velocity, path)

# evaluate the simulation results and (not programmed now!) add every simulated system as individual to ontology
if "_DataSheet" in name:
    name_sim = name.split("_DataSheet")[0]  

directory = path + name_sim + "/"
EvaluateMethanation.MinMax(name, directory)
EvaluateMethanation.Selectivity(directory)