# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 16:44:54 2022

@author: Lucky Luciano
"""
 
import networkx as nx
import functions
import sys

a = 0

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
    dict1 = {'node_group':g._node[grop]['node_group']}
    group= {grop:dict1}
    nx.set_node_attributes(W,group,'node_group')
    
# position der nodes übertragen
    
for position in wanted_list:
    xpos= g.nodes[position]['node_x']
    ypos= g.nodes[position]['node_y']
    W._node[position]['node_x'] = xpos
    W._node[position]['node_y'] = ypos
    
Path_graph = './Output/graphs_graphml/clean/graphml_pfd'

functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

f = nx.read_graphml(Path_graph) #graphml einladen

for grop in wanted_list:
    dict1 = {'node_group':g._node[grop]['node_group']}
    group= {grop:dict1}
    nx.set_node_attributes(f,group)
    dict2 = {'node_class':g._node[grop]['node_class']}
    clas= {grop:dict2}
    nx.set_node_attributes(f,clas)

nodes = list(f.nodes)

for node in nodes:
    attribute_dict = nx.get_node_attributes(f, node)
    if  node == nodes[0]:
                
        if    'inlet_temperature' in attribute_dict:
              print ()
        else: 
              print('No inlet temperatue')
              a = a+1
             
        if    'inlet_pressure' in attribute_dict:
              print ()
        else:
              print('No inlet pressure')
              a = a+1
        
        if    'inlet_mass_flow' in attribute_dict:
              print ()
        else: 
              print('No inlet mass flow')
              a = a+1
              
        if    'inlet_composition' in attribute_dict:
              print ()
        else: 
              print('No inlet composition')
              a = a+1
        
    if  f.nodes[node]['node_class'] == 'Vessel':  
        
        if    'tank_volume' in attribute_dict:
              print() 
        else: 
              print('Need Tank volume')
              a = a+1
        
    if  f.nodes[node]['node_class'] == 'Fluid pump':  
        
        if    'pressure_increase' in attribute_dict or 'energy_stream' in attribute_dict or 'outlet_pressure' in attribute_dict or 'power_required' in attribute_dict:
               print() 
        else:  
               print('Need further information about the Pump')
               a = a+1
        
    if  f.nodes[node]['node_class'] == 'Heat exchanger, detailed':  
        
        if    'temperature_difference' in attribute_dict or 'heat_added' in attribute_dict or 'outlet_temperature' in attribute_dict or 'heat_removed' in attribute_dict:
               print() 
        else:  
               print('Need further information about the Heater')
               a = a+1
        
    if  f.nodes[node]['node_class'] == 'Heat exchanger':  
        
        if    'temperature_difference' in attribute_dict or 'heat_added' in attribute_dict or 'outlet_temperature' in attribute_dict or 'heat_removed' in attribute_dict:
              print() 
        else:  
              print('Need further information about the Heater')
              a = a+1
        
    if  f.nodes[node]['node_class'] == 'Compressor':  
        
        if    'power_required' in attribute_dict or 'energy_stream' in attribute_dict or 'outlet_pressure' in attribute_dict or 'pressure_increase' in attribute_dict:
              print() 
        else:  
              print('Need further information about the Compressor')
              a = a+1
        
    if  f.nodes[node]['node_class'] == 'Separator':  
        
        if    'inlet_minimum' in attribute_dict or 'inlet_maximum' in attribute_dict or 'inlet_average' in attribute_dict:
              print() 
        else: 
              print('Need further information about the Compressor')
              a = a+1
        
    if  f.nodes[node]['node_class'] == 'CSTR':  
        
        if    'reaction_parameter' in attribute_dict:
              print ()
        else: 
              print('No reaction parameters')
              a = a+1
        
        if    'reactor_volume' in attribute_dict:
              print ()
        else: 
              print('No CSTR reactor volume')
              a = a+1
        
        if    'arrhenius_parameter' in attribute_dict or 'user_defined_function' in attribute_dict:
              print() 
        else: 
              print('Need further information about the CSTR')
              a = a+1
        
        if    'temperature_managment' in attribute_dict:
              print() 
        else: 
              print('Need further information about temperature managment in the CSTR')
              a = a+1

    if  f.nodes[node]['node_class'] == 'PFR':  
        
        if    'reaction_parameter' in attribute_dict:
              print ()
        else: 
              print('No reaction parameters')
              a = a+1
        
        if    'reactor_volume' in attribute_dict:
              print ()
        else: 
              print('No PFR reactor volume')
              a = a+1
        
        if    'inlet_minimum' in attribute_dict or 'inlet_maximum' in attribute_dict or 'inlet_average' in attribute_dict:
              print() 
        else: 
              print('Need further information about the PFR')
              a = a+1
        
        if    'arrhenius_parameter' in attribute_dict or 'user_defined_function' in attribute_dict:
              print() 
        else:
              print('Need further information about the PFR')
              a = a+1
        
        if    'temperature_managment' in attribute_dict:
              print() 
        else: 
              print('Need further information about temperature managment in the PFR')
              a = a+1
if a==0:
        
        print('Programm is ready for simulation')
        
else:
    
        print('ERROR: input parameters are missing')
              
              
              
              
              
              