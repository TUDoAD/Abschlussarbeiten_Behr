
import networkx as nx
import DWSIMfunctions

def startsimulationfromgraphml(graph, inlet_temperature,inlet_pressure, compoundscompoundflow):
    
    
    nodes = list(graph.nodes)
    first_node = nodes[0] 
    #add compounds    

        
    for node in nodes:
        
        if node == 'column' == nodes[0]:
            lk_mole_fraction_in_distillate = graph._node[first_node]['lk_mole_fraction_in_distillate'] 
            hk_mole_fraction_in_distillate = graph._node[first_node]['hk_mole_fraction_in_distillate']
            reflux_ratio = graph._node[first_node]['reflux_ratio']
            light_key_compound = graph._node[first_node]['light_key_compound']
            heavy_key_compound = graph._node[first_node]['heavy_key_compound']
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Column(inlet_temperature, inlet_pressure, inlet_stream, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_temperature2 = DWSIMfunctions.m3.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            outlet_pressure2 = DWSIMfunctions.m3.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            before_node = node
            successors = graph.successors(node)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict2 = []
            list2 = list(DWSIMfunctions.m3.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow2': dict2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node =='column' != nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
            lk_mole_fraction_in_distillate = graph._node[node]['lk_mole_fraction_in_distillate'] 
            hk_mole_fraction_in_distillate = graph._node[node]['hk_mole_fraction_in_distillate']
            reflux_ratio = graph._node[node]['reflux_ratio']
            light_key_compound = graph._node[node]['light_key_compound']
            heavy_key_compound = graph._node[node]['heavy_key_compound']
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure']
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.Column(inlet_temperature, inlet_pressure, inlet_stream, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_temperature2 = DWSIMfunctions.m3.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            outlet_pressure2 = DWSIMfunctions.m3.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Vessel' == nodes[0]: 
            tank_volume = graph._node[first_node]['tank_volume'] 
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Vessel' != nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            inlet_stream = dict()
            tank_volume = graph._node[node]['tank_volume'] 
            DWSIMfunctions.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Tank' == nodes[0]: 
            tank_volume = graph._node[first_node]['tank_volume'] 
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Tank' != nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            inlet_stream = dict()
            tank_volume = graph._node[node]['tank_volume'] 
            DWSIMfunctions.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Silo' == nodes[0]: 
            tank_volume = graph._node[first_node]['tank_volume'] 
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Silo' != nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            inlet_stream = dict()
            tank_volume = graph._node[node]['tank_volume'] 
            DWSIMfunctions.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
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
            stochiometry = graph._node[node]['stochiometry']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.PFR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry, reactor_diameter, reactor_length, reactor_volume, arrhenius_parameter)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'PFR' != nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  

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
            stochiometry = graph._node[node]['stochiometry']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            inlet_temperature = graph._node[before_node]['inlet_temperature'] 
            inlet_pressure = graph._node[before_node]['inlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.PFR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry, reactor_diameter, reactor_length, reactor_volume, arrhenius_parameter)            
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
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
            stochiometry = graph._node[node]['stochiometry']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.CSTR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry,reactor_volume, arrhenius_parameter)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'CSTR' != nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
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
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.CSTR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry,reactor_volume, arrhenius_parameter)            
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
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
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Heater(inlet_temperature, inlet_pressure, inlet_stream, added_energy_stream, outlet_temperature, deltat)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Heater' != nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
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
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.Heater(inlet_temperature, inlet_pressure, inlet_stream, added_energy_stream, outlet_temperature, deltat)            
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
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
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Cooler(inlet_temperature, inlet_pressure, inlet_stream, removed_energy_stream, outlet_temperature, deltat)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node =='Cooler'!= nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
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
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.Cooler(inlet_temperature, inlet_pressure, inlet_stream, removed_energy_stream, outlet_temperature, deltat)            
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Heat exchanger, detailed'== nodes[0]:
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_transfer'] 
            inlet_stream = compoundscompoundflow
            inlet_stream2 = graph._node[node]['compoundscompoundflow2']
            inlet_temperature2 = graph._node[node]['inlet_temperature2']
            inlet_pressure2 = graph._node[node]['inlet_pressure2']
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_transfer']
            DWSIMfunctions.Heat_exchanger(inlet_temperature, inlet_pressure, inlet_temperature2, inlet_pressure2, inlet_stream, inlet_stream2, heat_exchange_area, global_heat_transfer)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Heat exchanger, detailed'!= nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
            inlet_stream2 = graph._node[node]['compoundscompoundflow2']
            inlet_temperature2 = graph._node[node]['inlet_temperature2']
            inlet_pressure2 = graph._node[node]['inlet_pressure2']
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_tranmsfer']
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.Heat_exchanger(inlet_temperature, inlet_pressure, inlet_temperature2, inlet_pressure2, inlet_stream, inlet_stream2, heat_exchange_area, global_heat_transfer)                
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
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
            inlet_stream2 = graph._node[node]['compoundscompoundflow2']
            DWSIMfunctions.Pump(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, power_required)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Pump'!= nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
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
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.Pump(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, power_required)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
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
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Compressor(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream)
            before_node = node
            inlet_temperature = DWSIMfunctions.m2.GetTemperature()
            inlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            compoundscompoundflow = dict2
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Compressor'!= nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
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
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.Compressor(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Separator'== nodes[0]:
            inlet_stream = compoundscompoundflow
            DWSIMfunctions.Separator(inlet_temperature, inlet_pressure, inlet_stream)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict2 = []
            list2 = list(DWSIMfunctions.m3.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow2': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_temperature2 = DWSIMfunctions.m3.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            outlet_pressure2 = DWSIMfunctions.m3.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if node == 'Separator'!= nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True:  
            DWSIMfunctions.Separator(inlet_temperature, inlet_pressure, inlet_stream)
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            inlet_stream = graph._node[before_node]['compoundscompoundflow']
            DWSIMfunctions.Separator(inlet_temperature, inlet_pressure, inlet_stream)
            before_node = node
            dict2 = []
            list2 = list(DWSIMfunctions.m2.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow': dict2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict2 = []
            list2 = list(DWSIMfunctions.m3.Get_OverallComposition)
            for key in compoundscompoundflow:
                for value in list2:
                    dict2.append(key, value)
            dict1 = {'compoundscompoundflow2': dict2}
            group= {node:dict1}
            compoundscompoundflow = dict2
            nx.set_node_attributes(graph,group)
            outlet_temperature = DWSIMfunctions.m2.GetTemperature()
            outlet_temperature2 = DWSIMfunctions.m3.GetTemperature()
            outlet_pressure = DWSIMfunctions.m2.GetPressure()
            outlet_pressure2 = DWSIMfunctions.m3.GetPressure()
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
graph = nx.read_graphml('C:/Users/Lucky Luciano/Documents/GitHub/Abschlussarbeiten_Behr/Kaemmerling/Output/graphs_graphml/clean/graphml_pfd3')
startsimulationfromgraphml(graph, 298.15, 100000, {"Water" : 0.5,'Ethanol' : 0.5})
    
         







