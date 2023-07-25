# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 11:31:05 2023

@author: mvoel
"""

import os

import pythoncom
pythoncom.CoInitialize()
import clr
import System

from System.IO import Directory, Path, File
from System import String, Environment
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\mvoel\\AppData\Local\\DWSIM\\"

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
#clr.AddReference(dwsimpath + "TcpComm.dll")
#clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

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

# create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

# data input
"""
Schauen ob das soweit automatisiert werden kann, dass folgender Abschnitt automatisiert mit Input abläuft.
Zum erstellen des Codes zunächst noch mit Elnaz Daten.
"""
names = ["Laccase", "ABTS_ox", "ABTS_red"]
relative_densities = [677.3/1000.0, 694.2/1000.0, 712.1/1000.0]  # relative
nbps = [46 + 273.15, 65 + 273.15, 85 + 273.15]  # K

# bulk c7+ pseudocompund creator settings
"""
Dient als Referenz, da manche Werte gefehlt haben, ebenso wie bei mw0, sg0, nbp0. Ich sollte mir ebenfalls eine passende Substanz heraussuchen.
"""
Tccorr = "Riazi-Daubert (1985)"
Pccorr = "Riazi-Daubert (1985)"
AFcorr = "Lee-Kesler (1976)"
MWcorr = "Winn (1956)"
adjustZR = True
adjustAf = True

# initial values for MW, SG, NBP

mw0 = 65
sg0 = 0.65
nbp0 = 310

# pseudocompund generator

comps = GenerateCompounds()

for i in range(len(names)):

    # Will generate one pseudocopund for each item on the list of assay data.

    comp_results = comps.GenerateCompounds(names[i], 1, Tccorr, Pccorr, AFcorr, MWcorr, adjustAf, adjustZR, None, relative_densities[i], nbps[i], None, None, None, None, mw0, sg0, nbp0)
    
    comp_values = list(comp_results.Values)
    comp_values[0].Name = names[i]
    comp_values[0].ConstantProperties.Name = names[i]
    comp_values[0].ComponentName = names[i]
    
    # save the copund to a JSON file, which ca be loaded back on any simulation
    
    System.IO.File.WriteAllText("E:\\Bibliothek\\Documents\\GitHub\\Abschlussarbeiten_Behr\\VoelkenrathMA\\substances\\" + str(names[i]) + ".json", JsonConvert.SerializeObject(comp_values[0].ConstantProperties, Formatting.Indented))
        