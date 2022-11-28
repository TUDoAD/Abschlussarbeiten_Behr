# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 11:36:37 2022

@author: Lucky Luciano
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 17:08:33 2022

@author: Lucky Luciano
"""


#delete dwsim_newui

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
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings

Directory.SetCurrentDirectory(dwsimpath)

#create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

def CSTR(temperature, pressure, compoundscompoundflow, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometrie,reactor_volume, arrhenius_parameter):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    CSTR1 = sim.AddObject(ObjectType.RCT_CSTR, 100, 50, "CSTR")
    sim.ConnectObjects(m1.GraphicObject, CSTR1.GraphicObject, -1, -1)
    sim.ConnectObjects(CSTR1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, CSTR1.GraphicObject, -1, -1)
    
    
#set cstr operation mode


        

            
    if adiabatic != 0:
        CSTR1.ReactorOperationMode = Reactors.OperationMode.Adiabatic
        
    if isothermic != 0:
        CSTR1.ReactorOperationMode = Reactors.OperationMode.Isothermic
      
    if outlet_temperature != 0:
        CSTR1.ReactorOperationMode = Reactors.OperationMode.Isothermic


    CSTR1.Volume = reactor_volume #m^3      
    sim.AutoLayout()
    
# add property package

    sim.CreateAndAddPropertyPackage("Raoult's Law")

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])
       
       # stoichiometric coefficients
    for components in stochiometrie:
        
           comps = Dictionary()
           comps.Add(components, stochiometrie[components]);

       # direct order coefficients
    for components in direct_order:
           
           dorders = Dictionary()
           dorders.Add(components, stochiometrie[components]);
           
        # reverse order coefficients
    for components in stochiometrie:
        
           rorders = Dictionary()
           rorders.Add(components, stochiometrie[components]);

    kr1 = sim.CreateKineticReaction("N-butyl acetate Production", "Production of N-butyl acetae", 
                   comps, dorders, rorders, "1-butanol", "Liquid","Molar Concentration", "kmol/m3", "kmol/[m3.h]", arrhenius_parameter, 0.0, 0.0, 0.0, "", "")
          
    sim.AddReaction(kr1)
    sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)

#request a calculation

    Settings.SolverMode = 0

    errors = interf.CalculateFlowsheet2(sim)
    



#save file

    fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "heatersample.dwxmz")

    interf.SaveFlowsheet(sim, fileNameToSave, True)

#save the pfd to an image and display it

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
    
CSTR(300.0,100000.0,{"Water" : 9.57},200000,0,0,0)