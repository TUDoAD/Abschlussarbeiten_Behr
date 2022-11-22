import networkx as nx
import functions
import matplotlib.pyplot as plt

def dexpi2pfd(Path_graph):

    Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

    functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

    g = nx.read_graphml(Path_graph) #graphml einladen
    
    nodes = list(g.nodes)
    
    a = 0
    b = 0
    
    for x in nodes:
        
        #node = nodes[x] 
        
        if g._node[x]['node_class'] == 'Pipe tee':
           
           newlist = list(g.successors(x))
           
           g.remove_node(x)
           
           a = a+1
           
           for z in newlist:
              
               if g._node[z]['node_class'] == 'Pipe tee':                 
                 
                  newlist = list(g.successors(z))
                 
                  g.remove_node(z)
                 
                  b = b+1
                 
               elif g._node[z]['node_class'] == 'Valve (general)':
                     
                    newlist = list(g.successors(z))
                     
                    g.remove_node(z)
                   
                    b = b+1
               
               elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                  
                    newlist = list(g.successors(z))
                  
                    g.remove_node(z)
                   
                    b = b+1
                  
               elif  g._node[z]['node_class'] == 'Funnel':
               
                     newlist = list(g.successors(z))
               
                     g.remove_node(z)
                   
                     b = b+1
                   
               elif  g._node[z]['node_class'] == 'Orifice plate':
               
                     newlist = list(g.successors(z))
               
                     g.remove_node(z)
                    
                     b = b+1
                   
               elif  g._node[z]['node_class'] == 'Flange':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
               elif  g._node[z]['node_class'] == 'Safety valve, angled type':
                  
                     newlist = list(g.successors(z))
                  
                     g.remove_node(z)
                      
                     b = b+1
                      
               elif  g._node[z]['node_class'] == 'Valve, ball type':
               
                     newlist = list(g.successors(z))
               
                     g.remove_node(z)
                   
                     b = b+1
                   
               elif  g._node[z]['node_class'] == 'Valve,globe type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
               elif  g._node[z]['node_class'] == 'Steam trap':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                  
               else:
                  
                     g.add_edge(nodes[a],nodes[b])
                  
        elif g._node[x]['node_class'] == 'Valve (general)':
            
            newlist = list(g.successors(x))
            
            g.remove_node(x)
            
            a = a+1
            
            for z in newlist:
               
               if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                  newlist = list(g.successors(z))
                  
                  g.remove_node(z)
                  
                  b = b+1
                  
               elif g._node[z]['node_class'] == 'Valve (general)':
                      
                    newlist = list(g.successors(z))
                      
                    g.remove_node(z)
                    
                    b = b+1
                
               elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                    newlist = list(g.successors(z))
                   
                    g.remove_node(z)
                    
                    b = b+1
                   
               elif g._node[z]['node_class'] == 'Funnel':
                
                    newlist = list(g.successors(z))
                
                    g.remove_node(z)
                    
                    b = b+1
                    
               elif g._node[z]['node_class'] == 'Orifice plate':
                
                    newlist = list(g.successors(z))
                
                    g.remove_node(z)
                    
                    b = b+1
                    
               elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
               elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                    newlist = list(g.successors(z))
                   
                    g.remove_node(z)
                       
                    b = b+1
                       
               elif g._node[z]['node_class'] == 'Valve, ball type':
                
                    newlist = list(g.successors(z))
                
                    g.remove_node(z)
                    
                    b = b+1
                    
               elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
               elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                   
               else:
                   
                   g.add_edge(nodes[a],nodes[b])
                   
        elif g._node[x]['node_class'] == 'Flap trap (from2)':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                 if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                  newlist = list(g.successors(z))
                  
                  g.remove_node(z)
                  
                  b = b+1
                  
                 elif g._node[z]['node_class'] == 'Valve (general)':
                      
                      newlist = list(g.successors(z))
                      
                      g.remove_node(z)
                    
                      b = b+1
                
                 elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                      newlist = list(g.successors(z))
                   
                      g.remove_node(z)
                    
                      b = b+1
                   
                 elif g._node[z]['node_class'] == 'Funnel':
                
                      newlist = list(g.successors(z))
                
                      g.remove_node(z)
                    
                      b = b+1
                    
                 elif g._node[z]['node_class'] == 'Orifice plate':
                
                      newlist = list(g.successors(z))
                
                      g.remove_node(z)
                    
                      b = b+1
                    
                 elif g._node[z]['node_class'] == 'Flange':
                 
                      newlist = list(g.successors(z))
                 
                      g.remove_node(z)
                     
                      b = b+1
                     
                 elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                      newlist = list(g.successors(z))
                   
                      g.remove_node(z)
                       
                      b = b+1
                       
                 elif g._node[z]['node_class'] == 'Valve, ball type':
                
                      newlist = list(g.successors(z))
                
                      g.remove_node(z)
                    
                      b = b+1
                    
                 elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                      newlist = list(g.successors(z))
                 
                      g.remove_node(z)
                     
                      b = b+1
                     
                 elif g._node[z]['node_class'] == 'Steam trap':
                 
                      newlist = list(g.successors(z))
                 
                      g.remove_node(z)
                     
                      b = b+1
                   
                 else:
                   
                      g.add_edge(nodes[a],nodes[b])
                      
        elif g._node[x]['node_class'] == 'Funnel':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                   newlist = list(g.successors(z))
                  
                   g.remove_node(z)
                 
                   b = b+1
                  
                elif g._node[z]['node_class'] == 'Valve (general)':
                      
                     newlist = list(g.successors(z))
                      
                     g.remove_node(z)
                    
                     b = b+1
                
                elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                    
                     b = b+1
                   
                elif g._node[z]['node_class'] == 'Funnel':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Orifice plate':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                       
                     b = b+1
                       
                elif g._node[z]['node_class'] == 'Valve, ball type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                   
                else:
                   
                     g.add_edge(nodes[a],nodes[b])
                     
        elif g._node[x]['node_class'] == 'Orifice plate':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                   newlist = list(g.successors(z))
                  
                   g.remove_node(z)
                  
                   b = b+1
                  
                elif g._node[z]['node_class'] == 'Valve (general)':
                      
                     newlist = list(g.successors(z))
                      
                     g.remove_node(z)
                    
                     b = b+1
                
                elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                    
                     b = b+1
                   
                elif g._node[z]['node_class'] == 'Funnel':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Orifice plate':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                       
                     b = b+1
                       
                elif g._node[z]['node_class'] == 'Valve, ball type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                   
                else:
                   
                     g.add_edge(nodes[a],nodes[b])  
                     
        elif g._node[x]['node_class'] == 'Flange':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                   newlist = list(g.successors(z))
                  
                   g.remove_node(z)
                  
                   b = b+1
                  
                elif g._node[z]['node_class'] == 'Valve (general)':
                      
                     newlist = list(g.successors(z))
                      
                     g.remove_node(z)
                    
                     b = b+1
                
                elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                    
                     b = b+1
                   
                elif g._node[z]['node_class'] == 'Funnel':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Orifice plate':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(nodes[z])
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                     newlist = list(g.successors(nodes[z]))
                   
                     g.remove_node(z)
                       
                     b = b+1
                       
                elif g._node[z]['node_class'] == 'Valve, ball type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                else:
                   
                     g.add_edge(nodes[a],nodes[b])
                     
        elif g._node[x]['node_class'] == 'Safety valve, angled type':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                   newlist = list(g.successors(z))
                  
                   g.remove_node(z)
                  
                   b = b+1
                  
                elif g._node[z]['node_class'] == 'Valve (general)':
                      
                     newlist = list(g.successors(z))
                      
                     g.remove_node(z)
                    
                     b = b+1
                
                elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                    
                     b = b+1
                   
                elif g._node[z]['node_class'] == 'Funnel':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Orifice plate':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                       
                     b = b+1
                       
                elif g._node[z]['node_class'] == 'Valve, ball type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(nodes[z])
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(nodes[z]))
                 
                     g.remove_node(z)
                     
                     b = b+1
                   
                else:
                   
                     g.add_edge(nodes[a],nodes[b])
                   
        elif g._node[x]['node_class'] == 'Valve, ball type':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                   newlist = list(g.successors(z))
                  
                   g.remove_node(z)
                  
                   b = b+1
                  
                elif g._node[z]['node_class'] == 'Valve (general)':
                      
                     newlist = list(g.successors(z))
                      
                     g.remove_node(z)
                    
                     b = b+1
                
                elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                    
                     b = b+1
                   
                elif g._node[z]['node_class'] == 'Funnel':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Orifice plate':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                       
                     b = b+1
                       
                elif g._node[z]['node_class'] == 'Valve, ball type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Valve, globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                else:
                        
                     g.add_edge(nodes[a],nodes[b])
                             
        elif g._node[x]['node_class'] == 'Valve, globe type':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                   newlist = list(g.successors(z))
                  
                   g.remove_node(z)
                  
                   b = b+1
                  
                elif g._node[z]['node_class'] == 'Valve (general)':
                      
                     newlist = list(g.successors(z))
                      
                     g.remove_node(z)
                    
                     b = b+1
                
                elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                    
                     b = b+1
                   
                elif g._node[z]['node_class'] == 'Funnel':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Orifice plate':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                       
                     b = b+1
                       
                elif g._node[z]['node_class'] == 'Valve, ball type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                else:
                   
                     g.add_edge(nodes[a],nodes[b])

        elif g._node[x]['node_class'] == 'Steam trap':
            
             newlist = list(g.successors(x))
            
             g.remove_node(x)
            
             a = a+1
            
             for z in newlist:
               
                if g._node[z]['node_class'] == 'Pipe tee':                 
                  
                   newlist = list(g.successors(z))
                  
                   g.remove_node(z)
                  
                   b = b+1
                  
                elif g._node[z]['node_class'] == 'Valve (general)':
                      
                     newlist = list(g.successors(z))
                      
                     g.remove_node(z)
                    
                     b = b+1
                
                elif g._node[z]['node_class'] == 'Flap trap (from 2)':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                    
                     b = b+1
                   
                elif g._node[z]['node_class'] == 'Funnel':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Orifice plate':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Flange':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Safety valve, angled type':
                   
                     newlist = list(g.successors(z))
                   
                     g.remove_node(z)
                       
                     b = b+1
                       
                elif g._node[z]['node_class'] == 'Valve, ball type':
                
                     newlist = list(g.successors(z))
                
                     g.remove_node(z)
                    
                     b = b+1
                    
                elif g._node[z]['node_class'] == 'Valve,globe type':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                elif g._node[z]['node_class'] == 'Steam trap':
                 
                     newlist = list(g.successors(z))
                 
                     g.remove_node(z)
                     
                     b = b+1
                     
                else:
                   
                     g.add_edge(nodes[x],nodes[z])
       
        elif g._node[x]['node_class'] == 'Fluid pump':    #redundante Pumpen entfernen
            
             node = nodes[a]           
            
             size = len(node)
            
             num = node[size-1]
            
             if int(num) % 2 == 0:
                
                g.remove_node(x)
                
                b = b+1
                
             else:
                 
                  b = b+1
            
                  continue
           
        else:
            
             a = a+1
            
             continue
       
    plt.show()
    

dexpi2pfd('./Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml')
           
    
   
        
            
    
           
         

    




