# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 13:40:14 2023

@author: smmcvoel
"""
import yaml
import owlready2

## Import all necessary DWSIM packages
import os
import uuid
import clr

import pythoncom
import System
pythoncom.CoInitialize()

from System import String, Environment
from System.IO import Directory, Path, File
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\smmcvoel\\AppData\\Local\\DWSIM7\\"

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
#clr.AddReference(dwsimpath + "TcpComm.dll")
#clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")
clr.AddReference(dwsimpath + "DWSIM.FlowsheetSolver.dll")
clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
clr.AddReference(dwsimpath + "Newtonsoft.Json")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

from enum import Enum
from DWSIM import FlowsheetSolver
from DWSIM import Interfaces
from System import *

from System.Linq import *
from DWSIM import *
from DWSIM import FormPCBulk
from DWSIM.Interfaces import *
from DWSIM.Interfaces.Enums import *

from DWSIM.Interfaces.Enums.GraphicObjects import *

from Newtonsoft.Json import JsonConvert, Formatting

from DWSIM.Thermodynamics import *
from DWSIM.Thermodynamics.BaseClasses import *
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import *

from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization import GenerateCompounds
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization.Methods import *

#Directory.SetCurrentDirectory(dwsimpath)

# create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()


def CreateSubstanceJSON(data):
    ## Creates a JSON-file for every substance which is not in DWSIM database by calling the compound creation wizard
    ## For the most catalyst-subtrate complexes there is not data such as boiling point etc.
    ## This parameters get estimated with the pure components
    """
    Public Function GenerateCompounds(prefix As String, count As Integer, TCcorr As String, PCcorr As String, AFcorr As String, MWcorr As String, 
                                      AdjustAF As Boolean, AdjustZR As Boolean, mwi As Nullable(Of Double), sgi As Nullable(Of Double),
                                      tbi As Nullable(Of Double), v1i As Nullable(Of Double), v2i As Nullable(Of Double),
                                      t1i As Nullable(Of Double), t2i As Nullable(Of Double),
                                      _mw0 As Double, _sg0 As Double, _tb0 As Double) As Dictionary(Of String, ICompound)
    """    
    water = sim.AvailableCompounds["Water"]
    compounds = sim.AvailableCompounds
    compounds_list = list(compounds)
    
    for i in range(len(compounds_list)):
        value = compounds_list[i].get_Value()
        cas = value.CAS_Number
        if '7732-18-5' == cas:
            print("Successful")
    return water


def CreateSimulationFlowsheet(data):
    ## Creates a simulation flowsheet for the given reaction system
    # define streams, inlet, outlet, energie
    stream_info = []
    for i in range(len(data[0]["Mixture"][0]["mole_fraction"])):    
        print(i)
        
        
def run():
    # load yaml-datafile
    # ACHTUNG: Übergabe des yaml-file zum Ende hin Variabel gestalten, sodass gesamter Workflow
    # mit einem einzigen Befehl ausgeführt werden kann
    # ACHTUNG: Onto-Klassen sind voerst im DataSheet auskommentiert, da sie Probleme beim Import gemacht haben
    # --> Lösung sollte allgemeingültig sein, d.h. die Klassen vorher zu definieren klappt nur wenn es automatisiert geht
    
    with open("linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
        data = yaml.safe_load(file)
        
    water = CreateSubstanceJSON(data)
    return water
    #CreateSimulationFlowsheet(data)
    
    