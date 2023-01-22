import networkx as nx
f = nx.read_graphml('./Output/graphs_graphml/clean/graphml_pfd')
nodes = list(f.nodes)
for unitoperation in nodes:
    if  f._node[unitoperation]['node_class'] == 'Column':
            dict1 = {'light_key_compound':'Ethanol'}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'heavy_key_compound':'Water'}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'lk_mole_fraction_in_distillate':0.01}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'hk_mole_fraction_in_distillate':0.01}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'reflux_ratio':1.4}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
             
    if  f._node[unitoperation]['node_class'] == 'Vessel':
            dict1 = {'tank_volume':'100.0'}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
         
    if  f._node[unitoperation]['node_class'] == 'Silo':
            dict1 = {'tank_volume':'100.0'}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            
    if  f._node[unitoperation]['node_class'] == 'Pump':
            dict1 = {'outlet_temperature':100.0}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
        
    if  f._node[unitoperation]['node_class'] == 'Fluid pump':
            dict1 = {'outlet_pressure':100.0}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            
    if  f._node[unitoperation]['node_class'] == 'Heat exchanger, detailed':
            dict1 = {'outlet_pressure':100000.0}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'Compound':'Water'}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'Flow':1.0}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'inlet_temperature2':300.0}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'inlet_pressure2':100000.0}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
            dict1 = {'heat_exchange_area':1.0}
            group= {unitoperation:dict1}
            nx.set_node_attributes(f,group)
nx.write_graphml(f,'./Output/graphs_graphml/clean/graphml_pfd_filled')

