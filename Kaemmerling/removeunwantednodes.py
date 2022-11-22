
import networkx as nx
import functions
import matplotlib.pyplot as plt



Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

g = nx.read_graphml(Path_graph) #graphml einladen
    
nodes = list(g.nodes)
    
a = 0

unwantednodes = []
    
for x in nodes:
           
           newlist = list(g.successors(x)) 
           
           for z in newlist:
              
               if g._node[z]['node_class'] == 'Pipe tee':  
                   
                   if (a+1) < len(nodes):
                       
                      g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                      
                      a = a+1
                 
                      unwantednodes.append(z)
                 
               elif g._node[z]['node_class'] == 'Valve (general)':
                     
                   if (a+1) < len(nodes):
                       
                      g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                      
                      a = a+1
                 
                      unwantednodes.append(z)
               
               elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                  
                    if (a+1) < len(nodes):
                        
                       g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                       
                       a = a+1
                  
                       unwantednodes.append(z)
                  
               elif  g._node[z]['node_class'] == 'Funnel':
               
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                        
                        a = a+1
                   
                        unwantednodes.append(z)
                   
               elif  g._node[z]['node_class'] == 'Orifice plate':
               
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                        
                        a = a+1
                   
                        unwantednodes.append(z)
                   
               elif  g._node[z]['node_class'] == 'Flange':
                
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                        
                        a = a+1
                   
                        unwantednodes.append(z)
                    
               elif  g._node[z]['node_class'] == 'Safety valve, angled type':
                  
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                        
                        a = a+1
                   
                        unwantednodes.append(z)
                      
               elif  g._node[z]['node_class'] == 'Valve, ball type':
               
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                        
                        a = a+1
                   
                        unwantednodes.append(z)
                   
               elif  g._node[z]['node_class'] == 'Valve,globe type':
                
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                        
                        a = a+1
                   
                        unwantednodes.append(z)
                    
               elif  g._node[z]['node_class'] == 'Steam trap':
                
                     if (a+1) < len(nodes):
                         
                        g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
                        
                        a = a+1
                   
                        unwantednodes.append(z)
                        
               elif g._node[z]['node_class'] == 'Pipe tee ':  
            
                    if (a+1) < len(nodes):
                
                       g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
               
                       a = a+1
          
                       unwantednodes.append(z)
                       
               elif g._node[z]['node_class'] == 'Fluid pump':    #redundante Pumpen entfernen           
            
                    size = len(z)
            
                    num = z[size-1]
                    
                    g.add_edge(nodes[a],nodes[a+1], edge_class='Piping',edge_sub_class='Main pipe')
            
                    if int(num) % 2 != 0:
                
                       unwantednodes.append(z)

unwanted_list = list(dict.fromkeys(unwantednodes))

for t in unwanted_list:
    
    g.remove_node(t)
                
       
nx.write_graphml(g,'./Output/graphs_graphml/clean/graphml_pfd')
functions.plot_graph2('./Output/graphs_graphml/clean/graphml_pfd', './Output/graphs_plots_clean')