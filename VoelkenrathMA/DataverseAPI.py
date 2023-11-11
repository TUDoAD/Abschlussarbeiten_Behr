# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 08:34:58 2023

@author: smmcvoel

ATTENTION (Checklist before calling upload):
    - API-Token Expiration date: 2024-11-01
    - Adjust Title for the Dataset
    - Adjust Description for your dataset
    - Adjust Directory in which the files are
    - Adjust Ontology u want to extend
    
    - Adjust (maybe) the names for the individuals (line 127)
"""
import os
import yaml
import owlready2

from pathlib import Path
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset, Datafile


def upload():
    ## Adjustments    
    title = "DWSIM Methanation (x_co2=0,2, with Downstream)"
    descr = "Automatic generated simulation-files for the Ni-catalyzed Methanation of Carbon Dioxide (x_co2=0,2) with Downstream."
    folder_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/NewReaction_06/"
    onto_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/ontologies/MV-Onto.owl"
    
    ## Uploading the simulation-files
    print("Uploading files...")
    base_url = "https://nfdirepo.fokus.fraunhofer.de"
    api_key = "8df62666-c3a5-4246-bed2-b1f37b5f5fab"
    dataverse_alias = "tudo-ProcessSimulations"
    
    # create a NativeAPI instance
    api = NativeApi (base_url, api_key)
    response = api.get_info_version()
    #print("API-status: " + str(response.json()))
    
    # create an dataset
    ds = Dataset()
    ds.set({"title": title})
    ds.set({"author": [{'authorName': "Behr, Alexander"}, {'authorName': "Völkenrath, Marc"}]})
    ds.set({"dsDescription": [{"dsDescriptionValue": descr}]})
    ds.set({"datasetContact": [{"datasetContactEmail": "alexander.behr@tu-dortmund.de", "datasetContactName": "Behr, Alexander"},
                               {"datasetContactEmail": "marc.voelkenrath@tu-dortmund.de", "datasetContactName": "Völkenrath, Marc"}]})
    ds.set({"subject": ["Engineering", "Chemistry"]})
    #print("Metadata for Dataset complete: " + str(ds.validate_json()))
    
    # upload dataset and get ds_pid
    response = api.create_dataset(dataverse_alias, ds.json())
    ds_pid = response.json()["data"]["persistentId"]
    print("API-status_ds: " + str(response.json()))
    
    # create datafile
    file_list = [str(file) for file in Path(folder_path).glob("*")]
    
    urls = []
    for file in file_list:
        df = Datafile()    
        df.set({"pid": ds_pid, "filename": file})
    
        # upload datafile
        response = api.upload_datafile(ds_pid, file, df.json())
        file_id = response.json()['data']['files'][0]["dataFile"]["id"]
        url = "https://nfdirepo.fokus.fraunhofer.de/file.xhtml?fileId=" + str(file_id) + "&version=DRAFT"
        urls.append([file, url])
        
        
    ## Add Information to Ontologie
    # load ontology
    onto = owlready2.get_ontology(onto_path).load()

    # load simulation files
    for file in os.listdir(folder_path):

        if file.endswith('.yaml'):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r') as data_file:
                data = yaml.safe_load(data_file)

            for i in range(len(data)):
                if "Reaction_Type" in data[i]:
                    reaction_type = data[i]["Reaction_Type"]
                if "Mixture" in data[i]:
                    temperature = data[i]["Mixture"][0]["temperature"]
                    pressure = data[i]["Mixture"][0]["pressure"]
                    velocity = data[i]["Mixture"][0]["velocity"]
                    
                    # set frac_co and frac_ar to False, because they are not in every simulation
                    # this way, there is no problem with the dataproperties (MolarFraction...)
                    frac_co = False
                    frac_ar = False
                    for j in range(len(data[i]["Mixture"][0]["mole_fraction"])):
                        if "CO2" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_co2 = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "CO" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_co = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "H2" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_h2 = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "Ar" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_ar = data[i]["Mixture"][0]["mole_fraction"][j][1]

                if "hasDownstream" in data[i]:
                    downstream = data[i]["hasDownstream"]
                if "Turnover" in data[i]:
                    for j in range(len(data[i]["Turnover"])):
                        if "X_CO2" in data[i]["Turnover"][j][0]:
                            turn_co2 = data[i]["Turnover"][j][1]
                        if "X_H2" in data[i]["Turnover"][j][0]:
                            turn_h2 = data[i]["Turnover"][j][1]
                        if "X_CO" in data[i]["Turnover"][j][0]:
                            turn_co = data[i]["Turnover"][j][1]
                if "Yield" in data[i]:
                    yield_ch4 = data[i]["Yield"][1]
                if "Selectivity" in data[i]:
                    selectivity = data[i]["Selectivity"]

            # create the individuals
            with onto:
                class_string = "*" + reaction_type
                class_reaction_type = onto.search(iri=class_string)[0]

                individual_name = "Sim_" + reaction_type + "_" + str(frac_co2) + "_" + str(temperature) + "K_" + str(pressure) + "Pa_" + str(velocity) + "ms"
                individual = class_reaction_type(individual_name)
                
                individual.hasMolarFractionCarbonDioxide.append(frac_co2)
                individual.hasMolarFractionHydrogen.append(frac_h2)
                if frac_co:
                    individual.hasMolarFractionCarbonMonoxide.append(frac_co)
                if frac_ar:
                    individual.hasMolarFractionCarbonMonoxide.append(frac_ar)
                    
                url = "https://nfdirepo.fokus.fraunhofer.de/dataset.xhtml?persistentId=" + ds_pid + "&version=DRAFT"
                ind_comment = f"Dataset: {url}"
                individual.comment.append(ind_comment)
                
                file_path = file_path.replace("/", "\\")
                for i in range(len(urls)):
                    if file_path == urls[i][0]:
                        ind_comment = "LinkML-file: " + urls[i][1]
                        individual.comment.append(ind_comment)
                    # change ending .yaml -> .dwxmz
                    if (file_path[:-4] + "dwxmz")== urls[i][0]:
                        ind_comment = "DWSIM-file: " + urls[i][1]
                        individual.comment.append(ind_comment)
                    
                    
                individual.hasSimulatedDownstream.append(downstream)
                individual.hasSimulatedReactionPressure.append(pressure)
                individual.hasSimulatedReactionTemperature.append(temperature)
                individual.hasSimulatedReactionVelocity.append(velocity)
                
                individual.hasTurnoverHydrogen.append(turn_h2)
                individual.hasTurnoverCarbonDioxide.append(turn_co2)
                
                individual.hasYieldMethane.append(yield_ch4)
                
                individual.hasSelectivity.append(selectivity)
                
                onto.save(onto_path)