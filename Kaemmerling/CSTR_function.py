
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

    kr1 = sim.CreateKineticReaction("Ethyl acetate Production", "Production of ethyl acetate", 
                   comps1, dorders1, rorders1, base_compound, "Liquid","Molar Concentration", "kmol/m3", "kmol/[m3.h]", arrhenius_parameter, 0.0, 0.0, 0.0, "", "")
          
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
    
# set compounds
    
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         

       m1.SetOverallCompoundMassFlow(key, compoundscompoundflow[key])
    
# add property package

    stables = PropertyPackages.RaoultPropertyPackage()

    sim.AddPropertyPackage(stables)

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
    
# function call    
CSTR(343.15,100000.0,{"Ethanol" : 0.48, 'Acetic acid' : 0.5, 'Water' : 0.02, 'Ethyl acetate' : 0.0},1,0,0,'Ethanol',{"Ethanol" : 1.0, 'Acetic acid' : 1.0, 'Water': 0.0, 'Ethyl acetate': 0.0}, {"Ethanol" : 0.0, 'Acetic acid' : 0.0, 'Water': 0.0, 'Ethyl acetate': 0.0},{"Ethanol" : -1.0, 'Acetic acid' : -1.0, 'Water':1.0, 'Ethyl acetate': 1.0}, 0.14, 0.005)