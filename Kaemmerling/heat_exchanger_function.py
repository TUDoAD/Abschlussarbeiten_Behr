


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

def Heat_exchanger(temperature_inlet1, pressure_inlet1, temperature_inlet2, pressure_inlet2, compoundscompoundflow1, compoundscompoundflow2, heat_exchange_area):

#add compounds
    
    for key in compoundscompoundflow1:
        
       sim.AddCompound(key)
        
       print(key)
       
       
       for key2 in compoundscompoundflow2:
        
           if key != key2:
        
              sim.AddCompound(key2)
        
              print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet1")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet1")
    m3 = sim.AddObject(ObjectType.MaterialStream, 250, 50, "inlet2")
    m4 = sim.AddObject(ObjectType.MaterialStream, 350, 50, "outlet2")
    h_ex1 = sim.AddObject(ObjectType.HeatExchanger, 100, 50, "heat_exchanger")
    sim.ConnectObjects(m1.GraphicObject, h_ex1.GraphicObject, -1, -1)
    sim.ConnectObjects(h_ex1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(m3.GraphicObject, h_ex1.GraphicObject, -1, -1)
    sim.ConnectObjects(h_ex1.GraphicObject, m4.GraphicObject, -1, -1)
    
    
    
    sim.AutoLayout()
    
# add property package

    sim.CreateAndAddPropertyPackage("Raoult's Law") 

#set inlet stream properties

    m1.SetTemperature(temperature_inlet1) # k
    
    m1.SetPressure(pressure_inlet1) # pa    

    m3.SetTemperature(temperature_inlet2) # k
    
    m3.SetPressure(pressure_inlet2) # pa     
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow1:
         
       print(compoundscompoundflow1[key])
         
       m1.SetOverallCompoundMassFlow(key , compoundscompoundflow1[key])

    for key in compoundscompoundflow2:
         
       print(compoundscompoundflow2[key])
         
       m3.SetOverallCompoundMassFlow(key , compoundscompoundflow2[key])
       
       h_ex1.set_Area(heat_exchange_area)

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
    
Heat_exchanger(300.0,100000.0, 400.0, 100000.0, {"Water" : 1.0}, {"Ethanol" : 1.0},1.0)
