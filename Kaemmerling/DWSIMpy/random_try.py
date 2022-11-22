# -*- coding: utf-8 -*-
"""
Created on Mon May 30 19:41:48 2022

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

carbonmonoxide = sim.AvailableCompounds["CarbonMonoxide"]

methanol = sim.AvailableCompounds["Methanol"]
import clr
import System
 
clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
 
reactor = Flowsheet.GetFlowsheetSimulationObject("REACTOR")
 
profile = reactor.points
 
cnames = reactor.ComponentConversions.Keys.ToArray()
 
n = cnames.Count
 
Spreadsheet.Worksheets[0].Cells["A1"].Data = "Reactor Length (m)"
 
for i in range(0, n-1):
    Spreadsheet.Worksheets[0].Cells[0, i+1].Data = cnames[i]
 
j = 1
for pointset in profile:
    Spreadsheet.Worksheets[0].Cells[j, 0].Data = pointset[0]
    tmols = 0
    for i in range (1, n):
        tmols += pointset[i]
    for i in range (1, n):
            Spreadsheet.Worksheets[0].Cells[j, i].Data = pointset[i] / tmols
    j += 1
    
   

    # compounds mole frac
    # set up reaction kinetics
    # set up stochiometric


    sim.SelectedCompounds.Add(hydrogen.Name, hydrogen)

    sim.SelectedCompounds.Add(carbonmonoxide.Name, carbonmonoxide)

    sim.SelectedCompounds.Add(methanol.Name, methanol)



    # create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "vapour")
    m3 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "liquid")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    r1 = sim.AddObject(ObjectType.Reactor, 100, 50, "reactor")

    # ERROR: Reaktorname=? 

    sim.ConnectObjects(m1.GraphicObject, r1.GraphicObject, -1, -1)
    sim.ConnectObjects(r1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, r1.GraphicObject, -1, -1)
    sim.ConnectObjects(r1.GraphicObject, m3.GraphicObject, -1, -1)

    sim.AutoLayout()

    # steam tables property package

    stables = PropertyPackages.RaoultPropertyPackage()

    sim.AddPropertyPackage(stables)

    # set inlet stream temperature
    # default properties: T = 593.15 K, P = 101325 Pa, Mass Flow = 1500 kg/s

    m1.SetTemperature(593.15) # K
    m1.SetMassFlow(0.5) # kg/s
    m1.SetPressure(7000000) # Pa

    r1.CalcMode = UnitOperations.Reactor_Conversion.CalculationMode.Conversion
    r1.Conversion = 0.8 

    # request a calculation

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
