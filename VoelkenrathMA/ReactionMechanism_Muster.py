# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 09:19:16 2023

@author: smmcvoel
"""
import yaml
import math
#import owlready2

## Import all necessary DWSIM packages
import os
import uuid
import clr

import pythoncom
import System
pythoncom.CoInitialize()

from System import String, Environment, Array
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


Directory.SetCurrentDirectory(dwsimpath)

# create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

def createReactionScript(obj_name):
    GUID = obj_name
    sim.Scripts.Add(GUID, FlowsheetSolver.Script())
    sim.Scripts.TryGetValue(GUID)[1].Linked = True
    sim.Scripts.TryGetValue(GUID)[1].LinkedEventType = Interfaces.Enums.Scripts.EventType.ObjectCalculationStarted
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectName = obj_name
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectType = Interfaces.Enums.Scripts.ObjectType.FlowsheetObject
    sim.Scripts.TryGetValue(GUID)[1].PythonInterpreter = Interfaces.Enums.Scripts.Interpreter.IronPython
    sim.Scripts.TryGetValue(GUID)[1].Title = obj_name
    sim.Scripts.TryGetValue(GUID)[1].ScriptText = str()


def createReaction(data):
    # add reaction (Evtl. muss der ganze folgende Abschnitt variabel gestaltet werden)
    # ACHTUNG: Definieren den Reaktionname z.b. als ID_1&2 und übergebe diesen an createReactionScript, sonst wird das Skript nicht verknüpft.
    comps = Dictionary[str, float]()
    dorders = Dictionary[str, float]()
    rorders = Dictionary[str, float]()
    
    sim.AddCompound("Hydrogen")
    sim.AddCompound("Nickel")
    sim.AddCompound("H-Ni")
    
    #comps.Add("Carbon monoxide", -1)
    comps.Add("Hydrogen", -1.0)
    comps.Add("Nickel", -2.0)
    comps.Add("H-Ni", 2.0)
    
    #dorders.Add("Carbon monoxide", 0)
    dorders.Add("Hydrogen", 0.0)
    dorders.Add("Nickel", 0.0)
    dorders.Add("H-Ni", 1.0)
    
    #rorders.Add("Carbon monoxide", 0)
    rorders.Add("Hydrogen", 0.0)
    rorders.Add("Nickel", 0.0)
    rorders.Add("H-Ni", 0.0)
    
    # "Methanation" --> reaction_name
    reaction_kinetic = sim.CreateKineticReaction("Methanation","Testing the DWSIM-Python functions in this Simulation", comps, dorders, rorders,
                                                 "Hydrogen", "Mixture", "Fugacities", "Pa", "mol/[m3.s]",
                                                 10E+20, 200000, 30E+25, 400000, "", "")
    sim.AddReaction(reaction_kinetic)
    sim.AddReactionToSet(reaction_kinetic.ID, "DefaultSet", True, 0)
    
    createReactionScript("Methanation")
    myreaction = sim.GetReaction("Methanation")
    myscripttitle = "Methanation"
    myscript = sim.Scripts[myscripttitle]
    
    #ACHTUNG: kinetik-Gleichung unterscheidet sich teilweise um einen Term, entweder zwei Skripte schreiben und mit if abfragen welches benötigt
    # oder ein Skript schreiben und falls nicht benötigt eine variable so definieren das Term =0 wird. (Wahrscheinlich ist Methode 2 angenehmer)
    # indention is stupid but necessary, because script isnt running in DWSIM with the "right" python indention
    myscript.ScriptText = str("""import math                              
from System import Array
from DWSIM.Thermodynamics import *

import clr
clr.AddReference('DWSIM.MathOps.DotNumerics')
from DotNumerics.ODE import *

R = 8.314

A_1 = 10E20
b_1 = -0.5
EA_1 = 20000

A_2 = 30E25
b_2 = 0.5
EA_2 = 40000

k_1 = A_1 * math.pow(T, b_1) * math.exp(-EA_1/(R*T))
k_2 = A_2 * math.pow(T, b_2) * math.exp(-EA_2/(R*T))

r = (k_1 * R1 * R2) - (k_2 * P1 * P2)""")
                              
    myreaction.ReactionKinetics = ReactionKinetics(1)
    myreaction.ScriptTitle = myscripttitle
    return reaction_kinetic    
    

def simulation(name, data):
    # get compounds from DWISM
    #carbon_monoxide = sim.AvailableCompounds["Carbon monoxide"]
    #hydrogen = sim.AvailableCompounds["Hydrogen"]
    #methane = sim.AvailableCompounds["Nickel"]
    #water = sim.AvailableCompounds["H-Ni"] 
    
    # add compounds to simulation
    #sim.SelectedCompounds.Add(carbon_monoxide.Name, carbon_monoxide)
    #sim.SelectedCompounds.Add(hydrogen.Name, hydrogen)
    #sim.SelectedCompounds.Add(methane.Name, methane)
    #sim.SelectedCompounds.Add(water.Name, water)

    # material
    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "feed")
    m2 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "outlet")
    
    # energy
    e1 = sim.AddObject(ObjectType.EnergyStream, 50, 100, "power")
    
    # device
    r1 = sim.AddObject(ObjectType.RCT_PFR, 100, 75, "reactor")
    
    # get flowsheet objects as object
    m1 = m1.GetAsObject()
    m2 = m2.GetAsObject()
    e1 = e1.GetAsObject()
    r1 = r1.GetAsObject()
    
    # connect Objects
    r1.ConnectFeedMaterialStream(m1,0)
    r1.ConnectProductMaterialStream(m2,0)
    r1.ConnectFeedEnergyStream(e1,1)
    
    # add property package
    sim.CreateAndAddPropertyPackage("NRTL")
    
    # specify parameter (material)
    composition = Array[float]((0.75, 0.25, 0.0, 0.0)) # Achtung: Zusammen mit dem Hinzufügen der Komponenten variabel gestalten
    m1.SetOverallComposition(composition)
    
    m1.SetTemperature(data[0]["Mixture"][0]["temperature"])
    V_flow = math.pi * (data[1]["Reactor"][0]["tube_diameter"]/2) ** 2 * data[0]["Mixture"][0]["velocity"]
    m1.SetVolumetricFlow(V_flow)
    
    # specify parameter (reactor); doesnt make a difference if diameter or length is choosen
    r1.Volume = data[1]["Reactor"][0]["reactive_volume"]
    r1.Length = data[1]["Reactor"][0]["tube_length"]
    #r1.Diameter = data[1]["Reactor"][0]["tube_diameter"]
    r1.NumberOfTubes = data[1]["Reactor"][0]["num_tubes"]
    
    if data[1]["Reactor"][0]["calculation_mode"] == "isothermal":
        r1.ReactorOperationMode = Reactors.OperationMode.Isothermic
    elif data[1]["Reactor"][0]["calculation_mode"] == "adiabatic":
        r1.ReactorOperationMode = Reactors.OperationMode.Adiabatic
    else:
        print("Error accured while setting the ReactorOperationMode!")
    
    reaction_system = createReaction(data)

    # set Solver Mode
    Settings.SolveMode = 0
    
    errors = interf.CalculateFlowsheet2(sim)
    
    # save file as dwxmz
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
    stri = MemoryStream()
    d.SaveTo(stri)
    image = Image.FromStream(stri)
    imgPath = Path.Combine("C:\\Users\\smmcvoel\\Desktop\\Temporäre Ablage", fileName_pic)
    #imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), fileName_pic)
    image.Save(imgPath, ImageFormat.Png)
    stri.Dispose()
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
    
    with open("C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
        data = yaml.safe_load(file)
        
    simulation(name, data)

   