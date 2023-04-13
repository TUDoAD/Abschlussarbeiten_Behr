# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 18:01:59 2023

@author: 49157
"""

# Beispielaufruf
reactants = {'ABTS_red': -4, 'Oxygen': -1, 'Laccase': -7.5219E-05}
products = {'ABTS_ox': 4, 'Water': 2}

# Reaktionsgleichung definieren
# Gleichung in EnzymeML nicht gegeben
def get_reaction_equation(reactants, products):
    equation = ''
    for reactant, coeff in reactants.items():
        equation += f'{abs(coeff)} {reactant} + '
    equation = equation[:-3]  # Entfernt das letzte '+'
    equation += ' -> '
    for product, coeff in products.items():
        equation += f'{abs(coeff)} {product} + '
    equation = equation[:-3]  # Entfernt das letzte '+'
    return equation

def get_coefficient(species, coefficients):
    if species in coefficients:
        return coefficients[species]
    else:
        return 0  # Wenn die Spezies nicht in den Koeffizienten enthalten ist, ist der Koeffizient 0

equation = get_reaction_equation(reactants, products)
ABTS_ox_coeff = get_coefficient('ABTS_ox', products)
Water_coeff = get_coefficient('Water', products)
ABTS_red_coeff = get_coefficient('ABTS_red', reactants)
Oxygen_coeff = get_coefficient('Oxygen', reactants)
Laccase_coeff = get_coefficient('Laccase', reactants)

# Substanzen und ihre Koeffizienten in Variablen speichern
ABTS_red = ('ABTS_red', ABTS_red_coeff)
Oxygen = ('Oxygen', Oxygen_coeff)
Laccase = ('Laccase', Laccase_coeff)
ABTS_ox = ('ABTS_ox', ABTS_ox_coeff)
Water = ('Water', Water_coeff)

# Auf die Substanzen und ihre Koeffizienten zugreifen
#print(f'Substanz: {ABTS_red[0]}, Koeffizient: {ABTS_red[1]}')
#print(f'Substanz: {Oxygen[0]}, Koeffizient: {Oxygen[1]}')
#print(f'Substanz: {Laccase[0]}, Koeffizient: {Laccase[1]}')
#print(f'Substanz: {ABTS_ox[0]}, Koeffizient: {ABTS_ox[1]}')
#print(f'Substanz: {Water[0]}, Koeffizient: {Water[1]}')
