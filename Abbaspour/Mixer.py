# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 09:30:46 2023

@author: 49157
"""

import os

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
clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "System.Buffers.dll")

clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

# Create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

# Add compounds
methanol = sim.AvailableCompounds["Methanol"]
water = sim.AvailableCompounds["Water"]

sim.SelectedCompounds.Add(methanol.Name, methanol)
sim.SelectedCompounds.Add(water.Name, water)

# Create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 10, 10, "inlet1")
m2 = sim.AddObject(ObjectType.MaterialStream, 10, 60, "inlet2")
m3 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
MIX1 = sim.AddObject(ObjectType.Mixer, 100, 50, "Mixer")

m1 = m1.GetAsObject()
m2 = m2.GetAsObject()
m3 = m3.GetAsObject()
MIX1 = MIX1.GetAsObject()

# m1.Phases[0].Properties.molarfraction = 1

sim.ConnectObjects(m1.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(MIX1.GraphicObject, m3.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, MIX1.GraphicObject, -1, -1)


# Peng Robinson Property Package
stables = PropertyPackages.PengRobinsonPropertyPackage()
sim.AddPropertyPackage(stables)

# Set Temperature
m1.SetTemperature(298.15) # Kelvin
m2.SetTemperature(298.15) # Kelvin

# Request calculation
Settings.SolverMode = 0
errors = interf.CalculateFlowsheet2(sim)

# Save file
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "Mixer.dwxmz")
interf.SaveFlowsheet(sim, fileNameToSave, True)

# Save the seperator to an image and display it
clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

PFDSurface = sim.GetSurface()

bmp = SKBitmap(600, 300)
canvas = SKCanvas(bmp)
canvas.Scale(3.0)
PFDSurface.UpdateCanvas(canvas)
d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
str = MemoryStream()
d.SaveTo(str)
image = Image.FromStream(str)
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "mixing.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image

im = Image.open(imgPath)
im.show()