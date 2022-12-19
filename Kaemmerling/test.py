# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 12:46:33 2022

@author: Lucky Luciano
"""

bla = {}
for i in range(5):
    if i != 0:
        bla["variable%s" % i] = "variable%s" % i

print (bla)

import networkx as nx
graph = nx.read_graphml('C:/Users/Lucky Luciano/Documents/GitHub/Abschlussarbeiten_Behr/Kaemmerling/Output/graphs_graphml/clean/graphml_pfd3')

graph.in_edges('HE139')

myDict = {200:'OK', 404:'Not Found', 502:'Bad Gateway'}
values = ["Not Found"]
keys = [k for k, v in myDict.items() if v in values]
k = keys[0]
print(k)



