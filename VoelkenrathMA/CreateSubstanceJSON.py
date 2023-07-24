# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 11:31:05 2023

@author: mvoel
"""

import os
import pythoncom

# initialize the COM-Infrastucture (Component Object Model)
pythoncom.CoInitialize()

import clr
import System

from System import String, Environment
from System.IO import Directory, Path, File
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\mvoel\\AppData\Local\\DWSIM\\"

# adding the DWSIM dll's to the python interpreter

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