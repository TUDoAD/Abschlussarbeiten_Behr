# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 09:32:55 2023

@author: smmcvoel
"""

import json
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
name = "NewReaction_06_DataSheet"
path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/"

# specify the simulated temperature, pressure and velocity
with open("parameter.json") as json_file:
    para = json.load(json_file)
    
temperature = para["temperature"] # K
pressure = para["pressure"] # Pa
res_t = para["res_t"] # m/s

# execute the script which calls the simulation as subprocess
CallSubprocess.call_subprocess(name, temperature, pressure, res_t, path)

# evaluate the simulation results and (not programmed now!) add every simulated system as individual to ontology
if "_DataSheet" in name:
    name_sim = name.split("_DataSheet")[0]  

directory = path + name_sim + "/"
#EvaluateMethanation.MinMax(name, directory)
#EvaluateMethanation.Selectivity(directory)