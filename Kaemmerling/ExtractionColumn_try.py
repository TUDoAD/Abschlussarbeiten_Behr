# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 09:58:34 2022

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
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings



# create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

# add compounds

MTBE = sim.AvailableCompounds["Methyl tert-butyl ether"]

water = sim.AvailableCompounds["Water"]

aceticacid = sim.AvailableCompounds["Acetic acid"]



sim.SelectedCompounds.Add(MTBE.Name, MTBE)

sim.SelectedCompounds.Add(water.Name, water)

sim.SelectedCompounds.Add(aceticacid.Name, aceticacid)



# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "Feed")
m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "Retentat")
m3 = sim.AddObject(ObjectType.MaterialStream, 100, 50, "Raffinat")
m4 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "Solvent")
Extraction_Column = sim.AddObject(ObjectType.AbsorptionColumn, 100, 50, "Extraction_Column")


sim.ConnectObjects(m1.GraphicObject, Extraction_Column.GraphicObject, -1, -1)
sim.ConnectObjects(Extraction_Column.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(Extraction_Column.GraphicObject, m3.GraphicObject, -1, -1)
sim.ConnectObjects(m4.GraphicObject, Extraction_Column.GraphicObject, -1, -1)

sim.AutoLayout()

# Peng Robinson Property Package

stables = PropertyPackages.UNIQUACPropertyPackage()

sim.AddPropertyPackage(stables)

# set inlet stream conditions
#Overall Mass flow = 1 kg/s

m1.SetTemperature(298.15) # K
m1.SetOverallCompoundMassFlow("Methyl tert-butyl ether", 0.0) #kg/s
m1.SetOverallCompoundMassFlow("Water", 0.5) #kg/s
m1.SetOverallCompoundMassFlow("Acetic acid", 0.5) #kg/s
m4.SetOverallCompoundMassFlow("Methyl tert-butyl ether", 1.0) #kg/s
m4.SetOverallCompoundMassFlow("Water", 0.0) #kg/s
m4.SetOverallCompoundMassFlow("Acetic acid", 0.0) #kg/s


Extraction_Column.OpMode = 1



#PFR1.set_ComponentDescription("", "BaseCompound")


# request calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)

#print(String.Format("Mole frac: {0} ", m3.GetOverallComposition))
#print(String.Format("Mole frac: {0} ", m4.GetOverallComposition))

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
