def missing_parameters_inGraphML (f):
    import networkx as nx
    a = 0
    nodes = list(f.nodes)

    for node in nodes:
        attribute_dict = nx.get_node_attributes(f, node)
        if  node == nodes[0]:
                
            if    'inlet_temperature' in attribute_dict:
                print ()
            else: 
                print('No inlet temperatue')
                a = a+1
              
            if    'inlet_pressure' in attribute_dict:
                print ()
            else:
                print('No inlet pressure')
                a = a+1
        
            if    'inlet_mass_flow' in attribute_dict:
                print ()
            else: 
                print('No inlet mass flow')
                a = a+1
              
            if    'inlet_composition' in attribute_dict:
                print ()
            else: 
                print('No inlet composition')
                a = a+1
        
        if  f.nodes[node]['node_class'] == 'Vessel':  
        
            if    'tank_volume' in attribute_dict:
                print() 
            else: 
                print('Need Tank volume')
                a = a+1
        
        if  f.nodes[node]['node_class'] == 'Fluid pump':  
        
            if    'pressure_increase' in attribute_dict or 'energy_stream' in attribute_dict or 'outlet_pressure' in attribute_dict or 'power_required' in attribute_dict:
                print() 
            else:  
                print('Need further information about the Pump')
                a = a+1
        
        if  f.nodes[node]['node_class'] == 'Heat exchanger, detailed':  
        
            if    'temperature_difference' in attribute_dict or 'heat_added' in attribute_dict or 'outlet_temperature' in attribute_dict or 'heat_removed' in attribute_dict:
                print() 
            else:  
                print('Need further information about the Heater')
                a = a+1
        
        if  f.nodes[node]['node_class'] == 'Heat exchanger':  
        
            if    'temperature_difference' in attribute_dict or 'heat_added' in attribute_dict or 'outlet_temperature' in attribute_dict or 'heat_removed' in attribute_dict:
                print() 
            else:  
                print('Need further information about the Heater')
                a = a+1
        
        if  f.nodes[node]['node_class'] == 'Compressor':  
        
            if    'power_required' in attribute_dict or 'energy_stream' in attribute_dict or 'outlet_pressure' in attribute_dict or 'pressure_increase' in attribute_dict:
                print() 
            else:  
                print('Need further information about the Compressor')
                a = a+1
        
        if  f.nodes[node]['node_class'] == 'Separator':  
        
            if    'inlet_minimum' in attribute_dict or 'inlet_maximum' in attribute_dict or 'inlet_average' in attribute_dict:
                print() 
            else: 
                print('Need further information about the Compressor')
                a = a+1
        
        if  f.nodes[node]['node_class'] == 'CSTR':  
        
            if    'reaction_parameter' in attribute_dict:
                print ()
            else: 
                print('No reaction parameters')
                a = a+1
        
            if    'reactor_volume' in attribute_dict:
                print ()
            else: 
                print('No CSTR reactor volume')
                a = a+1
        
            if    'arrhenius_parameter' in attribute_dict or 'user_defined_function' in attribute_dict:
                print() 
            else: 
                print('Need further information about the CSTR')
                a = a+1
        
            if    'temperature_managment' in attribute_dict:
                print() 
            else: 
                print('Need further information about temperature managment in the CSTR')
                a = a+1

        if  f.nodes[node]['node_class'] == 'PFR':  
        
            if    'reaction_parameter' in attribute_dict:
                print ()
            else: 
              print('No reaction parameters')
              a = a+1
        
            if    'reactor_volume' in attribute_dict:
                print ()
            else: 
                print('No PFR reactor volume')
                a = a+1
        
            if    'inlet_minimum' in attribute_dict or 'inlet_maximum' in attribute_dict or 'inlet_average' in attribute_dict:
                print() 
            else: 
                print('Need further information about the PFR')
                a = a+1
        
            if    'arrhenius_parameter' in attribute_dict or 'user_defined_function' in attribute_dict:
                print() 
            else:
                print('Need further information about the PFR')
                a = a+1
        
            if    'temperature_managment' in attribute_dict:
                print() 
            else: 
                print('Need further information about temperature managment in the PFR')
                a = a+1
    if a==0:
        
            print('Programm is ready for simulation')
        
    else:
    
            print('ERROR: input parameters are missing')
              
              
              
              
              
              