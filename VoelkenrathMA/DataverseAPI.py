# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 08:34:58 2023

@author: smmcvoel

ATTENTION:
    - API-Token Expiration date: 2024-11-01
    - Adjust Name (line: ds.set({title...) for the Dataset
    - Adjust Directory in which the files are
    -> Maybe as Function with name and dir as input
    
ToDo:
    - Beschreibung des Datensatzes variabel machen, sodass diese auch darstellt worin sich die Datensätze unterscheiden.
    -> Molanteile, Downstream sollte dazu reichen
    - 
"""
import os
import owlready2

from pathlib import Path
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset, Datafile


base_url = "https://nfdirepo.fokus.fraunhofer.de"
api_key = "8df62666-c3a5-4246-bed2-b1f37b5f5fab"
dataverse_alias = "tudo-ProcessSimulations"

# create a NativeAPI instance
api = NativeApi (base_url, api_key)
response = api.get_info_version()
#print("API-status: " + str(response.json()))

# create an dataset
ds = Dataset()
ds.set({"title": "API-test"})
ds.set({"author": [{'authorName': "Behr, Alexander"}, {'authorName': "Völkenrath, Marc"}]})
descr = "Automatic generated simulation-files for the Ni-catalyzed Methanation of Carbon Dioxide."
ds.set({"dsDescription": [{"dsDescriptionValue": descr}]})
ds.set({"datasetContact": [{"datasetContactEmail": "alexander.behr@tu-dortmund.de", "datasetContactName": "Behr, Alexander"},
                           {"datasetContactEmail": "marc.voelkenrath@tu-dortmund.de", "datasetContactName": "Völkenrath, Marc"}]})
ds.set({"subject": ["Engineering", "Chemistry"]})
#print("Metadata for Dataset complete: " + str(ds.validate_json()))

# upload dataset and get ds_pid
response = api.create_dataset(dataverse_alias, ds.json())
ds_pid = response.json()["data"]["persistentId"]
#print("API-status_ds: " + str(response.json()))

# create datafile
folder_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/NewReaction_01/"
file_list = [str(file) for file in Path(folder_path).glob("*")]

for df_filename in file_list:
    df = Datafile()    
    df.set({"pid": ds_pid, "filename": df_filename})

    # upload datafile
    response = api.upload_datafile(ds_pid, df_filename, df.json())
    #print("API-status_df: " + str(response.json()))
