# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 06:39:56 2024

@author: chern
"""


import requests
import pandas as pd
path='./output/NAME_OF_EXCEL.xlsx'
papers=pd.read_excel(path, sheet_name='distinct_eid')
#  ScienceDirect API key
api_key = '173ea79a3547e18083fed35e7356bb62' # c4c1c384a5eb47dc15ddde06584e07ba

# ScienceDirect API URL
#base_url = 'https://api.elsevier.com/content/article/doi/'
base_url= 'https://api.elsevier.com/content/article/eid/'

#doi = '10.1016/j.jngse.2014.11.010'
#name=doi.rsplit('/', 1)[-1][0:-1]

# Set the headers with the API key
headers = {'X-ELS-APIKey': api_key}
for r in papers.itertupels():
# eid of the paper you want to retrieve    
    eid= r.eid
    # Construct the full URL
    full_url = f'{base_url}{eid}'
    name=eid.replace('.','')
    # Make the request to the ScienceDirect API
    response = requests.get(full_url, headers=headers)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the XML content to a file
        with open('{}.xml'.format(name), 'w', encoding='utf-8') as file:
            file.write(response.text)
        print('XML content saved to paper.xml')
    else:
        # Print an error message if the request was unsuccessful
        print(f"Error: {response.status_code}\n{response.text}")









