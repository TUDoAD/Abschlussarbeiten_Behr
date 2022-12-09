#benötigt graphen mit allen einträgen und input strom
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
import networkx as nx
import functions

Directory.SetCurrentDirectory(dwsimpath)

#create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

def startsimulatinfromgraphml(graph, inlet_temperature, inlet_pressure, compoundscompoundflow):
    a = 0
    #add compounds    
    for key in compoundscompoundflow:
        sim.AddCompound(key)
        print(key)
        
    #add mass streams
    number_of_mass_flows = 2 + nx.number_of_edges(graph)
    for i in range(number_of_mass_flows):
        globals()['m_{}'.format(i)] = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
    
    #add energy streams
        
    nodes = list(graph.nodes)
    for node in nodes:

        if graph._node[node]['node_class'] == 'Column':
            a = a+2
        if graph._node[node]['node_class'] == 'heater':
            a = a+1
        if graph._node[node]['node_class'] == 'cooler':
            a = a+1
        if graph._node[node]['node_class'] == 'PFR':
            a = a+1
        if graph._node[node]['node_class'] == 'CSTR':
            a = a+1
        if graph._node[node]['node_class'] == 'compressor':
            a = a+1
        if graph._node[node]['node_class'] == 'pump':
            a = a+1
    for i in range(a):
        globals()['e_{}'.format(i)] = sim.AddObject(ObjectType.EnergyStream, 50, 50, "inlet")
        

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
    m_0.SetTemperature(inlet_temperature) # K # als string?
    m_0.SetPressure(inlet_pressure) # Pa # als string?
    for key in compoundscompoundflow:
         
       print(compoundscompoundflow[key])
         
       m_0.SetOverallCompoundMolarFlow(key , compoundscompoundflow[key])

    for node in nodes:
       if graph._node[node]['node_class'] == 'Vessel':
           node = sim.AddObject(ObjectType.Tank, 200, 50, "tank")
           node.CalcMode = UnitOperations.Tank.set_Volume
           node.set_Volume(graph.nodes[node]['tank_volume']) #m^3
       if graph._node[node]['node_class'] == 'Tank':
           node = sim.AddObject(ObjectType.Tank, 200, 50, "tank")
           node.CalcMode = UnitOperations.Tank.set_Volume
           node.set_Volume(graph.nodes[node]['tank_volume']) #m^3
       if graph._node[node]['node_class'] == 'Silo':
           node = sim.AddObject(ObjectType.Tank, 200, 50, "tank")
           node.CalcMode = UnitOperations.Tank.set_Volume
           node.set_Volume(graph.nodes[node]['tank_volume']) #m^3
           
       if graph._node[node]['node_class'] == 'Pump':
           node = sim.AddObject(ObjectType.Pump, 200, 50, "pump")
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.OutletPressure 
               node.set_Pout(graph.nodes[node]['outlet_pressure']) # pa
                              
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.Power 
               node.PowerRequired(graph.nodes[node]['power_required'])
                   
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.EnergyStream
               node.set_EnergyFlow(graph.nodes[node]['energy_stream'])
               
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.Delta_P
               node.set_DeltaP(graph.nodes[node]['pressure_increase'])
               
       if graph._node[node]['node_class'] == 'Compressor':
           node = sim.AddObject(ObjectType.Compressor, 200, 50, "compressor")
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.OutletPressure 
               node.set_Pout(graph.nodes[node]['outlet_pressure']) # pa
                              
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.Power 
               node.PowerRequired(graph.nodes[node]['power_required'])
                   
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.EnergyStream
               node.set_EnergyFlow(graph.nodes[node]['energy_stream'])
               
           if graph._node[node][node]!= 0:
               node.CalcMode = UnitOperations.Pump.CalculationMode.Delta_P
               node.set_DeltaP(graph.nodes[node]['pressure_increase'])
               
       if graph._node[node]['node_class'] == 'CSTR':
           CSTR1 = sim.AddObject(ObjectType.RCT_CSTR, 100, 50, "CSTR") 
           # stoichiometric coefficients
           
           comps = graph.nodes[node]['stochiometry']
           comps1 = Dictionary[str, float]()
           for key1 in comps:  
               value = comps[key1]
               comps1.Add(key1, value);
               
           # direct order coefficients
           
           dorders = graph.nodes[node]['direct_order']
           dorders1 = Dictionary[str, float]()
           for key2 in dorders:  
               value = dorders[key2]
               dorders1.Add(key2, value);
               
           # reverse order coefficients
            
           rorders = graph.nodes[node]['reverse_order']
           rorders1 = Dictionary[str, float]()
           for key3 in rorders:  
               value = rorders[key3]
               rorders1.Add(key3, value);

           kr1 = sim.CreateKineticReaction("N-butyl acetate Production", "Production of N-butyl acetate", 
                       comps1, dorders1, rorders1, "1-butanol", "Liquid","Molar Concentration", "kmol/m3", "kmol/[m3.h]", graph.nodes[node]['arrhenius_parameter'], 0.0, 0.0, 0.0, "", "")
              
           sim.AddReaction(kr1)
           sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)
       
           if graph.nodes[node]['adiabatic'] != 0:
               node.ReactorOperationMode = Reactors.OperationMode.Adiabatic
           
           if graph.nodes[node]['isothermic'] != 0:
                node.ReactorOperationMode = Reactors.OperationMode.Isothermic
         
           if graph.nodes[node]['outlet_temperature'] != 0:
               node.ReactorOperationMode = Reactors.OperationMode.OutletTemperature


           node.Volume = graph.nodes[node]['reactor_volume'] #m^3  
           
       if graph._node[node]['node_class'] == 'PFR':
           node = sim.AddObject(ObjectType.RCT_PFR, 100, 50, "PFR")
           # stoichiometric coefficients        
           comps = graph.nodes[node]['stochiometry']
           comps1 = Dictionary[str, float]()
           for key1 in comps:  
               value = comps[key1]
               comps1.Add(key1, value);

           # direct order coefficients        
           dorders = graph.nodes[node]['direct_order']
           dorders1 = Dictionary[str, float]()
           for key2 in dorders:  
               value = dorders[key2]
               dorders1.Add(key2, value);
               
           # reverse order coefficients       
           rorders = graph.nodes[node]['reverse_order']
           rorders1 = Dictionary[str, float]()
           for key3 in rorders:  
               value = rorders[key3]
               rorders1.Add(key3, value);

           kr1 = sim.CreateKineticReaction("N-butyl acetate Production", "Production of N-butyl acetate", 
                       comps1, dorders1, rorders1, "1-butanol", "Liquid","Molar Concentration", "kmol/m3", "kmol/[m3.h]", graph.nodes[node]['arrhenius_parameter'], 0.0, 0.0, 0.0, "", "")
              
           sim.AddReaction(kr1)
           sim.AddReactionToSet(kr1.ID, "DefaultSet", 'true', 0)
       
#set pfr operation mode

           if graph.nodes[node]['isothermic']!= 0:
               node.ReactorOperationMode = Reactors.OperationMode.Isothermic
        
           if graph.nodes[node]['adiabatic']!= 0:
               node.CalcMode = UnitOperations.RCT_PFR.CalculationMode.Power 
               node.ReactorOperationMode = Reactors.OperationMode.Adiabatic
            
           if graph.nodes[node]['outlet_temperature']!= 0:
               node.CalcMode = UnitOperations.RCT_PFR.CalculationMode.EnergyStream
               node.ReactorOperationMode = Reactors.OperationMode.OutletTemperature
        
           if graph.nodes[node]['reactor_diameter']!= 0:
               node.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Diameter
               node.Diameter = graph.nodes[node]['reactor_diameter'] #m
        
           if graph.nodes[node]['reactor_length']!= 0:
               node.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length
               node.Length = graph.nodes[node]['reactor_length']  #m
    
    
           node.Volume = graph.nodes[node]['reactor_volume'] #m^3
           
       if graph._node[node]['node_class'] == 'Cooler':
            node = sim.AddObject(ObjectType.Cooler, 200, 50, "cooler")
            #set cooler operation mode
            if graph.nodes[node]['heat_removed']!= 0:
                node.CalcMode = UnitOperations.Heater.CalculationMode.HeatAdded 
                node.set_DeltaQ(nodes[node]['heat_removed']) # j
            
            if nodes[node]['outlet_temperature']!= 0:
                node.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature 
                node.OutletTemperature = nodes[node]['outlet_temperature'] # k
            
            if nodes[node]['deltat']!= 0:
                node.CalcMode = UnitOperations.Heater.CalculationMode.TemperatureChange
                node.set_DeltaT(nodes[node]['deltat']) # k
           
       if graph._node[node]['node_class'] == 'Heater':
            node = sim.AddObject(ObjectType.Heater, 100, 50, "heater")
            #set heater operation mode
            if graph.nodes[node]['heat_added']!= 0:
                node.CalcMode = UnitOperations.Heater.CalculationMode.HeatAdded 
                node.set_DeltaQ(nodes[node]['heat_added']) # j
            
            if nodes[node]['outlet_temperature']!= 0:
                node.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature 
                node.OutletTemperature = nodes[node]['outlet_temperature'] # k
            
            if nodes[node]['deltat']!= 0:
                node.CalcMode = UnitOperations.Heater.CalculationMode.TemperatureChange
                node.set_DeltaT(nodes[node]['deltat']) # k
           
       if graph._node[node]['node_class'] == 'Heat exchanger':
          node = sim.AddObject(ObjectType.HeatExchanger, 100, 50, "heat_exchanger")
          node.set_Area(graph.nodes[node]['heat_exchange_area'])
          node.set_Q(graph.nodes[node]['global_heat_transfer'])
           
       if graph._node[node]['node_class'] == 'Heat exchanger, detailed':    
          node = sim.AddObject(ObjectType.HeatExchanger, 100, 50, "heat_exchanger")
          node.set_Area(graph.nodes[node]['heat_exchange_area'])
          node.set_Q(graph.nodes[node]['global_heat_transfer'])
          
       if graph._node[node]['node_class'] == 'Column':
          node = sim.AddObject(ObjectType.ShortcutColumn, 200, 50, "Column")          
          node.m_lightkey =graph.nodes[node]['light_key_compound']
          node.m_heavykey =graph.nodes[node]['heavy_key_compound'] 
          node.m_heavykeymolarfrac =graph.nodes[node]['hk_mole_fraction_in_distillate']
          node.m_lightkeymolarfrac =graph.nodes[node]['lk_mole_fraction_in_distillate']
          node.m_refluxratio =graph.nodes[node]['reflux_ratio']
       if graph._node[node]['node_class'] == 'Separator':
          node = sim.AddObject(ObjectType.Vessel, 200, 50, "separator")



    # request calculation

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



