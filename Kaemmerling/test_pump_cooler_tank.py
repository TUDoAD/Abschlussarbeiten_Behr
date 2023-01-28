# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 10:54:29 2023

@author: Lucky Luciano
"""

import networkx as nx

G = nx.DiGraph()
G.add_node('pump1')
G.add_node('pfr1')
G.add_node('tank1')
G.add_edge('pfr1','tank1')
G.add_edge('pump1','pfr1')
dict2 = {'node_class':'Tank'}
clas= {'tank1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'node_class':'PFR'}
clas= {'pfr1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'outlet_temperature':293.15}
clas= {'cooler1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'node_class':'Pump'}
clas= {'pump1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'outlet_pressure':200000.0}
clas= {'pump1':dict2}
nx.set_node_attributes(G,clas)
dict2 = {'tank_volume':100.0}
clas= {'tank1':dict2}
nx.set_node_attributes(G,clas)

nx.write_graphml(G,'./Output/graphs_graphml/clean/graphml_test_cooler')