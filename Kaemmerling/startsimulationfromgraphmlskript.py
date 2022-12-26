import networkx as nx
import DWSIMfunctions


inlet_temperature = 293.15
inlet_pressure = 100000.0
compoundscompoundflow = {"Water" : 9.57}
graph = nx.read_graphml('C:/Users/Lucky Luciano/Documents/GitHub/Abschlussarbeiten_Behr/Kaemmerling/Output/graphs_graphml/clean/graphml_pfd3')
nodes = list(graph.nodes) # list all nodes
first_node = nodes[0]
node_class = graph._node[first_node]['node_class']
for node in nodes:



     
    if graph._node[node]['node_class'] == 'Vessel':  # start next function only if it was not run before (dict condition) and if it is in the successor li
     # set tank volume
     tank_volume = graph._node[node]['tank_volume'] 
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
     # get successors from node to find out which node is next 
     successors = graph.successors(node)
     # saves that this node is already simulated and avoids that it is simulated again
     dict1 = {'simulated_node':'TRUE'}
     group= {node:dict1}
     nx.set_node_attributes(graph,group)
     
            
    if graph._node[node]['node_class'] == 'Pump'!= nodes[0] and node in successors == True and 'simulated_node' not in graph._node[node] == True: # start next function only if it was not run before (dict condition) and if it is in the successor list
            # set pump parameter
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
            # read data from graphml
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
            # get successors from node to find out which node is next 
            successors = graph.successors(node)
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)