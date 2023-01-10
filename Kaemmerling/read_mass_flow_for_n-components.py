dict2 = {}
list2 = [9.57, 1.0] # mass fracs
total_mass_flow_list = []
for mass_frac in list2:
    total_compound_mass_flow = mass_frac*2
    total_mass_flow_list.append(total_compound_mass_flow)
compoundscompoundflow = {"Water" : 9.57, 'Ethanol' : 1.0}
list3 = list(compoundscompoundflow.keys())
for key in list3:
    for value in list2:
        dict2[key] = value
        list2.remove(value)
        break
