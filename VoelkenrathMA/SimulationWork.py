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
    
    # Achtung: Bevor die Substanzen muss noch eine Abfrage durchgeführt werden welche Substanzen bereits in DWSIM vorhanden sind.
    # Zuordnung in DWSIM leider nur durch CAS möglich, woher bekomme ich diese?
    # Pubchem-API geht nicht, ChEBI-API läuft nur mit ID's diese habe ich allerdings auch nicht
    """
    water = sim.AvailableCompounds["Water"]
    compounds = sim.AvailableCompounds
    compounds_list = list(compounds)
    
    for i in range(len(compounds_list)):
        value = compounds_list[i].get_Value()
        cas = value.CAS_Number
        if '7732-18-5' == cas:
    """
    print("")
    


def CreateSimulation(data):
    ## Creates a simulation flowsheet for the given reaction system
    
    # create and connect objects
    # Wasser anschließend durch eigene Edukte ersetzen
    water = sim.AvailableCompounds["Water"]
    sim.SelectedCompounds.Add(water.Name, water)
    
    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    h1 = sim.AddObject(ObjectType.Heater, 100, 50, "heater")
    
    m1 = m1.GetAsObject()
    m2 = m2.GetAsObject()
    e1 = e1.GetAsObject()
    h1 = h1.GetAsObject()
    
    sim.ConnectObjects(m1.GraphicObject, h1.GraphicObject, -1, -1)
    sim.ConnectObjects(h1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, h1.GraphicObject, -1, -1)
    
    sim.AutoLayout()
    
    stables = PropertyPackages.SteamTablesPropertyPackage()
    sim.AddPropertyPackage(stables)
    
    m1.SetTemperature(300.0) # Kelvin
    m1.SetMassFlow(100.0) # kg/s --> evtl. VolumeFlow auch möglich
    
    h1.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature
    h1.OutletTemperature = 400 # Kelvin
    
    Settings.SolverMode = 0
    
    errors = interf.CalculateFlowsheet2(sim)
    
    print(String.Format("Heater Heat Load: {0} kW", h1.DeltaQ))
    
    # save file
    fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "heatersample.dwxmz")
    
    interf.SaveFlowsheet(sim, fileNameToSave, True)
    
    # packages to draw and save the pdf to an image and display it
    clr.AddReference(dwsimpath + "SkiaSharp.dll")
    clr.AddReference("System.Drawing")
    
    from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
    from System.IO import MemoryStream
    from System.Drawing import Image
    from System.Drawing.Imaging import ImageFormat
        
    # save the pdf to an image and display it
    PFDSurface = sim.GetSurface()
    
    bmp = SKBitmap(1024, 768)
    canvas = SKCanvas(bmp)
    canvas.Scale(1.0)
    PFDSurface.UpdateCanvas(canvas)
    d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
    str = MemoryStream()
    d.SaveTo(str)
    image = Image.FromStream(str)
    imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "pfd.png")
    image.Save(imgPath, ImageFormat.Png)
    str.Dispose()
    canvas.Dispose()
    bmp.Dispose()
    
    from PIL import Image
    
    im = Image.open(imgPath)
    im.show()
    
        
def run():
    # load yaml-datafile
    # ACHTUNG: Übergabe des yaml-file zum Ende hin Variabel gestalten, sodass gesamter Workflow
    # mit einem einzigen Befehl ausgeführt werden kann
    # ACHTUNG: Onto-Klassen sind voerst im DataSheet auskommentiert, da sie Probleme beim Import gemacht haben
    # --> Lösung sollte allgemeingültig sein, d.h. die Klassen vorher zu definieren klappt nur wenn es automatisiert geht
    
    with open("linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
        data = yaml.safe_load(file)
   
    #CreateSubstanceJSON(data)
    CreateSimulation(data)
    
    