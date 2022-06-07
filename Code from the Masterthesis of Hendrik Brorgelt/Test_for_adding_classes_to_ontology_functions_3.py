import emmopy
import Cython
import collections
import os
import types
import json
import collections
from collections import OrderedDict
from ontopy import World
from ontopy.utils import write_catalog
import owlready2
import pandas as pd
import numpy as np
import time
from mergedeep import merge
import matplotlib.pyplot as plt
# import plotly.express as px
import plotly.graph_objects as go
import pymongo
from pymongo import MongoClient
import copy

world = World()

owlready2.JAVA_EXE = 'C:/Users/hendr/Desktop/Protege-5.5.0/jre/bin/java.exe'

owlready2.onto_path.append('C:/Users/hendr/Documents/GitHub/Hendrik_Borgelt_Masterthesis')
emmo = world.get_ontology('emmo_inferred_20220216_trying_classes_2.rdf')
emmo.name = 'emmo'
emmo.load()
emmo.sync_python_names()
emmo.base_iri = "http://emmo.info/emmo#"


def search_for_name_option_in_dict(dictionary):
    for k, v in list(dictionary.items()):
        if type(v) == dict:
            for k_2, v_2 in list(dictionary[k].items()):
                if 'Option' in k_2:
                    dictionary[k][''.join(k) + ' ' + ''.join(k_2)] = dictionary[k].pop(k_2)
            search_for_name_option_in_dict(dictionary[k])


def name_all_subkeys_after_individual_key(subdict, individual_key):
    if type(subdict) == dict:
        for k, v in list(subdict.items()):
            subdict[''.join(individual_key) + ' ' + ''.join(k)] = subdict.pop(k)
            name_all_subkeys_after_individual_key(subdict[''.join(individual_key) + ' ' + ''.join(k)], individual_key)


def change_name_to_named_individual(dictionary, list_of_names):
    for k_1, v_1 in list(dictionary.items()):
        if type(v_1) == dict:
            for k_2, v_2 in list(dictionary[k_1].items()):
                if k_1 in list_of_names:
                    dictionary[k_1][(''.join(k_2) + ' ' + ''.join('Individual'))] = dictionary[k_1].pop(k_2)
            change_name_to_named_individual(dictionary[k_1], list_of_names)


def append_key_to_list(diction):
    list_of_key_for_translator = []
    for k_3, v_3 in diction.items():
        list_of_key_for_translator.append(k_3)
        if type(v_3) == dict:
            sublist = append_key_to_list(v_3)
            for i_3 in sublist:
                list_of_key_for_translator.append(i_3)
    return list_of_key_for_translator


def create_merged_dict(dict_to_be_merged):
    dict_merged = OrderedDict()
    for i_4_int in dict_to_be_merged:
        merge(dict_merged, dict_to_be_merged[i_4_int])
    return dict_merged


def search_for_index(name_int, list_onto_classes_int):
    for i in list_onto_classes_int:
        if i[0] == name_int:
            onto_thing = i[1]
            return onto_thing
        else:
            pass


def list_of_emmo_classes(emmo_int=emmo):
    list_emmo_classes = list(emmo_int.classes())
    for i_1, i_2 in enumerate(list_emmo_classes):
        list_emmo_classes[i_1] = i_2.prefLabel
        list_emmo_classes[i_1] = [str(list_emmo_classes[i_1][0]), i_2]
    return list_emmo_classes


def list_of_emmo_data_properties(emmo_int=emmo):
    list_emmo_data_properties = list(emmo_int.data_properties())
    for i_1, i_2 in enumerate(list_emmo_data_properties):
        list_emmo_data_properties[i_1] = [i_2.get_python_name(), i_2]
    return list_emmo_data_properties


def list_of_emmo_object_properties(emmo_int=emmo):
    list_emmo_object_properties = list(emmo_int.object_properties())
    for i_1, i_2 in enumerate(list_emmo_object_properties):
        list_emmo_object_properties[i_1] = [i_2.get_python_name(), i_2]
    return list_emmo_object_properties


def list_of_emmo_individuals(emmo_int=emmo):
    list_emmo_individuals = list(emmo_int.individuals())
    for i_1, i_2 in enumerate(list_emmo_individuals):
        list_emmo_individuals[i_1] = [i_2.get_preflabel(), i_2]
    return list_emmo_individuals


def return_sub_dict(dictionary, keyword):
    if type(dictionary) == dict or type(dictionary) == collections.OrderedDict:
        for key_1, value_1 in dictionary.items():
            if keyword in key_1:
                return value_1
            else:
                if return_sub_dict(value_1, keyword) is None:
                    pass
                if return_sub_dict(value_1, keyword) is not None:
                    return return_sub_dict(value_1, keyword)


def return_sub_dict_and_path(dictionary, keyword):
    if type(dictionary) == dict or type(dictionary) == collections.OrderedDict:
        for key_1, value_1 in dictionary.items():
            if keyword == key_1:
                return value_1, key_1
            else:
                if return_sub_dict_and_path(value_1, keyword) is not None:
                    a_1, b_1 = return_sub_dict_and_path(value_1, keyword)
                    if type(b_1) == str:
                        return a_1, (key_1,) + (b_1,)
                    else:
                        return a_1, (key_1,) + tuple(list(b_1))


def search_for_ind_in_dict(dict_all, ind_name, dict_of_individual_a):
    for key_int_1, value_int_1 in dict_all.items():
        if return_sub_dict_and_path(value_int_1, ind_name) is None:
            continue
        individual_dict, tuple_int = return_sub_dict_and_path(value_int_1,
                                                              ind_name)  # list_of_keys_containing_individuals[2])
        if not dict_of_individual_a:
            dict_of_individual_a.append([ind_name + '_' + str(len(dict_of_individual_a)), [key_int_1], individual_dict])
            indiv_name = ind_name + '_' + str(len(dict_of_individual_a))
        elif individual_dict not in [i_int[2] for i_int in dict_of_individual_a]:
            dict_of_individual_a.append([ind_name + '_' + str(len(dict_of_individual_a)), [key_int_1], individual_dict])
            indiv_name = ind_name + '_' + str(len(dict_of_individual_a))
        elif individual_dict in [i_int[2] for i_int in dict_of_individual_a]:
            for i_int in dict_of_individual_a:
                if individual_dict == i_int[2]:
                    if key_int_1 not in i_int[1]:
                        i_int[1].append(key_int_1)
                    indiv_name = i_int[0]
        return dict_of_individual_a, tuple_int, indiv_name


def swap_dict_individual(tuple_keys, dict_int, ind_name):
    if tuple_keys:
        if len(tuple_keys) >= 2:
            dict_int[tuple_keys[0]] = swap_dict_individual(tuple_keys[1:], dict_int[tuple_keys[0]], ind_name)
            return dict_int
        else:
            if 'Individuals_json_Links' not in dict_int[tuple_keys[0]].keys():
                dict_int[tuple_keys[0]]['Individuals_json_Links'] = ind_name
            else:
                if isinstance(dict_int[tuple_keys[0]]['Individuals_json_Links'], str):
                    dict_int[tuple_keys[0]]['Individuals_json_Links'] = [
                        dict_int[tuple_keys[0]]['Individuals_json_Links'], ind_name]
                else:
                    dict_int[tuple_keys[0]]['Individuals_json_Links'].append(ind_name)
            try:
                del dict_int[tuple_keys[0]][ind_name.split(',')[-1].rstrip('.json').split('+')[-1].split('_')[0]]
            except:
                test = True
            # dict_int[tuple_keys[0]]] = ind_name # oldest and definetly wrong structure since it only generates one link
            test = True
            return dict_int
    else:
        print('Error: tuple is Empty')


def search_for_key_instances(all_sims_int, dict_of_key_sections_int):
    for key_int_2_int, value_int_2_int in dict_of_key_sections_int.items():
        for i_int in value_int_2_int:
            dict_of_individual_d_int = []
            for i_2_int, i_3_int in all_sims_int.items():
                if search_for_ind_in_dict({i_2_int: i_3_int}, i_int, dict_of_individual_d_int) is None:
                    pass
                else:
                    dict_of_individual_d_int, tuple_c_int, current_ind_name_int = search_for_ind_in_dict(
                        {i_2_int: i_3_int}, i_int, dict_of_individual_d_int)
            try:
                os.makedirs('./folder_for_dict_individuals/' + str(key_int_2_int) + '/' + str(i_int))
            except:
                pass
            for i_4_int in dict_of_individual_d_int:
                with open('./folder_for_dict_individuals/' + str(key_int_2_int) + '/' + str(i_int) + '/' + str(
                        i_4_int[0]) + ".json", "w") as out_file:
                    json.dump({'dict': i_4_int[2], 'Sims': i_4_int[1]}, out_file)


def search_for_ind_in_dict_2(dict_all, ind_name, dict_of_individual_a, true_dict_name):
    for key_int_1, value_int_1 in dict_all.items():
        if return_sub_dict_and_path(value_int_1, ind_name) is None:
            continue
        individual_dict, tuple_int = return_sub_dict_and_path(value_int_1,
                                                              ind_name)  # list_of_keys_containing_individuals[2])
        if not dict_of_individual_a:
            dict_of_individual_a.append(
                [ind_name + '_' + str(len(dict_of_individual_a)), [true_dict_name], individual_dict])
            indiv_name = ind_name + '_' + str(len(dict_of_individual_a))
        elif individual_dict not in [i_int[2] for i_int in dict_of_individual_a]:
            dict_of_individual_a.append(
                [ind_name + '_' + str(len(dict_of_individual_a)), [true_dict_name], individual_dict])
            indiv_name = ind_name + '_' + str(len(dict_of_individual_a))
        elif individual_dict in [i_int[2] for i_int in dict_of_individual_a]:
            for i_int in dict_of_individual_a:
                if individual_dict == i_int[2]:
                    if true_dict_name not in i_int[1]:
                        i_int[1].append(true_dict_name)
                    indiv_name = i_int[0]
        return dict_of_individual_a, tuple_int, indiv_name


def search_for_name_in_dict_and_rename(dictionary, rename):
    for k_3, v_3 in list(dictionary.items()):
        if type(v_3) == dict:
            for k_2, v_2 in list(dictionary[k_3].items()):
                if rename in k_2:
                    dictionary[k_3][''.join(k_3) + ' ' + ''.join(k_2)] = dictionary[k_3].pop(k_2)
            search_for_name_in_dict_and_rename(dictionary[k_3], rename)


def save_and_archiv_instances(all_sims_int, dict_of_key_sections_int):
    for key_int_2_int, value_int_2_int in dict_of_key_sections_int.items():
        for i_int in value_int_2_int:
            dict_of_individual_d_int = []
            for i_2_int, i_3_int in all_sims_int.items():
                if search_for_ind_in_dict({i_2_int: i_3_int}, i_int, dict_of_individual_d_int) is None:
                    pass
                else:
                    dict_of_individual_d_int, tuple_c_int, current_ind_name_int = search_for_ind_in_dict(
                        {i_2_int: i_3_int}, i_int, dict_of_individual_d_int)
            try:
                os.makedirs('./dict_inst/' + str(key_int_2_int) + '/' + str(i_int))
            except:
                pass
            for i_4_int in dict_of_individual_d_int:
                with open('./dict_inst/' + str(key_int_2_int) + '/' + str(i_int) + '/' + str(i_4_int[0]) + ".json",
                          "w") as out_file:
                    json.dump({'dict': i_4_int[2], 'Sims': i_4_int[1]}, out_file)


def return_subdict(dict_int, tuple_int):
    return_dict = dict_int
    if isinstance(tuple_int, str):
        if tuple_int not in return_dict:
            return None
        else:
            return_dict = return_dict[tuple_int]
    elif isinstance(tuple_int, tuple):
        for i_int in tuple_int:
            try:
                if i_int not in return_dict:
                    return None
                else:
                    return_dict = return_dict[i_int]
            except:
                test_1 = True
                pass
    return return_dict


def add_tuples_and_str_to_tuple_or_str(tuple_1_int, tuple_2_int):
    return_tuple = tuple_1_int
    if isinstance(return_tuple, str):
        if isinstance(tuple_2_int, str):
            return_tuple = (return_tuple, tuple_2_int)
        else:
            return_tuple = (return_tuple,) + tuple_2_int
    else:
        if isinstance(tuple_2_int, str):
            return_tuple = return_tuple + (tuple_2_int,)
        else:
            return_tuple = return_tuple + tuple_2_int
    return return_tuple


def add_tuples_and_str_to_tuple(tuple_list):
    if len(tuple_list) <= 1:
        return_tuple = tuple_list[0]
    if len(tuple_list) <= 2:
        return_tuple = add_tuples_and_str_to_tuple_or_str(tuple_list[0], tuple_list[0])
    else:
        for number, tuple_int in enumerate(tuple_list):
            if number == 0:
                return_tuple = tuple_int
            else:
                return_tuple = add_tuples_and_str_to_tuple_or_str(return_tuple, tuple_int)
    return return_tuple


def check_if_inst_key_in_dict(all_sims_merged_int, tuple_of_keys):
    if return_sub_dict_and_path(all_sims_merged_int, tuple_of_keys) is not None:
        full_return_dict_and_path = return_sub_dict_and_path(all_sims_merged_int, tuple_of_keys)
        if full_return_dict_and_path is not None:
            dict_merged_int = all_sims_merged_int
            dict_merged_int_updated = return_subdict(dict_merged_int, full_return_dict_and_path[1])
            return dict_merged_int, dict_merged_int_updated, full_return_dict_and_path
        else:
            return None
    else:
        return None


def save_and_archiv_named_instances(all_sims_int, list_of_keys_containing_named_sub_instances_int):
    all_sims_merged_int = create_merged_dict(all_sims_int)
    for tuple_of_keys in list_of_keys_containing_named_sub_instances_int:
        if check_if_inst_key_in_dict(all_sims_merged_int, tuple_of_keys) is not None:
            dict_merged_int, dict_merged_int_updated, full_return_dict_and_path = check_if_inst_key_in_dict(
                all_sims_merged_int, tuple_of_keys)
            for inst_name in dict_merged_int_updated:
                dict_of_individual_f_int = []
                tuple_for_all_sims = full_return_dict_and_path[1]
                for key_int in all_sims_int:
                    if return_subdict(all_sims_int[key_int], tuple_for_all_sims + (inst_name,)) is not None:
                        dict_to_be_appended = return_subdict(all_sims_int[key_int], tuple_for_all_sims + (inst_name,))
                        dict_of_individual_f_int = search_for_inst_in_inst_dict(dict_to_be_appended, inst_name,
                                                                                dict_of_individual_f_int, key_int)
                if dict_of_individual_f_int:
                    try:
                        os.makedirs('./dict_inst_2/Named_inst_2')
                    except:
                        pass
                for i_9 in dict_of_individual_f_int:
                    # change_name_option_for_instances(dict_of_individual_f_int, str(inst_name) + str('+') + str(i_9[0]) + str('.json'))
                    with open(
                            './dict_inst_2/Named_inst_2/' + str(tuple_of_keys) + str(',') + str(i_9[0]) + str('.json'),
                            "w") as out_file:
                        json.dump({'dict': i_9[2], 'Sims': i_9[1], 'Tuple': tuple_for_all_sims}, out_file)


def save_and_archiv_named_sub_instances(all_sims_int, list_of_keys_containing_named_sub_instances_int):
    all_sims_merged_int = create_merged_dict(all_sims_int)
    for number_sub_inst, tuple_of_keys in enumerate(list_of_keys_containing_named_sub_instances_int):
        if return_sub_dict_and_path(all_sims_merged_int, tuple_of_keys[0]) is None:
            pass
        else:
            for sub_inst_name in return_sub_dict_and_path(all_sims_merged_int, tuple_of_keys[0])[0]:
                i_11_int = return_sub_dict_and_path(all_sims_merged_int, tuple_of_keys[0])
                dict_of_individual_e_int = []
                current_dict_merged_int = all_sims_merged_int
                for i_15_int in i_11_int[1]:
                    current_dict_merged_int = current_dict_merged_int[i_15_int]
                if return_sub_dict_and_path(current_dict_merged_int[sub_inst_name], tuple_of_keys[1]) is None:
                    pass
                else:
                    for i_17_int in return_sub_dict_and_path(current_dict_merged_int[sub_inst_name], tuple_of_keys[1])[
                        0].keys():
                        dict_of_individual_e_int = []
                        for i_7_int, i_8_int in all_sims_int.items():
                            current_dict_int = all_sims_int[i_7_int]
                            for tuple_int in i_11_int[1]:
                                current_dict_int = current_dict_int[tuple_int]
                            if search_for_ind_in_dict_2(current_dict_int, i_17_int, dict_of_individual_e_int,
                                                        i_7_int) is None:
                                pass
                            else:
                                dict_of_individual_e_int, tuple_e_int, current_ind_name_int = search_for_ind_in_dict_2(
                                    current_dict_int, i_17_int, dict_of_individual_e_int, i_7_int)
                        try:
                            os.makedirs('./dict_inst_2/Named_sub_inst/' + str(tuple_of_keys[0]) + str('_') + str(
                                tuple_of_keys[1]) + str('/') + str(sub_inst_name) + '/' + str(i_17_int))
                        except:
                            pass
                        for i_9 in dict_of_individual_e_int:
                            with open('./dict_inst_2/Named_sub_inst/' + str(tuple_of_keys[0]) + str('_') + str(
                                    tuple_of_keys[1]) + str('/') + ''.join(sub_inst_name) + '/' + ''.join(
                                i_17_int) + '/' + str(sub_inst_name) + str('+') + str(i_9[0]) + ".json",
                                      "w") as out_file:
                                json.dump({'dict': i_9[2], 'Sims': i_9[1], 'Tuple': i_11_int[1]}, out_file)
    return dict_of_individual_e_int, tuple_e_int, current_ind_name_int


def save_and_archiv_named_sub_instances_2(all_sims_int, list_of_keys_containing_named_sub_instances_int):
    all_sims_merged_int = create_merged_dict(all_sims_int)
    for tuple_of_keys in list_of_keys_containing_named_sub_instances_int:
        if check_if_inst_key_in_dict(all_sims_merged_int, tuple_of_keys[0]) is not None:
            dict_merged_int, dict_merged_int_updated, full_return_dict_and_path = check_if_inst_key_in_dict(
                all_sims_merged_int, tuple_of_keys[0])
            for inst_name in return_sub_dict_and_path(dict_merged_int, tuple_of_keys[0])[0]:
                if check_if_inst_key_in_dict(dict_merged_int_updated[inst_name], tuple_of_keys[1]) is not None:
                    sub_dict_merged_int, sub_dict_merged_int_updated, full_return_sub_dict_and_path = check_if_inst_key_in_dict(
                        dict_merged_int_updated[inst_name], tuple_of_keys[1])
                    for sub_inst_name in sub_dict_merged_int_updated:
                        dict_of_individual_f_int = []
                        tuple_for_all_sims = add_tuples_and_str_to_tuple(
                            [full_return_dict_and_path[1], inst_name, full_return_sub_dict_and_path[1]])
                        for key_int in all_sims_int:
                            if return_subdict(all_sims_int[key_int], tuple_for_all_sims + (sub_inst_name,)) is not None:
                                dict_to_be_appended = return_subdict(all_sims_int[key_int],
                                                                     tuple_for_all_sims + (sub_inst_name,))
                                dict_of_individual_f_int = search_for_inst_in_inst_dict(dict_to_be_appended,
                                                                                        sub_inst_name,
                                                                                        dict_of_individual_f_int,
                                                                                        key_int)
                        if dict_of_individual_f_int:
                            try:
                                os.makedirs('./dict_inst_2/Named_sub_inst_2')
                            except:
                                pass
                        for i_9 in dict_of_individual_f_int:
                            change_name_option_for_instances(dict_of_individual_f_int,
                                                             str(inst_name) + str('+') + str(sub_inst_name) + str(
                                                                 '+') + str(i_9[0]) + str('.json'))
                            with open('./dict_inst_2/Named_sub_inst_2/' + str(tuple_of_keys[0]) + str('-') + str(
                                    tuple_of_keys[1]) + str(',') + str(inst_name) + str('+') + str(i_9[0]) + str(
                                '.json'), "w") as out_file:
                                json.dump({'dict': i_9[2], 'Sims': i_9[1], 'Tuple': tuple_for_all_sims}, out_file)


def save_and_archiv_named_sub_sub_instances(all_sims_int, list_of_keys_containing_named_sub_instances_int):
    all_sims_merged_int = create_merged_dict(all_sims_int)
    for tuple_of_keys in list_of_keys_containing_named_sub_instances_int:
        if check_if_inst_key_in_dict(all_sims_merged_int, tuple_of_keys[0]) is not None:
            dict_merged_int, dict_merged_int_updated, full_return_dict_and_path = check_if_inst_key_in_dict(
                all_sims_merged_int, tuple_of_keys[0])
            for inst_name in return_sub_dict_and_path(dict_merged_int, tuple_of_keys[0])[0]:
                if check_if_inst_key_in_dict(dict_merged_int_updated[inst_name], tuple_of_keys[1]) is not None:
                    sub_dict_merged_int, sub_dict_merged_int_updated, full_return_sub_dict_and_path = check_if_inst_key_in_dict(
                        dict_merged_int_updated[inst_name], tuple_of_keys[1])
                    for sub_inst_name in return_sub_dict_and_path(sub_dict_merged_int, tuple_of_keys[1])[0]:
                        if check_if_inst_key_in_dict(sub_dict_merged_int_updated[sub_inst_name],
                                                     tuple_of_keys[2]) is not None:
                            sub_sub_dict_merged_int, sub_sub_dict_merged_int_updated, full_return_sub_sub_dict_and_path = check_if_inst_key_in_dict(
                                sub_dict_merged_int_updated[sub_inst_name], tuple_of_keys[2])
                            if tuple_of_keys[2] == 'FLUID MODELS':
                                for sub_sub_inst_name in sub_sub_dict_merged_int_updated:
                                    dict_of_individual_f_int = []
                                    tuple_for_all_sims = add_tuples_and_str_to_tuple(
                                        [full_return_dict_and_path[1], inst_name, full_return_sub_dict_and_path[1],
                                         sub_inst_name, full_return_sub_sub_dict_and_path[1]])
                                    for key_int in all_sims_int:
                                        if return_subdict(all_sims_int[key_int], tuple_for_all_sims) is not None:
                                            dict_to_be_appended = return_subdict(all_sims_int[key_int],
                                                                                 tuple_for_all_sims)
                                            dict_of_individual_f_int = search_for_inst_in_inst_dict(dict_to_be_appended,
                                                                                                    sub_inst_name,
                                                                                                    dict_of_individual_f_int,
                                                                                                    key_int)
                                    if dict_of_individual_f_int:
                                        try:
                                            os.makedirs('./dict_inst_2/Named_sub_sub_inst_2')
                                        except:
                                            pass
                                    for i_9 in dict_of_individual_f_int:
                                        with open('./dict_inst_2/Named_sub_sub_inst_2/' + str(tuple_of_keys[0]) + str(
                                                '-') + str(tuple_of_keys[1]) + str('-') + str(tuple_of_keys[2]) + str(
                                            ',') + str(inst_name) + str('+') + str(i_9[0].split('_')[0]) + str(
                                            '+') + str('FLUID MODELS') + '_' + str(i_9[0].split('_')[1]) + str(
                                            '.json'), "w") as out_file:
                                            json.dump({'dict': i_9[2], 'Sims': i_9[1], 'Tuple': tuple_for_all_sims},
                                                      out_file)
                                        # with open('./dict_inst_2/Named_sub_sub_inst_2/' + str(tuple_of_keys[0]) + str('-') + str(tuple_of_keys[1]) + str('-') + str(tuple_of_keys[2]) + str(',') + str(inst_name) + str('+') + str(i_9[0]) + str('.json'), "w") as out_file:
                                        #     json.dump({'dict': i_9[2], 'Sims': i_9[1], 'Tuple': tuple_for_all_sims}, out_file)
                            else:
                                for sub_sub_inst_name in sub_sub_dict_merged_int_updated:
                                    dict_of_individual_f_int = []
                                    tuple_for_all_sims = add_tuples_and_str_to_tuple(
                                        [full_return_dict_and_path[1], inst_name, full_return_sub_dict_and_path[1],
                                         sub_inst_name, full_return_sub_sub_dict_and_path[1]])
                                    for key_int in all_sims_int:
                                        if return_subdict(all_sims_int[key_int],
                                                          tuple_for_all_sims + (sub_sub_inst_name,)) is not None:
                                            dict_to_be_appended = return_subdict(all_sims_int[key_int],
                                                                                 tuple_for_all_sims + (
                                                                                     sub_sub_inst_name,))
                                            dict_of_individual_f_int = search_for_inst_in_inst_dict(dict_to_be_appended,
                                                                                                    sub_sub_inst_name,
                                                                                                    dict_of_individual_f_int,
                                                                                                    key_int)
                                    if dict_of_individual_f_int:
                                        try:
                                            os.makedirs('./dict_inst_2/Named_sub_sub_inst_2')
                                        except:
                                            pass
                                    for i_9 in dict_of_individual_f_int:
                                        change_name_option_for_instances(dict_of_individual_f_int,
                                                                         str(inst_name) + str('+') + str(
                                                                             sub_inst_name) + str('+') + str(
                                                                             i_9[0]) + str('.json'))
                                        with open('./dict_inst_2/Named_sub_sub_inst_2/' + str(tuple_of_keys[0]) + str(
                                                '-') + str(tuple_of_keys[1]) + str('-') + str(tuple_of_keys[2]) + str(
                                            ',') + str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(
                                            i_9[0]) + str('.json'), "w") as out_file:
                                            json.dump({'dict': i_9[2], 'Sims': i_9[1], 'Tuple': tuple_for_all_sims},
                                                      out_file)


def save_and_archiv_named_sub_sub_sub_instances(all_sims_int, list_of_keys_containing_named_sub_instances_int):
    all_sims_merged_int = create_merged_dict(all_sims_int)
    for tuple_of_keys in list_of_keys_containing_named_sub_instances_int:
        if check_if_inst_key_in_dict(all_sims_merged_int, tuple_of_keys[0]) is not None:
            dict_merged_int, dict_merged_int_updated, full_return_dict_and_path = check_if_inst_key_in_dict(
                all_sims_merged_int, tuple_of_keys[0])
            for inst_name in return_sub_dict_and_path(dict_merged_int, tuple_of_keys[0])[0]:
                if check_if_inst_key_in_dict(dict_merged_int_updated[inst_name], tuple_of_keys[1]) is not None:
                    sub_dict_merged_int, sub_dict_merged_int_updated, full_return_sub_dict_and_path = check_if_inst_key_in_dict(
                        dict_merged_int_updated[inst_name], tuple_of_keys[1])
                    for sub_inst_name in return_sub_dict_and_path(sub_dict_merged_int, tuple_of_keys[1])[0]:
                        if check_if_inst_key_in_dict(sub_dict_merged_int_updated[sub_inst_name],
                                                     tuple_of_keys[2]) is not None:
                            sub_sub_dict_merged_int, sub_sub_dict_merged_int_updated, full_return_sub_sub_dict_and_path = check_if_inst_key_in_dict(
                                sub_dict_merged_int_updated[sub_inst_name], tuple_of_keys[2])
                            test_3 = return_sub_dict_and_path(sub_sub_dict_merged_int, tuple_of_keys[2])[0]
                            for sub_sub_inst_name in \
                                    return_sub_dict_and_path(sub_sub_dict_merged_int, tuple_of_keys[2])[0]:
                                # if sub_sub_inst_name == 'COMPONENT':
                                #     test_8 = sub_sub_inst_name
                                #     test_4 = check_if_inst_key_in_dict(sub_sub_dict_merged_int_updated, tuple_of_keys[3])
                                #     test_6 = sub_sub_dict_merged_int_updated
                                #     test_5 = False
                                # if check_if_inst_key_in_dict(sub_sub_dict_merged_int_updated[sub_sub_inst_name], tuple_of_keys[3]) is not None:
                                #     sub_sub_sub_dict_merged_int, sub_sub_sub_dict_merged_int_updated, full_return_sub_sub_sub_dict_and_path = check_if_inst_key_in_dict(sub_sub_dict_merged_int_updated[sub_sub_inst_name], tuple_of_keys[3])
                                if (tuple_of_keys[2] == 'FLUID MODELS') or (tuple_of_keys[2] == 'SOLID MODELS') or (
                                        tuple_of_keys[2] == 'DOMAIN MODELS'):
                                    if check_if_inst_key_in_dict(sub_sub_dict_merged_int_updated,
                                                                 tuple_of_keys[3]) is not None:
                                        sub_sub_sub_dict_merged_int, sub_sub_sub_dict_merged_int_updated, full_return_sub_sub_sub_dict_and_path = check_if_inst_key_in_dict(
                                            sub_sub_dict_merged_int_updated, tuple_of_keys[3])
                                        for sub_sub_sub_inst_name in sub_sub_sub_dict_merged_int_updated:
                                            dict_of_individual_f_int = []
                                            tuple_for_all_sims = check_if_tuple_multiplicity(
                                                add_tuples_and_str_to_tuple([full_return_dict_and_path[1], inst_name,
                                                                             full_return_sub_dict_and_path[1],
                                                                             sub_inst_name,
                                                                             full_return_sub_sub_dict_and_path[1],
                                                                             sub_sub_inst_name,
                                                                             full_return_sub_sub_sub_dict_and_path[1]]))
                                            test_9 = check_if_tuple_multiplicity(tuple_for_all_sims)
                                            test_10 = False
                                            for key_int in all_sims_int:
                                                test_7 = return_subdict(all_sims_int[key_int],
                                                                        tuple_for_all_sims + (sub_sub_sub_inst_name,))
                                                if return_subdict(all_sims_int[key_int], tuple_for_all_sims + (
                                                        sub_sub_sub_inst_name,)) is not None:
                                                    dict_to_be_appended = return_subdict(all_sims_int[key_int],
                                                                                         tuple_for_all_sims + (
                                                                                             sub_sub_sub_inst_name,))
                                                    dict_of_individual_f_int = search_for_inst_in_inst_dict(
                                                        dict_to_be_appended, sub_sub_sub_inst_name,
                                                        dict_of_individual_f_int, key_int)
                                            if dict_of_individual_f_int:
                                                try:
                                                    os.makedirs('./dict_inst_2/Named_sub_sub_sub_inst_2')
                                                except:
                                                    pass
                                            # change_name_option_for_instances(dict_of_individual_f_int, str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(sub_sub_inst_name) + str('+') + str(i_9[0]) + str('.json'))
                                            # for i_10 in dict_of_individual_f_int:
                                            #     search_for_name_option_in_dict(i_10[2])
                                            #     if 'Option' in i_10[2]:
                                            #     for keys_int_2 in list(i_10[2]):
                                            #         if 'Option' in keys_int_2:
                                            #             i_10[2][str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(sub_sub_inst_name) + str('+') + str(i_10[0]) + str('.json') + ' Option'] = i_10[2][keys_int_2]
                                            #             del i_10[2][keys_int_2]
                                            test_12121 = dict_of_individual_f_int
                                            test_12123 = inst_name, sub_inst_name, sub_sub_inst_name, \
                                                         tuple_for_all_sims[-3]
                                            test_12412 = tuple_of_keys
                                            if tuple_for_all_sims[-3] != 'Inlet':
                                                test_12312 = True
                                            for i_9 in dict_of_individual_f_int:
                                                # change_name_option_for_instances(dict_of_individual_f_int, str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(sub_sub_inst_name) + str('+') + str(i_9[0]) + str('.json'))
                                                with open('./dict_inst_2/Named_sub_sub_sub_inst_2/' + str(
                                                        tuple_of_keys[0]) + str('-') + str(tuple_of_keys[1]) + str(
                                                    '-') + str(tuple_of_keys[2]) + str('-') + str(
                                                    tuple_of_keys[3]) + str(',') + str(inst_name) + str('+') + str(
                                                    sub_inst_name) + str('+') + str(sub_sub_inst_name) + str(
                                                    '+') + str(i_9[0]) + str('.json'), "w") as out_file:
                                                    json.dump(
                                                        {'dict': i_9[2], 'Sims': i_9[1], 'Tuple': tuple_for_all_sims},
                                                        out_file)
                                else:
                                    if check_if_inst_key_in_dict(sub_sub_dict_merged_int_updated[sub_sub_inst_name],
                                                                 tuple_of_keys[3]) is not None:
                                        sub_sub_sub_dict_merged_int, sub_sub_sub_dict_merged_int_updated, full_return_sub_sub_sub_dict_and_path = check_if_inst_key_in_dict(
                                            sub_sub_dict_merged_int_updated[sub_sub_inst_name], tuple_of_keys[3])
                                        for sub_sub_sub_inst_name in sub_sub_sub_dict_merged_int_updated:
                                            dict_of_individual_f_int = []
                                            tuple_for_all_sims = check_if_tuple_multiplicity(
                                                add_tuples_and_str_to_tuple([full_return_dict_and_path[1], inst_name,
                                                                             full_return_sub_dict_and_path[1],
                                                                             sub_inst_name,
                                                                             full_return_sub_sub_dict_and_path[1],
                                                                             sub_sub_inst_name,
                                                                             full_return_sub_sub_sub_dict_and_path[1]]))
                                            test_9 = check_if_tuple_multiplicity(tuple_for_all_sims)
                                            test_10 = False
                                            for key_int in all_sims_int:
                                                test_7 = return_subdict(all_sims_int[key_int],
                                                                        tuple_for_all_sims + (sub_sub_sub_inst_name,))
                                                if return_subdict(all_sims_int[key_int], tuple_for_all_sims + (
                                                        sub_sub_sub_inst_name,)) is not None:
                                                    dict_to_be_appended = return_subdict(all_sims_int[key_int],
                                                                                         tuple_for_all_sims + (
                                                                                             sub_sub_sub_inst_name,))
                                                    dict_of_individual_f_int = search_for_inst_in_inst_dict(
                                                        dict_to_be_appended, sub_sub_sub_inst_name,
                                                        dict_of_individual_f_int, key_int)
                                            if dict_of_individual_f_int:
                                                try:
                                                    os.makedirs('./dict_inst_2/Named_sub_sub_sub_inst_2')
                                                except:
                                                    pass
                                            # change_name_option_for_instances(dict_of_individual_f_int, str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(sub_sub_inst_name) + str('+') + str(i_9[0]) + str('.json'))
                                            # for i_10 in dict_of_individual_f_int:
                                            #     search_for_name_option_in_dict(i_10[2])
                                            #     if 'Option' in i_10[2]:
                                            #     for keys_int_2 in list(i_10[2]):
                                            #         if 'Option' in keys_int_2:
                                            #             i_10[2][str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(sub_sub_inst_name) + str('+') + str(i_10[0]) + str('.json') + ' Option'] = i_10[2][keys_int_2]
                                            #             del i_10[2][keys_int_2]
                                            test_12121 = dict_of_individual_f_int
                                            test_12123 = inst_name, sub_inst_name, sub_sub_inst_name, \
                                                         tuple_for_all_sims[-3]
                                            test_12412 = tuple_of_keys
                                            if tuple_for_all_sims[-3] != 'Inlet':
                                                test_12312 = True
                                            for i_9 in dict_of_individual_f_int:
                                                # change_name_option_for_instances(dict_of_individual_f_int, str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(sub_sub_inst_name) + str('+') + str(i_9[0]) + str('.json'))
                                                with open('./dict_inst_2/Named_sub_sub_sub_inst_2/' + str(
                                                        tuple_of_keys[0]) + str('-') + str(tuple_of_keys[1]) + str(
                                                    '-') + str(tuple_of_keys[2]) + str('-') + str(
                                                    tuple_of_keys[3]) + str(',') + str(inst_name) + str('+') + str(
                                                    sub_inst_name) + str('+') + str(sub_sub_inst_name) + str(
                                                    '+') + str(i_9[0]) + str('.json'), "w") as out_file:
                                                    json.dump(
                                                        {'dict': i_9[2], 'Sims': i_9[1], 'Tuple': tuple_for_all_sims},
                                                        out_file)


def change_name_option_for_instances(dict_of_individual_f_int, inst_name_int):
    for i_10 in dict_of_individual_f_int:
        search_for_name_option_in_dict(i_10[2])
        for keys_int_2 in list(i_10[2]):
            if 'Option' in keys_int_2:
                i_10[2][inst_name_int + ' Option'] = i_10[2][keys_int_2]
                # i_10[2][str(inst_name) + str('+') + str(sub_inst_name) + str('+') + str(sub_sub_inst_name) + str('+') + str(i_10[0]) + str('.json') + ' Option'] = i_10[2][keys_int_2]
                del i_10[2][keys_int_2]


def check_if_tuple_multiplicity(tuple_int):
    for it, tup_int in enumerate(tuple_int[:-1]):
        if tup_int in tuple_int[it + 1]:
            tuple_int = tuple_int[:it + 1] + tuple_int[it + 2:]
            return tuple_int
    return tuple_int


def search_for_inst_in_inst_dict(dict_to_be_appended_int, ind_name, dict_of_individual_a, sim_name):
    if not dict_of_individual_a:
        dict_of_individual_a.append(
            [ind_name + '_' + str(len(dict_of_individual_a)), [sim_name], dict_to_be_appended_int])
    elif dict_to_be_appended_int not in [i_int[2] for i_int in dict_of_individual_a]:
        dict_of_individual_a.append(
            [ind_name + '_' + str(len(dict_of_individual_a)), [sim_name], dict_to_be_appended_int])
    elif dict_to_be_appended_int in [i_int[2] for i_int in dict_of_individual_a]:
        for i_int in dict_of_individual_a:
            if dict_to_be_appended_int == i_int[2]:
                if sim_name not in i_int[1]:
                    i_int[1].append(sim_name)
    return dict_of_individual_a


def transfer_data_to_mongo(data_int, mongo_db, mongo_collection, mongo_cluster):
    cluster_int = MongoClient(mongo_cluster)
    db_int = cluster_int[mongo_db]
    mongo_collection_int = db_int[mongo_collection]
    post = data_int
    mongo_collection_int.insert_one(post)


def transfer_instances_to_mongo_db(path, mongo_db, mongo_collection, mongo_cluster):
    for root, dirs, files in os.walk(path):
        for name_2 in files:
            if name_2.endswith(".json"):
                with open(root + str('/') + name_2, 'r') as in_file:
                    json_loaded = json.load(in_file)
                    instance_name = name_2
                    file_path = list(root.split('/'))[-1].split('\\')
                    instance_key = file_path[0]
                    instance_group = file_path[1]
                    print('root: ', root)
                    print('instance_key: ', instance_key)
                    print('instance_group: ', instance_group)
                    print('instance_name: ', instance_name)
                    transfer_data_to_mongo(
                        {'instance_name': instance_name, 'instance_key': instance_key, 'instance_group': instance_group,
                         'dict': json_loaded}, mongo_db, mongo_collection, mongo_cluster)


def transfer_simulation_dicts_to_mongo_db(path, mongo_db, mongo_collection, mongo_cluster):
    for root, dirs, files in os.walk(path):
        for name_2 in files:
            if name_2.endswith(".json"):
                with open(root + str('/') + name_2, 'r') as in_file:
                    json_loaded = json.load(in_file)
                    instance_name = name_2
                    transfer_data_to_mongo(
                        {'simulation': instance_name,
                         'dict': json_loaded}, mongo_db, mongo_collection, mongo_cluster)


def change_name_of_sub_sub_inst(all_sims, sub_sub_dict_folder_path):
    modified_all_sims = copy.deepcopy(all_sims)
    for root_3, dirs_3, files_3 in os.walk(sub_sub_dict_folder_path):
        for name_3 in files_3:
            with open(root_3 + str('/') + name_3, 'r') as in_file:
                loaded_json = json.load(in_file)
                for i_1_int in modified_all_sims:
                    if i_1_int in loaded_json['Sims']:  # todo
                        tuple_int = loaded_json['Tuple']
                        swap_dict_individual(tuple_int, modified_all_sims[i_1_int], name_3)
    return modified_all_sims


def rename_dict_chapters_for_translator(dict_int, list_of_keys_int, current_name_int=''):
    for k_int, v_int in list(dict_int.items()):
        if isinstance(v_int, str):
            for i_int in list_of_keys_int:
                if k_int == i_int:
                    pass
                else:
                    dict_int[current_name_int + ' ' + k_int] = v_int
            del dict_int[k_int]
        elif isinstance(v_int, (dict, OrderedDict)):
            key_found = False
            for i_int in list_of_keys_int:
                if isinstance(i_int, tuple) & bool(key_found is False):
                    temp_name = ''
                    for i_2_int in i_int:
                        if len(temp_name) == 0:
                            temp_name += i_2_int
                        else:
                            temp_name += ' ' + i_2_int
                        if k_int == i_2_int:
                            key_found = True
                            dict_int[temp_name] = rename_dict_chapters_for_translator(dict_int[k_int], list_of_keys_int,
                                                                                      temp_name)
                            if temp_name != k_int:
                                dict_int.pop(k_int)
                    if key_found:
                        break
                elif isinstance(i_int, str) & bool(key_found is False):
                    if k_int == i_int:
                        key_found = True
                        dict_int[k_int] = rename_dict_chapters_for_translator(dict_int[k_int], list_of_keys_int, i_int)
                    if key_found:
                        break
            if not key_found:
                if current_name_int == '':
                    dict_int[k_int] = rename_dict_chapters_for_translator(dict_int[k_int], list_of_keys_int,
                                                                          current_name_int)
                else:
                    dict_int[current_name_int + ' ' + k_int] = rename_dict_chapters_for_translator(dict_int[k_int],
                                                                                                   list_of_keys_int,
                                                                                                   current_name_int)
                    dict_int.pop(k_int)
        else:
            print('ERROR not dict/OrderedDict/str as value but type: ', type(v_int))
    return dict_int


def start_rename_dict_chapters_for_translator(dict_int, list_of_keys_int):
    for i in list(dict_int):
        dict_int[i]['CFX Command Language for Run'] = rename_dict_chapters_for_translator(
            dict_int[i]['CFX Command Language for Run'], list_of_keys_int)
    return dict_int


def flatten_dict_to_list(dict_int):
    flattened_dict_list_int = []
    for key_int, value_int in dict_int.items():
        if key_int in flattened_dict_list_int:
            print(key_int)
        else:
            flattened_dict_list_int.append(key_int)
            if isinstance(value_int, (dict, OrderedDict)):
                if isinstance(flatten_dict_to_list(dict_int[key_int]), str):
                    flattened_dict_list_int.append(flatten_dict_to_list(dict_int[key_int]))
                else:
                    [flattened_dict_list_int.append(i) for i in flatten_dict_to_list(dict_int[key_int])]
    return flattened_dict_list_int


def check_tuple_as_list_for_match_and_concatenate(new_key_value, list_of_keys_int, list_to_be_checked):
    if new_key_value == 'ANALYSIS TYPE':
        test = True
    list_of_keys_int_2 = copy.deepcopy(list_of_keys_int)
    for i_1, i_2 in enumerate(list_of_keys_int_2):
        if isinstance(i_2, tuple):
            new_str_for_list = ''
            for i_3 in i_2:
                new_str_for_list += ' ' + i_3
            list_of_keys_int_2[i_1] = new_str_for_list.lstrip(' ')
    if (list_to_be_checked[0] + ' ' + new_key_value) in list_of_keys_int_2:
        list_after_check = (list_to_be_checked[0] + ' ' + new_key_value, '', True)
    elif (list_to_be_checked[1] + ' ' + new_key_value) in list_of_keys_int_2:
        list_after_check = (list_to_be_checked[1] + ' ' + new_key_value, '', True)
    elif new_key_value in list_of_keys_int_2:
        list_after_check = (new_key_value, '', True)
    else:
        list_after_check = (list_to_be_checked[0], new_key_value, False)
    if new_key_value == 'ANALYSIS TYPE':
        test_2 = True
    return list_after_check


def start_rename_dict_chapters_for_translator_3(dict_int, list_of_keys_int):
    for i in list(dict_int):
        dict_int[i]['CFX Command Language for Run'] = rename_dict_chapters_for_translator_3(
            dict_int[i]['CFX Command Language for Run'], list_of_keys_int)
        if 'SOLUTION UNITS' in dict_int[i].keys():
            test_12345 = True
    return dict_int


def rename_dict_chapters_for_translator_3(dict_int, list_of_keys_int, current_name_int='', test_tuple=('', '', False)):
    for k_int, v_int in list(dict_int.items()):
        test_for_test_tuple = check_tuple_as_list_for_match_and_concatenate(k_int, list_of_keys_int, test_tuple)
        if k_int == 'SOLUTION UNITS':
            test = True
        if isinstance(v_int, str):
            for i_int in list_of_keys_int:
                if k_int == i_int:
                    pass
                else:
                    dict_int[current_name_int + ' ' + k_int] = v_int
            del dict_int[k_int]
        elif isinstance(v_int, (dict, OrderedDict)):
            if test_for_test_tuple[2]:
                dict_int[test_for_test_tuple[0]] = rename_dict_chapters_for_translator_3(dict_int[k_int],
                                                                                         list_of_keys_int,
                                                                                         test_for_test_tuple[0],
                                                                                         test_for_test_tuple)
                if test_for_test_tuple[0] != k_int:
                    dict_int.pop(k_int)
            else:
                dict_int[test_for_test_tuple[0] + ' ' + k_int] = rename_dict_chapters_for_translator_3(dict_int[k_int],
                                                                                                       list_of_keys_int,
                                                                                                       test_for_test_tuple[
                                                                                                           0],
                                                                                                       test_for_test_tuple)
                dict_int.pop(k_int)
        else:
            print('ERROR not dict/OrderedDict/str as value but type: ', type(v_int))
        if k_int == 'SOLUTION UNITS':
            test = True
    return dict_int


def replace_key_to_additional_dict_initialization(dict_int, key_int):
    dict_int, additional_dict_int = replace_key_to_additional_dict(dict_int, key_int)
    dict_int.update(additional_dict_int)
    return dict_int


def replace_key_to_additional_dict(dict_int, replace_key_int):
    additional_dict_int = dict()
    if isinstance(dict_int, (dict, OrderedDict)):
        for key_int, v_int in list(dict_int.items()):
            if replace_key_int in key_int:
                additional_dict_int = {key_int: dict_int[key_int].pop(key_int)}
            else:
                dict_int, additional_dict_int = replace_key_to_additional_dict(dict_int[key_int], replace_key_int)
    return dict_int, additional_dict_int


def change_names_in_dict_by_adding_prefix_2(dictionary, list_of_names_to_be_preffixed):
    dict_int = dictionary
    for k_1, v_1 in list(dict_int.items()):
        if type(v_1) is dict:
            dict_int[' '.join(list_of_names_to_be_preffixed) + ' ' + k_1] = change_names_in_dict_by_adding_prefix_2(v_1,
                                                                                                                    list_of_names_to_be_preffixed)
            dict_int.pop(k_1)
            test_1 = dictionary
        else:
            if '.json Option' in k_1:
                dict_int[' '.join(list_of_names_to_be_preffixed) + ' ' + 'Individual Option'] = dict_int.pop(k_1)
            else:
                dict_int[' '.join(list_of_names_to_be_preffixed) + ' ' + ''.join(k_1)] = dict_int.pop(k_1)
    return dict_int


def search_for_name_source_in_dict(dictionary):
    for k, v in list(dictionary.items()):
        source_name_changed = False
        if type(v) == dict:
            for k_2, v_2 in list(dictionary[k].items()):
                if '\\' in k_2:
                    test_1 = k + '\\' + '\\'.join(k_2.split('\\')[1:])
                    test_2 = test_1.split('=')
                    if len(test_2) == 2:
                        test_4 = copy.deepcopy(dictionary)
                        dictionary[test_2[0].rstrip(' ')] = test_2[1].lstrip(' ')
                        dictionary.pop(k)
                        # dictionary[k][k + '\\' + '\\'.join(k_2.split('\\')[1:])] = dictionary[k].pop(k_2)
                        source_name_changed = True
                elif '/' in k_2:
                    test_1 = k + '\\' + '\\'.join(k_2.split('\\')[1:])
                    test_2 = test_1.split('=')
                    if len(test_2) == 2:
                        test_4 = copy.deepcopy(dictionary)
                        dictionary[test_2[0].rstrip(' ')] = test_2[1].lstrip(' ')
                        dictionary.pop(k)
                        # dictionary[k][k + '\\' + '\\'.join(k_2.split('/')[1:])] = dictionary[k].pop(k_2)
                        source_name_changed = True
            if not source_name_changed:
                search_for_name_source_in_dict(dictionary[k])
            else:
                test = k
                test_5 = True


def modify_ontologiy_by_adding_classes(dict_of_excel_translator_int, emmo_int):
    n_iter_counter = 0
    length_of_emmo_classes_before = len(list_of_emmo_classes(emmo_int))
    while (bool(n_iter_counter <= 10) & bool(not (all(dict_of_excel_translator_int['Implementation_Check']) & bool(
            dict_of_excel_translator_int['Implementation_Check'][0] == False)))):
        n_iter_counter += 1
        list_onto_superclass = list(dict_of_excel_translator_int['Onto_superclass'].values())
        list_onto_name = list(dict_of_excel_translator_int['Onto_name'].values())
        list_dict_names = list(dict_of_excel_translator_int['Dict_name'].values())
        list_implementation_check = list(dict_of_excel_translator_int['Implementation_Check'].values())
        zipped_list = zip(list_onto_superclass,
                          list_onto_name,
                          list_dict_names,
                          list_implementation_check)
        for iterator, (item_1, item_2, item_3, item_4) in enumerate(zipped_list):
            list_onto_classes = list_of_emmo_classes(emmo_int)
            if bool(not item_4) & bool(item_1 in list([i_1[0] for i_1 in list_onto_classes])):
                dict_of_excel_translator_int['Implementation_Check'][iterator] = True
                with emmo_int:
                    new_class = types.new_class(item_2, (search_for_index(item_1, list_onto_classes),))
                    new_class.prefLabel = [owlready2.locstr(item_2, lang='en')]
    print('number of EMMO.classes added:   ', len(list_of_emmo_classes(emmo_int)) - length_of_emmo_classes_before)
    print('number of EMMO.classes missing: ', len(dict_of_excel_translator_int['Implementation_Check']) - (
            len(list_of_emmo_classes(emmo_int)) - length_of_emmo_classes_before))
    return emmo_int


def dict_to_emmo_individual_for_str(emmo_int, dict_int, dict_of_excel_trans_int, list_sim_indiv, emmo_indiv,
                                    last_indiv):
    list_of_emmo_individuals(emmo_int)
    list_sim_emmo_name = [search_for_index(sim_indiv, list_of_emmo_individuals(emmo_int)) for sim_indiv in
                          list_sim_indiv]
    emmo_indiv_name = search_for_index(emmo_indiv, list_of_emmo_individuals(emmo_int))
    last_indiv_emmo_name = search_for_index(last_indiv, list_of_emmo_individuals(emmo_int))


def dict_to_emmo_individual(emmo_int, dict_int, dict_of_excel_trans_int, list_sim_indiv, emmo_indiv, last_indiv):
    list_of_emmo_individuals(emmo_int)
    list_sim_emmo_name = [search_for_index(sim_indiv, list_of_emmo_individuals(emmo_int)) for sim_indiv in
                          list_sim_indiv]
    emmo_indiv_name = search_for_index(emmo_indiv, list_of_emmo_individuals(emmo_int))
    last_indiv_emmo_name = search_for_index(last_indiv, list_of_emmo_individuals(emmo_int))
    for key_int, value_int in dict_int.items():
        if 'CEL' in key_int:
            test_121 = key_int
        name_for_trans_check = key_int.split('-')[0].rstrip(' ') + key_int.split('-')[2]
        # try:
        #     name_for_trans_check = key_int.split('-')[0].rstrip(' ') + key_int.split('-')[2]
        # except:
        #     test = True
        if isinstance(value_int, (dict, OrderedDict)):
            if name_for_trans_check in list(dict_of_excel_trans_int['Dict_name'].values()):
                test_122 = True
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(name_for_trans_check)]]
                new_indiv_class = search_for_index(indiv_class, list_of_emmo_classes(emmo_int))
                if key_int.split('-')[2]:
                    new_indiv_name = key_int.split('-')[1] + '_' + key_int.split('-')[2].title().replace(' ', '')
                    new_indiv_class(new_indiv_name)
                    indiv_emmo_name = search_for_index(new_indiv_name, list_of_emmo_individuals(emmo_int))
                    [indiv_emmo_name.hasSimulation.append(sim_emmo_name) for sim_emmo_name in list_sim_emmo_name]
                    indiv_emmo_name.hasIndividual.append(emmo_indiv_name)
                    emmo_int = create_and_link_property(key_int.split('-')[2].title().replace(' ', ''), owlready2.ObjectProperty,
                                                        last_indiv, new_indiv_name, emmo_int)
                    dict_to_emmo_individual(emmo_int, value_int, dict_of_excel_trans_int, list_sim_indiv, emmo_indiv,
                                            new_indiv_name)
                else:
                    new_indiv_name = last_indiv
                    # new_indiv_class(new_indiv_name)
                    # indiv_emmo_name = search_for_index(new_indiv_name, list_of_emmo_individuals(emmo_int))
                    # [indiv_emmo_name.hasSimulation.append(sim_emmo_name) for sim_emmo_name in list_sim_emmo_name]
                    # indiv_emmo_name.hasIndividual.append(emmo_indiv_name)
                    # emmo_int = create_and_link_property(key_int.split('-')[2].title().replace(' ', ''), owlready2.ObjectProperty,
                    #                                     last_indiv, new_indiv_name, emmo_int)
                    dict_to_emmo_individual(emmo_int, value_int, dict_of_excel_trans_int, list_sim_indiv, emmo_indiv,
                                            new_indiv_name)
            else:
                # pass
                print(f'Name not found1: {name_for_trans_check} \n with key_int {key_int}')
        elif isinstance(value_int, (str, list)):
            if 'Individuals_json_Links' in key_int:
                if not isinstance(value_int, str):
                    for i_1 in value_int:
                        name_to_check = i_1.strip('.json').split(',')[-1].title().replace(' ', '').replace('+', '_')
                        if name_to_check in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
                            defined_indiv_emmo_name = search_for_index(name_to_check,
                                                                       list_of_emmo_individuals(emmo_int))
                            emmo_indiv_name.hasDefinedIndividual.append(defined_indiv_emmo_name)
                            # emmo_int = create_and_link_property(last_indiv.split('_')[-1], owlready2.ObjectProperty, last_indiv, name_to_check, emmo_int)
                            # emmo_int = create_and_link_property(key_int.split('-')[2].replace(' ', ''), owlready2.ObjectProperty, last_indiv, new_indiv_name, emmo_int)
                            # print(list_sim_emmo_name)
                        else:
                            print('Individual not found: ', name_to_check)
                else:
                    name_to_check = value_int.strip('.json').split(',')[-1].title().replace(' ', '').replace('+', '_')
                    if name_to_check in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
                        defined_indiv_emmo_name = search_for_index(name_to_check, list_of_emmo_individuals(emmo_int))
                        emmo_indiv_name.hasDefinedIndividual.append(defined_indiv_emmo_name)
                        # emmo_int = create_and_link_property(last_indiv.split('_')[-1], owlready2.ObjectProperty, last_indiv, name_to_check, emmo_int)
                        # emmo_int = create_and_link_property(key_int.split('-')[2].replace(' ', ''), owlready2.ObjectProperty, last_indiv, new_indiv_name, emmo_int)
                        # print(list_sim_emmo_name)
                    else:
                        print('Individual not found: ', name_to_check)
            elif ('Option' in key_int) & (last_indiv == emmo_indiv):
                emmo_indiv_name.hasOption.append(value_int)
            elif 'Option' in key_int:
                last_indiv_emmo_name.hasOption.append(value_int)
            elif '.json' in value_int:
                test = True  # todo impelemntation for connecting to individual of other loop
            elif name_for_trans_check in list(dict_of_excel_trans_int[
                                                  'Dict_name'].values()):  # todo implementation of connection between individuals
                # print(name_for_trans_check)
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(name_for_trans_check)]]
                new_indiv_class = search_for_index(indiv_class, list_of_emmo_classes(emmo_int))
                new_indiv_name = key_int.split('-')[1] + '_' + key_int.split('-')[2].title().replace(' ', '')
                new_indiv_class(new_indiv_name)
                indiv_emmo_name = search_for_index(new_indiv_name, list_of_emmo_individuals(emmo_int))
                indiv_emmo_name.prefLabel = new_indiv_name
                [indiv_emmo_name.hasSimulation.append(sim_emmo_name) for sim_emmo_name in list_sim_emmo_name]
                indiv_emmo_name.hasIndividual.append(emmo_indiv_name)
                Data_prop_name_check = 'has' + key_int.split('-')[2].replace(' ', '')
                if len(str(value_int).split('[')) == 2:
                    try:
                        indiv_value = float(value_int.split('[')[0])
                    except:
                        indiv_value = 'Error'
                    indiv_unit = value_int.split('[')[1].rstrip(']')
                    with emmo_int:
                        hasDataPropValue = types.new_class(Data_prop_name_check + 'Value', (owlready2.DataProperty,))
                        hasDataPropValue.python_name = 'hasdataPropValue'
                        indiv_emmo_name.hasdataPropValue.append(indiv_value)
                        hasDataPropUnit = types.new_class(Data_prop_name_check + 'Unit', (owlready2.DataProperty,))
                        hasDataPropUnit.python_name = 'hasdataPropUnit'
                        indiv_emmo_name.hasdataPropUnit.append(indiv_unit)
                else:
                    with emmo_int:
                        hasDataProp = types.new_class(Data_prop_name_check, (owlready2.DataProperty,))
                        hasDataProp.python_name = 'hasdataProp'
                        indiv_emmo_name.hasdataProp.append(value_int)
                if last_indiv != emmo_indiv:  # todo change from has Setting to hasIndividual Name
                    last_indiv_emmo_name.hasSetting.append(indiv_emmo_name)
            else:
                # pass
                print(f'Name not found2: {name_for_trans_check} \n with key_int {key_int}')
        else:
            print('Error')


def start_dict_to_emmo_individuals(dict_int, name_int, dict_of_excel_trans_int, emmo_int=emmo, test=False):
    new_name_int = []
    new_name_int.append(name_int.rstrip('.json').split(',')[0].replace('-', ' '))
    new_name_int.append(name_int.rstrip('.json').split(',')[1].replace(' ', '').replace('-', ' ').replace('+', '_'))
    if isinstance(dict_int['dict'], (dict, OrderedDict)):
        if ('FLUID MODELS' in name_int):
            if ('COMPONENT' not in name_int):
                test_2 = new_name_int[0], '-' + new_name_int[1] + '-'
                test = True
        change_names_in_dict_by_adding_prefix_2(dict_int['dict'], (new_name_int[0], '-' + new_name_int[1] + '-'))
        if ('FLUID MODELS' in name_int):
            if ('COMPONENT' not in name_int):
                test_2 = new_name_int[0], '-' + new_name_int[1] + '-'
                test = True
        if new_name_int[1] not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
            if new_name_int[0] + ' Individual' in {'FLOW DOMAIN FLUID MODELS Individual',
                                                   'FLOW DOMAIN SOLID MODELS Individual',
                                                   'FLOW DOMAIN DOMAIN MODELS Individual',
                                                   'FLOW DOMAIN SUBDOMAIN Individual'}:
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0])]]
                test_3 = True
            else:
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0] + ' Individual')]]
            emmo_indiv_class = search_for_index(indiv_class, list_of_emmo_classes(emmo_int))
            emmo_indiv_class(new_name_int[1])
        for i_1 in dict_int['Sims']:
            sim_name = i_1.replace('-', '_').replace(' ', '_')
            if sim_name not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
                emmo_int.MathematicalSimulations(sim_name)
            emmo_sim_name = search_for_index(sim_name, list_of_emmo_individuals(emmo_int))
            emmo_indiv_name = search_for_index(new_name_int[1], list_of_emmo_individuals(emmo_int))
            emmo_indiv_name.hasSimulation.append(emmo_sim_name)
        list_of_sims = [item.replace('-', '_').replace(' ', '_') for item in dict_int['Sims']]
        dict_to_emmo_individual(emmo_int, dict_int['dict'], dict_of_excel_trans_int, list_of_sims, new_name_int[1],
                                new_name_int[1])
    else:
        # print(name_int, ' has only str as dict_entry')
        if new_name_int[1] not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
            if new_name_int[0] + ' Individual' in {'FLOW DOMAIN FLUID MODELS Individual',
                                                   'FLOW DOMAIN SUBDOMAIN Individual'}:
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0])]]
            else:
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0] + ' Individual')]]
            emmo_indiv_class = search_for_index(indiv_class, list_of_emmo_classes(emmo_int))
            emmo_indiv_class(new_name_int[1])
        for i_1 in dict_int['Sims']:
            sim_name = i_1.replace('-', '_').replace(' ', '_')
            if sim_name not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
                emmo_int.MathematicalSimulations(sim_name)
            emmo_sim_name = search_for_index(sim_name, list_of_emmo_individuals(emmo_int))
            emmo_indiv_name = search_for_index(new_name_int[1], list_of_emmo_individuals(emmo_int))
            emmo_indiv_name.hasSimulation.append(emmo_sim_name)
        list_of_sims = [item.replace('-', '_').replace(' ', '_') for item in dict_int['Sims']]
        Data_prop_name_check = 'has' + new_name_int[0]
        if len(str(dict_int['dict']).split('[')) == 2:
            try:
                indiv_value = float(dict_int['dict'].split('[')[0])
            except:
                indiv_value = 'Error'
            indiv_unit = dict_int['dict'].split('[')[1].rstrip(']')
            with emmo_int:
                hasDataPropValue = types.new_class(Data_prop_name_check + 'Value', (owlready2.DataProperty,))
                hasDataPropValue.python_name = 'hasdataPropValue'
                emmo_indiv_name.hasdataPropValue.append(indiv_value)
                hasDataPropUnit = types.new_class(Data_prop_name_check + 'Unit', (owlready2.DataProperty,))
                hasDataPropUnit.python_name = 'hasdataPropUnit'
                emmo_indiv_name.hasdataPropUnit.append(indiv_unit)
        else:
            with emmo_int:
                hasDataProp = types.new_class(Data_prop_name_check, (owlready2.DataProperty,))
                hasDataProp.python_name = 'hasdataProp'
                emmo_indiv_name.hasdataProp.append(dict_int['dict'])
        pass
    return emmo_int


def create_and_link_property(prop_name_base, prop_type, indiv_source, indiv_target, emmo_int=emmo):
    if not prop_name_base:
        Object_prop_name_check = 'hasProgramSetting'
        inverse_object_prop_name_check = 'isProgramSettingOf'
    else:
        Object_prop_name_check = 'has' + prop_name_base
        inverse_object_prop_name_check = 'is' + prop_name_base + 'Of'
    with emmo_int:
        hasObjectProp = types.new_class(Object_prop_name_check, (prop_type,))
        hasObjectProp.prefLabel = [owlready2.locstr(Object_prop_name_check, lang='en')]
        hasObjectProp.python_name = Object_prop_name_check

        ##

        exec('emmo_int.%s.%s.append(emmo_int.%s)' % (
            indiv_source, Object_prop_name_check, indiv_target))  # dont use or change this function elsewhere

        ##

        if prop_type == owlready2.ObjectProperty:
            isinverseObjectProp = types.new_class(inverse_object_prop_name_check, (prop_type,))
            isinverseObjectProp.prefLabel = [owlready2.locstr(inverse_object_prop_name_check, lang='en')]
            isinverseObjectProp.python_name = inverse_object_prop_name_check
            # hasObjectProp.inverse_property = isinverseObjectProp

            ##
            test = (indiv_target, inverse_object_prop_name_check, indiv_source)
            exec('emmo_int.%s.%s.append(emmo_int.%s)' % (
                indiv_target, inverse_object_prop_name_check, indiv_source))  # dont use or change this function elsewhere

            ##
            # hasObjectProp.inverse_property = isinverseObjectProp
    return emmo_int

def create_and_link_inverse_property(prop_name_base, prop_type, indiv_source, indiv_target, emmo_int=emmo):
    if not prop_name_base:
        inverse_object_prop_name_check = 'isProgramSettingOf'
    else:
        inverse_object_prop_name_check = 'is' + prop_name_base + 'Of'
    if prop_type == owlready2.ObjectProperty:
        with emmo_int:
            isinverseObjectProp = types.new_class(inverse_object_prop_name_check, (prop_type,))
            isinverseObjectProp.prefLabel = [owlready2.locstr(inverse_object_prop_name_check, lang='en')]
            isinverseObjectProp.python_name = inverse_object_prop_name_check
            # hasObjectProp.inverse_property = isinverseObjectProp

            ##
            test = (indiv_target, inverse_object_prop_name_check, indiv_source)
            exec('emmo_int.%s.%s.append(emmo_int.%s)' % (
                indiv_target, inverse_object_prop_name_check, indiv_source))  # dont use or change this function elsewhere

            ##
    return emmo_int


def create_and_link_property2(prop_name_base, prop_type, indiv_source, indiv_target, emmo_int=emmo):
    if not prop_name_base:
        Object_prop_name_check = 'hasProgramSetting'
        inverse_object_prop_name_check = 'isProgramSettingOf'
    else:
        Object_prop_name_check = 'has' + prop_name_base
        inverse_object_prop_name_check = 'is' + prop_name_base + 'Of'
    with emmo_int:
        hasObjectProp = types.new_class(Object_prop_name_check, (prop_type,))
        hasObjectProp.prefLabel = [owlready2.locstr(Object_prop_name_check, lang='en')]
        hasObjectProp.python_name = Object_prop_name_check

        ##

        exec('emmo_int.%s.%s.append(emmo_int.%s)' % (
            indiv_source, Object_prop_name_check, indiv_target))  # dont use or change this function elsewhere

        ##

        if prop_type == owlready2.ObjectProperty:
            isinverseObjectProp = types.new_class(inverse_object_prop_name_check, (prop_type,))
            isinverseObjectProp.prefLabel = [owlready2.locstr(inverse_object_prop_name_check, lang='en')]
            isinverseObjectProp.python_name = inverse_object_prop_name_check
            # hasObjectProp.inverse_property = isinverseObjectProp

            ##
            test = (indiv_target, inverse_object_prop_name_check, indiv_source)
            exec('emmo_int.%s.%s.append(emmo_int.%s)' % (
                indiv_target, inverse_object_prop_name_check, indiv_source))  # dont use or change this function elsewhere

            ##
            hasObjectProp.inverse_property = isinverseObjectProp
    return emmo_int


def add_own_kpis_and_save_figs(all_sims_int):
    new_con_dict = dict()
    for i_1_int in all_sims_int:
        plt.close()
        try:
            dict_section_with_data_int = all_sims_int[i_1_int]['Solver']['Convergence History']['Iterations']
            data_dict = dict()
            data_dict.update({i_3_int: {'Rate': [], 'RMS Res': [], 'Max Res': []} for i_3_int in
                              dict_section_with_data_int['1']['Equation']})
            for i_2_int in 'Rate', 'RMS Res', 'Max Res':
                for i_4_int, i_5_int in enumerate(dict_section_with_data_int['1']['Equation']):
                    data_dict[i_5_int][i_2_int].extend([float(dict_section_with_data_int[i_6_int][i_2_int][
                                                                  dict_section_with_data_int['1']['Equation'].index(
                                                                      i_5_int)]) for i_6_int in
                                                        dict_section_with_data_int])
            for i_7_int in data_dict:
                data_dict[i_7_int].update({'Cleaned_Conv_without_Plateau': []})
                for i_8_int in data_dict[i_7_int]['RMS Res'][2:]:
                    if i_8_int > (data_dict[i_7_int]['RMS Res'][-1] * 1.5):
                        data_dict[i_7_int]['Cleaned_Conv_without_Plateau'].append(i_8_int)
                data_dict[i_7_int].update({'Convergence_Rate': np.divide(
                    np.add(np.array(data_dict[i_7_int]['Cleaned_Conv_without_Plateau'][1:]),
                           -np.array([data_dict[i_7_int]['RMS Res'][-1]] * len(
                               data_dict[i_7_int]['Cleaned_Conv_without_Plateau'][:-1]))),
                    np.add(np.array(data_dict[i_7_int]['Cleaned_Conv_without_Plateau'][:-1]),
                           -np.array([data_dict[i_7_int]['RMS Res'][-1]] * len(
                               data_dict[i_7_int]['Cleaned_Conv_without_Plateau'][:-1]))))})
                try:
                    data_dict[i_7_int].update({'min_Conv': data_dict[i_7_int]['Convergence_Rate'].min()})
                    data_dict[i_7_int].update({'max_Conv': data_dict[i_7_int]['Convergence_Rate'].max()})
                    data_dict[i_7_int].update({'arit_mean_Conv': data_dict[i_7_int]['Convergence_Rate'].mean()})
                    try:
                        data_dict[i_7_int].update({'geo_mean_Conv': np.power(np.prod(data_dict[i_7_int]['Convergence_Rate']),(1 / data_dict[i_7_int]['Convergence_Rate'].size))})
                    except:
                        pass
                    plt.ioff()
                    colors_int = ['r', 'y', 'c', 'g', 'b', 'k', 'm']
                    for i_15_int, i_10_int in enumerate(data_dict):
                        # plt.semilogy(range(len(data_dict[i_10_int]['Cleaned_Conv_without_Plateau'])),
                        #              data_dict[i_10_int]['Cleaned_Conv_without_Plateau'], color=colors_int[i_15_int])
                        plt.semilogy(range(len(data_dict[i_10_int]['RMS Res'])), data_dict[i_10_int]['RMS Res'], color='k')   #, color=colors_int[i_15_int])
                        plt.xlabel('Iterations [-]')
                        plt.ylabel('RMS Residual of [-]')
                        plt.grid(True)
                        plt.xlim(0,len(data_dict[i_10_int]['RMS Res']))
                        # plt.semilogy(range(len(data_dict[i_10_int]['RMS Res'])),
                        #              [data_dict[i_10_int]['RMS Res'][-1] for i in
                        #               range(len(data_dict[i_10_int]['RMS Res']))], color=colors_int[i_15_int], linestyle='--')
                        # plt.semilogy(range(len(data_dict[i_10_int]['RMS Res'])), data_dict[i_10_int]['RMS Res'][-1] * range(len(data_dict[i_10_int]['RMS Res'])))
                        # if data_dict[i_10_int]['arit_mean_Conv'] < 1:
                        #     plt.semilogy(range(len(data_dict[i_10_int]['Cleaned_Conv_without_Plateau'])), [
                        #         data_dict[i_10_int]['RMS Res'][0] * data_dict[i_10_int]['arit_mean_Conv'] ** i_11_int
                        #         for i_11_int in range(len(data_dict[i_10_int]['Cleaned_Conv_without_Plateau']))], '-.')
                        # plt.savefig(f'images/figure_{i_1_int}.pdf', dpi=300)
                        test = f'images/figure_{i_1_int}_{i_10_int}.png'
                        plt.savefig(f'images/figure_{i_1_int}_{i_10_int}.png', dpi=300, bbox_inches = "tight")
                        plt.close()
                except:
                    pass
            new_con_dict.update({i_1_int: data_dict})
        except KeyError as err:
            print('KeyError for', i_1_int, 'missing key: ', err)
        except SyntaxError as err2:
            print('SyntaxError for', i_1_int, 'has: ', err2)

    return new_con_dict


def return_sub_dict_and_path_2(dictionary, keyword):
    if type(dictionary) == dict or type(dictionary) == collections.OrderedDict:
        for key_1, value_1 in dictionary.items():
            if keyword == key_1:
                return value_1, key_1
            else:
                if return_sub_dict_and_path_2(value_1, keyword) is not None:
                    a_1, b_1 = return_sub_dict_and_path_2(value_1, keyword)
                    if type(b_1) == str:
                        return a_1, (key_1,) + (b_1,)
                    else:
                        return a_1, (key_1,) + tuple(list(b_1))


def return_path(dictionary, keyword):
    if isinstance(dictionary, (dict, OrderedDict)):
        for key_1, value_1 in dictionary.items():
            if keyword == key_1:
                return key_1
            else:
                if return_sub_dict_and_path_2(value_1, keyword) is not None:
                    b_1 = return_sub_dict_and_path_2(value_1, keyword)
                    if type(b_1) == str:
                        return (key_1,) + (b_1,)
                    else:
                        return (key_1,) + tuple(list(b_1))


def add_multiple_tuples_to_tuple(list_of_tuples):
    new_tuple = tuple()
    for i in list_of_tuples:
        new_tuple = add_tuples_and_str_to_tuple_or_str(new_tuple, i)
    return new_tuple


def check_if_tuple_in_dict_return_path(dict_int, tuple_tbc_int, dict_of_prev_inst_int_1, bool_for_named_inst):
    if not dict_of_prev_inst_int_1:
        dict_of_prev_inst_int = {'': {'Key_Tuples': tuple(),
                                      'Inst_Tuples': tuple(),
                                      'Path_Tuples': ('CFX Command Language for Run',)
                                      }}
    else:
        dict_of_prev_inst_int = dict_of_prev_inst_int_1
    dict_of_next_inst = dict()
    for i in dict_of_prev_inst_int:
        path_tuples = dict_of_prev_inst_int[i]['Path_Tuples']
        sub_dict_int = return_subdict(dict_int, path_tuples)
        if bool_for_named_inst:
            if return_sub_dict_and_path_2(sub_dict_int, tuple_tbc_int):
                dict_int_2, path_tuple = return_sub_dict_and_path_2(sub_dict_int, tuple_tbc_int)
                for i_2 in dict_int_2:
                    key_name = (i + '+' + i_2).lstrip('+')
                    dict_of_next_inst[key_name] = copy.deepcopy(dict_of_prev_inst_int[i])
                    dict_of_next_inst[key_name]['Key_Tuples'] = dict_of_next_inst[key_name]['Key_Tuples'] + (i_2,)
                    dict_of_next_inst[key_name]['Path_Tuples'] = add_multiple_tuples_to_tuple(
                        [dict_of_next_inst[key_name]['Path_Tuples'], path_tuple, (i_2,)])
                    dict_of_next_inst[key_name]['Inst_Tuples'] = add_tuples_and_str_to_tuple_or_str(
                        dict_of_next_inst[key_name]['Inst_Tuples'], tuple_tbc_int)

        else:
            if return_sub_dict_and_path_2(sub_dict_int, tuple_tbc_int):
                key_name = (i + '+' + tuple_tbc_int).lstrip('+')
                to_be_discarded, path_tuple = return_sub_dict_and_path_2(sub_dict_int, tuple_tbc_int)
                dict_of_next_inst[key_name] = dict_of_prev_inst_int[i]
                dict_of_next_inst[key_name]['Key_Tuples'] = \
                    dict_of_next_inst[key_name]['Key_Tuples'] + (tuple_tbc_int,)
                dict_of_next_inst[key_name]['Path_Tuples'] = \
                    add_multiple_tuples_to_tuple([dict_of_next_inst[key_name]['Path_Tuples'], path_tuple])
                dict_of_next_inst[key_name]['Inst_Tuples'] = add_tuples_and_str_to_tuple_or_str(
                    dict_of_next_inst[key_name]['Inst_Tuples'], tuple_tbc_int)
    return dict_of_next_inst


def change_list_of_tuples_to_list_of_str(list_of_tuples):
    for i_1, i_2 in enumerate(list_of_tuples):
        if isinstance(i_2, tuple):
            new_str_for_list = ''
            for i_3 in i_2:
                new_str_for_list += ' ' + i_3
            list_of_tuples[i_1] = new_str_for_list.lstrip(' ')
    return list_of_tuples


def check_if_key_str_is_name_inst(key_str_int, list_of_named_inst_int):
    if any([(True if i_2 == key_str_int else False) for i_2 in list_of_named_inst_int]):
        return True
    else:
        return False


def new_dicts_to_individualdicts(dict_int, list_of_keys_tbc, tuple_list_of_named_inst_int,
                                 tuple_list_of_non_named_inst_int, all_dicts_int, path_int):
    str_list_of_named_inst_int = change_list_of_tuples_to_list_of_str(tuple_list_of_named_inst_int)
    str_list_of_non_named_inst_int = change_list_of_tuples_to_list_of_str(tuple_list_of_non_named_inst_int)
    out_dict = dict()
    for i in list_of_keys_tbc:
        if i == 'EXPRESSIONS':
            test = True
        else:
            test = False
        name_tbc = ''
        dict_of_inst_int = dict()
        if isinstance(i, str):
            dict_of_inst_int = check_if_tuple_in_dict_return_path(dict_int, i, dict_of_inst_int,
                                                                  check_if_key_str_is_name_inst(i,
                                                                                                str_list_of_named_inst_int))
            # print(name_tbc, i, check_if_key_str_is_name_inst(name_tbc, str_list_of_named_inst_int))
            pass
        else:
            for i_1, i_2 in enumerate(i):
                name_tbc = ' '.join([name_tbc, i_2]).lstrip(' ')
                dict_of_inst_int = check_if_tuple_in_dict_return_path(dict_int, i_2, dict_of_inst_int,
                                                                      check_if_key_str_is_name_inst(name_tbc,
                                                                                                    str_list_of_named_inst_int))
                # print(name_tbc, i[:i_1 + 1], check_if_key_str_is_name_inst(name_tbc, str_list_of_named_inst_int))

        search_for_name_in_outdict_and_save(all_dicts_int, dict_of_inst_int, path_int)


def search_for_name_in_outdict_and_save(all_sims_int, outdict_int, path_int):
    # test_list = list()
    for i in outdict_int:
        name_inst = '-'.join(outdict_int[i]['Inst_Tuples']) + ',' + str(i)
        tuple_path = outdict_int[i]['Path_Tuples']
        list_of_individuals = []
        for i_2 in all_sims_int:
            if return_subdict(all_sims_int[i_2], tuple_path):
                sub_dict_int = return_subdict(all_sims_int[i_2], tuple_path)
                list_of_individuals = search_for_inst_in_inst_dict_2(
                    sub_dict_int, name_inst,
                    list_of_individuals, i_2)
        for i_1 in list_of_individuals:
            # test_list.append(i_1)
            try:
                os.makedirs(path_int)
            except:
                pass
            with open(path_int + i_1[0] + ".json", "w") as out_file:
                json.dump({'dict': i_1[2], 'Sims': i_1[1], 'Tuple': outdict_int[i]['Path_Tuples']}, out_file)
            # print(i_1[0])
    # for i_3 in test_list:
    #     print(i_3)
    # return test_list


def search_for_inst_in_inst_dict_2(dict_to_be_appended_int, ind_name, dict_of_individual_a, sim_name):
    if not dict_of_individual_a:
        dict_of_individual_a.append(
            [ind_name + '_' + str(len(dict_of_individual_a)), [sim_name], dict_to_be_appended_int])
    elif dict_to_be_appended_int not in [i_int[2] for i_int in dict_of_individual_a]:
        dict_of_individual_a.append(
            [ind_name + '_' + str(len(dict_of_individual_a)), [sim_name], dict_to_be_appended_int])
    elif dict_to_be_appended_int in [i_int[2] for i_int in dict_of_individual_a]:
        for i_int in dict_of_individual_a:
            if dict_to_be_appended_int == i_int[2]:
                if sim_name not in i_int[1]:
                    i_int[1].append(sim_name)
    return dict_of_individual_a


def change_name_of_sub_sub_inst_2(all_sims, sub_sub_dict_folder_path, tuple_list_of_named_inst_int):
    str_list_of_named_inst_int = change_list_of_tuples_to_list_of_str(tuple_list_of_named_inst_int)
    modified_all_sims = copy.deepcopy(all_sims)
    for root_3, dirs_3, files_3 in os.walk(sub_sub_dict_folder_path):
        for name_3 in files_3:
            with open(root_3 + str('/') + name_3, 'r') as in_file:
                loaded_json = json.load(in_file)
                for i_1_int in modified_all_sims:
                    if i_1_int in loaded_json['Sims']:  # todo
                        tuple_int = loaded_json['Tuple']
                        if check_if_key_str_is_name_inst(name_3.split(',')[0], str_list_of_named_inst_int):
                            swap_dict_individual_2(tuple_int, modified_all_sims[i_1_int], name_3)
                        else:
                            swap_dict_individual_2(tuple_int[:-1], modified_all_sims[i_1_int], name_3)
    return modified_all_sims


def find_rename_and_replace_inst_dict(dict_int, list_instances_tbc, tuple_list_of_named_inst_int,
                                      tuple_list_of_non_named_inst_int, path_int):
    merged_dict_int = create_merged_dict(copy.deepcopy(dict_int))
    new_dicts_to_individualdicts(merged_dict_int, list_instances_tbc, tuple_list_of_named_inst_int,
                                 tuple_list_of_non_named_inst_int, dict_int, path_int)
    out_dict_int = change_name_of_sub_sub_inst_2(dict_int, path_int, tuple_list_of_non_named_inst_int)
    return out_dict_int


def archiv_and_change_all_instances(dict_of_ordered_instances, dict_int, tuple_list_of_named_inst_int,
                                    tuple_list_of_non_named_inst_int):
    dict_to_be_changed = copy.deepcopy(dict_int)
    for i in dict_of_ordered_instances:
        list_instances_tbc = dict_of_ordered_instances[i]['list_instances_tbc']
        path_int = dict_of_ordered_instances[i]['path']
        dict_to_be_changed = find_rename_and_replace_inst_dict(dict_to_be_changed, list_instances_tbc,
                                                               tuple_list_of_named_inst_int,
                                                               tuple_list_of_non_named_inst_int, path_int)


def swap_dict_individual_2(tuple_keys, dict_int, ind_name):
    if tuple_keys:
        if len(tuple_keys) >= 2:
            dict_int[tuple_keys[0]] = swap_dict_individual_2(tuple_keys[1:], dict_int[tuple_keys[0]], ind_name)
            return dict_int
        else:
            if 'Individuals_json_Links' not in dict_int[tuple_keys[0]].keys():
                dict_int[tuple_keys[0]]['Individuals_json_Links'] = ind_name
            else:
                if isinstance(dict_int[tuple_keys[0]]['Individuals_json_Links'], str):
                    dict_int[tuple_keys[0]]['Individuals_json_Links'] = [
                        dict_int[tuple_keys[0]]['Individuals_json_Links'], ind_name]
                else:
                    dict_int[tuple_keys[0]]['Individuals_json_Links'].append(ind_name)
            try:
                del dict_int[tuple_keys[0]][ind_name.split(',')[-1].rstrip('.json').split('+')[-1].split('_')[0]]
            except:
                test = True
            # dict_int[tuple_keys[0]]] = ind_name # oldest and definetly wrong structure since it only generates one link
            test = True
            return dict_int
    else:
        print('Error: tuple is Empty')


def search_instance_folder_and_insert_into_emmo(path_int, dict_of_excel_translator_int, tuple_list_of_named_inst_int,
                                                tuple_list_of_non_named_inst_int, emmo_int=emmo):
    temp_list = copy.deepcopy(tuple_list_of_named_inst_int)
    list_of_named_inst_int = change_list_of_tuples_to_list_of_str(temp_list)
    temp_list_2 = copy.deepcopy(tuple_list_of_non_named_inst_int)
    list_of_non_named_inst_int = change_list_of_tuples_to_list_of_str(temp_list_2)
    list_of_inst_int = list_of_named_inst_int + list_of_non_named_inst_int
    for root_3, dirs_3, files_3 in os.walk(path_int):
        for name_3 in files_3:
            with open(root_3 + str('/') + name_3, 'r') as in_file:
                dict_for_emmo_instances = json.load(in_file)
            start_dict_to_emmo_individuals_2(dict_for_emmo_instances, name_3, dict_of_excel_translator_int,
                                             list_of_inst_int, emmo_int, test=False)
    return emmo_int


def change_filepath_name_in_dict(dict_int):
    for k_int, v_int in list(dict_int.items()):
        if ' = ' in k_int:
            # test = k_int.split(' = ')[0].rstrip(' ')
            # print(f'k_int : {k_int} \n k_int.split() : {test}')
            try:
                dict_int[k_int.split(' = ')[0].rstrip(' ')] = k_int.split(' = ')[1].lstrip(' ') + list(v_int.keys())[0]
            except:
                test =1
            del dict_int[k_int]
        elif isinstance(v_int, (dict, OrderedDict)):
            change_filepath_name_in_dict(v_int)


def change_names_in_dict_by_adding_prefix_3(dictionary, list_of_names_to_be_preffixed, list_of_inst_int):
    dict_int = dictionary
    for k_1, v_1 in list(dict_int.items()):
        if type(v_1) is dict:
            if any([(True if i_2 == k_1 else False) for i_2 in list_of_inst_int]):
                test = list([([i_2, k_1] if i_2 == k_1 else '') for i_2 in list_of_inst_int])
                test = True
                list_of_names_to_be_preffixed = (k_1, list_of_names_to_be_preffixed[-1],)
                dict_int[k_1 + ' ' +list_of_names_to_be_preffixed[-1]] = \
                    change_names_in_dict_by_adding_prefix_3(v_1, list_of_names_to_be_preffixed, list_of_inst_int)
                # dict_int[' '.join([k_1, list_of_names_to_be_preffixed[-1]]) + ' ' + k_1] = \
                #     change_names_in_dict_by_adding_prefix_3(v_1, list_of_names_to_be_preffixed_1, list_of_inst_int)
                dict_int.pop(k_1)
                pass
            else:
                dict_int[' '.join(list_of_names_to_be_preffixed) + ' ' + k_1] = \
                    change_names_in_dict_by_adding_prefix_3(v_1, list_of_names_to_be_preffixed, list_of_inst_int)
                dict_int.pop(k_1)
            test_1 = dictionary
        else:
            if '.json Option' in k_1:
                dict_int[' '.join(list_of_names_to_be_preffixed) + ' ' + 'Individual Option'] = dict_int.pop(k_1)
            else:
                dict_int[' '.join(list_of_names_to_be_preffixed) + ' ' + ''.join(k_1)] = dict_int.pop(k_1)
    return dict_int

def start_dict_to_emmo_individuals_2(dict_int, name_int, dict_of_excel_trans_int, list_of_named_inst_int, emmo_int=emmo, test=False):
    new_name_int = []
    new_name_int.append(name_int.rstrip('.json').split(',')[0].replace('-', ' '))
    new_name_int.append(name_int.rstrip('.json').split(',')[1].title().replace(' ', '').replace('-', ' ').replace('+', '_'))  #todo check where the second .title() needs to be
    if isinstance(dict_int['dict'], (dict, OrderedDict)):
        change_names_in_dict_by_adding_prefix_3(dict_int['dict'], (new_name_int[0], '-' + new_name_int[1] + '-'), list_of_named_inst_int)
        if new_name_int[1] not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
            # if new_name_int[0] + ' Individual' in {'FLOW DOMAIN FLUID MODELS Individual',
            #                                        'FLOW DOMAIN SOLID MODELS Individual',
            #                                        'FLOW DOMAIN DOMAIN MODELS Individual',
            #                                        'FLOW DOMAIN SUBDOMAIN Individual'}:
            #     indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
            #         list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0])]]
            #     test_3 = True
            # else:
            #     indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
            #         list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0] + ' Individual')]]:
            indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0] + ' Individual')]]
            emmo_indiv_class = search_for_index(indiv_class, list_of_emmo_classes(emmo_int))
            emmo_indiv_class(new_name_int[1])
        for i_1 in dict_int['Sims']:
            sim_name = i_1.replace('-', '_').replace(' ', '_').replace(',', '__').replace('.','__')
            if sim_name not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
                emmo_int.MathematicalSimulations(sim_name)
            emmo_sim_name = search_for_index(sim_name, list_of_emmo_individuals(emmo_int))
            emmo_indiv_name = search_for_index(new_name_int[1], list_of_emmo_individuals(emmo_int))
            emmo_indiv_name.hasSimulation.append(emmo_sim_name)
            emmo_sim_name.isSimulationOf.append(emmo_indiv_name)
        list_of_sims = [item.replace('-', '_').replace(' ', '_').replace(',', '__').replace('.','__') for item in dict_int['Sims']]
        dict_to_emmo_individual(emmo_int, dict_int['dict'], dict_of_excel_trans_int, list_of_sims, new_name_int[1],
                                new_name_int[1])
    else:
        # print(name_int, ' has only str as dict_entry')
        if new_name_int[1] not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
            if new_name_int[0] + ' Individual' in {'FLOW DOMAIN FLUID MODELS Individual',
                                                   'FLOW DOMAIN SUBDOMAIN Individual'}:
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0])]]
            else:
                indiv_class = dict_of_excel_trans_int['Onto_name'][list(dict_of_excel_trans_int['Dict_name'].keys())[
                    list(dict_of_excel_trans_int['Dict_name'].values()).index(new_name_int[0] + ' Individual')]]
            emmo_indiv_class = search_for_index(indiv_class, list_of_emmo_classes(emmo_int))
            emmo_indiv_class(new_name_int[1])
        for i_1 in dict_int['Sims']:
            sim_name = i_1.replace('-', '_').replace(' ', '_').replace(',', '__').replace('.','__')
            if sim_name not in [item[0] for item in list_of_emmo_individuals(emmo_int)]:
                emmo_int.MathematicalSimulations(sim_name)
            emmo_sim_name = search_for_index(sim_name, list_of_emmo_individuals(emmo_int))
            emmo_indiv_name = search_for_index(new_name_int[1], list_of_emmo_individuals(emmo_int))
            emmo_indiv_name.hasSimulation.append(emmo_sim_name)
            emmo_sim_name.isSimulationOf.append(emmo_indiv_name)
        list_of_sims = [item.replace('-', '_').replace(' ', '_').replace(',', '__').replace('.','__') for item in dict_int['Sims']]
        Data_prop_name_check = 'has' + new_name_int[0].title()
        if len(str(dict_int['dict']).split('[')) == 2:
            try:
                indiv_value = float(dict_int['dict'].split('[')[0])
            except:
                indiv_value = 'Error'
            indiv_unit = dict_int['dict'].split('[')[1].rstrip(']')
            with emmo_int:
                hasDataPropValue = types.new_class(Data_prop_name_check + 'Value', (owlready2.DataProperty,))
                hasDataPropValue.python_name = 'hasdataPropValue'
                emmo_indiv_name.hasdataPropValue.append(indiv_value)
                hasDataPropUnit = types.new_class(Data_prop_name_check + 'Unit', (owlready2.DataProperty,))
                hasDataPropUnit.python_name = 'hasdataPropUnit'
                emmo_indiv_name.hasdataPropUnit.append(indiv_unit)
        else:
            with emmo_int:
                hasDataProp = types.new_class(Data_prop_name_check, (owlready2.DataProperty,))
                hasDataProp.python_name = 'hasdataProp'
                emmo_indiv_name.hasdataProp.append(dict_int['dict'])
        pass
    return emmo_int


def create_add_and_save_KPIs_in_ontology_and_images(dict_int, emmo = emmo):
    with emmo:
        KPIs = add_own_kpis_and_save_figs(dict_int)
        for i_int in KPIs:
            sim_name = i_int.replace('-', '_').replace(' ', '_').replace(',', '__').replace('.','__')
            emmo_sim_name = search_for_index(sim_name, list_of_emmo_individuals(emmo))
            # try:
            for i_int_2 in KPIs[i_int]:
                for i_int_4 in ['Rate', 'RMS Res', 'Max Res', 'Convergence_Rate']:
                    try:
                        with emmo:
                            DataPropName = ('hasFinal' + i_int_2 + i_int_4 + 'Value').replace(' ', '').replace('-', '')
                            hasDataProp = types.new_class(DataPropName, (owlready2.DataProperty,))
                            hasDataProp.python_name = DataPropName
                            if not ((i_int_4 == 'Convergence_Rate') & (not isinstance(KPIs[i_int][i_int_2][i_int_4], list))):
                                exec('%s.%s.append(%s)' % (emmo_sim_name, DataPropName, KPIs[i_int][i_int_2][i_int_4][-1]))
                    except KeyError:
                        print(i_int, i_int_4, KeyError)
                for i_int_5 in ['max_Conv', 'arit_mean_Conv', 'geo_mean_Conv']:
                    if i_int_5 in KPIs[i_int][i_int_2].keys():
                        with emmo:
                            DataPropName = ('has' + i_int_2 + i_int_5 + 'Value').replace(' ', '').replace('-', '')
                            hasDataProp = types.new_class(DataPropName, (owlready2.DataProperty,))
                            hasDataProp.python_name = DataPropName
                            exec('%s.%s.append(%s)' % (emmo_sim_name, DataPropName, KPIs[i_int][i_int_2][i_int_5]))
    return KPIs, emmo
