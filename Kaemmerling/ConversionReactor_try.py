# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 14:00:17 2022

@author: Lucky Luciano
"""

"""
Created on Wed Jun  1 22:02:43 2022

@author: Lucky Luciano
"""

# delete dwsim_newui

import os

fileTest = r"C:\Users\Lucky Luciano\Documents\DWSIM Application Data\dwsim_newui.ini"

try:
    os.remove(fileTest)
except OSError as e:
    print(e)
else:
    print("File is deleted successfully")

import pythoncom
pythoncom.CoInitialize()

import clr

from System.IO import Directory, Path, File
from System import String, Environment

dwsimpath = "C:\\Users\\Lucky Luciano\\AppData\\Local\\DWSIM 8\\"

clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")

clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations
from DWSIM.UnitOperations import Reactors
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings
import DWSIM.Interfaces

# create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

# add compounds

hydrogen = sim.AvailableCompounds["Hydrogen"]

carbonmonoxide = sim.AvailableCompounds["Carbon monoxide"]

methanol = sim.AvailableCompounds["Methanol"]

# add reaction

comps1 = {"Hydrogen": -1, "Carbon monoxide": -1,  "Methanol": 1}


kr1 = sim.CreateConversionReaction("Methanol Production", "Production of Methanol from Hydrogen and WaterCarbon Monoxide",comps1, "", "", "")
   
   
sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)

sim.SelectedCompounds.Add(hydrogen.Name, hydrogen)

sim.SelectedCompounds.Add(methanol.Name, methanol)

sim.SelectedCompounds.Add(carbonmonoxide.Name, carbonmonoxide)

# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
Conversion = sim.AddObject(ObjectType.RCT_Conversion, 100, 50, "Conversion")

sim.ConnectObjects(m1.GraphicObject, Conversion.GraphicObject, -1, -1)
sim.ConnectObjects(Conversion.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(e1.GraphicObject, Conversion.GraphicObject, -1, -1)

sim.AutoLayout()

# Peng Robinson Property Package

stables = PropertyPackages.RaoultPropertyPackage()

sim.AddPropertyPackage(stables)

# set inlet stream conditions


m1.SetTemperature(593.15) # K
m1.SetOverallCompoundMassFlow("Hydrogen", 1200) 
m1.SetOverallCompoundMassFlow("Methanol", 0) 
m1.SetOverallCompoundMassFlow("Carbon monoxide", 300) 

m1.SetPressure("7000000 Pa") # Pa



# isothermic

Conversion.ReactorOperationMode = 0



# request calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)

Energy = e1.EnergyFlow
 
print('Energy (kW): ' + str(Energy))

# save file

fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "reactorsample.dwxmz")

interf.SaveFlowsheet(sim, fileNameToSave, True)

# save the pfd to an image and display it

clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

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
