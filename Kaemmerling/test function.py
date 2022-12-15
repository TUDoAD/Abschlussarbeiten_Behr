# -*- coding: utf-8 -*-
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

# add water

water = sim.AvailableCompounds["Water"]

sim.SelectedCompounds.Add(water.Name, water)

# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
p1 = sim.AddObject(ObjectType.Pump, 100, 50, "pump")
sim.ConnectObjects(m1.GraphicObject, p1.GraphicObject, -1, -1)
sim.ConnectObjects(p1.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(e1.GraphicObject, p1.GraphicObject, -1, -1)
p1.CalcMode = UnitOperations.Pump.CalculationMode.OutletPressure
p1.set_Pout(500000)

m3 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet2")
t1 = sim.AddObject(ObjectType.Tank, 100, 50, "tank")
sim.ConnectObjects(m2.GraphicObject, t1.GraphicObject, -1, -1)
sim.ConnectObjects(t1.GraphicObject, m3.GraphicObject, -1, -1)


sim.AutoLayout()

# steam tables property package

stables = PropertyPackages.SteamTablesPropertyPackage()

sim.AddPropertyPackage(stables)

# set inlet stream temperature
# default properties: T = 298.15 K, P = 101325 Pa, Mass Flow = 1 kg/s

m1.SetTemperature(293.15) # K
m1.SetMassFlow(1.0) # kg/s



# request a calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)


Energy = e1.EnergyFlow
 

print('Energy (kW): ' + str(Energy))

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


