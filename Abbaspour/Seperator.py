import os
import pythoncom
pythoncom.CoInitialize()

import clr

from System.IO import Directory, Path, File
from System import String, Environment

dwsimpath = "C:\\Users\\49157\\AppData\\Local\\DWSIM8\\"

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
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

# Create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

# Add compounds
hydrogen = sim.AvailableCompounds["Hydrogen"]
water = sim.AvailableCompounds["Water"]
nitrogen = sim.AvailableCompounds["Nitrogen"]

sim.SelectedCompounds.Add(hydrogen.Name, hydrogen)
sim.SelectedCompounds.Add(water.Name, water)
sim.SelectedCompounds.Add(nitrogen.Name, nitrogen)

# Create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 100, 50, "outlet1")
m3 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet2")
SEP1 = sim.AddObject(ObjectType.Vessel, 100, 50, "Separator")

m1 = m1.GetAsObject()
m2 = m2.GetAsObject()
m3 = m3.GetAsObject()
SEP1 = SEP1.GetAsObject()

sim.ConnectObjects(m1.GraphicObject, SEP1.GraphicObject, -1, -1)
sim.ConnectObjects(SEP1.GraphicObject, m3.GraphicObject, -1, -1)
sim.ConnectObjects(SEP1.GraphicObject, m2.GraphicObject, -1, -1)

sim.AutoLayout()

# Peng Robinson Property Package
stables = PropertyPackages.PengRobinsonPropertyPackage()
sim.AddPropertyPackage(stables)


# Request calculation
Settings.SolverMode = 0
errors = interf.CalculateFlowsheet2(sim)

# Save file
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "Seperator.dwxmz")
interf.SaveFlowsheet(sim, fileNameToSave, True)

# Save the seperator to an image and display it
clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

PFDSurface = sim.GetSurface()

bmp = SKBitmap(1024, 768)
canvas = SKCanvas(bmp)
canvas.Scale(3.0)
PFDSurface.UpdateCanvas(canvas)
d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
str = MemoryStream()
d.SaveTo(str)
image = Image.FromStream(str)
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "sep.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image

im = Image.open(imgPath)
im.show()