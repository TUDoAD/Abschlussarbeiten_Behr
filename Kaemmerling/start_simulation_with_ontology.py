import networkx as nx
import DWSIMOntology 
import os
from System.IO import Directory
from owlready2 import *
import json
onto_world = owlready2.World()
onto = onto_world.get_ontology("./rdf-new.owl").load()

def startsimulationfromgraphml(graph, inlet_temperature,inlet_pressure, compoundscompoundflow):
    Laufvar = 1
    work_dir = os.getcwd()
    nodes = list(graph.nodes) # list all nodes
    first_node = nodes[0] 
    node_class = graph._node[first_node]['node_class']

    for node in nodes:
        
        if graph._node[node]['node_class'] == 'Column' == node_class:
            # set column parameter
            lk_mole_fraction_in_distillate = graph._node[first_node]['lk_mole_fraction_in_distillate'] 
            hk_mole_fraction_in_distillate = graph._node[first_node]['hk_mole_fraction_in_distillate']
            reflux_ratio = graph._node[first_node]['reflux_ratio']
            light_key_compound = graph._node[first_node]['light_key_compound']
            heavy_key_compound = graph._node[first_node]['heavy_key_compound']
            inlet_stream = compoundscompoundflow
            # start DWSIM simulation
            Laufvar = Laufvar +1
            DWSIMOntology.Column(inlet_temperature, inlet_pressure, inlet_stream, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound, Laufvar)
            # set node as last node
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            # get data from simulation and save it in graphml
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_temperature2 = UnitOperation._node['unitoperation']['outlet_temperature2']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            outlet_pressure2 = UnitOperation._node['unitoperation']['outlet_pressure2']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] =='Column' != node_class and node in successors and 'simulated_node' not in graph._node[node]:  # start next function only if it was not run before (dict condition) and if it is in the successor list
            # set column parameter 
            lk_mole_fraction_in_distillate = graph._node[node]['lk_mole_fraction_in_distillate'] 
            hk_mole_fraction_in_distillate = graph._node[node]['hk_mole_fraction_in_distillate']
            reflux_ratio = graph._node[node]['reflux_ratio']
            light_key_compound = graph._node[node]['light_key_compound']
            heavy_key_compound = graph._node[node]['heavy_key_compound']
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure']
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            # start DWSIM simulation
            Laufvar = Laufvar +1
            DWSIMOntology.Column1(inlet_temperature, inlet_pressure, inlet_stream, lk_mole_fraction_in_distillate, hk_mole_fraction_in_distillate, reflux_ratio, light_key_compound, heavy_key_compound, Laufvar)
            # set node as last node
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            # get data from simulation and save it in graphml
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_temperature2 = UnitOperation._node['unitoperation']['outlet_temperature2']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            outlet_pressure2 = UnitOperation._node['unitoperation']['outlet_pressure2']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Vessel' == node_class: 
            # set tank volume
            tank_volume = graph._node[first_node]['tank_volume'] 
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)

            
        if graph._node[node]['node_class'] == 'Vessel' != node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            # set tank volume
            tank_volume = graph._node[node]['tank_volume'] 
            Laufvar = Laufvar +1
            DWSIMOntology.Tank1(inlet_temperature, inlet_pressure, inlet_stream, tank_volume, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)

            
        if graph._node[node]['node_class'] == 'Tank' == node_class: 
            # set tank volume
            tank_volume = graph._node[first_node]['tank_volume'] 
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Tank' and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            # set tank volume
            tank_volume = graph._node[node]['tank_volume'] 
            Laufvar = Laufvar +1
            DWSIMOntology.Tank1(inlet_temperature, inlet_pressure, inlet_stream, tank_volume, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Silo' == node_class: 
            # set tank volume
            tank_volume = graph._node[first_node]['tank_volume'] 
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.Tank(inlet_temperature, inlet_pressure, inlet_stream, tank_volume, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Silo' != node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list
           # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            # set tank volume
            tank_volume = graph._node[node]['tank_volume']
            Laufvar = Laufvar +1
            DWSIMOntology.Tank1(inlet_temperature, inlet_pressure, inlet_stream, tank_volume, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'PFR' == node_class:
            # set PFR parameter
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            if 'reactor_length' in graph[node]:
                    reactor_length = graph._node[node]['reactor_length']
            else:
                    reactor_length = 0
            if 'reactor_diameter' in graph[node]:
                    reactor_diameter = graph._node[node]['reactor_diameter']
            else:
                    reactor_diameter = 0
            base_compound = graph._node[node]['base_compound']
            direct_order = graph._node[node]['direct_order']
            reverse_order = graph._node[node]['reverse_order']
            stochiometry = graph._node[node]['stochiometry']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.PFR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry, reactor_diameter, reactor_length, reactor_volume, arrhenius_parameter, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'PFR' != node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list  
            # set PFR parameter
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            if 'reactor_length' in graph[node]:
                    reactor_length = graph._node[node]['reactor_length']
            else:
                    reactor_length = 0
            if 'reactor_diameter' in graph[node]:
                    reactor_diameter = graph._node[node]['reactor_diameter']
            else:
                    reactor_diameter = 0
            base_compound = graph._node[node]['base_compound']
            direct_order = graph._node[node]['direct_order']
            reverse_order = graph._node[node]['reverse_order']
            stochiometry = graph._node[node]['stochiometry']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.PFR1(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry, reactor_diameter, reactor_length, reactor_volume, arrhenius_parameter, Laufvar)            
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'CSTR' == node_class:
            # set CSTR parameter
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            base_compound = graph._node[node]['base_compound']
            direct_order = graph._node[node]['direct_order']
            reverse_order = graph._node[node]['reverse_order']
            stochiometry = graph._node[node]['stochiometry']
            reactor_volume = graph._node[node]['reactor_volume']
            arrhenius_parameter = graph._node[node]['arrhenius_parameter']
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.CSTR(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry,reactor_volume, arrhenius_parameter, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'CSTR' != node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list
            # set CSTR parameter
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'adiabatic' in graph[node]:
                adiabatic = graph._node[node]['adiabatic']
            else:
                adiabatic = 0
            if 'isothermic' in graph[node]:
                isothermic = graph._node[node]['isothermic']
            else:
                isothermic = 0
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.CSTR1(inlet_temperature, inlet_pressure, inlet_stream, isothermic, adiabatic, outlet_temperature, base_compound, direct_order, reverse_order, stochiometry,reactor_volume, arrhenius_parameter, Laufvar)            
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Heater' == node_class:
            # set heater parameter
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                deltat = 0
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.Heater(inlet_temperature, inlet_pressure, inlet_stream, added_energy_stream, outlet_temperature, deltat, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Heater' != node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list  
            # set heater parameter          
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                deltat = 0
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.Heater1(inlet_temperature, inlet_pressure, inlet_stream, added_energy_stream, outlet_temperature, deltat)            
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] =='Cooler'== node_class:
            # set cooler parameter
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'removed_energy_stream' in graph[node]:
                removed_energy_stream = graph._node[node]['removed_energy_stream']
            else:
                removed_energy_stream = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                deltat = 0
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.Cooler(inlet_temperature, inlet_pressure, inlet_stream, removed_energy_stream, outlet_temperature, deltat, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] =='Cooler'!= node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list
            # set cooler parameter
            if 'outlet_temperature' in graph[node]:
                outlet_temperature = graph._node[node]['outlet_temperature']
            else:
                outlet_temperature = 0
            if 'deltat' in graph[node]:
                deltat = graph._node[node]['deltat']
            else:
                pressure_increase = 0
            if 'removed_energy_stream' in graph[node]:
                removed_energy_stream = graph._node[node]['removed_energy_stream']
            else:
                removed_energy_stream = 0
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.Cooler1(inlet_temperature, inlet_pressure, inlet_stream, removed_energy_stream, outlet_temperature, deltat, Laufvar)            
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)#
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Heat exchanger, detailed'== node_class:
            # set heat exchanger parameter
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_transfer'] 
            inlet_stream = compoundscompoundflow
            inlet_stream2 = graph._node[node]['compoundscompoundflow2']
            inlet_temperature2 = graph._node[node]['inlet_temperature2']
            inlet_pressure2 = graph._node[node]['inlet_pressure2']
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_transfer']
            Laufvar = Laufvar +1
            DWSIMOntology.Heat_exchanger(inlet_temperature, inlet_pressure, inlet_temperature2, inlet_pressure2, inlet_stream, inlet_stream2, heat_exchange_area, global_heat_transfer, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Heat exchanger, detailed'!= node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list
            # set heat exchanger parameter
            inlet_stream2 = graph._node[node]['compoundscompoundflow2']
            inlet_temperature2 = graph._node[node]['inlet_temperature2']
            inlet_pressure2 = graph._node[node]['inlet_pressure2']
            heat_exchange_area = graph._node[node]['heat_exchange_area']
            global_heat_transfer = graph._node[node]['global_heat_tranmsfer']
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature']
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.Heat_exchanger1(inlet_temperature, inlet_pressure, inlet_temperature2, inlet_pressure2, inlet_stream, inlet_stream2, heat_exchange_area, global_heat_transfer, Laufvar)                
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Pump'== node_class:
            # set pump parameter
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            inlet_stream = compoundscompoundflow
            print(Laufvar, type(Laufvar))
            DWSIMOntology.Pump(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, power_required, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID_str = str(Laufvar)
            #onto_world = owlready2.World()
            onto_updated = onto_world.get_ontology("./rdf-new_out.owl").load()
            individual_searched = onto_updated.search_one(iri=onto.base_iri+"Composition"+ProcessID_str)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            Laufvar = Laufvar +1
            
        if graph._node[node]['node_class'] == 'Pump'!= node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list
            # set pump parameter
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.Pump1(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, power_required, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_temperature']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            #onto_world = owlready2.World()
            onto2 = onto_world.get_ontology("./rdf-new_out.owl").load()
            individual_searched_2 = onto2.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched_2.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Compressor'== node_class:
            # set compressor parameter
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.Compressor(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Compressor'!= node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list  
            # set compressor parameter
            if 'outlet_pressure' in graph[node]:
                outlet_pressure = graph._node[node]['outlet_pressure']
            else:
                outlet_pressure = 0
            if 'pressure_increase' in graph[node]:
                pressure_increase = graph._node[node]['pressure_increase']
            else:
                pressure_increase = 0
            if 'power_required' in graph[node]:
                power_required = graph._node[node]['power_required']
            else:
                power_required = 0
            if 'added_energy_stream' in graph[node]:
                added_energy_stream = graph._node[node]['added_energy_stream']
            else:
                added_energy_stream = 0
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.Compressor1(inlet_temperature, inlet_pressure, inlet_stream, outlet_pressure, pressure_increase, added_energy_stream, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Separator'== node_class:
            inlet_stream = compoundscompoundflow
            Laufvar = Laufvar +1
            DWSIMOntology.Separator(inlet_temperature, inlet_pressure, inlet_stream, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_temperature2 = UnitOperation._node['unitoperation']['outlet_temperature2']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            outlet_pressure2 = UnitOperation._node['unitoperation']['outlet_pressure2']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            
        if graph._node[node]['node_class'] == 'Separator'!= node_class and node in successors and 'simulated_node' not in graph._node[node]: # start next function only if it was not run before (dict condition) and if it is in the successor list 
            # read data from graphml
            inlet_temperature = graph._node[before_node]['outlet_temperature'] 
            inlet_pressure = graph._node[before_node]['outlet_pressure'] 
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            inlet_stream = json.loads(comment_string[0].replace("'","\""))
            Laufvar = Laufvar +1
            DWSIMOntology.Separator1(inlet_temperature, inlet_pressure, inlet_stream, Laufvar)
            before_node = node
            UnitOperation = nx.read_graphml('./Output/graphs_graphml/clean/UnitOperation_Graph')
            outlet_temperature = UnitOperation._node['unitoperation']['outlet_temperature']
            outlet_temperature2 = UnitOperation._node['unitoperation']['outlet_temperature2']
            outlet_pressure = UnitOperation._node['unitoperation']['outlet_pressure']
            outlet_pressure2 = UnitOperation._node['unitoperation']['outlet_pressure2']
            dict1 = {'outlet_temperature':outlet_temperature}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_temperature2':outlet_temperature2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure':outlet_pressure}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            dict1 = {'outlet_pressure2':outlet_pressure2}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            # get successors from node to find out which node is next 
            successors = list(graph.successors(node))
            # saves that this node is already simulated and avoids that it is simulated again
            dict1 = {'simulated_node':'TRUE'}
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
            ProcessID = str(Laufvar)
            individual_searched = onto.search_one(iri=onto.base_iri+"Composition"+ProcessID)
            comment_string = individual_searched.comment
            dict1 = json.loads(comment_string[0].replace("'","\""))
            group= {node:dict1}
            nx.set_node_attributes(graph,group)
    Directory.SetCurrentDirectory(work_dir)
    nx.write_graphml(graph,'./Output/graphs_graphml/clean/Graph_after_simulation')
            
graph = nx.read_graphml('C:/Users/Lucky Luciano/Documents/GitHub/Abschlussarbeiten_Behr/Kaemmerling/Output/graphs_graphml/clean/graphml_test')
#graph = nx.read_graphml('C:/Users/Lucky Luciano/Documents/GitHub/Abschlussarbeiten_Behr/Kaemmerling/Output/graphs_graphml/clean/graphml_pfd3')
startsimulationfromgraphml(graph, 298.15, 100000.0, {"Water" : 0.5, 'Ethanol': 0.5})