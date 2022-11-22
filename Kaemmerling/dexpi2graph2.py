# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 14:11:39 2022

@author: Lucky Luciano
"""

import networkx as nx
import functions
import matplotlib.pyplot as plt



def dexpi2pfd(Path_graph):

    Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

    functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

    g = nx.read_graphml(Path_graph) #graphml einladen
    
    g_block = g.copy()
    
    nodes = list (g_block.nodes)
    
    node_ID_block=nx.get_node_attributes(g_block, 'node_ID')
    node_group_block=nx.get_node_attributes(g_block, 'node_group')
    

            
            
            
            
            
    
    