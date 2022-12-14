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

