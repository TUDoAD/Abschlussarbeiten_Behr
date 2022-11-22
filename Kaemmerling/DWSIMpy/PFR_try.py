# -*- coding: utf-8 -*-
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
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\Lucky Luciano\\AppData\\Local\\DWSIM 8\\"

clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")
clr.AddReference(dwsimpath + "System.Buffers.dll")

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

water = sim.AvailableCompounds["Water"]

glykol = sim.AvailableCompounds["Ethylene glycol"]

oxide = sim.AvailableCompounds["Ethylene oxide"]

# add reaction

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
rorders = Dictionary[str, float]({"Ethylene oxide": 0.0, "Water": 0.0, "Ethylene glycol": 0.0})
rorders.Add("Ethylene oxide", 0.0);
rorders.Add("Water", 0.0);
rorders.Add("Ethylene glycol", 0.0);

sim.AddCompound("Water")
sim.AddCompound("Ethylene glycol")
sim.AddCompound("Ethylene oxide")

#class AttrDict(dict):
   # def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        #self.__dict__ = self

#comps1 = AttrDict()
#comps1.a = 1
#comps1.b = 2

#class AttrDict(dict):
   # def __init__(self, *args, **kwargs):
       # super().__init__(*args, **kwargs)
       # self.__dict__ = self

#rorders = AttrDict()
#rorders.a = 1
#rorders.b = 2

#class AttrDict(dict):
    #def __init__(self, *args, **kwargs):
       # super().__init__(*args, **kwargs)
       # self.__dict__ = self

#dorders = AttrDict()
#dorders.a = 1
#dorders.b = 2



#comps1 = [{ "Ethylene oxide", -1 }, {"Water", -1 }, { "Ethylene glycol", 1}]
#dorders =  [{ "Ethylene oxide",  1}, {"Water", 0 }, { "Ethylene glycol", 0}]
#rorders = [{ "Ethylene oxide",  0}, {"Water", 0 }, { "Ethylene glycol", 0}]

#comps1 = {{ "Ethylene oxide", -1 }, {"Water", -1 }, { "Ethylene glycol", 1}}
#dorders =  {{ "Ethylene oxide",  1}, {"Water", 0 }, { "Ethylene glycol", 0}}
#rorders = {{ "Ethylene oxide",  0}, {"Water", 0 }, { "Ethylene glycol", 0}}


#comps1 = ({ "Ethylene oxide", -1 }, {"Water", -1 }, { "Ethylene glycol", 1})
#dorders =  ({ "Ethylene oxide",  1}, {"Water", 0 }, { "Ethylene glycol", 0})
#rorders = ({ "Ethylene oxide",  0}, {"Water", 0 }, { "Ethylene glycol", 0})

#comps1 = {[ "Ethylene oxide", -1 ], ["Water", -1 ], [ "Ethylene glycol", 1]}
#dorders =  ({ "Ethylene oxide",  1}, {"Water", 0 }, { "Ethylene glycol", 0})
#rorders = ({ "Ethylene oxide",  0}, {"Water", 0 }, { "Ethylene glycol", 0})

#comps1 = Dictionary[String, Object]()
#comps1['Entry 1'] = 'Water'
#comps1['Entry 2'] = -1
#comps1['Entry 3'] = 'Ethylene oxide'
#comps1['Entry 4'] = -1
#comps1['Entry 5'] = 'Ethlene glycol'
#comps1['Entry 6'] = 1

#dorders = Dictionary[String, Object]()
#dorders['Entry 1'] = 'Water'
#dorders['Entry 2'] = 0
#dorders['Entry 3'] = 'Ethylene oxid'
#dorders['Entry 4'] = 1
#dorders['Entry 5'] = 'Ethylene glycol'
#dorders['Entry 6'] = 0

#rorders = Dictionary[String, Object]()
#rorders['Entry1'] = 'Water'
#rorders['Entry2'] = 0
#rorders['Entry3'] = 'Ethylene oxid'
#rorders['Entry4'] = 0
#rorders['Entry5'] = 'Ethylene glycol'
#rorders['Entry6'] = 0

#comps1 = {"Water": -1, "Ethylene oxide": -1,  "Ethylene glycol": 1}

#dorders = {"Water": 0, "Ethylene oxide": 1,  "Ethylene glycol": 0}

#rorders = {"Water": 0, "Ethylene oxide": 0,  "Ethylene glycol": 0}

   

#kr1 = sim.CreateKineticReaction("Ethylene Glycol Production", "Production of Ethylene Glycol from Ethylene Oxide and Water",
           # comps, dorders, rorders, "Ethylene oxide", "Mixture","Molar Concentration", "kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")
kr1 = sim.CreateKineticReaction("Ethylene Glycol Production", "Production of Ethylene Glycol from Ethylene Oxide and Water", 
            comps, dorders, rorders, "Ethylene oxide", "Mixture","Molar Concentration", "kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")
   
sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)




# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
PFR1 = sim.AddObject(ObjectType.RCT_PFR, 100, 50, "PFR")

sim.ConnectObjects(m1.GraphicObject, PFR1.GraphicObject, -1, -1)
sim.ConnectObjects(PFR1.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(e1.GraphicObject, PFR1.GraphicObject, -1, -1)

sim.AutoLayout()



# set inlet stream conditions

sim.CreateAndAddPropertyPackage("Raoult's Law")
m1.SetTemperature(328.2) # K
m1.SetOverallCompoundMolarFlow("Water", 9.57) 
m1.SetOverallCompoundMolarFlow("Ethylene oxide", 2.39) 
 

#m1.SetPressure("20000000 Pa") # Pa

PFR1.ReactorOperationMode = Reactors.OperationMode.Isothermic
PFR1.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length
PFR1.Length = 1.2 #m
PFR1.Volume = 1.0 #m^3

# isothermic

#PFR1.ReactorOperationMode = 0



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
