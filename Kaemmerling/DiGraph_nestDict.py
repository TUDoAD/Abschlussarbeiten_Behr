import networkx as nxg=nx.DiGraph()g.add_nodes_from(['A','B','C'])g.add_edges_from([('A','B'),('A','C')])nx.draw(g, with_labels=True)data = {'Ethanol': {'wt-%': 20.5,                    'vapor_fraction': 30},        'Methanol': {'wt-%': 79.5,                            'vapor_fraction': 60}        }g._node['A']['process_data']=dataprint(g.in_edges('A'))print(g.out_edges('A'))nx.write_graphml(g,'./Output/graphs_graphml/clean/nested_dicts')