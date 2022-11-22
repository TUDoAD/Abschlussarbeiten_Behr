# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 11:49:28 2022

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
from System.Collections.Generic import Dictionary

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
from DWSIM.UnitOperations import Reactors
from DWSIM.GlobalSettings import Settings
import DWSIM.Interfaces



# create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

# add compounds

hydrogen = sim.AvailableCompounds["Hydrogen"]

ammonia = sim.AvailableCompounds["Ammonia"]

nitrogen = sim.AvailableCompounds["Nitrogen"]

sim.AddCompound("Hydrogen")
sim.AddCompound("Ammonia")
sim.AddCompound("Nitrogen")


# stoichiometric coefficients
comps = Dictionary[str, float]()
comps.Add("Hydrogen", -3.0);
comps.Add("Ammonia", 2.0);
comps.Add("Nitrogen", -1.0);


# direct order coefficients
dorders = Dictionary[str, float]()
dorders.Add("Hydrogen", 1.0);
dorders.Add("Ammonia", 0.0);
dorders.Add("Nitrogen", 1.0);


# reverse order coefficients
rorders = Dictionary[str, float]()
rorders.Add("Hydrogen", 0.0);
rorders.Add("Ammonia", 0.0);
rorders.Add("Nitrogen", 0.0);


kr1 = sim.CreateKineticReaction("Ammonia Production", "Haber-Bosch synthesis", 
            comps, dorders, rorders, "Hydrogen", "Vapor","Molar Concentration", "kmol/m3", "kmol/[m3.h]", 0.004, 0.0, 0.0, 0.0, "", "")
   
sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)



# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 0, 50, "compressor_inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "compressor_outlet")
m3 = sim.AddObject(ObjectType.MaterialStream, 350, 50, "reactor_outlet")
m4 = sim.AddObject(ObjectType.MaterialStream, 550, 50, "cooler_outlet")
m5 = sim.AddObject(ObjectType.MaterialStream, 750, 50, "valve_outlet")
m6 = sim.AddObject(ObjectType.MaterialStream, 850, 50, "separator_vapor_outlet")
m7 = sim.AddObject(ObjectType.MaterialStream, 850, 200, "separator_liquid_outlet")
m8 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "tank_outlet")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 100, "power1")
e2 = sim.AddObject(ObjectType.EnergyStream, 250, 100, "power2")
e3 = sim.AddObject(ObjectType.EnergyStream, 450, 300, "power3")
PFR1 = sim.AddObject(ObjectType.RCT_PFR, 250, 50, "PFR")
COO1 = sim.AddObject(ObjectType.Cooler, 450, 200, "Cooler")
C1 = sim.AddObject(ObjectType.Compressor, 100, 50, "Compressor")
SEP1 = sim.AddObject(ObjectType.Vessel, 800, 50, "Separator")
t1 = sim.AddObject(ObjectType.Tank, 950, 200, "Tank")
V1 = sim.AddObject(ObjectType.Valve, 650, 50, "Valve")


sim.ConnectObjects(m1.GraphicObject, C1.GraphicObject, -1, -1)
sim.ConnectObjects(C1.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, PFR1.GraphicObject, -1, -1)
sim.ConnectObjects(PFR1.GraphicObject, m3.GraphicObject, -1, -1)
sim.ConnectObjects(m3.GraphicObject, COO1.GraphicObject, -1, -1)
sim.ConnectObjects(COO1.GraphicObject, m4.GraphicObject, -1, -1)
sim.ConnectObjects(m4.GraphicObject, V1.GraphicObject, -1, -1)
sim.ConnectObjects(V1.GraphicObject, m5.GraphicObject, -1, -1)
sim.ConnectObjects(m5.GraphicObject, SEP1.GraphicObject, -1, -1)
sim.ConnectObjects(SEP1.GraphicObject, m6.GraphicObject, -1, -1)
sim.ConnectObjects(SEP1.GraphicObject, m7.GraphicObject, -1, -1)
sim.ConnectObjects(m7.GraphicObject, t1.GraphicObject, -1, -1)
sim.ConnectObjects(t1.GraphicObject, m8.GraphicObject, -1, -1)
sim.ConnectObjects(e1.GraphicObject, C1.GraphicObject, -1, -1)
sim.ConnectObjects(e2.GraphicObject, PFR1.GraphicObject, -1, -1)
sim.ConnectObjects(COO1.GraphicObject, e3.GraphicObject, -1, -1)


#sim.AutoLayout()

# Peng Robinson Property Package

stables = PropertyPackages.PengRobinsonPropertyPackage()

sim.AddPropertyPackage(stables)

# set inlet stream conditions
#Overall Molar flow = 1 kg/s

m1.SetTemperature(298.15) # K
m1.SetOverallCompoundMolarFlow("Hydrogen", 0.5) #kg/s
m1.SetOverallCompoundMolarFlow("Nitrogen", 0.5) #kg/s
m1.SetOverallCompoundMolarFlow("Ammonia", 0.0) #kg/s
m1.SetPressure("100000 Pa") # Pa

PFR1.Length = 1.5 #m
PFR1.Volume = 1.0 #m^3

COO1.CalcMode = UnitOperations.Cooler.CalculationMode.OutletTemperature
COO1.OutletTemperature = 300 # K

C1.CalcMode = UnitOperations.Compressor.CalculationMode.OutletPressure
C1.set_POut(2000000.0) #Pa

V1.CalcMode = UnitOperations.Valve.CalculationMode.OutletPressure
V1.set_OutletPressure(10000) #Pa

t1.CalcMode = UnitOperations.Tank.set_Volume
t1.set_Volume(100) #m^3

#isothermic

PFR1.ReactorOperationMode = 0


#insert Reaction




# request calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)

Energy1 = e1.EnergyFlow
Energy2 = e2.EnergyFlow
Energy3 = e3.EnergyFlow
 

print('Energy (kW): ' + str(Energy1))
print('Energy (kW): ' + str(Energy2))
print('Energy (kW): ' + str(Energy3))

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
