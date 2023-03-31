# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 21:27:49 2023

@author: 49157
"""

import os
import uuid
import clr 
import pythoncom
import System
pythoncom.CoInitialize()

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
clr.AddReference(dwsimpath + "DWSIM.FlowsheetSolver.dll")
clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
clr.AddReference(dwsimpath + "Newtonsoft.Json")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

from DWSIM import FlowsheetSolver
from DWSIM import Interfaces
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

def createScript(obj_name):
    #GUID = str(uuid.uuid1())
    GUID = obj_name
    sim.Scripts.Add(GUID, FlowsheetSolver.Script())
    #By not declaring the ID the tabs of each script is not loaded
    #sim.Scripts.TryGetValue(GUID)[1].ID = GUID
    sim.Scripts.TryGetValue(GUID)[1].Linked = True
    sim.Scripts.TryGetValue(GUID)[1].LinkedEventType = Interfaces.Enums.Scripts.EventType.ObjectCalculationStarted
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectName = obj_name
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectType = Interfaces.Enums.Scripts.ObjectType.FlowsheetObject
    sim.Scripts.TryGetValue(GUID)[1].PythonInterpreter = Interfaces.Enums.Scripts.Interpreter.IronPython
    sim.Scripts.TryGetValue(GUID)[1].Title = obj_name
    sim.Scripts.TryGetValue(GUID)[1].ScriptText = str('Michealis Menten Kinetic\nkr1 = sim.CreateKineticReaction("ABTS Oxidation", "ABTS Oxidation using Laccase",comps, dorders, rorders, "ABTS_ox", "Mixture", "Molar Concentration","kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")\nsim.AddReaction(kr1)\nsim.AddReactionToSet(kr1.ID, "DefaultSet", True, 0)')
                                                      
createScript('ABTS kinetics')

# Add compounds
sim.AddCompound("Laccase")
sim.AddCompound("ABTS Oxidized")
sim.AddCompound("ABTS Reduced")
sim.AddCompound("Water")
sim.AddCompound("Oxygen")


# Stoichiometric coefficients
comps = Dictionary[str, float]()
#comps.Add("Laccase", -1.0);
comps.Add("Water", 2.0);
comps.Add("Oxygen", -1.0);
comps.Add("ABTS Oxidized", 4.0);
comps.Add("ABTS Reduced", -4.0);


# Direct order coefficients
dorders = Dictionary[str, float]()
#dorders.Add("Laccase", 0.0);
dorders.Add("Water", 0.0);
dorders.Add("Oxygen", 0.0);
dorders.Add("ABTS Oxidized", 1.0);
dorders.Add("ABTS Reduced", 0.0);


# Reverse order coefficients
rorders = Dictionary[str, float]()
#rorders.Add("Laccase", 0.0);
rorders.Add("Water", 0.0);
rorders.Add("Oxygen", 0.0);
rorders.Add("ABTS Oxidized", 0.0);
rorders.Add("ABTS Reduced", 0.0);


# Add all objects
m1 = sim.AddObject(ObjectType.MaterialStream, 0, 10, "Oxygen")
m2 = sim.AddObject(ObjectType.MaterialStream, 0, 60, "ABTS Reduced")
m3 = sim.AddObject(ObjectType.MaterialStream, 100, 50, "Mixture")
m4 = sim.AddObject(ObjectType.MaterialStream, 250, 50, "Product")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 90, "Heat")
pfr = sim.AddObject(ObjectType.RCT_PFR, 150, 50, "PFR")
MIX1 = sim.AddObject(ObjectType.Mixer, 50, 50, "Mixer")
 
m1 = m1.GetAsObject()
m2 = m2.GetAsObject()
m3 = m3.GetAsObject()
m4 = m4.GetAsObject()
e1 = e1.GetAsObject()
MIX1 = MIX1.GetAsObject()
pfr = pfr.GetAsObject()


# Connect the inlet streams
sim.ConnectObjects(m1.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(MIX1.GraphicObject, m3.GraphicObject, -1, -1)

pfr.ConnectFeedMaterialStream(m3, 0)
pfr.ConnectProductMaterialStream(m4, 0)
pfr.ConnectFeedEnergyStream(e1, 1)


# PFR properties (fix pressure drop inside reactor)
pfr.ReactorOperationMode = Reactors.OperationMode.Isothermic
pfr.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length
pfr.Volume = 1.0; # m3
pfr.Length = 1.0; # m

# Set Property Package
sim.CreateAndAddPropertyPackage("Raoult's Law")

# Set stream temperature
m1.SetTemperature(311.15) # Kelvin
m2.SetTemperature(311.15) # Kelvin
m3.SetTemperature(311.15) # Kelvin
m4.SetTemperature(311.15) # Kelvin

# Set molar flow
m1.SetMolarFlow(0.0) # will set by compound

m1.SetOverallCompoundMolarFlow("Oxygen", 1.0) # mol/s
# Amount of Enzyme neglectable
# m1.SetOverallCompoundMolarFlow("Laccase", 0.0)  # mol/s
m1.SetOverallCompoundMolarFlow("ABTS Reduced", 0.0)  # mol/s

m2.SetOverallCompoundMolarFlow("Oxygen", 0.0) # mol/s
# m2.SetOverallCompoundMolarFlow("Laccase", 1.0)  # mol/s
m2.SetOverallCompoundMolarFlow("ABTS Reduced", 1.0)  # mol/s

#sim.AddReaction(kr1)
#sim.AddReactionToSet(kr1.ID, "DefaultSet", True, 0)


# request a calculation
errors = interf.CalculateFlowsheet4(sim);


# save file
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), 
                              "02_ABTS Oxidation.dwxmz")
interf.SaveFlowsheet(sim, fileNameToSave, True)


# save the pfd to an image and display it
clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

PFDSurface = sim.GetSurface()
bmp = SKBitmap(1000, 600)
canvas = SKCanvas(bmp)
canvas.Scale(0.5)
PFDSurface.ZoomAll(bmp.Width, bmp.Height)
PFDSurface.UpdateCanvas(canvas)
d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
str = MemoryStream()
d.SaveTo(str)
image = Image.FromStream(str)
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "02_ABTS Oxidation.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image
im = Image.open(imgPath)
im.show()