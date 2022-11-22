
import networkx as nx
import functions
import matplotlib.pyplot as plt

a = 1

Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

g = nx.read_graphml(Path_graph) #graphml einladen
    
nodes = list(g.nodes)

wantednodes = []

W = nx.DiGraph()
    
for x in nodes:
           
           newlist = list(g.successors(x)) 
           
           for z in newlist:            
                 
               if  g._node[z]['node_class'] == 'Column':
                             
                     wantednodes.append(z)
               
               elif  g._node[z]['node_class'] == 'Heat exchanger, detailed':
                  
                     wantednodes.append(z)
                  
               elif  g._node[z]['node_class'] == 'Vessel':
               
                     wantednodes.append(z)
                       
               elif g._node[z]['node_class'] == 'Fluid pump':    #redundante Pumpen entfernen           
            
                    size = len(z)
            
                    num = z[size-1]
            
                    if int(num) % 2 == 0:
                
                       wantednodes.append(z)

wanted_list = list(dict.fromkeys(wantednodes))

W.add_nodes_from(wantednodes)

for w in wanted_list: 
    
    if a < len(wanted_list):
    
           paths = nx.shortest_simple_paths(g, w, wanted_list[a])
           
           path = tuple(paths)
           
           for y in path:
               
               index = path.index(y)
           
               if index < len(path) and W._node[y]['node_class'] == 'Fluid pump': 
               
                   continue
           
               elif  index < len(path) and W._node[y]['node_class'] == 'Vessel':
               
                   continue
           
               elif  index < len(path) and W._node[y]['node_class'] == 'Heat exchanger, detailed':
               
                   continue
           
               elif  index < len(path) and W._node[y]['node_class'] == 'Column':
                
                   continue
            
               else:
           
                   W.add_edge(wanted_list[a-1], wanted_list[a], edge_class='Piping',edge_sub_class='Main pipe')
    
                   a = a+1
    else:  
    
        break
                
       
nx.write_graphml(g,'./Output/graphs_graphml/clean/graphml_pfd')
functions.plot_graph2('./Output/graphs_graphml/clean/graphml_pfd', './Output/graphs_plots_clean')