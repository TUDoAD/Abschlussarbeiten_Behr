# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 11:55:50 2022

@author: Lucky Luciano
"""

# delete dwsim_newui
# TODO: 

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
import math
from System import Array



# create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

# add compounds

water = sim.AvailableCompounds["Water"]

ethanol = sim.AvailableCompounds["Ethanol"]



sim.AddCompound("Water")
sim.AddCompound("Ethanol")



# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 0, 50, "dest_inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "dest_head")
m3 = sim.AddObject(ObjectType.MaterialStream, 350, 50, "dest_bottom")
m4 = sim.AddObject(ObjectType.MaterialStream, 550, 50, "pump1_outlet")
m5 = sim.AddObject(ObjectType.MaterialStream, 750, 50, "tank1_outlet")
m6 = sim.AddObject(ObjectType.MaterialStream, 850, 50, "splitter_inlet")
m7 = sim.AddObject(ObjectType.MaterialStream, 850, 200, "heat_ex_inlet")
m8 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "heat_ex_outlet")
m9 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "splitter_outlet1")
m10 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "splitter_outlet2")
m11 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "tank2_outlet")
m12 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "tank3_outlet")
m13 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "mixer_outlet")
m14 = sim.AddObject(ObjectType.MaterialStream, 1000, 300, "pump2_outlet")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 100, "power1")
e2 = sim.AddObject(ObjectType.EnergyStream, 250, 100, "power2")
e3 = sim.AddObject(ObjectType.EnergyStream, 450, 300, "power3")
e4 = sim.AddObject(ObjectType.EnergyStream, 450, 300, "power4")
DEST1 = sim.AddObject(ObjectType.ShortcutColumn, 250, 50, "DEST")
Heat_ex = sim.AddObject(ObjectType.HeatExchanger, 450, 200, "Heat_ex")
Split1 = sim.AddObject(ObjectType.Splitter, 100, 50, "Splitter")
T1 = sim.AddObject(ObjectType.Tank, 800, 50, "Tank1")
T2 = sim.AddObject(ObjectType.Tank, 800, 50, "Tank2")
MIX1 = sim.AddObject(ObjectType.Mixer, 950, 200, "Mixer")
P1 = sim.AddObject(ObjectType.Pump, 650, 50, "Pump")
T3 = sim.AddObject(ObjectType.Tank, 800, 50, "Tank3")
P2 = sim.AddObject(ObjectType.Pump, 650, 50, "Pump2")

sim.ConnectObjects(m1.GraphicObject, DEST1.GraphicObject, -1, -1)
sim.ConnectObjects(DEST1.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(DEST1.GraphicObject, m3.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, Heat_ex.GraphicObject, -1, -1)
sim.ConnectObjects(m3.GraphicObject, P1.GraphicObject, -1, -1)
sim.ConnectObjects(P1.GraphicObject, m4.GraphicObject, -1, -1)
sim.ConnectObjects(m4.GraphicObject, T1.GraphicObject, -1, -1)
sim.ConnectObjects(T1.GraphicObject, m5.GraphicObject, -1, -1)
sim.ConnectObjects(Heat_ex.GraphicObject, m6.GraphicObject, -1, -1)
sim.ConnectObjects(m6.GraphicObject, Split1.GraphicObject, -1, -1)
sim.ConnectObjects(Split1.GraphicObject, m9.GraphicObject, -1, -1)
sim.ConnectObjects(Split1.GraphicObject, m10.GraphicObject, -1, -1)
sim.ConnectObjects(m9.GraphicObject, T2.GraphicObject, -1, -1)
sim.ConnectObjects(m10.GraphicObject, T3.GraphicObject, -1, -1)
sim.ConnectObjects(T3.GraphicObject, m12.GraphicObject, -1, -1)
sim.ConnectObjects(T2.GraphicObject, m11.GraphicObject, -1, -1)
sim.ConnectObjects(m11.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(m12.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(MIX1.GraphicObject, m13.GraphicObject, -1, -1)
sim.ConnectObjects(m13.GraphicObject, P2.GraphicObject, -1, -1)
sim.ConnectObjects(P2.GraphicObject, m14.GraphicObject, -1, -1)
sim.ConnectObjects(e1.GraphicObject, DEST1.GraphicObject, -1, -1)
sim.ConnectObjects(DEST1.GraphicObject, e2.GraphicObject, -1, -1)
sim.ConnectObjects(e3.GraphicObject, P1.GraphicObject, -1, -1)
sim.ConnectObjects(e4.GraphicObject, P2.GraphicObject, -1, -1)
sim.ConnectObjects(m8.GraphicObject, Heat_ex.GraphicObject, -1, -1)
sim.ConnectObjects(Heat_ex.GraphicObject, m7.GraphicObject, -1, -1)
sim.AutoLayout()

# Peng Robinson Property Package

stables = PropertyPackages.PengRobinsonPropertyPackage()

sim.AddPropertyPackage(stables)

# set inlet stream conditions
#Overall Molar flow = 1 kg/s

m1.SetTemperature(298.15) # K
m1.SetOverallCompoundMolarFlow("Water", 0.5) #kg/s
m1.SetOverallCompoundMolarFlow("Ethanol", 0.5) #kg/s
m1.SetPressure("100000 Pa") # Pa


T1.CalcMode = UnitOperations.Tank.set_Volume
T1.set_Volume(100) #m^3

T2.CalcMode = UnitOperations.Tank.set_Volume
T2.set_Volume(100) #m^3

T3.CalcMode = UnitOperations.Tank.set_Volume
T3.set_Volume(100) #m^3

DEST1.m_lightkey = "Ethanol"
DEST1.m_heavykey = "Water"
DEST1.m_heavykeymolarfrac = 0.01
DEST1.m_lightkeymolarfrac = 0.01
DEST1.m_refluxratio = 1.4



# request calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)

Energy1 = e1.EnergyFlow
Energy2 = e2.EnergyFlow
Energy3 = e3.EnergyFlow
Energy4 = e4.EnergyFlow
 

print('Energy (kW): ' + str(Energy1))
print('Energy (kW): ' + str(Energy2))
print('Energy (kW): ' + str(Energy3))
print('Energy (kW): ' + str(Energy4))

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

import networkx as nx
import functions

a = 1

b = 0

Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

g = nx.read_graphml(Path_graph) #graphml einladen

# relevante nodes finden und in neuen graphen einfügen
    
nodes = list(g.nodes)

wantednodes = []

W = nx.DiGraph()
    
for x in nodes:
           
           newlist = list(g.successors(x)) 
           
           for z in newlist:            
                 
               if  g._node[z]['node_class'] == 'Column':
                             
                     wantednodes.append(z)
               
               elif  g._node[z]['node_class'] == 'Heat exchanger, detailed':
                  
                     wantednodes.append(z)
                  
               elif  g._node[z]['node_class'] == 'Vessel':
               
                     wantednodes.append(z)
                     
               elif  g._node[z]['node_class'] == 'Silo':
   
                     wantednodes.append(z)
                       
               elif g._node[z]['node_class'] == 'Fluid pump':    #redundante Pumpen entfernen           
            
                    size = len(z)
            
                    num = z[size-1]
            
                    if int(num) % 2 == 0:
                
                       wantednodes.append(z)

wanted_list = list(dict.fromkeys(wantednodes)) # doppelte einträge entfernen

W.add_nodes_from(wantednodes)

# verdbindungen der nodes herstellen

for w in wanted_list: 
    
    for p in wanted_list:
    
        if w != p and nx.has_path(g,w,p) == True:
        
            paths = nx.all_shortest_paths(g,w,p)
            path = tuple(paths)
        
            for m in wanted_list:

                for n in path[0]:
                
                    if m == n:
                     
                       b = b+1
                     
            if b == 2:
                
               W.add_edge(w, p, edge_class='Piping',edge_sub_class='Main pipe')
                
               b = 0
                
            else:
                
                b = 0
                
# node atrributes übertragen

for grop in wanted_list:
    group= g._node[grop]['node_group']
    nx.set_node_attributes(W,group,'node_group')
    
# position der nodes übertragen
    
for position in wanted_list:
    xpos= g.nodes[position]['node_x']
    ypos= g.nodes[position]['node_y']
    W._node[position]['node_x'] = xpos
    W._node[position]['node_y'] = ypos
    
# plot erzeugen
                      
nx.write_graphml(W,'./Output/graphs_graphml/clean/graphml_pfd')
functions.plot_graph2('./Output/graphs_graphml/clean/graphml_pfd', './Output/graphs_plots_clean')
f = nx.read_graphml('./Output/graphs_graphml/clean/graphml_pfd')

########################################################################
### inputs für die jeweiligen UO müssen graphen eingetragen werden !!!##
########################################################################
for grop in wanted_list:
    dict1 = {'node_group':g._node[grop]['node_group']}
    group= {grop:dict1}
    nx.set_node_attributes(f,group)
    dict2 = {'node_class':g._node[grop]['node_class']}
    clas= {grop:dict2}
    nx.set_node_attributes(f,clas)
for unitoperation in wanted_list:
    if  f._node[unitoperation]['node_class'] == 'Column':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature1':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m3.GetTemperature()
        dict1 = {'outlet_temperature2':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m2.GetPressure()
        dict1 = {'outlet_pressure1':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m3.GetPressure()
        dict1 = {'outlet_pressure2':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow1':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition1':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m3.GetMassFlow() 
        dict1 = {'outlet_mass_flow2':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m3.GetOverallComposition())
        dict1 = {'outlet_composition2':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        heater_energy = e1.EnergyFlow
        dict1 = {'heater_energy':heater_energy}  #energy muss allgemein gehalten werden
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        cooler_energy = e2.EnergyFlow
        dict1 = {'cooler_energy':cooler_energy}  #energy muss allgemein gehalten werden
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Vessel':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m2.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        tank_volume = T1.get_Volume()  #T1 muss allgemein für jeden Tank geändert werden
        dict1 = {'tank_volume':tank_volume}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Pump':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m2.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e4.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Compressor':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m1.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e3.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Separator':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m2.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'PFR':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m1.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e3.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'CSTR':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m1.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e3.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Cooler':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m1.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e3.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Heater':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m1.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e3.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Heat exchanger':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_temperature2 = m3.GetTemperature()
        dict1 = {'inlet_temperature2':inlet_temperature2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = Heat_ex.get_ColdSideOutletTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature2 = Heat_ex.get_HotSideOutletTemperature()
        dict1 = {'outlet_temperature2':outlet_temperature2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure2 = m3.GetPressure()
        dict1 = {'inlet_pressure2':inlet_pressure2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m2.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure2 = m4.GetPressure()
        dict1 = {'outlet_pressure2':outlet_pressure2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow2 = m3.GetMassFlow() 
        dict1 = {'inlet_mass_flow2':inlet_mass_flow2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow2 = m4.GetMassFlow() 
        dict1 = {'outlet_mass_flow2':outlet_mass_flow2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        heat_exchange_area = Heat_ex.get_Area()
        dict1 = {'heat_exchange_area':heat_exchange_area}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        global_heat_transfer = Heat_ex.GetPowerGeneratedOrConsumed
        dict1 = {'global_heat_transfer':global_heat_transfer}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition2 = list(m4.GetOverallComposition())
        dict1 = {'inlet_composition2':inlet_composition2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition2 = list(m4.GetOverallComposition())
        dict1 = {'outlet_composition2':outlet_composition2}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Fluid pump':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m1.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e3.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Heat exchanger, detailed':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m1.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        energy_flow = e3.EnergyFlow   #energy muss allgemein gehalten werden
        dict1 = {'energy_flow':energy_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
    if  f._node[unitoperation]['node_class'] == 'Vessel':
        inlet_temperature = m1.GetTemperature()
        dict1 = {'inlet_temperature':inlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_temperature = m2.GetTemperature()
        dict1 = {'outlet_temperature':outlet_temperature}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_pressure = m1.GetPressure()
        dict1 = {'inlet_pressure':inlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_pressure = m2.GetPressure()
        dict1 = {'outlet_pressure':outlet_pressure}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_mass_flow = m1.GetMassFlow() 
        dict1 = {'inlet_mass_flow':inlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_mass_flow = m2.GetMassFlow() 
        dict1 = {'outlet_mass_flow':outlet_mass_flow}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        inlet_composition = list(m1.GetOverallComposition())
        dict1 = {'inlet_composition':inlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        outlet_composition = list(m2.GetOverallComposition())
        dict1 = {'outlet_composition':outlet_composition}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)
        tank_volume = T1.get_Volume()  #T1 muss allgemein für jeden Tank geändert werden
        dict1 = {'tank_volume':tank_volume}
        group= {unitoperation:dict1}
        nx.set_node_attributes(f,group)