
import networkx as nx
import functions

a = 1

b = 0

Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

g = nx.read_graphml(Path_graph) #graphml einladen

# relevante nodes finden und in neuen graphen einfügen
    
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
                     
               elif  g._node[z]['node_class'] == 'Silo':
   
                     wantednodes.append(z)
                       
               elif g._node[z]['node_class'] == 'Fluid pump':    #redundante Pumpen entfernen           
            
                    size = len(z)
            
                    num = z[size-1]
            
                    if int(num) % 2 == 0:
                
                       wantednodes.append(z)

wanted_list = list(dict.fromkeys(wantednodes)) # doppelte einträge entfernen

W.add_nodes_from(wantednodes)

# verdbindungen der nodes herstellen

for w in wanted_list: 
    
    for p in wanted_list:
    
        if w != p and nx.has_path(g,w,p) == True:
        
            paths = nx.all_shortest_paths(g,w,p)
            path = tuple(paths)
        
            for m in wanted_list:

                for n in path[0]:
                
                    if m == n:
                     
                        b = b+1
                     
            if b == 2:
                
               W.add_edge(w, p, edge_class='Piping',edge_sub_class='Main pipe')
                
               b = 0
                
            else:
                
                b = 0
                
# node atrributes übertragen

for grop in wanted_list:
    group= g._node[grop]['node_group']
    group= {grop:group}
    nx.set_node_attributes(W,group,'node_group')
for grop in wanted_list:
    group= g._node[grop]['node_class']
    group= {grop:group}
    nx.set_node_attributes(W,group,'node_class')
for grop in wanted_list:
    group= g._node[grop]['node_name']
    group= {grop:group}
    nx.set_node_attributes(W,group,'node_name')
for grop in wanted_list:
    group= g._node[grop]['node_material']
    group= {grop:group}
    nx.set_node_attributes(W,group,'node_material')
for grop in wanted_list:
    group= g._node[grop]['node_operation']
    group= {grop:group}
    nx.set_node_attributes(W,group,'node_operation')
    
    
# position der nodes übertragen
    
for position in wanted_list:
    xpos= g.nodes[position]['node_x']
    ypos= g.nodes[position]['node_y']
    W._node[position]['node_x'] = xpos
    W._node[position]['node_y'] = ypos
    
# plot erzeugen
                      
nx.write_graphml(W,'./Output/graphs_graphml/clean/graphml_pfd')
functions.plot_graph2('./Output/graphs_graphml/clean/graphml_pfd', './Output/graphs_plots_clean')