
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

nodes = list(f.nodes) # list all nodes from graph

# search string in dictionary 

for node in nodes:
    attribute_dict = nx.get_node_attributes(f, node)
    if  f.nodes[node]['node_group'] == 'Vessel':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('Vessel got inlet temperature')
        else: print('No Vessel inlet temperatue')
        
        if    'inlet_pressure' in attribute_dict:
              print ('Vessel got inlet pressure')
        else: print('No Vessel inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('Vessel got inlet mass flow')
        else: print('No Vessel inlet temperatue')
        
        if    'tank_volume' in attribute_dict:
              print() 
        else:  print('Need Tank volume')
        
    if  f.nodes[node]['node_group'] == 'Fluid pump':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('Pump got inlet temperature')
        else: print('No Pump inlet temperatue')
        
        if    'inlet_pressure' in attribute_dict:
              print ('Pump got inlet pressure')
        else: print('No Pump inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('Pump got inlet mass flow')
        else: print('No Pump inlet temperatue')
        
        if    'pressure_increase' in attribute_dict or 'energy_stream' in attribute_dict or 'outlet_pressure' in attribute_dict or 'power_required' in attribute_dict:
              print() 
        else:  print('Need further information about the Pump')
        
    if  f.nodes[node]['node_group'] == 'Heat exchanger, detailed':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('Heater got inlet temperature')
        else: print('No Heater inlet temperatue')
        
        if    'inlet_pressure' in attribute_dict:
              print ('Heater got inlet pressure')
        else: print('No Heater inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('Heater got inlet mass flow')
        else: print('No Heater inlet temperatue')
        
        if    'temperature_difference' in attribute_dict or 'heat_added' in attribute_dict or 'outlet_temperature' in attribute_dict or 'heat_removed' in attribute_dict:
              print() 
        else:  print('Need further information about the Heater')
        
    if  f.nodes[node]['node_group'] == 'Heat exchanger':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('Heater got inlet temperature')
        else: print('No Heater inlet temperatue')
        
        if    'inlet_pressure' in attribute_dict:
              print ('Heater got inlet pressure')
        else: print('No Heater inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('Heater got inlet mass flow')
        else: print('No Heater inlet temperatue')
        
        if    'temperature_difference' in attribute_dict or 'heat_added' in attribute_dict or 'outlet_temperature' in attribute_dict or 'heat_removed' in attribute_dict:
              print() 
        else:  print('Need further information about the Heater')
        
    if  f.nodes[node]['node_group'] == 'Compressor':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('Compressor got inlet temperature')
        else: print('No Compressor inlet temperatue')
        
        if    'inlet_pressure' in attribute_dict:
              print ('Compressor got inlet pressure')
        else: print('No Compressor inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('Compressor got inlet mass flow')
        else: print('No Compressor inlet temperatue')
        
        if    'power_required' in attribute_dict or 'energy_stream' in attribute_dict or 'outlet_pressure' in attribute_dict or 'pressure_increase' in attribute_dict:
              print() 
        else:  print('Need further information about the Compressor')
        
    if  f.nodes[node]['node_group'] == 'Separator':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('Separator got inlet temperature')
        else: print('No Separator inlet temperatue')
        
        if    'inlet_pressure' in attribute_dict:
              print ('Separator got inlet pressure')
        else: print('No Separator inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('Separator got inlet mass flow')
        else: print('No Separator inlet temperatue')
        
        if    'inlet_minimum' in attribute_dict or 'inlet_maximum' in attribute_dict or 'inlet_average' in attribute_dict:
              print() 
        else: print('Need further information about the Compressor')
        
    if  f.nodes[node]['node_group'] == 'CSTR':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('CSTR got inlet temperature')
        else: print('No CSTR inlet temperatue')
        
        if    'inlet_mass_frac' in attribute_dict:
              print ('CSTR got inlet mass frac')
        else: print('No CSTR inlet mass frac')
        
        if    'inlet_pressure' in attribute_dict:
              print ('CSTR got inlet pressure')
        else: print('No CSTR inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('CSTR got inlet mass flow')
        else: print('No CSTR inlet temperatue')
        
        if    'reaction_parameter' in attribute_dict:
              print ()
        else: print('No reaction parameters')
        
        if    'reactor_volume' in attribute_dict:
              print ('CSTR got reactor volume')
        else: print('No CSTR reactor volume')
        
        if    'inlet_minimum' in attribute_dict or 'inlet_maximum' in attribute_dict or 'inlet_average' in attribute_dict:
              print() 
        else: print('Need further information about the CSTR')
        
        if    'arrhenius_parameter' in attribute_dict or 'user_defined_function' in attribute_dict:
              print() 
        else: print('Need further information about the CSTR')
        
        if    'temperature_managment' in attribute_dict:
              print() 
        else: print('Need further information about temperature managment in the CSTR')

    if  f.nodes[node]['node_group'] == 'PFR':  
        
        if    'inlet_temperature' in attribute_dict:
              print ('PFR got inlet temperature')
        else: print('No PFR inlet temperatue')
        
        if    'inlet_mass_frac' in attribute_dict:
              print ('PFR got inlet mass frac')
        else: print('No PFR inlet mass frac')
        
        if    'inlet_pressure' in attribute_dict:
              print ('CSTR got inlet pressure')
        else: print('No CSTR inlet pressure')
        
        if    'inlet_mass_flow' in attribute_dict:
              print ('PFR got inlet mass flow')
        else: print('No PFR inlet temperatue')
        
        if    'reaction_parameter' in attribute_dict:
              print ()
        else: print('No reaction parameters')
        
        if    'reactor_volume' in attribute_dict:
              print ('PFR got reactor volume')
        else: print('No PFR reactor volume')
        
        if    'inlet_minimum' in attribute_dict or 'inlet_maximum' in attribute_dict or 'inlet_average' in attribute_dict:
              print() 
        else: print('Need further information about the PFR')
        
        if    'arrhenius_parameter' in attribute_dict or 'user_defined_function' in attribute_dict:
              print() 
        else: print('Need further information about the PFR')
        
        if    'temperature_managment' in attribute_dict:
              print() 
        else: print('Need further information about temperature managment in the PFR')
        
        
        
        