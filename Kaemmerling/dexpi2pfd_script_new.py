# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 15:24:15 2022

@author: Lucky Luciano
"""

import networkx as nx
import functions
import matplotlib.pyplot as plt



Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

g = nx.read_graphml(Path_graph) #graphml einladen
    
nodes = list(g.nodes)
    
a = 0
    
for x in nodes:
           
           newlist = list(g.successors(x)) 
           
           for z in newlist:
              
               if g._node[z]['node_class'] == 'Pipe tee':  
                   
                   if (a+1) < len(nodes):
                       
                      g.add_edge(nodes[a],nodes[a+1])
                      
                      a = a+1
                 
                      g.remove_node(z)
                 
               elif g._node[z]['node_class'] == 'Valve (general)':
                     
                   if (a+1) < len(nodes):
                       
                      g.add_edge(nodes[a],nodes[a+1])
                      
                      a = a+1
                 
                      g.remove_node(z)
               
               elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                  
                    if (a+1) < len(nodes):
                        
                       g.add_edge(nodes[a],nodes[a+1])
                       
                       a = a+1
                  
                       g.remove_node(z)
                  
               elif  g._node[z]['node_class'] == 'Funnel':
               
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1])
                        
                        a = a+1
                   
                        g.remove_node(z)
                   
               elif  g._node[z]['node_class'] == 'Orifice plate':
               
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1])
                        
                        a = a+1
                   
                        g.remove_node(z)
                   
               elif  g._node[z]['node_class'] == 'Flange':
                
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1])
                        
                        a = a+1
                   
                        g.remove_node(z)
                    
               elif  g._node[z]['node_class'] == 'Safety valve, angled type':
                  
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1])
                        
                        a = a+1
                   
                        g.remove_node(z)
                      
               elif  g._node[z]['node_class'] == 'Valve, ball type':
               
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1])
                        
                        a = a+1
                   
                        g.remove_node(z)
                   
               elif  g._node[z]['node_class'] == 'Valve,globe type':
                
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1])
                        
                        a = a+1
                   
                        g.remove_node(z)
                    
               elif  g._node[z]['node_class'] == 'Steam trap':
                
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1])
                        
                        a = a+1
                   
                        g.remove_node(z)
                       
               elif g._node[z]['node_class'] == 'Fluid pump':    #redundante Pumpen entfernen           
            
                    size = len(z)
            
                    num = z[size-1]
            
                    if int(num) % 2 == 0:
                
                       g.remove_node(z)
                
       
plt.show()
    

