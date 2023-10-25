# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 08:59:20 2023

@author: smmcvoel
"""
import os
import yaml
import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

# path variable gestalten, indem der Name der Reaktion und somit der Name des Ordners übergeben wird
folder = "C:\\Users\\smmcvoel\\Documents\\GitHub\\Abschlussarbeiten_Behr\\VoelkenrathMA\\linkml\\new_reaction_2023-10-23_wide-dice\\"

results= []
temperature = []
pressure = []
velocity = []
concentration = []

for file in os.listdir(folder):
    try:
        if file.endswith('.yaml'):
            file_path = os.path.join(folder, file)
            with open(file_path, 'r') as data_file:
                data = yaml.safe_load(data_file)
                
            temperature_ = data[0]["Mixture"][0]["temperature"] # K
            pressure_ = data[0]["Mixture"][0]["pressure"] # Pa
            velocity_ = data[0]["Mixture"][0]["velocity"] # m/s
            concentration_ = data[6]["Methane"][-1] # mol/m3 [Methane]
            
            #print(temperature_, pressure_, velocity_)
            
            temperature.append(temperature_)
            pressure.append(pressure_)
            velocity.append(velocity_)
            concentration.append(concentration_)
            
            temp = {'temperature':temperature_, 'pressure':pressure_, 'velocity': velocity_,'concentration': concentration_}
            
            results.append(temp)
    except IndexError:
        print(f"Simulation error in simu: {file}")
        print(" ")

       
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(pressure, velocity, concentration, c=temperature, cmap='viridis')

minima_index = concentration.index(min(concentration))
print(f'Minimal methane concentration is: {concentration[minima_index]} mol/m3')
print(f'The conditions for the minimum are: T={temperature[minima_index]}, p={pressure[minima_index]}, v={velocity[minima_index]}')
maxima_index = concentration.index(max(concentration))
print(f'Maximal methane concentration is: {concentration[maxima_index]} mol/m3.')
print(f'The conditions for the maximum are: T={temperature[maxima_index]}, p={pressure[maxima_index]}, v={velocity[maxima_index]}')

ax.scatter(pressure[minima_index], velocity[minima_index], min(concentration), c='red', marker='o', s=100, label='Minimum')
ax.scatter(pressure[maxima_index], velocity[maxima_index], max(concentration), c='green', marker='o', s=100, label='Maximum')

ax.set_xlabel('Pressure Pa')
ax.set_ylabel('Velocity m/s')
ax.set_zlabel('Concentration mol/m3')

fig.colorbar(scatter)

ax.set_title('Methanation')
#ACHTUNG ABLAGEORT ANPASSEN
plt.savefig("Methanation_small-dice.svg")
plt.show()
         