# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 10:10:14 2022

@author: 49157
"""
import pythoncom
pythoncom.CoInitialize()
import clr
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
clr.AddReference(dwsimpath + "System.Buffers.dll")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

Directory.SetCurrentDirectory(dwsimpath)

interf = Automation3()
sim = interf.CreateFlowsheet()

# add compounds

sim.AddCompound("Water")
sim.AddCompound("Ethylene glycol")
sim.AddCompound("Ethylene oxide")

# add kinetic reaction

# stoichiometric coefficients
comps = Dictionary[str, float]()
comps.Add("Ethylene oxide", -1.0);
comps.Add("Water", -1.0);
comps.Add("Ethylene glycol", 1.0);

# direct order coefficients
dorders = Dictionary[str, float]()
dorders.Add("Ethylene oxide", 1.0);
dorders.Add("Water", 0.0);
dorders.Add("Ethylene glycol", 0.0);

# reverse order coefficients
rorders = Dictionary[str, float]()
rorders.Add("Ethylene oxide", 0.0);
rorders.Add("Water", 0.0);
rorders.Add("Ethylene glycol", 0.0);

# create kinetic reaction object
# https://dwsim.org/api_help/html/M_DWSIM_FlowsheetBase_FlowsheetBase_CreateKineticReaction.htm
# https://github.com/DanWBR/dwsim/blob/1103a3144734b7e1f20071aae98503a5e62daf35/DWSIM.FlowsheetBase/FlowsheetBase.vb#L3646
kr1 = sim.CreateKineticReaction("Ethylene Glycol Production", "Production of Ethylene Glycol from Ethylene Oxide and Water", 
        comps, dorders, rorders, "Ethylene oxide", "Mixture", "Molar Concentration", "kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")

sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", True, 0)

# add objects
# https://dwsim.org/api_help/html/M_DWSIM_FlowsheetBase_FlowsheetBase_AddObject.htm
m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "outlet")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "heat")
pfr = sim.AddObject(ObjectType.RCT_PFR, 100, 50, "reactor")
 
m1 = m1.GetAsObject()
m2 = m2.GetAsObject()
e1 = e1.GetAsObject()
pfr = pfr.GetAsObject()

# connect streams to PFR

# https://dwsim.org/api_help/html/M_DWSIM_Interfaces_ISimulationObject_ConnectFeedMaterialStream.htm
pfr.ConnectFeedMaterialStream(m1, 0)

# https://dwsim.org/api_help/html/M_DWSIM_Interfaces_ISimulationObject_ConnectProductMaterialStream.htm
pfr.ConnectProductMaterialStream(m2, 0)

# https://dwsim.org/api_help/html/M_DWSIM_Interfaces_ISimulationObject_ConnectFeedEnergyStream.htm
pfr.ConnectFeedEnergyStream(e1, 1)

# PFR properties
# https://dwsim.org/api_help/html/T_DWSIM_UnitOperations_Reactors_Reactor_PFR.htm
pfr.ReactorOperationMode = Reactors.OperationMode.Isothermic
pfr.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length
pfr.Volume = 1.0; # m3
pfr.Length = 1.2; # m

sim.AutoLayout()

# property package

# https://github.com/DanWBR/dwsim/blob/1103a3144734b7e1f20071aae98503a5e62daf35/DWSIM.FlowsheetBase/FlowsheetBase.vb#L3801
# https://github.com/DanWBR/dwsim/blob/1103a3144734b7e1f20071aae98503a5e62daf35/DWSIM.FlowsheetBase/FlowsheetBase.vb#L3787
sim.CreateAndAddPropertyPackage("Raoult's Law")

m1.SetTemperature(328.2) # K

m1.SetMolarFlow(0.0) # will set by compound

m1.SetOverallCompoundMolarFlow("Ethylene oxide", 2.39) # mol/s
m1.SetOverallCompoundMolarFlow("Water", 9.57)  # mol/s

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
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "pfr_reactor.dwxmz")
interf.SaveFlowsheet(sim, fileNameToSave, True)

# save the pfd to an image and display it
clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

PFDSurface = sim.GetSurface()
bmp = SKBitmap(800, 600)
canvas = SKCanvas(bmp)
canvas.Scale(1.0)
PFDSurface.ZoomAll(bmp.Width, bmp.Height)
PFDSurface.UpdateCanvas(canvas)
d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
str = MemoryStream()
d.SaveTo(str)
image = Image.FromStream(str)
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "PFD_reactor.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image
im = Image.open(imgPath)
im.show()