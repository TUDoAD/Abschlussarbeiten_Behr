# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:22:24 2023

@author: smmcvoel
"""
import math
import yaml
from collections import Counter


def calcCoefficient(mechanism):
    coefficients = {}
    for i in range(len(mechanism)):
        coefficient = f"k{i}"
        
        R = 8.31446261815324 # J/(mol K)
        
        EA = mechanism[i]["reactions"][0]["EA"] * 1000 # kJ/mol --> J/mol
        b = mechanism[i]["reactions"][0]["beta"]
        if "S0" in mechanism[i]["reactions"][0]:
            A = mechanism[i]["reactions"][0]["S0"]
        elif "A_cm_units" in mechanism[i]["reactions"][0]:
            A = mechanism[i]["reactions"][0]["A_cm_units"]
        else:
            print("Some unexpected error occured while calculating the reaction rate coefficient!")
        
        T = 420 # K
        # ACHTUNG: T hier vorgelegt, sollte im richtigen Skript allerdings von DWSIM abgerufen werden für den Fall, dass ein Mechanismus simuliert
        # wird der nicht isotherm ist.
        # ACHTUNG: Hier fehlt noch der letzte Abschnitt: Was ist theta?
        value = A * math.pow(T, b) * math.exp(-EA/(R*T))
        
        coefficients[coefficient] = value
    
    for i in range(len(coefficients)):
        print(f"k{i}: " + str(coefficients[f"k{i}"]) + " J/mol")
        print(" ")
    
    return coefficients
    

def createEquationSystem(substances, mechanism, coefficients):
    equations = []
    for sub in substances:
        eqn = f"d[{sub}]/dx ="
        
        for i in range(len(mechanism)):
            educts = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[0].split("+")
            products = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[1].split("+")
            
            if sub in educts:
                #print("educts: " + sub + " " + str(educts) + str(products))
                count = Counter(educts)
                stoichiometry = count[sub]
                stoichiometry_str = f" - k[{i}]*y[{substances.index(educts[0])-1}"
                
                for educt in educts[1:]:
                    stoichiometry_str += f"]*y[{substances.index(educt)-1}"
                
                stoichiometry_str += "]"
                
                #print(f"... stoich. coeff. is: {stoichiometry}")
                #print(educts[0])
                eqn = eqn + stoichiometry_str
                
            elif sub in products:
                #print("product: " + sub + " " + str(educts) + str(products))
                count = Counter(products)
                stoichiometry = count[sub]
                stoichiometry_str = f" + k[{i}]*y[{substances.index(educts[0])-1}"
                
                for educt in educts[1:]:
                    stoichiometry_str += f"]*y[{substances.index(educt)-1}"
                
                stoichiometry_str += "]"
                
                #print(f"... stoich. coeff. is: {stoichiometry}")
                #print(products[0])
                eqn = eqn + stoichiometry_str
        
        equations.append(eqn)
    
    """
    for i in range(len(equations)):
        print(equations[i])
        print(" ")
    """
    return equations


#def differentialEquations():
        

def run():
    #with open("E:/Bibliothek/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
    with open("C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
        data = yaml.safe_load(file)
        
    mechanism = data[2]["ChemicalReaction"][0]
    substances = data[0]["Mixture"][0]["substances"]
    
    coefficients = calcCoefficient(mechanism)
    equations = createEquationSystem(substances, mechanism, coefficients)
    
    return equations, coefficients
    
