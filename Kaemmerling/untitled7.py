# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 17:00:30 2023

@author: Lucky Luciano
"""
i = 0
import networkx as nx

Heater1 = nx.Graph()
Heater1.add_node('heater')
outlet_temperature = 270.0
dict1 = {'outlet_temperature':outlet_temperature}
group= {'heater':dict1}
nx.set_node_attributes(Heater1,group)
outlet_pressure = 500000.0
dict1 = {'outlet_pressure':outlet_pressure}
group= {'heater':dict1}
nx.set_node_attributes(Heater1,group)
dict2 = {}
list2 = [9.57]

compoundscompoundflow = {'Water':1.0}

key1 = list(compoundscompoundflow.keys())
h = key1[0]
dict1 = {'compounds': h}
group= {'heater':dict1}
nx.set_node_attributes(Heater1,group)


key = [1.0]
k = key[0]
dict1 = {'flow': k}
group= {'heater':dict1}
nx.set_node_attributes(Heater1,group)
#for value in list2:
 #           dict1 = {'flow': value}
  #          group= {'heater':dict1}
   #         nx.set_node_attributes(Heater1,group)
nx.write_graphml(Heater1,'./Output/graphs_graphml/clean/Heater_Graph')


#for key in list3:
 #   for value in list2:
  #      dict2[key] = value
   #     list2.remove(value)
    #    break