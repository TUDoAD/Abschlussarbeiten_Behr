# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:22:35 2023

@author: smmcvoel
"""

import json
import subprocess
    

def ExecDetchemDriver():
    ## Calling DETCHEM Driver
    # define file path
    path = "C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/cli/dist/"
    cli = path + "cli.js"
    dci = path + "input/Methanation_Ni_DETCHEM.txt"
    ckt = path + "input/Methanation_thermdata.txt"
    mol = path + "input/moldata.txt"
    sur = "Ni=2.55e-5" # maybe variable with future "DETCHEM Driver"
    
    command = ["node", cli, "--dci", dci, "--ckt", ckt, "--moldata", mol, "--surface", sur]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.stderr:
        print("ExecDetchemDriver Fehlerausgabe", result.stderr)
        
    # convert from bytes to dict
    data_decode = result.stdout.decode("utf8")
    data_dict = json.loads(data_decode)
    
    """
    Dict muss aufgrund merkwürdiger Formatfusionen noch angepasst werden durch <Main> & <\MAIN>.
    Bevor der erhaltene String dann weiter in ein Dict umgewandelt wird, sollte die ids eine Ebene nach "innen"
    verschoben werden um später die Reihenfolge der Reaktionen festzulegen.
    --> ids müssen nicht verschoben werden, wenn ich STICK durch REACTION ersetzt sollten sie in der richtigen 
        Reihenfolge ins Dict geladen werden
    --> ersetze name=Ni mit name='Ni' & mol/m3=255... mit mol_m3='2,5555'
    """
    # WARNING: the following section maybe needs to be reworked with the next DETCHEM Driver and other mechanism
    
    return data_dict
    

def run():
    data = ExecDetchemDriver()
    return data