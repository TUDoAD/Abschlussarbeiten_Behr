# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 12:53:14 2023

@author: 49157
"""

import os

import pythoncom
pythoncom.CoInitialize()
import clr
import System

from System.IO import Directory, Path, File
from System import String, Environment
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\49157\\AppData\\Local\\DWSIM8\\"

clr.AddReference(dwsimpath + "DWSIM")
clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")
clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "System.Buffers.dll")

clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
clr.AddReference(dwsimpath + "Newtonsoft.Json")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

from System import *
from System.Linq import *
from DWSIM import *
from DWSIM import FormPCBulk
 
from DWSIM.Interfaces import *
from DWSIM.Interfaces.Enums import*
from DWSIM.Interfaces.Enums.GraphicObjects import *
from Newtonsoft.Json import JsonConvert, Formatting

from DWSIM.Thermodynamics import*
from DWSIM.Thermodynamics.BaseClasses import *
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import *
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization import GenerateCompounds
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization.Methods import *

Directory.SetCurrentDirectory(dwsimpath)

# Create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

# assay data from spreadsheet
 
names = ["Laccase", "ABTS_ox", "ABTS_red"]
relative_densities = [677.3/1000.0, 694.2/1000.0, 712.1/1000.0] # relative
nbps = [46 + 273.15, 65 + 273.15, 85 + 273.15] # K
 
n = 3
 
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
    
    # Will generate only 1 pseudocompound for each item on the list of assay data.
    # Normally we generate from 7 to 10 pseudocompounds for each set of assay data (MW, SG and NBP)
 
    comp_results = comps.GenerateCompounds(names[i], 1, Tccorr, Pccorr, AFcorr, 
                                           MWcorr, adjustAf, adjustZR, None, 
                                           relative_densities[i], nbps[i], None, 
                                           None, None, None, mw0, sg0, nbp0)
 
    comp_values = list(comp_results.Values)
    comp_values[0].Name = names[i]
    comp_values[0].ConstantProperties.Name = names[i]
    comp_values[0].ComponentName = names[i]
    
    # save the compound to a JSON file, which can be loaded back on any simulation
    # IMPORTANT: Save JSON file into "addcomps" file to be able to import the compound into simulation
 
    System.IO.File.WriteAllText("C:\\Users\\49157\\AppData\\Local\\DWSIM8\\addcomps\\"
                                + str(names[i]) + ".json", 
                                JsonConvert.SerializeObject(comp_values[0].ConstantProperties, 
                                                            Formatting.Indented))
