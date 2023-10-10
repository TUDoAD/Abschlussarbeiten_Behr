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
    
    #for i in range(len(coefficients)):
     #   print(f"k{i}: " + str(coefficients[f"k{i}"]) + " J/mol")
      #  print(" ")
    
    return coefficients
    

def createEquationSystem(substances, mechanism, coefficients):
    # setting the equation for the production rate s
    equations = []
    for sub in substances:
        eqn = f"s_{sub} ="
        
        # prüfe ob sub in educt oder produkt und setze -/+
        # zähle alle Komponenten in der Reaktion
        # setze alle educte ^- coeff in die Gleichung ein
        # setze alle produkte ^+coeff in die gleichung ein
        
        
        for i in range(len(mechanism)):
            educts = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[0].split("+")
            products = mechanism[i]["reactions"][0]["reaction_equation"].split(">")[1].split("+")
            
            
            if sub in educts:
                count_e = Counter(educts)
                stoichiometry = count_e[sub]
                educts = list(set(educts))
                
                stoichiometry_str = f" - {stoichiometry}*k[{i}]"
                
                for educt in educts:
                    stoichiometry_str += f" * y[{substances.index(educt)}]**-{count_e[educt]}"
                
                count_p = Counter(products)
                products = list(set(products))
                for product in products:
                    stoichiometry_str += f" * y[{substances.index(product)}]**{count_p[product]}"

                eqn = eqn + stoichiometry_str
               
            elif sub in products:
                count_p = Counter(products)
                stoichiometry = count_p[sub]
                products = list(set(products))
                
                stoichiometry_str = f" + {stoichiometry}*k[{i}]"
                
                for product in products:
                    stoichiometry_str += f" * y[{substances.index(product)}]**{count_p[product]}"
                    
                count_e = Counter(educts)
                educts = list(set(educts))
                print(count_e, educts)
                for educt in educts:
                    stoichiometry_str += f" * y[{substances.index(educt)}]**-{count_e[educt]}"
                     
                eqn = eqn + stoichiometry_str
            
                
        equations.append(eqn)
    
    """
    for i in range(len(equations)):
        print(equations[i])
        print(" ")
    """
    return equations


def createThetaSystem(substances, gamma):
    equations = []
    for sub in substances:
        eqn = f"d[Theta_{sub}]/dx ="
        sigma = 1 # Annahme, jedes Substrat nutzt einen Platz am Kat.        
        eqn += f"({sigma} * s_{sub})/{gamma}"
        equations.append(eqn)
    return equations
    

def run():
    #with open("E:/Bibliothek/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
    with open("C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
        data = yaml.safe_load(file)
        
    mechanism = data[2]["ChemicalReaction"][0]
    substances = data[0]["Mixture"][0]["substances"]
    
    adsorbed_species = []
    for sub in substances:
        if "-" in sub:
            adsorbed_species.append(sub)
    
    coefficients = calcCoefficient(mechanism)
    s_equations = createEquationSystem(substances, mechanism, coefficients)
    
    #ACHTUNG: Gamma muss noch dem YAML-Datenfile ugefügt werden
    gamma = 2.55e-5
    t_equations = createThetaSystem(adsorbed_species, gamma)
    
    return s_equations, t_equations
    
