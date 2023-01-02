import networkx as nx

f = nx.read_graphml('./Output/graphs_graphml/clean/Heater_Graph')
nodes = list(f.nodes)
a = f._node['heater']