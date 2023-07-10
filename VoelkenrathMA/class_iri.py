# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 11:53:26 2023

@author: mvoel
"""

import owlready2

# Skript bekommt eine Labelliste und prüft, in welcher Ontologie welche Klasse vorhanden ist. Für vorhandene Klassen, sollen die IRI's ausgelesen und in einer txt-Datei
# gespeichert werden.
# Im Optimalfall haben alle verwendeten Ontologien die selbe Top-Level Ontologie.

    
def create_list_IRI(class_list):
    
    txt = open("Class_IRI.txt", "a")
    
    # Liste mit Ontologien welche durchsucht werden sollen
    onto_list = ["http://purl.obolibrary.org/obo/chmo.owl"]
    
    # Definieren von leeren Listen
    class_found = []
    IRI_list = []
    
    # Lade Ontologien
    for i in onto_list:
        onto = owlready2.get_ontology(i).load()
        print(i + " loaded")
        
        # Suche nach Klassen in geladener Ontologie
        for j in class_list:
            class_j = onto.search_one(label = j)
            if class_j:
                class_found.append(class_j)
            else:
                print(f"Class '{j}' not found.")
        
        # Ausgabe der gefundenen Klassen und speicherung der IRI's
        for j in class_found:
            print(f"Class Found: {j}")
            iri_var = j.iri
            txt.write(iri_var + '\n')


"""
Code soll weiter angepasst werden. Sollten Klassen nicht in der ersten Ontologie vorhanden sein, soll eine weitere Ontologie durchsucht werden.

Eventuell über weitere Liste (class_not_found). 
Wenn class_not_found != leer: 
    suche in nächster Ontologie
Wenn class not_found != leer und alle Ontologien bereits durchsucht:
    fertige Liste mit nicht gefundenen Klassen ans
Wenn class_not_found == leer:
    brich Schleife ab
"""