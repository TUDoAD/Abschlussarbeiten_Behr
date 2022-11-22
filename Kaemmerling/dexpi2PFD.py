import networkx as nx
import functions

def dexpi2pfd(Path_graph):

    Path_graph = './Output/graphs_graphml/noPCE/DEXPI_Distillation_noMSR.xml'

    functions.plot_graph2(Path_graph, './Output/graphs_plots') #plot function

    g = nx.read_graphml(Path_graph) #graphml einladen
    
    nodes = g.nodes()

    




