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
import json
import yaml
import time
import owlready2

from pathlib import Path
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset, Datafile


def _primitive_field(type_name, value):
    return {
        "typeName": type_name,
        "multiple": False,
        "typeClass": "primitive",
        "value": str(value),
    }


def _compound_field(type_name, fields):
    return {
        "typeName": type_name,
        "multiple": False,
        "typeClass": "compound",
        "value": {field["typeName"]: field for field in fields},
    }


def _metadata_block(name, display_name, fields):
    return {"name": name, "displayName": display_name, "fields": fields}


def _build_dataset_metadata(dataset, simulation_data):
    sections = {
        name: value
        for section in simulation_data
        for name, value in section.items()
    }
    mixture = sections["Mixture"][0]
    reactor = sections["Reactor"][0]
    reaction = sections["ChemicalReaction"][0][0]["reactions"][0]
    temperature = mixture["temperature"][0]["outlet"]
    pressure = mixture["pressure"]
    residence_time = mixture["residence time"]
    feed = ", ".join(
        f"{species}={fraction}"
        for species, fraction in mixture["mole_fraction"]
    )
    not_reported = "Not reported in this simulation dataset."

    custom_blocks = {
        "catcorebascatmetadata": _metadata_block(
            "catcorebascatmetadata",
            "CatCore Metadata",
            [
                _primitive_field("catalysisResearchField", "Heterogeneous catalysis"),
                _primitive_field("reactionType", sections["Reaction_Type"]),
                _primitive_field("activeSite", "Nickel (Ni) surface"),
            ],
        ),
        "synthesisbascatmetadata": _metadata_block(
            "synthesisbascatmetadata",
            "Synthesis Metadata",
            [
                _compound_field(
                    "mandatorySynthesis",
                    [
                        _primitive_field(
                            "nominalCompositin",
                            "Nickel (Ni); composition details not specified",
                        ),
                        _primitive_field("catalystMeasuredProperties", not_reported),
                        _primitive_field(
                            "precursor",
                            "Not applicable; catalyst synthesis is not described.",
                        ),
                        _primitive_field(
                            "preparationMethod",
                            "Not applicable; catalyst preparation is not described.",
                        ),
                    ],
                )
            ],
        ),
        "characterizationbascatmetadata": _metadata_block(
            "characterizationbascatmetadata",
            "Characterization Metadata",
            [
                _compound_field(
                    "mandatoryCharacterization",
                    [
                        _primitive_field("equipment", not_reported),
                        _primitive_field("characterizationTechnique", not_reported),
                    ],
                )
            ],
        ),
        "reactionbascatmetadata": _metadata_block(
            "reactionbascatmetadata",
            "Reaction Metadata",
            [
                _compound_field(
                    "mandatoryReaction",
                    [
                        _primitive_field(
                            "catalystQuantity",
                            f"{reactor['catalyst_loading']} (unit not specified in YAML)",
                        ),
                        _primitive_field(
                            "reactorDesignType",
                            f"Isothermal tubular reactor; {reactor['num_tubes']} tube(s)",
                        ),
                        _primitive_field(
                            "reactant",
                            f"Feed mole fractions: {feed}; reaction: "
                            f"{reaction['reaction_equation']}",
                        ),
                        _primitive_field(
                            "operationParameters",
                            f"Outlet temperature={temperature} K; pressure={pressure} Pa; "
                            f"residence time={residence_time} (unit unspecified in YAML; "
                            "filename labels this value in ms); "
                            f"calculation mode={reactor['calculation_mode']}; "
                            f"tube diameter={reactor['tube_diameter']}; "
                            f"tube length={reactor['tube_length']}",
                        ),
                        _primitive_field(
                            "productIdentificationMethod",
                            "Products are calculated by the simulation; no experimental "
                            "identification method is reported.",
                        ),
                    ],
                )
            ],
        ),
        "simulationbascatmetadata": _metadata_block(
            "simulationbascatmetadata",
            "Simulation Metadata",
            [
                _compound_field(
                    "mandatorySimulation",
                    [
                        _primitive_field(
                            "simulationMethod",
                            "DWSIM simulation; model and solver details not specified.",
                        ),
                        _primitive_field(
                            "calculatedProperty",
                            "Outlet composition, turnover, methane yield, and normalized "
                            "selectivity.",
                        ),
                    ],
                )
            ],
        ),
    }

    metadata = json.loads(dataset.json())
    metadata["datasetVersion"]["metadataBlocks"].update(custom_blocks)
    return json.dumps(metadata)


def _prepare_simulations(root, description):
    groups = sorted(path for path in root.glob("NewReaction_*") if path.is_dir())
    simulation_folders = sorted(
        simulation
        for group in groups
        for simulation in group.iterdir()
        if simulation.is_dir()
    )
    if not simulation_folders:
        raise FileNotFoundError(f"No simulation folders found under {root}")

    prepared = []
    for simulation_folder in simulation_folders:
        files_by_suffix = {
            suffix: list(simulation_folder.glob(f"*{suffix}"))
            for suffix in (".dwxmz", ".ttl", ".yaml")
        }
        if any(len(files) != 1 for files in files_by_suffix.values()):
            counts = {suffix: len(files) for suffix, files in files_by_suffix.items()}
            raise ValueError(f"Expected one .dwxmz, .ttl, and .yaml in {simulation_folder}: {counts}")

        files = tuple(files_by_suffix[suffix][0] for suffix in (".dwxmz", ".ttl", ".yaml"))
        if len(list(simulation_folder.iterdir())) != len(files):
            raise ValueError(f"Unexpected additional files in {simulation_folder}")

        with files[2].open("r", encoding="utf-8") as data_file:
            simulation_data = yaml.safe_load(data_file)

        dataset = Dataset()
        dataset.set({"title": simulation_folder.name})
        dataset.set({"author": [{'authorName': "Sommer-Behr, Alexander"}, {'authorName': "Völkenrath, Marc"}]})
        dataset.set({"dsDescription": [{"dsDescriptionValue": f"{description} Simulation group: {simulation_folder.parent.name}."}]})
        dataset.set({"datasetContact": [{"datasetContactEmail": "alexander.behr@tu-dortmund.de", "datasetContactName": "Behr, Alexander"},
                                         {"datasetContactEmail": "marc.voelkenrath@tu-dortmund.de", "datasetContactName": "Völkenrath, Marc"}]})
        dataset.set({"subject": ["Engineering", "Chemistry"]})
        metadata = _build_dataset_metadata(dataset, simulation_data)
        prepared.append((simulation_folder, files, simulation_data, metadata))

    return prepared


def _add_ontology_record(ontology, simulation_folder, simulation_data, dataset_pid, file_urls):
    sections = {
        name: value
        for section in simulation_data
        for name, value in section.items()
    }
    mixture = sections["Mixture"][0]
    fractions = dict(mixture["mole_fraction"])
    temperature = mixture["temperature"][0]["outlet"]
    pressure = mixture["pressure"]
    residence_time = mixture["residence time"]
    outlet_section = sections.get("Outlet Composition", sections.get("Sep_Gas Composition", []))
    outlet = dict(outlet_section)
    turnover = dict(sections.get("Turnover", []))
    selectivity = sections.get("Selectivity_normed", [{}])[0]
    yield_data = sections.get("Yield", [])

    reaction_class = next(
        (item for item in ontology.search(iri="*Methanation") if str(item) == "reac4cat.Methanation"),
        None,
    )
    if reaction_class is None:
        raise ValueError("Ontology class reac4cat.Methanation was not found")

    individual_name = (
        f"Sim_{simulation_folder.parent.name}_{sections['Reaction_Type']}_"
        f"{fractions.get('CO2')}_{temperature}K_{pressure}Pa_{residence_time}s_wd"
    )
    with ontology:
        individual = reaction_class(individual_name)

        def append_unique(property_values, value):
            if value is not None and value not in property_values:
                property_values.append(value)

        append_unique(individual.hasMolarFractionCarbonDioxide, fractions.get("CO2"))
        append_unique(individual.hasMolarFractionHydrogen, fractions.get("H2"))
        append_unique(individual.hasMolarFractionArgon, fractions.get("Ar"))
        append_unique(individual.hasSimulatedDownstream, sections.get("hasDownstream"))
        append_unique(individual.hasSimulatedReactionPressure, pressure)
        append_unique(individual.hasSimulatedReactionTemperature, temperature)
        append_unique(individual.hasSimulatedReactionResidenceTime, residence_time)
        append_unique(individual.hasOutletMolarFractionCarbonDioxide, outlet.get("CO2"))
        append_unique(individual.hasOutletMolarFractionWater, outlet.get("H2O"))
        append_unique(individual.hasOutletMolarFractionHydrogen, outlet.get("H2"))
        append_unique(individual.hasOutletMolarFractionMethane, outlet.get("CH4"))
        append_unique(individual.hasOutletMolarFractionCarbonMonoxide, outlet.get("CO"))
        append_unique(individual.hasOutletMolarFractionArgon, outlet.get("Ar"))
        append_unique(individual.hasTurnoverHydrogen, turnover.get("X_H2"))
        append_unique(individual.hasTurnoverCarbonDioxide, turnover.get("X_CO2"))
        append_unique(individual.hasYieldMethane, yield_data[1] if len(yield_data) > 1 else None)
        append_unique(individual.hasSelectivity_CO2_CH4, selectivity.get("CH4"))
        append_unique(individual.hasSelectivity_CO2_CO, selectivity.get("CO"))

        dataset_url = (
            "https://nfdirepo.fokus.fraunhofer.de/dataset.xhtml?persistentId="
            f"{dataset_pid}&version=DRAFT"
        )
        comments = [f"Dataset: {dataset_url}"]
        labels = {".dwxmz": "DWSIM-file", ".ttl": "TTL-file", ".yaml": "LinkML-file"}
        comments.extend(
            f"{labels[path.suffix.lower()]}: {url}"
            for path, url in file_urls.items()
        )
        for comment in comments:
            append_unique(individual.comment, comment)


def upload():
    start = time.time()
    ## Adjustments    
    title = "DWSIM Methanation (x_co2=0.04, with Downstream)"
    descr = "Automated simulation result file for the Ni-catalyzed Methanation of Carbon Dioxide (x_co2=0.04) with downstream process."
    #folder_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/linkml/NewReaction_06/"
    folder_path = "./linkml/with_ttl/NewReaction_01"
    #onto_path = "C:/Users/smmcvoel/Documents/GitHub/Abschlussarbeiten_Behr/VoelkenrathMA/ontologies/MV-Onto.owl"
    onto_path = "./ontologies/test-onto_ASB.owl"
    
    ## Uploading the simulation-files
    print("Uploading files...")
#    base_url = "https://nfdirepo.fokus.fraunhofer.de"
    base_url = "https://nfdirepo.fokus.fraunhofer.de"
    api_key = "466ba301-fc88-404b-8649-327db3cd38ab"
    dataverse_alias = "TUDO_ProcessSimulation_test"
    
    # create a NativeAPI instance
    api = NativeApi(base_url, api_key)
    response = api.get_info_version()
    #print("API-status: " + str(response.json()))
    
    # create an dataset
    ds = Dataset()
    ds.set({"title": title})
    ds.set({"author": [{'authorName': "Sommer-Behr, Alexander"}, {'authorName': "Völkenrath, Marc"}]})
    ds.set({"dsDescription": [{"dsDescriptionValue": descr}]})
    ds.set({"datasetContact": [{"datasetContactEmail": "alexander.behr@tu-dortmund.de", "datasetContactName": "Behr, Alexander"},
                               {"datasetContactEmail": "marc.voelkenrath@tu-dortmund.de", "datasetContactName": "Völkenrath, Marc"}]})
    ds.set({"subject": ["Engineering", "Chemistry"]})
    #print("Metadata for Dataset complete: " + str(ds.validate_json()))

    file_list = [str(file) for file in Path(folder_path).glob("*") if file.is_file()]
    yaml_files = sorted(Path(folder_path).glob("*.yaml"))
    if not yaml_files:
        raise FileNotFoundError(f"No YAML metadata file found in {folder_path}")
    with yaml_files[0].open("r", encoding="utf-8") as data_file:
        simulation_data = yaml.safe_load(data_file)
    dataset_metadata = _build_dataset_metadata(ds, simulation_data)
    
    # upload dataset and get ds_pid
    response = api.create_dataset(dataverse_alias, dataset_metadata)
    if response.status_code != 201:
        raise RuntimeError(
            f"Dataverse dataset creation failed ({response.status_code}): {response.text}"
        )
    ds_pid = response.json()["data"]["persistentId"]
    print("API-status_ds: " + str(response.json()))
    
    # create datafile
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
    print("Extend Ontology...")
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
                    temperature = data[i]["Mixture"][0]["temperature"][0]["outlet"]
                    pressure = data[i]["Mixture"][0]["pressure"]
                    res_t = data[i]["Mixture"][0]["residence time"]
                    
                    # set frac_co and frac_ar to False, because they are not in every simulation
                    # this way, there is no problem with the dataproperties (MolarFraction...)
                    frac_co = False
                    frac_ar = False
                    for j in range(len(data[i]["Mixture"][0]["mole_fraction"])):
                        if "CO2" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_co2 = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        #if "CO" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                        #    frac_co = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "H2" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_h2 = data[i]["Mixture"][0]["mole_fraction"][j][1]
                        if "Ar" in data[i]["Mixture"][0]["mole_fraction"][j][0]:
                            frac_ar = data[i]["Mixture"][0]["mole_fraction"][j][1]
                # without Downstream
                if "Outlet Composition" in data[i]:
                    for k in range(len(data[i]["Outlet Composition"])):
                        if "CO2" == data[i]["Outlet Composition"][k][0]:
                            frac_out_co2 = data[i]["Outlet Composition"][k][1]
                        if "H2" == data[i]["Outlet Composition"][k][0]:
                            frac_out_h2 = data[i]["Outlet Composition"][k][1]
                        if "CH4" == data[i]["Outlet Composition"][k][0]:
                            frac_out_ch4 = data[i]["Outlet Composition"][k][1]
                        if "H2O" == data[i]["Outlet Composition"][k][0]:
                            frac_out_h2o = data[i]["Outlet Composition"][k][1]
                        if "Ar" == data[i]["Outlet Composition"][k][0]:
                            frac_out_ar = data[i]["Outlet Composition"][k][1]
                        if "CO" == data[i]["Outlet Composition"][k][0]:
                            frac_out_co = data[i]["Outlet Composition"][k][1]
                # with Downstream            
                elif "Sep_Gas Composition" in data[i]:
                    for k in range(len(data[i]["Sep_Gas Composition"])):
                        if "CO2" == data[i]["Sep_Gas Composition"][k][0]:
                            frac_out_co2 = data[i]["Sep_Gas Composition"][k][1]
                        if "H2" == data[i]["Sep_Gas Composition"][k][0]:
                            frac_out_h2 = data[i]["Sep_Gas Composition"][k][1]
                        if "CH4" == data[i]["Sep_Gas Composition"][k][0]:
                            frac_out_ch4 = data[i]["Sep_Gas Composition"][k][1]
                        if "H2O" == data[i]["Sep_Gas Composition"][k][0]:
                            frac_out_h2o = data[i]["Sep_Gas Composition"][k][1]
                        if "Ar" == data[i]["Sep_Gas Composition"][k][0]:
                            frac_out_ar = data[i]["Sep_Gas Composition"][k][1]
                        if "CO" == data[i]["Sep_Gas Composition"][k][0]:
                            frac_out_co = data[i]["Sep_Gas Composition"][k][1]
                
                if "hasDownstream" in data[i]:
                    downstream = data[i]["hasDownstream"]
                if "Turnover" in data[i]:
                    for j in range(len(data[i]["Turnover"])):
                        if "X_CO2" in data[i]["Turnover"][j][0]:
                            turn_co2 = data[i]["Turnover"][j][1]
                        if "X_H2" in data[i]["Turnover"][j][0]:
                            turn_h2 = data[i]["Turnover"][j][1]
                        #if "X_CO" in data[i]["Turnover"][j][0]:
                        #    turn_co = data[i]["Turnover"][j][1]
                if "Yield" in data[i]:
                    yield_ch4 = data[i]["Yield"][1]
                if "Selectivity_normed" in data[i]:
                    selectivity_ch4 = data[i]["Selectivity_normed"][0]["CH4"]
                    selectivity_co = data[i]["Selectivity_normed"][0]["CO"]

            # create the individuals
            with onto:
                class_string = "*Methanation" #+ reaction_type
                class_reaction_type_list = onto.search(iri=class_string)
                for j in range(len(class_reaction_type_list)):
                    if str(class_reaction_type_list[j]) == "reac4cat.Methanation":
                        class_reaction_type = class_reaction_type_list[j]

                individual_name = "Sim_" + reaction_type + "_" + str(frac_co2) + "_" + str(temperature) + "K_" + str(pressure) + "Pa_" + str(res_t) + "s_wd"
                
                individual = class_reaction_type(individual_name)
                
                individual.hasMolarFractionCarbonDioxide.append(frac_co2)
                individual.hasMolarFractionHydrogen.append(frac_h2)
                #if frac_co:
                #    individual.hasMolarFractionCarbonMonoxide.append(frac_co)
                if frac_ar:
                    individual.hasMolarFractionArgon.append(frac_ar)
                    
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
                #individual.hasSimulatedReactionVelocity.append(velocity)
                individual.hasSimulatedReactionResidenceTime.append(res_t)
                
                individual.hasOutletMolarFractionCarbonDioxide.append(frac_out_co2)
                individual.hasOutletMolarFractionWater.append(frac_out_h2o)
                individual.hasOutletMolarFractionHydrogen.append(frac_out_h2)
                individual.hasOutletMolarFractionMethane.append(frac_out_ch4)
                individual.hasOutletMolarFractionCarbonMonoxide.append(frac_out_co)
                try:
                    individual.hasOutletMolarFractionArgon.append(frac_out_ar)
                except: UnboundLocalError
                
                individual.hasTurnoverHydrogen.append(turn_h2)
                individual.hasTurnoverCarbonDioxide.append(turn_co2)
                
                individual.hasYieldMethane.append(yield_ch4)
                
                individual.hasSelectivity_CO2_CH4.append(selectivity_ch4)
                individual.hasSelectivity_CO2_CO.append(selectivity_co)
                
                onto.save(onto_path)
               
    end = time.time()
    time_needed = end-start
    print(time_needed)
    

if __name__ == "__main__":
    upload()