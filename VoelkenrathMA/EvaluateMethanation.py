# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 08:59:20 2023

@author: smmcvoel
"""
import os
import yaml
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D


def MinMax(name, directory):    
    results= []
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
                    
                temperature_ = data[0]["Mixture"][0]["temperature"] # K
                pressure_ = data[0]["Mixture"][0]["pressure"] # Pa
                velocity_ = data[0]["Mixture"][0]["velocity"] # m/s
                concentration_ = data[6]["Methane"][-1] # mol/m3 [Methane]
                
                temperature.append(temperature_)
                pressure.append(pressure_)
                velocity.append(velocity_)
                concentration.append(concentration_)
                
                temp = {'temperature':temperature_, 'pressure':pressure_, 'velocity': velocity_,'concentration': concentration_}
                
                results.append(temp)
        except IndexError:
            print(f"Simulation error in simu: {file}")
            print(" ")
    
    # set color range
    colors = [(0,0,1), (1,0,0)] # blue, red
    cmap_ = LinearSegmentedColormap.from_list('CustomColors', colors, N=256)
     
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(pressure, velocity, concentration, c=temperature, cmap=cmap_)
    
    # get minimal and maximal outlet concentration
    minima_index = concentration.index(min(concentration))
    print(f'Minimal methane concentration is: {concentration[minima_index]} mol/m3')
    print(f'The conditions for the minimum are: T={temperature[minima_index]}, p={pressure[minima_index]}, v={velocity[minima_index]}')
    
    maxima_index = concentration.index(max(concentration))
    print(f'Maximal methane concentration is: {concentration[maxima_index]} mol/m3.')
    print(f'The conditions for the maximum are: T={temperature[maxima_index]}, p={pressure[maxima_index]}, v={velocity[maxima_index]}')
    
    ax.scatter(pressure[minima_index], velocity[minima_index], min(concentration), c='red', marker='o', s=75, label='Minimum')
    ax.scatter(pressure[maxima_index], velocity[maxima_index], max(concentration), c='green', marker='o', s=75, label='Maximum')
    
    ax.set_xlabel('Pressure Pa')
    ax.set_ylabel('Velocity m/s')
    ax.set_zlabel('Concentration mol/m3')
    
    fig.colorbar(scatter, label="Temperature", location='left')
    
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    plt.gca().xaxis.labelpad = 10
    plt.gca().yaxis.labelpad = 10
    plt.gca().zaxis.labelpad = 10
    
    #ax.set_title('Methanation')
    fig_name = directory + name + ".svg"
    plt.savefig(fig_name)
    plt.show()
         