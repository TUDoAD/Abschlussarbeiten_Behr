# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 08:32:06 2023

@author: 49157
"""

import clr
import System

dwsimpath = "C:\\Users\\49157\\AppData\\Local\\DWSIM8\\"

clr.AddReference(dwsimpath + "DWSIM")
clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
#clr.ImportExtensions(System.Linq)
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "Newtonsoft.Json")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
 
from System import *
from System.Linq import *
from DWSIM import *
from DWSIM import FormPCBulk
 
from DWSIM.Interfaces import *
from DWSIM.Interfaces.Enums import*
from DWSIM.Interfaces.Enums.GraphicObjects import *
 
from DWSIM.Thermodynamics import*
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.Thermodynamics.BaseClasses import *
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import *
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization import GenerateCompounds
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization.Methods import *
 
from Newtonsoft.Json import JsonConvert, Formatting
from DWSIM.Automation import Automation3

# Create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()
 
# assay data from spreadsheet
 
names = ["NBP46", "NBP65", "NBP85", "NBP105", "NBP115"]
relative_densities = [677.3/1000.0, 694.2/1000.0, 712.1/1000.0, 729.2/1000.0, 739.7/1000.0] # relative
nbps = [46 + 273.15, 65 + 273.15, 85 + 273.15, 105 + 273.15, 115 + 273.15] # K
 
n = 5
 
# bulk c7+ pseudocompound creator settings
 
Tccorr = "Riazi-Daubert (1985)"
Pccorr = "Riazi-Daubert (1985)"
AFcorr = "Lee-Kesler (1976)"
MWcorr = "Winn (1956)"
adjustZR = True
adjustAf = True
 
# initial values for MW, SG and NBP
 
mw0 = 65
sg0 = 0.65
nbp0 = 310
 
# pseudocompound generator
 
comps = GenerateCompounds()
 
for i in range(0, n):
 
    # will generate only 1 pseudocompound for each item on the list of assay data. Normally we generate from 7 to 10 pseudocompounds for each set of assay data (MW, SG and NBP)
 
    comp_results = comps.GenerateCompounds(names[i], 1, Tccorr, Pccorr, AFcorr, MWcorr, adjustAf, adjustZR, None, relative_densities[i], nbps[i], None, None, None, None, mw0, sg0, nbp0)
 
    comp_values = list(comp_results.Values)
    comp_values[0].Name = names[i]
    comp_values[0].ConstantProperties.Name = names[i]
    comp_values[0].ComponentName = names[i]
 
    # save the compound to a JSON file, which can be loaded back on any simulation
 
    System.IO.File.WriteAllText("C:\\Users\\49157\\Desktop\\" + str(names[i]) + ".json", JsonConvert.SerializeObject(comp_values[0].ConstantProperties, Formatting.Indented))
 
    # the following is for calculation quality check only, not required but desired
 
    #myassay = DWSIM.SharedClasses.Utilities.PetroleumCharacterization.Assay.Assay(0, relative_densities[i], nbps[i], 0, 0, 0, 0)
    ms_check = Streams.MaterialStream("","")
    ms_check.SetFlowsheet(sim)
    #ms_check.PropertyPackage = sim.PropertyPackages.Values.ToList()[0]
 
    c1 = Compound(names[i], names[i])
    c1.ConstantProperties = comp_values[0].ConstantProperties
     
    ms_check.Phases[0].Compounds.Add(names[i], c1)
 
    c2 = Compound(names[i], names[i])
    c2.ConstantProperties = comp_values[0].ConstantProperties
     
    ms_check.Phases[1].Compounds.Add(names[i], c2)
 
    c3 = Compound(names[i], names[i])
    c3.ConstantProperties = comp_values[0].ConstantProperties
     
    ms_check.Phases[2].Compounds.Add(names[i], c3)
 
    c4 = Compound(names[i], names[i])
    c4.ConstantProperties = comp_values[0].ConstantProperties
 
    ms_check.Phases[3].Compounds.Add(names[i], c4)
 
    c5 = Compound(names[i], names[i])
    c5.ConstantProperties = comp_values[0].ConstantProperties
     
    ms_check.Phases[4].Compounds.Add(names[i], c5)
 
    c6 = Compound(names[i], names[i])
    c6.ConstantProperties = comp_values[0].ConstantProperties
     
    ms_check.Phases[5].Compounds.Add(names[i], c6)
 
    c7 = Compound(names[i], names[i])
    c7.ConstantProperties = comp_values[0].ConstantProperties
     
    ms_check.Phases[6].Compounds.Add(names[i], c7)
 
    c8 = Compound(names[i], names[i])
    c8.ConstantProperties = comp_values[0].ConstantProperties
     
    ms_check.Phases[7].Compounds.Add(names[i], c8)
 
    ms_check.EqualizeOverallComposition()
 
    #qc = QualityCheck(myassay, ms_check)
    #System.Windows.Forms.MessageBox.Show(str(names[i]) + " quality report:\n\n" + qc.GetQualityCheckReport())
    System.Windows.Forms.MessageBox.Show(str(names[i]))