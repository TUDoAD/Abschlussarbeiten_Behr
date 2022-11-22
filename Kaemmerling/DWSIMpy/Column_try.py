# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 12:43:40 2022

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

# add benzene, toluene

benzene = sim.AvailableCompounds["Benzene"]
toluene = sim.AvailableCompounds["Toluene"]

sim.SelectedCompounds.Add(benzene.Name, benzene)
sim.SelectedCompounds.Add(toluene.Name, toluene)

# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 150, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 350, 100, "outlet1")
m3 = sim.AddObject(ObjectType.MaterialStream, 350, 200, "outlet2")
e1 = sim.AddObject(ObjectType.EnergyStream, 250, 300, "heater duty")
e2 = sim.AddObject(ObjectType.EnergyStream, 350, 50, "cooler duty")
column1 = sim.AddObject(ObjectType.ShortcutColumn, 100, 50, "column")

sim.ConnectObjects(m1.GraphicObject, column1.GraphicObject, -1, -1)
sim.ConnectObjects(column1.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(e1.GraphicObject, column1.GraphicObject, -1, -1)
sim.ConnectObjects(column1.GraphicObject, e2.GraphicObject, -1, -1)
sim.ConnectObjects(column1.GraphicObject, m3.GraphicObject, -1, -1)



# raoults law

stables = PropertyPackages.RaoultPropertyPackage()

sim.AddPropertyPackage(stables)

# set inlet stream temperature
# set inlet mass flow
# default properties: P = 101325 Pa, Mole fraction: Benzene 0.5; Toluene 0.5

m1.SetTemperature(368.0) # K
m1.SetMassFlow(2.4) # kg/s


# set column


column1.m_lightkey = "Benzene"
column1.m_heavykey = "Toluene"
column1.m_heavykeymolarfrac = 0.01
column1.m_lightkeymolarfrac = 0.01
column1.m_refluxratio = 1.4


# request a calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)

print(String.Format("Heater duty: {0} kW", column1.m_Qb))
print(String.Format( "Cooler duty: {0} kW", column1.m_Qc))

# save file

fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "heatersample.dwxmz")

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
