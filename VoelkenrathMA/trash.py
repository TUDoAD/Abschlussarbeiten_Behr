# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 08:39:33 2023

@author: smmcvoel

Code, der funktioniert aber einfach nicht gebraucht wird für diese MA
"""

"""
DataWork.py
Funktion zum auslesen der Edukte und Produkte indem er die linke und rechte Seite aller Reaktionsschritte vergleicht.
"""
def GetEductAndProduct(data):
    ## Extract educts and products as seperate lists
    # getting every educt and product
    reactions = []
    for index, reaction in enumerate(data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"]):
        if type(reaction) == str:
            reac_eqn = reaction.splitlines()[0]
            reactions.append(reac_eqn)
        elif type(reaction) == dict:
            reac_dict = reac_dict =  data["pbr.inp"]["MAIN"]["MECHANISM"]["SURFACE"]["REACTION"][index]
            reac_eqn = reac_dict["#text"].splitlines()[0]
            reactions.append(reac_eqn)
    
    # create list with educts and product
    educt_eqn = []
    product_eqn = []
    for reaction in reactions:
        equation_split = reaction.split(">")
        educt_eqn.append(equation_split[0])
        product_eqn.append(equation_split[1])
    
    educt_all = [] # list with all possible educts
    for reaction in educt_eqn:
        re = reaction.replace(" ", "")
        educts = re.split("+")
        for i in educts:
            if "-" not in i:
                educt_all.append(i)

    product_all = [] # list with all possible products
    for reaction in product_eqn:
        re = reaction.replace(" ", "")
        products = re.split("+")
        for i in products:
            if "-" not in i:
                product_all.append(i)
            
    counter_educt = Counter(educt_all)
    counter_product = Counter(product_all)
        
    educt = []
    product = []
    
    # compare lists 
    for element, count in counter_educt.items():
        if element in counter_product:
            min_count = min(count, counter_product[element])
            educt.extend([element] * (count - min_count))
            product.extend([element] * (counter_product[element] - min_count))

