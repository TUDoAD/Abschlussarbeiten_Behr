# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 14:49:03 2023

@author: Lucky Luciano
"""

import networkx as nx

G = nx.path_graph(1)

labels = []

nx.set_node_attributes(G, labels, "labels")

labels.append("foo")

a = G.nodes[0]["labels"]