# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 08:43:28 2023

@author: smmcvoel
"""

import os
import pythoncom

pythoncom.CoInitialize()

import clr
import System

from System.IO import Directory, Path, File
from System import String, Environment
from System.Collections.Generic import Dictionary

dwsimpath = "C://Users/smmcvoel/AppData/Local/DWSIM7/"

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


def create_compound(compounds):    
    Directory.SetCurrentDirectory(dwsimpath)
    
    # create automation manager
    interf = Automation3()
    sim = interf.CreateFlowsheet()
    
    # data input
    """
    Data Input (name, rel-Dichte, nbps?) sollte automatisiert ablaufen. Als allgemeingültiger Input evtl. Smiles o.ä.
    Vergleich CreateSubstanceJSON
    Ideen:
        - Schaue nach Datenbanken, aus denen man die Infos auslesen kann. 
        - Abschätzen anhand ähnlicher Substanzen
    """
    
    # pseudocompound generator
    comps = GenerateCompounds()
    
    for i in range(len(compounds)):
        "ACHTUNG: relative_densities & nbps müssen angepasst werden, wenn ich die abfrage des Data-Input geklärt habe!"
        comp_res = comps.GenerateCompunds(compounds[i], 1,  Tccorr, Pccorr, AFcorr, MWcorr, adjustAf, adjustZR, None, relative_densities[i], nbps[i], None, None, None, None, mw0, sg0, nbp0)
        
        comp_values = list(comp_results.Values)
        comp_values[0].Name = compounds[i]
        comp_values[0].ConstantProperties.Name = compounds[i]
        comp_values[0].ComponentName = compounds[i]
        
        # save compound in JSON-file
        System.IO.File.WriteAllText("C://Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/substances" + str(compounds[i]) + ".json", JsonConvert.SerializeObject(comp_values[0].ConstantProperties, Formatting.Indented))