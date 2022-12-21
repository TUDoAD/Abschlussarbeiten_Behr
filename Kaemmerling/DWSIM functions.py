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
import DWSIM.Interfaces

#create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

def Heat_exchanger(temperature_inlet1, pressure_inlet1, temperature_inlet2, pressure_inlet2, compoundscompoundflow1, compoundscompoundflow2, heat_exchange_area, global_heat_transfer):

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

    stables = PropertyPackages.SteamTablesPropertyPackage()

    sim.AddPropertyPackage(stables) 

#set inlet stream properties

    m1.SetTemperature(temperature_inlet1) # k
    
    m1.SetPressure(pressure_inlet1) # pa    

    m3.SetTemperature(temperature_inlet2) # k
    
    m3.SetPressure(pressure_inlet2) # pa     
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow1:
         
       print(compoundscompoundflow1[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow1[key])

    for key in compoundscompoundflow2:
         
       print(compoundscompoundflow2[key])
         
       m3.SetOverallCompoundMolarFlow(key , compoundscompoundflow2[key])
       
       h_ex1.set_Area(heat_exchange_area)
       h_ex1.set_Q(global_heat_transfer)

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

def Cooler(temperature, pressure, compoundscompoundflow, heatremoved, outlettemperature, deltat):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    c1 = sim.AddObject(ObjectType.Cooler, 200, 50, "cooler")
    sim.ConnectObjects(m1.GraphicObject, c1.GraphicObject, -1, -1)
    sim.ConnectObjects(c1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(c1.GraphicObject, e1.GraphicObject, -1, -1)
    
    
#set cooler operation mode

    if heatremoved != 0:
        c1.CalcMode = UnitOperations.Heater.CalculationMode.HeatAdded 
        c1.set_DeltaQ(heatremoved) # j
            
    if outlettemperature != 0:
        c1.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature 
        c1.OutletTemperature = outlettemperature # k
            
    if deltat != 0:
        c1.CalcMode = UnitOperations.Heater.CalculationMode.TemperatureChange
        c1.set_DeltaT(deltat) # k
            
    
    sim.AutoLayout()
    
# add property package

    stables = PropertyPackages.SteamTablesPropertyPackage()

    sim.AddPropertyPackage(stables) 

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

#request a calculation

    Settings.SolverMode = 0

    errors = interf.CalculateFlowsheet2(sim)

    print(String.Format("cooler Heat Load: {0} kW", c1.DeltaQ))


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

def Tank(temperature, pressure, compoundscompoundflow, tank_volume):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    t1 = sim.AddObject(ObjectType.Tank, 200, 50, "tank")
    sim.ConnectObjects(m1.GraphicObject, t1.GraphicObject, -1, -1)
    sim.ConnectObjects(t1.GraphicObject, m2.GraphicObject, -1, -1)

    
    
#set pump operation mode


            
    sim.AutoLayout()
    
# add property package

    stables = PropertyPackages.SteamTablesPropertyPackage()

    sim.AddPropertyPackage(stables) 

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    #t1.CalcMode = UnitOperations.Tank.Volume
    t1.set_Volume(tank_volume) #m^3
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

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

def Separator(temperature, pressure, compoundscompoundflow):


    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
       
    #molefracs normalisieren
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "vapor_outlet")
    m3 = sim.AddObject(ObjectType.MaterialStream, 100, 100, 'liquid_outlet')
    SEP1 = sim.AddObject(ObjectType.Vessel, 200, 50, "separator")
    sim.ConnectObjects(m1.GraphicObject, SEP1.GraphicObject, -1, -1)
    sim.ConnectObjects(SEP1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(SEP1.GraphicObject, m3.GraphicObject, -1, -1)
    
    
    sim.AutoLayout()
    
# add property package

    stables = PropertyPackages.SteamTablesPropertyPackage()

    sim.AddPropertyPackage(stables) 

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

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

def Pump(temperature, pressure, compoundscompoundflow, outletpressure, pressureincrease, energystream, powerrequired):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    p1 = sim.AddObject(ObjectType.Pump, 200, 50, "pump")
    sim.ConnectObjects(m1.GraphicObject, p1.GraphicObject, -1, -1)
    sim.ConnectObjects(p1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, p1.GraphicObject, -1, -1)
    
    
#set pump operation mode

    if outletpressure != 0:
        p1.CalcMode = UnitOperations.Pump.CalculationMode.OutletPressure 
        p1.set_Pout(outletpressure) # pa
        
            
    if powerrequired != 0:
        p1.CalcMode = UnitOperations.Pump.CalculationMode.Power 
        p1.PowerRequired(powerrequired) 
            
    if energystream != 0:
        p1.CalcMode = UnitOperations.Pump.CalculationMode.EnergyStream
        p1.set_EnergyFlow(energystream)
        
    if pressureincrease != 0:
        p1.CalcMode = UnitOperations.Pump.CalculationMode.Delta_P
        p1.set_DeltaP(pressureincrease) 
            
    sim.AutoLayout()
    
# add property package

    stables = PropertyPackages.SteamTablesPropertyPackage()

    sim.AddPropertyPackage(stables) 

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

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

def PFR(temperature, pressure, compoundscompoundflow, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry, reactor_diameter, reactor_length, reactor_volume, arrhenius_parameter):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
       
       # stoichiometric coefficients
       
       comps = stochiometry
       comps1 = Dictionary[str, float]()
       for key1 in comps:  
           value = comps[key1]
           comps1.Add(key1, value);

       # direct order coefficients
       
       dorders = direct_order
       dorders1 = Dictionary[str, float]()
       for key2 in dorders:  
           value = dorders[key2]
           dorders1.Add(key2, value);
           
       # reverse order coefficients
        
       rorders = reverse_order
       rorders1 = Dictionary[str, float]()
       for key3 in rorders:  
           value = rorders[key3]
           rorders1.Add(key3, value);

           
    kr1 = sim.CreateKineticReaction("Reaction", "Reaction_set", comps1, dorders1, rorders1, base_compound, "Mixture","Molar Concentration", "kmol/m3", "kmol/[m3.h]", arrhenius_parameter, 0.0, 0.0, 0.0, "", "")
    sim.AddReaction(kr1)
    sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    PFR1 = sim.AddObject(ObjectType.RCT_PFR, 100, 50, "PFR")
    sim.ConnectObjects(m1.GraphicObject, PFR1.GraphicObject, -1, -1)
    sim.ConnectObjects(PFR1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, PFR1.GraphicObject, -1, -1)
    
    
#set pfr operation mode

    if isothermic != 0:
        PFR1.ReactorOperationMode = Reactors.OperationMode.Isothermic
        
    if adiabatic != 0:
        PFR1.CalcMode = UnitOperations.RCT_PFR.CalculationMode.Power 
        PFR1.ReactorOperationMode = Reactors.OperationMode.Adiabatic
            
    if outlet_temperature != 0:
        PFR1.CalcMode = UnitOperations.RCT_PFR.CalculationMode.EnergyStream
        PFR1.ReactorOperationMode = Reactors.OperationMode.OutletTemperature
        
    if reactor_diameter !=0:
        
        PFR1.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Diameter
        PFR1.Diameter = reactor_diameter #m
        
    if reactor_length !=0:
        
        PFR1.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length
        PFR1.Length = reactor_length #m
    
    
    PFR1.Volume = reactor_volume #m^3
        
            
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
    str1 = MemoryStream()
    d.SaveTo(str1)
    image = Image.FromStream(str1)
    imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "pfd.png")
    image.Save(imgPath, ImageFormat.Png)
    str1.Dispose()
    canvas.Dispose()
    bmp.Dispose()
    
    from PIL import Image

    im = Image.open(imgPath)
    im.show()

def Heater(temperature, pressure, compoundscompoundflow, heatadded, outlettemperature, deltat):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    h1 = sim.AddObject(ObjectType.Heater, 100, 50, "heater")
    sim.ConnectObjects(m1.GraphicObject, h1.GraphicObject, -1, -1)
    sim.ConnectObjects(h1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, h1.GraphicObject, -1, -1)
    
    
#set heater operation mode

    if heatadded != 0:
        h1.CalcMode = UnitOperations.Heater.CalculationMode.HeatAdded 
        h1.set_DeltaQ(heatadded) # j
            
    if outlettemperature != 0:
        h1.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature 
        h1.OutletTemperature = outlettemperature # k
            
    if deltat != 0:
        h1.CalcMode = UnitOperations.Heater.CalculationMode.TemperatureChange
        h1.set_DeltaT(deltat) # k


    
    sim.AutoLayout()
    
# add property package

    stables = PropertyPackages.SteamTablesPropertyPackage()

    sim.AddPropertyPackage(stables) 

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

#request a calculation

    Settings.SolverMode = 0

    errors = interf.CalculateFlowsheet2(sim)

    print(String.Format("Heater Heat Load: {0} kW", h1.DeltaQ))


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

def CSTR(temperature, pressure, compoundscompoundflow, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry,reactor_volume, arrhenius_parameter):

#add compounds

    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
       # stoichiometric coefficients
       
       comps = stochiometry
       comps1 = Dictionary[str, float]()
       for key1 in comps:  
           value = comps[key1]
           comps1.Add(key1, value);

       # direct order coefficients
       
       dorders = direct_order
       dorders1 = Dictionary[str, float]()
       for key2 in dorders:  
           value = dorders[key2]
           dorders1.Add(key2, value);
           
       # reverse order coefficients
        
       rorders = reverse_order
       rorders1 = Dictionary[str, float]()
       for key3 in rorders:  
           value = rorders[key3]
           rorders1.Add(key3, value);

    kr1 = sim.CreateKineticReaction("N-butyl acetate Production", "Production of N-butyl acetate", 
                   comps1, dorders1, rorders1, "1-butanol", "Liquid","Molar Concentration", "kmol/m3", "kmol/[m3.h]", arrhenius_parameter, 0.0, 0.0, 0.0, "", "")
          
    sim.AddReaction(kr1)
    sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)
    
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
        CSTR1.ReactorOperationMode = Reactors.OperationMode.OutletTemperature


    CSTR1.Volume = reactor_volume #m^3      
    sim.AutoLayout()
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         

       m1.SetOverallCompoundMassFlow(key, compoundscompoundflow[key])
    
# add property package

    sim.CreateAndAddPropertyPackage("Raoult's Law")

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    

    

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
    str1 = MemoryStream()
    d.SaveTo(str1)
    image = Image.FromStream(str1)
    imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "pfd.png")
    image.Save(imgPath, ImageFormat.Png)
    str1.Dispose()
    canvas.Dispose()
    bmp.Dispose()
    
    from PIL import Image

    im = Image.open(imgPath)
    im.show()

def Compressor(temperature, pressure, compoundscompoundflow, outletpressure, pressureincrease, energystream):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    comp1 = sim.AddObject(ObjectType.Compressor, 200, 50, "compressor")
    sim.ConnectObjects(m1.GraphicObject, comp1.GraphicObject, -1, -1)
    sim.ConnectObjects(comp1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, comp1.GraphicObject, -1, -1)
    
    
#set pump operation mode

    if outletpressure != 0:
        comp1.CalcMode = UnitOperations.Compressor.CalculationMode.OutletPressure 
        comp1.set_POut(outletpressure) # pa
            
    if energystream != 0:
        comp1.CalcMode = UnitOperations.Compressor.CalculationMode.EnergyStream
        comp1.set_EnergyFlow(energystream)
        
    if pressureincrease != 0:
        comp1.CalcMode = UnitOperations.Compressor.CalculationMode.Delta_P
        comp1.set_DeltaP(pressureincrease) # k
            
    sim.AutoLayout()
    
# add property package

    stables = PropertyPackages.SteamTablesPropertyPackage()

    sim.AddPropertyPackage(stables) 

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

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

def Column(temperature, pressure, compoundscompoundflow, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound):

#add compounds
    
    for key in compoundscompoundflow:
        
       sim.AddCompound(key)
        
       print(key)
    
    
#create and connect objects

    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet1")
    m3 = sim.AddObject(ObjectType.MaterialStream, 200, 50, 'outlet2')
    e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
    e2 = sim.AddObject(ObjectType.EnergyStream, 250, 50, "power")
    DEST1 = sim.AddObject(ObjectType.ShortcutColumn, 200, 50, "Column")
    sim.ConnectObjects(m1.GraphicObject, DEST1.GraphicObject, -1, -1)
    sim.ConnectObjects(DEST1.GraphicObject, m2.GraphicObject, -1, -1)
    sim.ConnectObjects(DEST1.GraphicObject, m3.GraphicObject, -1, -1)
    sim.ConnectObjects(e1.GraphicObject, DEST1.GraphicObject, -1, -1)
    sim.ConnectObjects(DEST1.GraphicObject, e2.GraphicObject, -1, -1)
    
    
    DEST1.m_lightkey = light_key_compound
    DEST1.m_heavykey = heavy_key_compound
    DEST1.m_heavykeymolarfrac = hk_mole_fraction_in_distillate
    DEST1.m_lightkeymolarfrac = lk_mole_fraction_in_distillate
    DEST1.m_refluxratio = reflux_ratio
            
    sim.AutoLayout()
    
# add property package

    stables = PropertyPackages.RaoultPropertyPackage()

    sim.AddPropertyPackage(stables)

#set inlet stream properties

    m1.SetTemperature(temperature) # k
    
    m1.SetPressure(pressure) # pa        
    
    m1.SetMolarFlow(0.0) # will be set by compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m1.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

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