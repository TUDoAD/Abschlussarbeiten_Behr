# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 15:26:48 2022

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

dwsimpath = "C:\\Users\\Lucky Luciano\\AppData\\Local\\DWSIM\\"

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
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings



# create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

# add compounds

hydrogen = sim.AvailableCompounds["Hydrogen"]

water = sim.AvailableCompounds["Water"]

nitrogen = sim.AvailableCompounds["Nitrogen"]



sim.SelectedCompounds.Add(hydrogen.Name, hydrogen)

sim.SelectedCompounds.Add(water.Name, water)

sim.SelectedCompounds.Add(nitrogen.Name, nitrogen)



# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 100, 50, "outlet1")
m3 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet2")
SEP1 = sim.AddObject(ObjectType.Vessel, 100, 50, "Separator")


sim.ConnectObjects(m1.GraphicObject, SEP1.GraphicObject, -1, -1)
sim.ConnectObjects(SEP1.GraphicObject, m3.GraphicObject, -1, -1)
sim.ConnectObjects(SEP1.GraphicObject, m2.GraphicObject, -1, -1)


sim.AutoLayout()

# Peng Robinson Property Package

stables = PropertyPackages.PengRobinsonPropertyPackage()

sim.AddPropertyPackage(stables)

#SEP1.SetPropertyValue("Outlet Stream 2", "Ammonia", 99)

# request calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)



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
