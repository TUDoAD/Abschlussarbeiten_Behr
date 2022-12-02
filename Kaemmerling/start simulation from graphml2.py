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


def startsimulationfromgraphml(graph):
    c = 0
    nodes = list(graph.nodes)
    first_node = nodes[0]
    inlet_temperature = graph._node[first_node]['inlet_temperature'] 
    inlet_pressure = graph._node[first_node]['inlet_pressure'] 
    composition = graph._node[first_node]['inlet_composition'] 
    mass_flow = graph._node[first_node]['inlet_mass_flow'] 
    compounds = graph._node[first_node]['compounds'] #dwsim function fehlt noch 
    inlet_stream = dict()
    for components in compounds:
        compound = compounds[c]
        compound_mass_frac = composition[c]
        compound_mass_flow = compound_mass_frac * mass_flow
        inlet_stream[compound].append(compound_mass_flow)
        c = c+1
        
    for node in nodes:
        
        if node == 'column' == nodes[0]:
            mass_flow = graph._node[first_node]['inlet_mass_flow'] 
            lk_mole_fraction_in_distillate = graph._node[first_node]['lk_mole_fraction_in_distillate'] 
            hk_mole_fraction_in_distillate = graph._node[first_node]['hk_mole_fraction_in_distillate']
            reflux_ratio = graph._node[first_node]['reflux_ratio']
            light_key_compound = graph._node[first_node]['light_key_compound']
            heavy_key_compound = graph._node[first_node]['heavy_key_compound']
            column_function.Column(inlet_temperature, inlet_pressure, inlet_stream, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound)
            before_node = 0
        if node =='column' != nodes[0]:  
            before_node = node[before_node]
            mass_flow = graph._node[node]['inlet_mass_flow'] 
            lk_mole_fraction_in_distillate = graph._node[node]['lk_mole_fraction_in_distillate'] 
            hk_mole_fraction_in_distillate = graph._node[before_node]['hk_mole_fraction_in_distillate']
            reflux_ratio = graph._node[before_node]['reflux_ratio']
            light_key_compound = graph._node[before_node]['light_key_compound']
            heavy_key_compound = graph._node[before_node]['heavy_key_compound']
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            column_function.Column(inlet_temperature, inlet_pressure, inlet_stream, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound)
            c = 0
            before_node = before_node +1
        if node == 'Vessel' == nodes[0]: 
            tank_volume = graph._node[first_node]['tank_volume'] 
            Tank_function.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = 0
                
        if node == 'Vessel' != nodes[0]:
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            tank_volume = graph._node[node]['tank_volume'] 
            Tank_function.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = before_node +1
            c = 0
            
            
            
        if node == 'PFR' == nodes[0]:
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            if 'reactor_length' in graph[node]:
                    reactor_length = graph._node[node]['reactor_length']
            else:
                    reactor_length = 0
            if 'reactor_diameter' in graph[node]:
                    reactor_diameter = graph._node[node]['reactor_diameter']
            else:
                    reactor_diameter = 0
            base_compound = graph._node[node]['base_compound']
            direct_order = graph._node[node]['direct_order']
            reverse_order = graph._node[node]['reverse_order']
            stochiometrie = graph._node[node]['stochiometrie']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            PFR_Function.PFR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometrie, reactor_diameter, reactor_length, reactor_volume, arrhenius_parameter)
            before_node = 0
            
        if node == 'PFR' != nodes[0]:

            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            if 'reactor_length' in graph[node]:
                    reactor_length = graph._node[node]['reactor_length']
            else:
                    reactor_length = 0
            if 'reactor_diameter' in graph[node]:
                    reactor_diameter = graph._node[node]['reactor_diameter']
            else:
                    reactor_diameter = 0
            base_compound = graph._node[node]['base_compound']
            direct_order = graph._node[node]['direct_order']
            reverse_order = graph._node[node]['reverse_order']
            stochiometrie = graph._node[node]['stochiometrie']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            PFR_Function.PFR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometrie, reactor_diameter, reactor_length, reactor_volume, arrhenius_parameter)            
            before_node = before_node +1
            c = 0
            
        if node == 'CSTR' == nodes[0]:
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            base_compound = graph._node[node]['base_compound']
            direct_order = graph._node[node]['direct_order']
            reverse_order = graph._node[node]['reverse_order']
            stochiometrie = graph._node[node]['stochiometrie']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            CSTR_function.CSTR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometrie,reactor_volume, arrhenius_parameter)
            before_node = 0
            
        if node == 'CSTR' != nodes[0]:
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            
            CSTR_function.CSTR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometrie,reactor_volume, arrhenius_parameter)            
            before_node = before_node +1
            c = 0
            
        if node == 'Heater' == nodes[0]:
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                deltat = 0
            Heater_function.Heater(inlet_temperature, inlet_pressure, inlet_stream, added_energy_stream, outlet_temperature, deltat)
            before_node = 0
            
        if node == 'Heater' != nodes[0]:
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                deltat = 0
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            Heater_function.Heater(inlet_temperature, inlet_pressure, inlet_stream, added_energy_stream, outlet_temperature, deltat)            
            before_node = before_node +1
            c = 0
            
        if node =='Cooler'== nodes[0]:
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'removed_energy_stream' in graph[node]:
                removed_energy_stream = graph._node[node]['removed_energy_stream']
            else:
                removed_energy_stream = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                deltat = 0
            cooler_function.Cooler(inlet_temperature, inlet_pressure, inlet_stream, removed_energy_stream, outlet_temperature, deltat)
            before_node = 0
            
        if node =='Cooler'!= nodes[0]:
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                pressure_increase = 0
            if 'removed_energy_stream' in graph[node]:
                removed_energy_stream = graph._node[node]['removed_energy_stream']
            else:
                removed_energy_stream = 0
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            cooler_function.Cooler(inlet_temperature, inlet_pressure, inlet_stream, removed_energy_stream, outlet_temperature, deltat)            
            before_node = before_node +1
            c = 0
            
        if node == 'Heat exchanger, detailed'== nodes[0]:
            composition2 = graph._node[node]['inlet_composition2']
            mass_flow2 = graph._node[node]['inlet_mass_flow2'] 
            compounds2 = graph._node[node]['compounds2'] #dwsim function fehlt noch 
            inlet_stream2 = dict()
            for components in compounds2:
                compound = compounds2[c]
                compound_mass_frac = composition2[c]
                compound_mass_flow = compound_mass_frac * mass_flow2
                inlet_stream2[compound].append(compound_mass_flow)
                c = c+1
            inlet_temperature2 = graph._node[node]['inlet_temperature2']
            inlet_pressure2 = graph._node[node]['inlet_pressure2']
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_transfer']
            heat_exchanger_function.Heat_exchanger(inlet_temperature, inlet_pressure, inlet_temperature2, inlet_pressure2, inlet_stream, inlet_stream2, heat_exchange_area, global_heat_transfer)
            before_node = 0
            
        if node == 'Heat exchanger, detailed'!= nodes[0]:
            composition2 = graph._node[node]['inlet_composition2']
            mass_flow2 = graph._node[node]['inlet_mass_flow2'] 
            compounds2 = graph._node[node]['compounds2'] #dwsim function fehlt noch 
            inlet_stream2 = dict()
            for components in compounds2:
                compound = compounds2[c]
                compound_mass_frac = composition2[c]
                compound_mass_flow = compound_mass_frac * mass_flow2
                inlet_stream2[compound].append(compound_mass_flow)
                c = c+1
            inlet_temperature2 = graph._node[node]['inlet_temperature2']
            inlet_pressure2 = graph._node[node]['inlet_pressure2']
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_tranmsfer']
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            heat_exchanger_function.Heat_exchanger(inlet_temperature, inlet_pressure, inlet_temperature2, inlet_pressure2, inlet_stream, inlet_stream2, heat_exchange_area, global_heat_transfer)                
            before_node = before_node +1
            c = 0
            
        if node == 'Pump'== nodes[0]:
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            Pump_function.Pump(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, power_required)
            before_node = 0
            
        if node == 'Pump'!= nodes[0]:
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            Pump_function.Pump(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, power_required)
            before_node = before_node +1
            c = 0
            
        if node == 'Compressor'== nodes[0]:
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            Compressor_function.Compressor(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream)
            before_node = 0
            
        if node == 'Compressor'!= nodes[0]:
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            Compressor_function.Compressor(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream)
            before_node = before_node +1
            c = 0
            
        if node == 'Separator'== nodes[0]:
            Separator_function.Separator(inlet_temperature, inlet_pressure, inlet_stream)
            before_node = 0
            
        if node == 'Separator'!= nodes[0]:
            Separator_function.Separator(inlet_temperature, inlet_pressure, inlet_stream)
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            composition = graph._node[before_node]['inlet_composition'] 
            mass_flow = graph._node[before_node]['inlet_mass_flow'] 
            compounds = graph._node[before_node]['compounds'] #dwsim function fehlt noch 
            inlet_stream = dict()
            for components in compounds:
                compound = compounds[c]
                compound_mass_frac = composition[c]
                compound_mass_flow = compound_mass_frac * mass_flow
                inlet_stream[compound].append(compound_mass_flow)
                c = c+1
            Separator_function.Separator(inlet_temperature, inlet_pressure, inlet_stream)
            before_node = before_node +1
            c = 0 
    
         







