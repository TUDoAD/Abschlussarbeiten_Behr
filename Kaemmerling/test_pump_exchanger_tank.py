# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 10:54:23 2023

@author: Lucky Luciano
"""

import networkx as nx

G = nx.DiGraph()
G.add_node('pump1')
G.add_node('tank1')
G.add_node('heat_exchanger1')
G.add_edge('pump1','heat_exchanger1')
G.add_edge('heat_exchanger1','tank1')
dict2 = {'node_class':'Heat exchanger, detailed'}
clas= {'heat_exchanger1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'heat_exchange_area':1.0}
clas= {'heat_exchanger1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'Compound':'Water'}
clas= {'heat_exchanger1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'Flow': 1.0}
clas= {'heat_exchanger1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'inlet_temperature2':300.0}
clas= {'heat_exchanger1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'inlet_pressure2':100000.0}
clas= {'heat_exchanger1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'node_class':'Tank'}
clas= {'tank1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'node_class':'Tank'}
clas= {'tank1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'node_class':'Pump'}
clas= {'pump1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'outlet_pressure':100000.0}
clas= {'pump1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'tank_volume':100.0}
clas= {'tank1':dict2}
nx.set_node_attributes(G,clas)
Compound = G._node['heat_exchanger1']['Compound']
Flow = G._node['heat_exchanger1']['Flow']
compoundscompoundflow2 = {Compound:Flow}

nx.write_graphml(G,'./Output/graphs_graphml/clean/graphml_test_exchanger')