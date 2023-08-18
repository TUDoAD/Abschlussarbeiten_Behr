# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:22:35 2023

@author: smmcvoel
"""
import json
import xmltodict
import subprocess
import regex as re    


def ExecDetchemDriver():
    ## Calling DETCHEM Driver and formatting data 
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
        print("ExecDETCHEMDriver Fehlerausgabe", result.stderr)
        
    # convert from bytes to dict
    data_decode = result.stdout.decode("utf8")
    data = json.loads(data_decode)
    
    # the subdict "pbr.inp" is here still in xml format, formatting and converting into dict
    pbr_xml = data["pbr.inp"]
    pbr_main = "<MAIN>" + pbr_xml + "</MAIN>"
    pbr_rep_1 = pbr_main.replace("<STICK>", "<REACTION>")
    pbr_rep_2 = pbr_rep_1.replace("</STICK>", "</REACTION>")
    pbr_rep_3 = pbr_rep_2.replace("mol/m2", "mol_m2")
    
    # replace two pattern: e.g. name=Ni --> name='Ni' & mol_m2=2.5500e-5 --> mol_m2='2.5500e-5'
    pattern_1 = re.compile(r"name=([A-Za-z0-9]+)")
    pattern_2 = re.compile(r"mol_m2=([\d.e+-]+)")
    
    pbr_rep_4 = re.sub(pattern_1, r"name='\1'", pbr_rep_3)
    pbr_rep_5 = re.sub(pattern_2, r"mol_m2='\1'", pbr_rep_4)
    
    pbr_dict = xmltodict.parse(pbr_rep_5)
    data["pbr.inp"] = pbr_dict
    
    return data
    

def run():
    data = ExecDetchemDriver()
    return data