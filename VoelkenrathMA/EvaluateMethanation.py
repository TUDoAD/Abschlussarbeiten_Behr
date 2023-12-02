# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 08:59:20 2023

@author: smmcvoel
"""
import os
import math
import yaml
import owlready2
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D


def MinMax(name, directory):
    # function checks, which of the simulation in the given parameter span have the highest and lowest outlet concentration
    results = []
    temperature = []
    pressure = []
    velocity = []
    concentration = []

    for file in os.listdir(directory):
        try:
            if file.endswith('.yaml'):
                file_path = os.path.join(directory, file)
                with open(file_path, 'r') as data_file:
                    data = yaml.safe_load(data_file)

                for i in range(len(data)):
                    if "Mixture" in data[i]:
                        # K
                        temperature_ = data[i]["Mixture"][0]["temperature"]
                        pressure_ = data[i]["Mixture"][0]["pressure"]  # Pa
                        velocity_ = data[i]["Mixture"][0]["residence time"]  # m/s

                for i in range(len(data)):
                    if "Methane" in data[i]:
                        # mol/m3 [Methane]
                        concentration_ = data[i]["Methane"][-1]

                temperature.append(temperature_)
                pressure.append(pressure_)
                velocity.append(velocity_)
                concentration.append(concentration_)

                temp = {'temperature': temperature_, 'pressure': pressure_,
                        'velocity': velocity_, 'concentration': concentration_}

                results.append(temp)
        except IndexError:
            print(f"Simulation error in simu: {file}")
            print(" ")

    # set color range
    colors = [(0, 0, 1), (1, 0, 0)]  # blue, red
    cmap_ = LinearSegmentedColormap.from_list('CustomColors', colors, N=256)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(pressure, velocity, concentration,
                         c=temperature, cmap=cmap_)

    # get minimal and maximal outlet concentration
    minima_index = concentration.index(min(concentration))
    print(
        f'Minimal methane concentration is: {concentration[minima_index]} mol/m3')
    print(
        f'The conditions for the minimum are: T={temperature[minima_index]}, p={pressure[minima_index]}, tau={velocity[minima_index]}')

    maxima_index = concentration.index(max(concentration))
    print(
        f'Maximal methane concentration is: {concentration[maxima_index]} mol/m3.')
    print(
        f'The conditions for the maximum are: T={temperature[maxima_index]}, p={pressure[maxima_index]}, tau={velocity[maxima_index]}')

    ax.scatter(pressure[minima_index], velocity[minima_index], min(
        concentration), c='red', marker='o', s=75, label='Minimum')
    ax.scatter(pressure[maxima_index], velocity[maxima_index], max(
        concentration), c='green', marker='o', s=75, label='Maximum')

    ax.set_xlabel('Pressure Pa')
    ax.set_ylabel('Residence time s')
    ax.set_zlabel('Concentration mol/m3')

    fig.colorbar(scatter, label="Temperature", location='left')

    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    plt.gca().xaxis.labelpad = 10
    plt.gca().yaxis.labelpad = 10
    plt.gca().zaxis.labelpad = 10

    # ax.set_title('Methanation')
    fig_name = directory + name + ".svg"
    plt.savefig(fig_name)
    plt.show()


def Selectivity(directory):
    for file in os.listdir(directory):

        if file.endswith('.yaml'):
            file_path = os.path.join(directory, file)
            with open(file_path, 'r') as data_file:
                data = yaml.safe_load(data_file)

            for i in range(len(data)):
                if "ChemicalReaction" in data[i]:
                    mechanism = data[i]["ChemicalReaction"][0]
                if "Reactor" in data[i]:
                    diameter = float(data[i]["Reactor"][0]["tube_diameter"])
                    #print("d: " + str(diameter))
                if "Mixture" in data[i]:
                    #velocity = float(data[i]["Mixture"][0]["velocity"])
                    molefractions = data[i]["Mixture"][0]["mole_fraction"]
                    #print("u: " + str(velocity))
                if "Hydrogen" in data[i]:
                    h2_0 = data[i]["Hydrogen"][0]
                    # print(h2_0)
                    h2 = data[i]["Hydrogen"][-1]
                    # print(h2)
                if "Carbon dioxide" in data[i]:
                    co2_0 = data[i]["Carbon dioxide"][0]
                    # print(h2_0)
                    co2 = data[i]["Carbon dioxide"][-1]
                    # print(h2)
                if "Methane" in data[i]:
                    ch4_0 = data[i]["Methane"][0]
                    # print(ch4_0)
                    ch4 = data[i]["Methane"][-1]
                    # print(ch4)

            equation = mechanism[0]["reactions"][0]["reaction_equation"]

            educts_ = equation.split(">")[0].split("+")
            educts = []
            for educt in educts_:
                if educt[0].isdigit():
                    educts.append([educt[1:], -int(educt[0])])
                else:
                    educts.append([educt, -1])

            products_ = equation.split(">")[1].split("+")
            products = []
            for product in products_:
                if product[0].isdigit():
                    products.append([product[1:], int(product[0])])
                else:
                    products.append([product, 1])
            
            for i in range(len(data)):
                if "Inlet" in data[i]:
                    for j in range(len(data[i]["Inlet"][0]["Comp_MolarFlow_In"])):
                        if data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][0] == "CO2":
                            n_co2_0 = data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][1]
                        if data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][0] == "H2":
                            n_h2_0 = data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][1]
                        if data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][0] == "CH4":
                            n_ch4_0 = data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][1]
                        if data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][0] == "H2O":
                            n_h2o_0 = data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][1]
                        if data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][0] == "CO":
                            n_co_0 = data[i]["Inlet"][0]["Comp_MolarFlow_In"][j][1]
            
                if "Outlet" in data[i]:
                    for j in range(len(data[i]["Outlet"][0]["Comp_MolarFlow_Out"])):
                        if data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][0] == "CO2":
                            n_co2 = data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][1]
                        if data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][0] == "H2":
                            n_h2 = data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][1]
                        if data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][0] == "CH4":
                            n_ch4 = data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][1]
                        if data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][0] == "H2O":
                            n_h2o = data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][1]
                        if data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][0] == "CO":
                            n_co = data[i]["Outlet"][0]["Comp_MolarFlow_Out"][j][1] 
            
            for educt in educts:
                if educt[0] == "H2":
                    v_h2 = educt[1]
                if educt[0] == "CO2":
                    v_co2 = educt[1]
            for product in products:
                if product[0] == "CH4":
                    v_ch4 = product[1]

            for i in range(len(molefractions)):
                if molefractions[i][0] == "CO2":
                    frac_co2 = molefractions[i][1]
                if molefractions[i][0] == "H2":
                    frac_h2 = molefractions[i][1]

            X_h2 = (n_h2_0 - n_h2)/n_h2_0
            X_co2 = (n_co2_0 - n_co2)/n_co2_0
    
            if frac_h2 > (4 * frac_co2):
                Y_ch4 = ((n_ch4 - n_ch4_0)/n_co2_0) * (abs(v_co2)/v_ch4)
                S_ch4 = Y_ch4 / X_co2
                S_co = ((n_co - n_co_0)/(n_co2_0 - n_co2)) * (abs(v_co2)/v_ch4)
                
                # print("h2")
            elif frac_h2 < (4 * frac_co2):
                Y_ch4 = ((n_ch4 - n_ch4_0)/n_h2_0) * (abs(v_h2)/v_ch4)
                S_ch4 = Y_ch4 / X_h2
                S_co = ((n_co - n_co_0)/(n_h2_0 - n_h2)) * (abs(v_h2)/v_ch4)
                # print("co2")
            elif frac_h2 == (4 * frac_co2):
                Y_ch4 = ((n_ch4 - n_ch4_0)/n_co2_0) * (abs(v_co2)/v_ch4)
                S_ch4 = Y_ch4 / X_co2
                S_co = ((n_co - n_co_0)/(n_co2_0 - n_co2)) * (abs(v_co2)/v_ch4)
                # print("h2_equal")
            else:
                print("Some weird error accured while calculation the yield!")
            
            sum_S = S_ch4 + S_co
            S_ch4 = S_ch4 / sum_S
            S_co = S_co / sum_S
            
            # save results
            data.append({"Turnover": [["X_CO2", X_co2], ["X_H2", X_h2]]})
            data.append({"Yield": ["Y_CH4", Y_ch4]})
            data.append({"Selectivity": [{"CH4": S_ch4, "CO":S_co}]})
            with open(file_path, 'w') as updated_data_file:
                yaml.dump(data, updated_data_file, default_flow_style=False)

        

