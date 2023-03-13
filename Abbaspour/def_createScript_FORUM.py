# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 11:16:19 2023

@author: 49157
"""

import clr
import uuid
import os

import pythoncom
pythoncom.CoInitialize()
import clr

import System
from System import *
from System.Threading import *
from System.Linq import *

from System.IO import Directory, Path, File
from System import String, Environment
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\49157\\AppData\\Local\\DWSIM8\\"

clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")
clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "System.Buffers.dll")

clr.AddReference(dwsimpath + "DWSIM.FlowsheetSolver.dll")
clr.AddReference("System.Core")
clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings
from DWSIM import FlowsheetSolver
from DWSIM import Interfaces

Directory.SetCurrentDirectory(dwsimpath)

# Create automation manager
interf = Automation3()
Flowsheet = interf.CreateFlowsheet()

def createScript(obj_name):
    #GUID = str(uuid.uuid1())
    GUID = obj_name
    Flowsheet.Scripts.Add(GUID, FlowsheetSolver.Script())
    #By not declaring the ID the tabs of each script is not loaded
    #Flowsheet.Scripts.TryGetValue(GUID)[1].ID = GUID
    Flowsheet.Scripts.TryGetValue(GUID)[1].Linked = True
    Flowsheet.Scripts.TryGetValue(GUID)[1].LinkedEventType = Interfaces.Enums.Scripts.EventType.ObjectCalculationStarted
    Flowsheet.Scripts.TryGetValue(GUID)[1].LinkedObjectName = obj_name
    Flowsheet.Scripts.TryGetValue(GUID)[1].LinkedObjectType = Interfaces.Enums.Scripts.ObjectType.FlowsheetObject
    Flowsheet.Scripts.TryGetValue(GUID)[1].PythonInterpreter = Interfaces.Enums.Scripts.Interpreter.IronPython
    Flowsheet.Scripts.TryGetValue(GUID)[1].Title = obj_name
    Flowsheet.Scripts.TryGetValue(GUID)[1].ScriptText = str("Whatever code of Python you want")

createScript("Test")
    
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "test.dwxmz")
interf.SaveFlowsheet(Flowsheet, fileNameToSave, True)    