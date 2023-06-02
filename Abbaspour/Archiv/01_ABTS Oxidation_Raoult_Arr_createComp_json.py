# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 14:54:15 2023

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
 
names = ["Laccase01", "ABTS_ox", "ABTS_red"]
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

# Add compounds 
sim.AddCompound("Laccase01")
sim.AddCompound("ABTS_ox")
sim.AddCompound("ABTS_red")
sim.AddCompound("Water")
sim.AddCompound("Oxygen")

# Stoichiometric coefficients
comps = Dictionary[str, float]()
comps.Add("Laccase01", -1.0);
comps.Add("Water", 2.0);
comps.Add("Oxygen", -1.0);
comps.Add("ABTS_ox", 4.0);
comps.Add("ABTS_red", -4.0);

# Direct order coefficients
dorders = Dictionary[str, float]()
dorders.Add("Laccase01", 0.0);
dorders.Add("Water", 0.0);
dorders.Add("Oxygen", 0.0);
dorders.Add("ABTS_ox", 1.0);
dorders.Add("ABTS_red", 0.0);

# Reverse order coefficients
rorders = Dictionary[str, float]()
rorders.Add("Laccase01", 0.0);
rorders.Add("Water", 0.0);
rorders.Add("Oxygen", 0.0);
rorders.Add("ABTS_ox", 0.0);
rorders.Add("ABTS_red", 0.0);

kr1 = sim.CreateKineticReaction("ABTS Oxidation", "ABTS Oxidation using Laccase", 
        comps, dorders, rorders, "ABTS_ox", "Mixture", "Molar Concentration", 
        "kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")

# Add all objects
m1 = sim.AddObject(ObjectType.MaterialStream, 0, 10, "Oxygen")
m2 = sim.AddObject(ObjectType.MaterialStream, 0, 60, "ABTS_red")
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

m1.SetTemperature(311.15) # Kelvin
m2.SetTemperature(311.15) # Kelvin
m3.SetTemperature(311.15) # Kelvin
m4.SetTemperature(311.15) # Kelvin

m1.SetMolarFlow(0.0) # will set by compound

m1.SetOverallCompoundMolarFlow("Oxygen", 1.0) # mol/s
m1.SetOverallCompoundMolarFlow("ABTS_red", 0.0)  # mol/

m2.SetOverallCompoundMolarFlow("Oxygen", 0.0) # mol/s
m2.SetOverallCompoundMolarFlow("ABTS_red", 1.0)  # mol/s

sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", True, 0)

# request a calculation

errors = interf.CalculateFlowsheet4(sim);

print("Reactor Heat Load: {0:.4g} kW".format(pfr.DeltaQ))
for c in pfr.ComponentConversions:
    if (c.Value > 0): print("{0} conversion: {1:.4g}%".format(c.Key, c.Value * 100.0))

if (len(errors) > 0):
    for e in errors:
        print("Error: " + e.ToString())

# reactor profiles (temperature, pressure and concentration)
coordinates = [] # volume coordinate in m3
names = [] # compound names
values = [] # concentrations in mol/m3 (0 to j, j = number of compounds - 1), temperature in K (j+1), pressure in Pa (j+2)

for p in pfr.points:
    coordinates.append(p[0])

for j in range(1, pfr.ComponentConversions.Count + 3):
    list1 = []
    for p in pfr.points:
        list1.append(p[j])
    values.append(list1)

for k in pfr.ComponentConversions.Keys:
    names.append(k)


# save file
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), 
                              "01_ABTS Oxidation.dwxmz")
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
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "01_ABTS Oxidation.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image
im = Image.open(imgPath)
im.show()
