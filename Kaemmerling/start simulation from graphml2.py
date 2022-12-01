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
import networkx as nx
import functions
import sys
import Heater_function
import PFR_Function
import CSTR_function
import column_function
import Tank_function
import Pump_function
import Compressor_function
import Separator_function
import cooler_function
import heat_exchanger_function

#for schleife

def startsimulationfromgraphml(graph):
    c = 0
    nodes = list(graph.nodes)
    first_node = nodes[0]
    inlet_temperature = graph._node[first_node]['inlet_temperature'] 
    inlet_pressure = graph._node[first_node]['inlet_pressure'] 
    composition = graph._node[first_node]['inlet_composition'] 
    mass_flow = graph._node[first_node]['inlet_mass_flow'] 
    compounds = graph._node[first_node]['compounds'] #dwsim function fehlt noch 
    compoundscompoundflow = dict()
    for components in compounds:
        compound = compounds[c]
        compound_mass_frac = composition[c]
        compound_mass_flow = compound_mass_frac * mass_flow
        compoundscompoundflow[compound].append(compound_mass_flow)
        c = c+1
        
    if nodes[0] == 'column':
        mass_flow = graph._node[first_node]['inlet_mass_flow'] 
        lk_mole_fraction_in_distillate = graph._node[first_node]['lk_mole_fraction_in_distillate'] 
        hk_mole_fraction_in_distillate = graph._node[first_node]['hk_mole_fraction_in_distillate']
        reflux_ratio = graph._node[first_node]['reflux_ratio']
        light_key_compound = graph._node[first_node]['light_key_compound']
        heavy_key_compound = graph._node[first_node]['heavy_key_compound']
        Column(inlet_temperature, inlet_pressure, compoundscompoundflow, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound)
        
    if nodes[0] == 'Vessel':
    if nodes[0] == 'PFR':
    if nodes[0] == 'CSTR':
    if nodes[0] == 'Heater':
    if nodes[0] == 'Cooler':
    if nodes[0] == 'Heat exchanger, detailed':
    if nodes[0] == 'Pump':
    if nodes[0] == 'Compressor':
    if nodes[0] == 'Separator':
    
         







