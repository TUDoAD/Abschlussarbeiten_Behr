# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 08:54:48 2023

@author: smmcvoel
"""

## Anfrage der ChEBI API mit requests
"""
import requests

base_url = "https://www.ebi.ac.uk/chebi/api/data/"

name = "Oxygen"

search_url= f"{base_url}compound/search?searchCategory=Name&searchTerm={name}"

response = requests.get(search_url)

if response.status_code == 200:
    data = response.json()
    
    if "searchResults" in data and data["searchResults"]:
        cas_number = data["searchResults"][0]["chebiAsciiName"]
        print(f"CAS-Nummer von {name}: {cas_number}")
    else:
        print(f"Keine Ergebnisse für {name} gefunden.")
else:
    print("Fehler beim Abrufen von Daten von der CHEBI-API.")

# https://www.ebi.ac.uk/chebi/advancedSearchFT.do?searchString=CO2&queryBean.stars=2
"""

## Anfrage der ChEBI API mit libchebypy
"""
from libchebipy import ChebiEntity

name = "Oxygen"
entity = ChebiEntity.get_name("CHEBI:26689")

if entity:
    cas = entity.get_cas()
    if cas:
        print(cas)
    else:
        print("No CAS found")
else:
    print("No Information found")
"""