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
                        velocity_ = data[i]["Mixture"][0]["velocity"]  # m/s

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
        f'The conditions for the minimum are: T={temperature[minima_index]}, p={pressure[minima_index]}, v={velocity[minima_index]}')

    maxima_index = concentration.index(max(concentration))
    print(
        f'Maximal methane concentration is: {concentration[maxima_index]} mol/m3.')
    print(
        f'The conditions for the maximum are: T={temperature[maxima_index]}, p={pressure[maxima_index]}, v={velocity[maxima_index]}')

    ax.scatter(pressure[minima_index], velocity[minima_index], min(
        concentration), c='red', marker='o', s=75, label='Minimum')
    ax.scatter(pressure[maxima_index], velocity[maxima_index], max(
        concentration), c='green', marker='o', s=75, label='Maximum')

    ax.set_xlabel('Pressure Pa')
    ax.set_ylabel('Velocity m/s')
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
                    velocity = float(data[i]["Mixture"][0]["velocity"])
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

            # calculation
            A = math.pi * (diameter/2) ** 2
            V_flow = velocity * A

            n_h2_0 = h2_0 * V_flow
            n_h2 = h2 * V_flow

            n_co2_0 = co2_0 * V_flow
            n_co2 = co2 * V_flow

            X_h2 = (n_h2_0 - n_h2)/n_h2_0
            #print("X(H2): " + str(X_h2))
            X_co2 = (n_co2_0 - n_co2)/n_co2_0
            #print("X(CO2): " + str(X_co2))

            n_ch4_0 = ch4_0 * V_flow
            n_ch4 = ch4 * V_flow

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

            if frac_h2 > (4 * frac_co2):
                Y_ch4 = ((n_ch4 - n_ch4_0)/n_co2_0) * (abs(v_co2)/v_ch4)
                S = Y_ch4 / X_co2
                # print("h2")
            elif frac_h2 < (4 * frac_co2):
                Y_ch4 = ((n_ch4 - n_ch4_0)/n_h2_0) * (abs(v_h2)/v_ch4)
                S = Y_ch4 / X_h2
                # print("co2")
            elif frac_h2 == (4 * frac_co2):
                Y_ch4 = ((n_ch4 - n_ch4_0)/n_h2_0) * (abs(v_h2)/v_ch4)
                S = Y_ch4 / X_h2
                # print("h2_equal")
            else:
                print("Some weird error accured while calculation the yield!")

            #print("Y(CH4): " + str(Y_ch4))
            #print("S(H2;CH4): " + str(S))

            # save results
            data.append({"Turnover": [["X_CO2", X_co2], ["X_H2", X_h2]]})
            data.append({"Yield": ["Y_CH4", Y_ch4]})
            data.append({"Selectivity": S})
            with open(file_path, 'w') as updated_data_file:
                yaml.dump(data, updated_data_file, default_flow_style=False)


def createIndividuals(directory):
    """Vor dem erzeugen der Individuen müssen die entsprechenden Dateien noch ins DataVerse geladen werden
    ACHTUNG: prüfe (zumindest bei Entwicklung) ob alles Datensätze vollständig und richtig sind bevor sie hochgeladen werden"""

    # load ontology
    onto_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/ontologies/MV-Onto.owl"
    onto = owlready2.get_ontology(onto_path).load()

    # load simulation files
    for file in os.listdir(directory):

        if file.endswith('.yaml'):
            file_path = os.path.join(directory, file)
            with open(file_path, 'r') as data_file:
                data = yaml.safe_load(data_file)

            for i in range(len(data)):
                if "Reaction_Type" in data[i]:
                    reaction_type = data[i]["Reaction_Type"]
                if "Mixture" in data[i]:
                    temperature = data[i]["Mixture"][0]["temperature"]
                    pressure = data[i]["Mixture"][0]["pressure"]
                    velocity = data[i]["Mixture"][0]["velocity"]
                    
                    # set frac_co and frac_ar to 0, because they are not in every simulation
                    # this way, there is no problem with the dataproperties (MolarFraction...)
                    frac_co = False
                    frac_ar = False
                    for j in range(len(data[i]["Mixture"][0]["mole_fraction"])):
                        if "CO2" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_co2 = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "CO" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_co = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "H2" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_h2 = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "Ar" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_ar = data[i]["Mixture"][0]["mole_fraction"][j][1]

                if "hasDownstream" in data[i]:
                    downstream = data[i]["hasDownstream"]
                if "Turnover" in data[i]:
                    for j in range(len(data[i]["Turnover"])):
                        if "X_CO2" in data[i]["Turnover"][j][0]:
                            turn_co2 = data[i]["Turnover"][j][1]
                        if "X_H2" in data[i]["Turnover"][j][0]:
                            turn_h2 = data[i]["Turnover"][j][1]
                        if "X_CO" in data[i]["Turnover"][j][0]:
                            turn_co = data[i]["Turnover"][j][1]
                if "Yield" in data[i]:
                    yield_ch4 = data[i]["Yield"][1]
                if "Selectivity" in data[i]:
                    selectivity = data[i]["Selectivity"]

            # create the individuals
            with onto:
                class_string = "*" + reaction_type
                class_reaction_type = onto.search(iri=class_string)[0]

                individual_name = "Sim_" + reaction_type + "_" + str(frac_co2) + "_" + str(temperature) + "K_" + str(pressure) + "Pa_" + str(velocity) + "ms"
                individual = class_reaction_type(individual_name)
                
                individual.hasMolarFractionCarbonDioxide.append(frac_co2)
                individual.hasMolarFractionHydrogen.append(frac_h2)
                if frac_co:
                    individual.hasMolarFractionCarbonMonoxide.append(frac_co)
                if frac_ar:
                    individual.hasMolarFractionCarbonMonoxide.append(frac_ar)
                    
                    
                individual.hasSimulatedDownstream.append(downstream)
                individual.hasSimulatedReactionPressure.append(pressure)
                individual.hasSimulatedReactionTemperature.append(temperature)
                individual.hasSimulatedReactionVelocity.append(velocity)
                
                individual.hasTurnoverHydrogen.append(turn_h2)
                individual.hasTurnoverCarbonDioxide.append(turn_co2)
                
                individual.hasYieldMethane.append(yield_ch4)
                
                individual.hasSelectivity.append(selectivity)
                
                onto.save(onto_path)