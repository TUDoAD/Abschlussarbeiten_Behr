# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 13:40:14 2023

@author: smmcvoel
"""
import yaml
import math
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
    


def ProcessSimulation(name, data):
    ## Creates a simulation flowsheet for the given reaction system
    
    # create and connect objects
    # Achtung: Wasser anschließend durch eigene Edukte ersetzen
    co2 = sim.AvailableCompounds["Carbon dioxide"]
    h2 = sim.AvailableCompounds["Hydrogen"]
    
    sim.SelectedCompounds.Add(co2.Name, co2)
    sim.SelectedCompounds.Add(h2.Name, h2)
    
    # material
    #m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet_1")
    #m2 = sim.AddObject(ObjectType.MaterialStream, 50, 100, "inlet_2")
    #m3 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "mixture")
    m4 = sim.AddObject(ObjectType.MaterialStream, 250, 50, "feed")
    m5 = sim.AddObject(ObjectType.MaterialStream, 400, 50, "outlet")
    m6 = sim.AddObject(ObjectType.MaterialStream, 500, 50, "gas_liquid")
    m7 = sim.AddObject(ObjectType.MaterialStream, 650, 50, "gas")
    m8 = sim.AddObject(ObjectType.MaterialStream, 650, 100, "liquid")
    
    # energy
    #e1 = sim.AddObject(ObjectType.EnergyStream, 150, 125, "power_heater")
    e2 = sim.AddObject(ObjectType.EnergyStream, 250, 125, "power_reactor")
    e3 = sim.AddObject(ObjectType.EnergyStream, 400, 125, "power_cooler")
    #e4 = sim.AddObject(ObjectType.EnergyStream, 500, 125, "power_separator")
    
    # devices
    #d1 = sim.AddObject(ObjectType.Mixer, 100, 75, "mixer")
    #h1 = sim.AddObject(ObjectType.Heater, 200, 75, "heater")
    r1 = sim.AddObject(ObjectType.RCT_PFR, 300, 75, "reactor")
    h2 = sim.AddObject(ObjectType.Heater, 450, 75, "cooler")
    s1 = sim.AddObject(ObjectType.ComponentSeparator, 550, 75, "gas-liquid separator")
     
    #m1 = m1.GetAsObject()
    #m2 = m2.GetAsObject()
    #m3 = m3.GetAsObject()
    m4 = m4.GetAsObject()
    m5 = m5.GetAsObject()
    m6 = m6.GetAsObject()
    m7 = m7.GetAsObject()
    m8 = m8.GetAsObject()
    #e1 = e1.GetAsObject()
    e2 = e2.GetAsObject()
    e3 = e3.GetAsObject()
    #e4 = e4.GetAsObject()
    #d1 = d1.GetAsObject()
    #h1 = h1.GetAsObject()
    h2 = h2.GetAsObject()
    r1 = r1.GetAsObject()
    s1 = s1.GetAsObject()
    
    #sim.ConnectObjects(m1.GraphicObject, d1.GraphicObject, -1, -1) # inlet 1 - mixer
    #sim.ConnectObjects(m2.GraphicObject, d1.GraphicObject, -1, -1) # inlet 2 - mixer
    #sim.ConnectObjects(d1.GraphicObject, m3.GraphicObject, -1, -1) # mixer - mixture
    #sim.ConnectObjects(m3.GraphicObject, h1.GraphicObject, -1, -1) # mixture - heater
    #sim.ConnectObjects(h1.GraphicObject, m4.GraphicObject, -1, -1) # heater - feed
    #sim.ConnectObjects(e1.GraphicObject, h1.GraphicObject, -1, -1) # power_heater - heater
    
    r1.ConnectFeedMaterialStream(m4, 0) # feed - reactor
    r1.ConnectProductMaterialStream(m5, 0) # reactor - outlet
    r1.ConnectFeedEnergyStream(e2, 1) # power_reactor - reactor
    
    sim.ConnectObjects(m5.GraphicObject, h2.GraphicObject, -1, -1) # outlet - cooler
    sim.ConnectObjects(e3.GraphicObject, h2.GraphicObject, -1, -1) # power_cooler - cooler
    sim.ConnectObjects(h2.GraphicObject, m6.GraphicObject, -1, -1) # cooler - gas_liquid
    sim.ConnectObjects(m6.GraphicObject, s1.GraphicObject, -1, -1) # gas_liquid - gas_liquid_separator
    #sim.ConnectObjects(e4.GraphicObject, s1.GraphicObject, -1, -1) # power_separator - gas_liquid_separator
    sim.ConnectObjects(s1.GraphicObject, m7.GraphicObject, -1, -1) # gas_liquid_separator - gas
    sim.ConnectObjects(s1.GraphicObject, m8.GraphicObject, -1, -1) # gas_liquid_separator - liquid
    
    
    #sim.AutoLayout() 
    sim.CreateAndAddPropertyPackage("Raoult's Law")
    #stables = PropertyPackages.SteamTablesPropertyPackage()
    #sim.AddPropertyPackage(stables)
    """
    ## specify simulation parameters via DataSheet
    m1.SetTemperature(293.0) # room temperature (20°C, 293K)
    m2.SetTemperature(293.0) # room temperature (20°C, 293K)
    m1.SetMassFlow(100.0) # kg/s
    m2.SetMassFlow(50.0) # kg/s
    """
    
    m4.SetTemperature(data[0]["Mixture"][0]["temperature"])
    V_flow = math.pi * (data[1]["Reactor"][0]["tube_diameter"]/2) ** 2 * data[0]["Mixture"][0]["velocity"]
    m4.SetVolumetricFlow(V_flow)
    
    # preheat the mixture up to reaction temperature
    #reaction_temperature = data[0]["Mixture"][0]["temperature"]
    #h1.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature
    #h1.OutletTemperature = reaction_temperature # Kelvin
    
    # set calculation mode and specify reactor-geometry
    if data[1]["Reactor"][0]["calculation_mode"] == "isothermal":
        r1.ReactorOperationMode = Reactors.OperationMode.Isothermic
    elif data[1]["Reactor"][0]["calculation_mode"] == "adiabatic":
        r1.ReactorOperationMode = Reactors.OperationMode.Adiabatic
    else:
        print("Error accured while setting the ReactorOperationMode!")
    
    # Volume has to be set and you can choose 1 of diameter or length
    r1.Volume = data[1]["Reactor"][0]["reactive_volume"]
    r1.Length = data[1]["Reactor"][0]["tube_length"]
    #r1.Diameter = data[1]["Reactor"][0]["tube_diameter"]
    r1.NumberOfTubes = data[1]["Reactor"][0]["num_tubes"]
    
    # cooling down to room temperature (20°C, 293K)
    h2.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature
    h2.OutletTemperature = 293 # Kelvin
    
    Settings.SolverMode = 0
    
    errors = interf.CalculateFlowsheet2(sim)
    
    # print results
    #print(String.Format("Heater Heat Load: {0} kW", h1.DeltaQ))
    print(String.Format("Cooler Heat Load: {0} kW", h2.DeltaQ))
    
    
    # save file
    fileName_dwsim = name + ".dwxmz"
    fileNameToSave = Path.Combine("C:\\Users\\smmcvoel\\Desktop\\Temporäre Ablage", fileName_dwsim)
    #fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), fileName_dwsim)
    
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
    
    fileName_pic = name + ".png"
    
    bmp = SKBitmap(1024, 768)
    canvas = SKCanvas(bmp)
    canvas.Scale(1.0)
    PFDSurface.UpdateCanvas(canvas)
    d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
    str = MemoryStream()
    d.SaveTo(str)
    image = Image.FromStream(str)
    imgPath = Path.Combine("C:\\Users\\smmcvoel\\Desktop\\Temporäre Ablage", fileName_pic)
    #imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), fileName_pic)
    image.Save(imgPath, ImageFormat.Png)
    str.Dispose()
    canvas.Dispose()
    bmp.Dispose()
    
    from PIL import Image
    
    im = Image.open(imgPath)
    im.show()
    
        
def run(name):
    # load yaml-datafile
    # ACHTUNG: Übergabe des yaml-file zum Ende hin Variabel gestalten, sodass gesamter Workflow
    # mit einem einzigen Befehl ausgeführt werden kann
    # ACHTUNG: Onto-Klassen sind voerst im DataSheet auskommentiert, da sie Probleme beim Import gemacht haben
    # --> Lösung sollte allgemeingültig sein, d.h. die Klassen vorher zu definieren klappt nur wenn es automatisiert geht
    
    with open("linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
        data = yaml.safe_load(file)
   
    #CreateSubstanceJSON(data)
    ProcessSimulation(name, data)
    
    