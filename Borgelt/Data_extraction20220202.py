import collections
import os
import numpy as np
import json
import matplotlib.pyplot as plt
from collections import OrderedDict
import re
import time


def segmenting_convergence(section_convergence):
    section_div_conv = []
    for line_con_1 in range(len(section_convergence)):
        if '===' in section_convergence[line_con_1]:
            section_div_conv.append(line_con_1)
        elif 'CFD' in section_convergence[line_con_1]:
            section_div_conv.append(line_con_1)
    return section_div_conv


def trimming_sections_conv(section_div_conv, section_convergence):
    dict_conv_sec = {}
    for secs_conv in range(len(section_div_conv) - 1):
        # todo function split_conv_sections
        next_section_conv = section_convergence[(section_div_conv[secs_conv] + 1):(section_div_conv[secs_conv + 1] - 1)]
        dict_conv_sec_next = {secs_conv: next_section_conv}
        dict_conv_sec.update(dict_conv_sec_next)
    return dict_conv_sec


def segmenting_sections_conv(dict_conv_sec):
    dict_conv_time = {}
    dict_conv_loop = {}
    n_conv_time = 0
    n_conv_loop = 0
    list_of_convergence_segments = []
    for dict_len in range(len(dict_conv_sec) - 1):
        if 'Timescale' in dict_conv_sec[dict_len][0]:
            n_conv_time += 1
            dict_conv_time.update({n_conv_time: dict_conv_sec[dict_len][:]})
            list_of_convergence_segments.append('Timescale')
        elif 'OUTER LOOP' in dict_conv_sec[dict_len][0]:
            n_conv_loop += 1
            dict_conv_loop.update({n_conv_loop: dict_conv_sec[dict_len][:]})
            list_of_convergence_segments.append('OUTER LOOP')
    return dict_conv_time, dict_conv_loop, list_of_convergence_segments


def convergence_internal_to_dict_iterations(dict_conv_loop):
    dict_conv_loop_it = {}
    for len_dict_loop in range(len(dict_conv_loop)):
        number_loop = dict_conv_loop[len_dict_loop + 1][0][
                      :dict_conv_loop[len_dict_loop + 1][0].index('C')].strip().split(
            '=')
        CPU_time_loop = dict_conv_loop[len_dict_loop + 1][0][
                        dict_conv_loop[len_dict_loop + 1][0].index('C') - 1:].strip().split(
            '=')
        number_loop = [s.strip() for s in number_loop]
        CPU_time_loop = [s.strip() for s in CPU_time_loop]
        dict_conv_loop_it.update(
            {(len_dict_loop + 1): {number_loop[0]: number_loop[1], CPU_time_loop[0]: CPU_time_loop[1]}})
        int_list_dict_loop = []
        for len_dict_loop_int in range(len(dict_conv_loop[len_dict_loop + 1]) - 1):
            if '----' not in dict_conv_loop[len_dict_loop + 1][len_dict_loop_int + 1]:
                dict_conv_loop_int = dict_conv_loop[len_dict_loop + 1][len_dict_loop_int + 1].strip()[1:-1].split('|')
                dict_conv_loop_int = [s.strip() for s in dict_conv_loop_int]
                int_list_dict_loop.append(dict_conv_loop_int)
        for i in list(int_list_dict_loop[1:]):
            if len(i) == 1:
                int_list_dict_loop.pop(int_list_dict_loop.index(i))
                test_12345 = i
        test_123 = int_list_dict_loop[1:]
        numpy_array = np.array(int_list_dict_loop[1:]).T.tolist()
        dict_out_loop = dict(zip(int_list_dict_loop[0], numpy_array))
        dict_conv_loop_it[len_dict_loop + 1].update(dict_out_loop)
    return dict_conv_loop_it


def convergence_internal_to_dict_time(dict_conv_time,
                                      pos_number):
    dict_conv_time_it = {}
    for len_dict_time in range(len(dict_conv_time)):
        dict_conv_time_it.update(
            {(len_dict_time + 1): {'TIMESCALE': pos_number[len_dict_time]}})
        int_list_dict_time = []
        for len_dict_time_int in range(len(dict_conv_time[len_dict_time + 1]) - 1):
            if '----' not in dict_conv_time[len_dict_time + 1][len_dict_time_int + 1]:
                dict_conv_time_int = dict_conv_time[len_dict_time + 1][len_dict_time_int + 1].strip()[1:-1].split('|')
                dict_conv_time_int = [s.strip() for s in dict_conv_time_int]
                int_list_dict_time.append(dict_conv_time_int)
        numpy_array = np.array(int_list_dict_time[1:]).T.tolist()
        dict_out_time = dict(zip(int_list_dict_time[0], numpy_array))
        dict_conv_time_it[len_dict_time + 1].update(dict_out_time)
    return dict_conv_time_it


def finding_sub_sub_sections_in_convergence(convergence_section):
    convergence_dict = []
    segmenting_line = [0]
    sections = []
    for lines_1 in range(len(convergence_section)-2):
        if bool(re.search('[=]{70}', convergence_section[lines_1])) & bool(re.search('[=]{70}', convergence_section[lines_1+2])):
            # print('True')
            sub_sub_section_key = convergence_section[lines_1+1].strip()
            segmenting_line.append(lines_1 + 1)
            # print(sub_sub_section_key)
    segmenting_line.append(len(convergence_section))
    # print('len:', len(convergence_section), 'segmenting_line:', segmenting_line)
    for lines_2 in range(len(segmenting_line)-1):
        sections.append(convergence_section[segmenting_line[lines_2]: segmenting_line[lines_2+1]])
        if bool(re.search('[=]{70}', sections[lines_2][-1])):
            sections[lines_2].pop(-1)
    return sections


def convergence_list_to_position_numbers(list_of_convergence_segments):
    pos_number = []
    for line in range(len(list_of_convergence_segments)):
        if 'Timescale' in list_of_convergence_segments[line]:
            pos_number.append(line-len(pos_number))
    return pos_number


def convergence_to_dict(section_convergence):
    subsubsections = finding_sub_sub_sections_in_convergence(section_convergence)
    section_div_conv = segmenting_convergence(subsubsections[0])
    dict_conv_sec = trimming_sections_conv(section_div_conv, section_convergence)
    dict_conv_time, dict_conv_loop, list_of_convergence_segments = segmenting_sections_conv(dict_conv_sec)
    dict_conv_loop_it = convergence_internal_to_dict_iterations(dict_conv_loop)
    pos_number = convergence_list_to_position_numbers(list_of_convergence_segments)
    dict_conv_time_it = convergence_internal_to_dict_time(dict_conv_time, pos_number)
    dict_out = {}
    dict_out.update({'Iterations': dict_conv_loop_it, 'Timescale': dict_conv_time_it, 'CPU':
        {section_convergence[-2].split(':')[0].strip(): section_convergence[-2].split(':')[-1].strip(),
         section_convergence[-1].split(':')[0].strip(): section_convergence[-1].split(':')[-1].strip()}})
    return dict_out


def line_to_diction_comm_lang(line_lang):
    if ':' in line_lang:
        a = line_lang.split(':')
    elif '=' in line_lang:
        a = line_lang.split('=')
    else:
        line_lang = line_lang + '= ERROR'
        a = line_lang.split('=')
    if a[1].strip() == '':
        a[1] = 'EMPTY'
        # print(line)
    dict_from_line = {a[0].strip(): a[1].lstrip()}
    return dict_from_line


def update_key(to_be_updated_dict, content_dict, key, *subkey):
    if subkey:
        to_be_updated_dict[key][subkey[0]].update(content_dict)
    elif to_be_updated_dict[key] != 'EMPTY':
        to_be_updated_dict[key].update(content_dict)
    else:
        to_be_updated_dict[key] = content_dict
    return to_be_updated_dict


def get_subsection_comm_lang(section_g):
    # leng = 0
    found_type_int_fun = True
    current_indentation_fun = len(section_g[0]) - len(section_g[0].lstrip())
    sub_section = []
    for line_int in range(len(section_g)):
        indentation = len(section_g[line_int]) - len(section_g[line_int].lstrip())
        if found_type_int_fun:
            if 'END' in section_g[line_int] and (indentation == current_indentation_fun):
                t_line_int = section_g[line_int].rstrip('\n')
                sub_section.append(t_line_int)
                found_type_int_fun = False
                break
            elif indentation < current_indentation_fun:
                break
            else:
                t_line_int = section_g[line_int].rstrip('\n')
                sub_section.append(t_line_int)
    # print('Subsection:', sub_section[0])
    # print('Subsection:', sub_section[-1])
    # if 'END' in sub_section[-1]:
    #     sub_section = sub_section[:-1]
    # leng = 1
    return sub_section  # , leng


def comm_lang_to_dict(section, indent_current):
    to_be_updated = False
    section_int = section
    section_indent = indent_current + 2
    dict_test = OrderedDict()
    last_key = []
    dict_test_indent = OrderedDict()
    last_sub_key = []
    while section_int:
        current_indent = len(section_int[0]) - len(section_int[0].strip())
        if dict_test_indent == OrderedDict():
            pass
        elif last_sub_key:
            dict_test = update_key(dict_test, dict_test_indent, last_key, last_sub_key)
        else:
            dict_test = update_key(dict_test, dict_test_indent, last_key)

        if 'END' in section_int[0]:
            section_int.pop(0)
        elif not section_indent < current_indent:  # parallel
            check_existing_keys = list(line_to_diction_comm_lang(section_int[0]))[0]  # Library, Flow, Flow, Command file, Simulation Control
            if check_existing_keys in dict_test.keys():  # if key already exists create NEW subkey
                try:
                    dict_test[check_existing_keys][last_sub_key].update(dict_test_indent)
                except:
                    test =1
                dict_test[check_existing_keys].update({list(line_to_diction_comm_lang(section_int[0]).items())[-1][-1]:
                                               OrderedDict()})
                last_key = check_existing_keys
                last_sub_key = list(line_to_diction_comm_lang(section_int[0]).items())[-1][-1]
            elif bool(list(line_to_diction_comm_lang(section_int[0]).items())[-1][-1] != 'EMPTY') & bool(re.search(':', section_int[0])):
                # if key not empty create FIRST subkey
                dict_test.update({list(line_to_diction_comm_lang(section_int[0]))[-1]:
                                      {list(line_to_diction_comm_lang(section_int[0]).items())[-1][-1]:
                                           OrderedDict()}})
                last_key = check_existing_keys
                last_sub_key = list(line_to_diction_comm_lang(section_int[0]).items())[-1][-1]
            else:
                dict_test.update({list(line_to_diction_comm_lang(section_int[0]))[0]: list((line_to_diction_comm_lang(section_int[0])).items())[-1][-1]})
                last_key = check_existing_keys
                last_sub_key = []
            dict_test_indent = OrderedDict()
            section_int.pop(0)

        else:  # indented
            next_section = get_subsection_comm_lang(section_int)
            next_section_key = list(line_to_diction_comm_lang(next_section[0]).items())[0][0]
            len_int = len(next_section)
            if next_section_key in dict_test_indent.keys():
                dict_test_indent[next_section_key].update(comm_lang_to_dict(next_section, section_indent)[next_section_key])
            else:
                dict_test_indent = comm_lang_to_dict(next_section, section_indent)
                # print(dict_test_indent)
            del section_int[:len_int]
    if dict_test_indent == OrderedDict():
        pass
    elif last_sub_key:
        dict_test = update_key(dict_test, dict_test_indent, last_key, last_sub_key)
    else:
        dict_test = update_key(dict_test, dict_test_indent, last_key)
    return dict_test


def file_to_section(path):
    section_all = []
    for file in os.listdir(path):
        if (file.endswith('.out')):
            outfile = open(os.path.join(path, file))
            print(outfile)
    with outfile as f_all:
        for line_all in f_all:
            t_line_all = str(line_all).rstrip('\n')
            section_all.append(t_line_all)
        file_out = file.split('.')[0]
    return section_all, file_out


def file_to_section_2(files_int):
    section_all = []
    for file in files_int:
        outfile = open(file)
        with outfile as f_all:
            for line_all in f_all:
                t_line_all = str(line_all).rstrip('\n')
                section_all.append(t_line_all)
            file_out = file.split('.')[0]
    return section_all, file_out


class Segmenting:
    def __init__(self, section):
        self.section = section
        self.line = []
        self.statement = []
        self.check, self.keyword = self.check_and_return_main_sections()

    @staticmethod
    def test_line_for_keyword_start_and_ending(section_line):
        statement = False
        if section_line:
            if bool('+' in section_line[-1]):  # & bool('+' in Section_all[line][0]):
                if section_line[1]:
                    if '+' in section_line[1]:
                        if not section_line[2:-2].strip('-'):
                            statement = True
        return statement

    @staticmethod
    def test_line_for_keyword_spacing(section_line):
        statement = False
        if section_line:
            if bool('|' in section_line[-1]):
                if section_line[1]:
                    if '|' in section_line[1]:
                        if not section_line[2:-2].strip():
                            statement = True
        return statement

    def check_and_return_main_sections(self):
        check = False
        keyword = []
        if self.test_line_for_keyword_start_and_ending(self.section[0]) & self.test_line_for_keyword_start_and_ending(self.section[4]):
            if self.test_line_for_keyword_spacing(self.section[1]) & self.test_line_for_keyword_spacing(self.section[3]):
                if self.section[3]:
                    if not bool('--' in self.section[2].strip().lstrip('|').rstrip('|')):
                        keyword = self.section[2].strip().lstrip('|').rstrip('|').strip()
                        check = True
        return check, keyword

    def check_and_return_subsection(self):
        check = False
        keyword = []
        if bool('' in self.section[0]) & bool('' in self.section[4]):
            if self.test_line_for_keyword_start_and_ending(self.section[1]) & self.test_line_for_keyword_start_and_ending(self.section[3]):
                if self.section[2]:
                    if not (bool('--' in self.section[2].strip().lstrip('|').rstrip('|')) | bool('|' in self.section[2].strip().lstrip('|').rstrip('|'))):
                        keyword = self.section[2].strip().lstrip('|').rstrip('|').strip()
                        check = True
        return check, keyword


def dividing_into_sections(out_file):
    dividing_lines = []
    dividing_lines_header = ['Initialization']
    for line in range(len(out_file) - 5):
        test = Segmenting(out_file[line:line+5])
        if test.check_and_return_main_sections()[0]:
            dividing_lines.append(line+2)
            dividing_lines_header.append(test.check_and_return_main_sections()[1])
    dividing_lines.append(len(out_file))
    return dividing_lines, dividing_lines_header


def determining_subsections_from_sections(section_all , dividing_lines):
    sub_sections = []
    last_entry = 0
    for entries in dividing_lines:
        sub_sections.append(section_all[last_entry:entries])
        last_entry = entries
    return sub_sections


def clean_subsections_end(subsection_list):
    for line in reversed(subsection_list[-2:]):
        if bool(line != '') & (
                bool(line.strip().strip('|').strip() == '') or bool(line.strip().strip('+').strip('-') == '')):
            subsection_list = subsection_list[:-1]
    if len(subsection_list[-4:]) == 4:
        for line_1 in reversed(subsection_list[-4:]):
            if line_1.strip() == '':
                subsection_list = subsection_list[:-1]
            else:
                break
    return subsection_list


def clean_subsections_start(subsection_list):
    table_found = False
    for line in subsection_list[:2]:
        if (bool(line != '') | bool(line != ' ')) & (bool(line.count('|') == 2)):
            subsection_list = subsection_list[1:]
            table_found = True
    if table_found:
        subsection_list = subsection_list[1:]
    for line_1 in subsection_list[:len(subsection_list)]:
        if bool(line_1 == '') or bool(line_1 == ' '):
            subsection_list = subsection_list[1:]
        else:
            break
    return subsection_list


def line_to_diction(line):
    if ':' in line:
        a = line.split(':')
    elif '=' in line:
        a = line.split('=')
    else:
        line = line + '= ERROR'
        a = line.split('=')
    dict_from_line = {a[0].strip(): a[1].lstrip()}
    return dict_from_line


def table_lines_to_content(section_lines):
    content = []
    multicolumn = False
    counter_1 = 0
    counter_2 = 0
    line_counter = []
    column_counter = []
    for line in section_lines:
        counter_2 = 0
        if multicolumn:
            # print('True:', line, content[-1])
            multicolumn = False
            added_content = [i.strip() for i in line.strip().strip('|').split('|')]
            # print(added_content)
            line_counter.append(counter_1)
            for to_be_edited_lines in range(len(content[-1])):
                content[-1][to_be_edited_lines] += added_content[to_be_edited_lines]
                # print(content[-1][to_be_edited_lines])
            continue

        if '|' not in line:
            continue
        else:
            line_content = [i.strip() for i in (''.join(line[1:])).strip('|').split('|')]
            new_line_content = []
            for iterator in range(len(line_content)):
                if re.search('([+][-])+', line_content[iterator]) is not None:
                    split_iterator = line_content[iterator].split('+-')
                    # print('Found:', line_content[iterator])
                    # print(split_iterator)
                    for line_iterator in range(len(split_iterator)):
                        if re.search('([-])+', split_iterator[line_iterator]) is not None:
                            split_iterator[line_iterator] = ''
                    new_line_content.extend(split_iterator)
                    multicolumn = True
                    column_counter.append(counter_2)
                else:
                    new_line_content.append(line_content[iterator])
                counter_2 += 1
            content.append(new_line_content)
        counter_1 += 1
    return content, line_counter, column_counter


def create_content_by_case(section_lines, case):  # case 0 = EMPTY, 1 = table, 2 = box, 3 = text
    content = OrderedDict()
    case_names = ['EMPTY', 'table', 'box', 'text']
    if case == 0:
        content = []
        for line in section_lines:
            content.append(line)
        pass
    elif case == 1:
        content, position, column = table_lines_to_content(section_lines)
        if position:
            list_array = []
            # print(content[1][:column[0]+1], )
            for lines_1 in range(len(content)):
                if lines_1 < position[0]-1:
                    next_line = [x for x in content[lines_1]]
                    list_array.append(next_line)
                    # print('1', next_line)
                else:
                    # next_line = [np.array(x) for x in content[lines_1][:column[0]+1]]
                    # next_line = np.append(next_line, [''])
                    # list_array = (content[lines_1][column[0] + 1:])
                    # next_line[-1] = np.array(list_array)
                    next_line = [x for x in content[lines_1][:column[0] + 1]]
                    list_insert = [x for x in content[lines_1][column[0] + 1:]]
                    next_line.append(list_insert)
                    list_array.append(next_line)
                    # print('2', next_line)
            # print(list_array)
            list(map(list, zip(*list_array)))
            # print(list_array)
            dict_table = OrderedDict()
            for entries in range(len(list_array)):
                dict_table.update({list_array[entries][0]: [list_array[entries][1:]]})
            # print(dict_table)
        else:
            dict_table = OrderedDict()
            array_1 = np.array([])
            for lines_2 in content:
                if lines_2 == content[0]:
                    next_line = [np.array(x) for x in lines_2]
                    array_1 = np.array(next_line)
                else:
                    next_line = [np.array(x) for x in lines_2]
                    array_1 = np.vstack([array_1, next_line])

            if array_1.ndim >= 2:
                keys_table = array_1[:, 0]
                items_table = array_1[:, 1:].tolist()
                dict_table = OrderedDict(zip(keys_table, items_table))
                content = dict_table
            else:
                print('Error: a table has smaller Dimension than x:2')

    elif case == 2:
        content = ''
        for line in section_lines:
            if '+' in line:
                pass
            else:
                string = line.strip().strip('|').strip()
                content += string + ' \n'
    else:
        for line in section_lines:  # todo fall für gleichen Namen einprogramieren
            if bool(line.count(':') >= 2) or bool(line.count('=') >= 2) or bool((line.count(':') + line.count('=')) >= 2):
                content.update({line.strip(): []})
            elif bool('\\' in line):
                content.update({line.strip(): []})
            elif bool(':' in line) or bool('=' in line):
                content.update(line_to_diction(line))
            else:
                content.update({line.strip(): []})
        # print(content)
    return content


def check_line(line, last_line):
    line_case = ['EMPTY', 'table', 'box', 'text']
    if bool(line.count('|') >= 3) or bool(line.count('+') >= 3):
        case = 1
        # print('Last:', line_case[last_line], line_case[case] + ':', line)
    elif bool(last_line == 1) & bool(line.count('+') == 2):
        case = 1
    elif bool(line.count('|') == 2) or bool(line.count('+') == 2):
        case = 2
        # print('Last:', line_case[last_line], line_case[case] + ':', line)
    elif bool(line != '') or bool(line != ' '):
        case = 3
        # print('Last:', line_case[last_line], line_case[case] + ':', line)
    else:
        case = 0
        # print('Last:', line_case[last_line], line_case[case] + ':', line)
    return case


def check_line_case(subsection_text):
    case = 0
    case_names = ['EMPTY', 'table', 'box', 'text']
    case_lines = []
    dict_number = 0
    dict_subsection = OrderedDict()
    while subsection_text:
        last_line = case
        case = check_line(subsection_text[0], last_line)
        if last_line != case:
            # print('last_line', last_line)
            # print('case changed', case_lines)
            # print(case, create_content_by_case(case_lines, last_line))
            if last_line == 0:
                case_lines = []
                case_lines.append(subsection_text[0])
                pass
                # print('case chanced', case_lines)
                # print(create_content_by_case(case_lines, last_line))
            else:
                dict_subsection.update(collections.OrderedDict(
                    {dict_number: collections.OrderedDict({case_names[case]: create_content_by_case(case_lines, last_line)})}))  #todo hier kann geprüft werden warum leere Zeilen eingefügt werden
                case_lines = []
                case_lines.append(subsection_text[0])
                dict_number += 1
        else:
            case_lines.append(subsection_text[0])
        subsection_text.pop(0)
    last_line = case
    dict_number += 1
    # print('last_line', last_line)
    dict_subsection.update(collections.OrderedDict({dict_number : collections.OrderedDict({case_names[case]: create_content_by_case(case_lines, last_line)})}))  #todo hier kann geprüft werden warum leere Zeilen eingefügt werden
    if last_line == 1:
        pass
        # print('last line', case_lines)
        # print(create_dict_by_case(case_lines, last_line))
    return dict_subsection


def text_to_subsection_dict(subsection_text, section_key, subsection_key):
    subsection_dict = OrderedDict()
    subsection_txt = subsection_text
    if bool(section_key == 'CFX Command Language for Run') & bool(subsection_key == 'Initialization'):
        subsection_dict = comm_lang_to_dict(subsection_text, -1)
        pass
    elif bool(section_key == 'Solver') & bool(subsection_key == 'Convergence History'):
        subsection_dict = convergence_to_dict(subsection_text)
        # subsection_dict = subsection_text
        pass
    else:
        # check_line_case(subsection_txt)
        subsection_dict = check_line_case(subsection_txt)
    return subsection_dict


def dividing_sections_into_subsections(section_all, sub_sections, dividing_lines_header):
    baseline = 0
    dict_sections = OrderedDict()
    n = 0
    line_test = 0
    list_all_subsection_keys = []
    for sections in sub_sections:
        list_subsections_keys = []
        list_subsections_line = []
        dict_subsections = OrderedDict()
        dict_subsections.update({'Initialization': line_test})
        line_test += 5
        for lines in range(len(sections)-5):
            line_test +=1
            baseline +=1
            test_2 = Segmenting(sections[lines:lines+5])
            if test_2.check_and_return_subsection()[0]:
                if test_2.check_and_return_subsection()[1] in list_all_subsection_keys:
                    string = str(test_2.check_and_return_subsection()[1]) + '_1'
                    m = 1
                    while string in list_all_subsection_keys:
                        m += 1
                        string = ''.join(list(string)[-1]+str(m))
                    list_subsections_keys.append(string)
                else:
                    list_subsections_keys.append(test_2.check_and_return_subsection()[1])
                list_all_subsection_keys.append(test_2.check_and_return_subsection()[1])
                list_subsections_line.append(line_test-4) # todo ich habe leider nicht verstanden, warum hier eine -4 hin muss'
                dict_subsections.update({list_subsections_keys[-1]: list_subsections_line[-1]})
        dict_subsections.update({'end': line_test})
        dict_sections.update({dividing_lines_header[n]: dict_subsections})
        n += 1
    line_1 = 0
    dict_test_2 = OrderedDict()
    for sec in dict_sections.keys():
        dict_test = OrderedDict()
        for subsec_1, subsec_2 in zip(list(dict_sections[sec].keys())[:-1], list(dict_sections[sec].keys())[1:]):
            line_test_1 = dict_sections[sec][subsec_1]
            line_test_2 = dict_sections[sec][subsec_2]
            if re.search(".*\\d.*", subsec_1):
                subsec_1 = subsec_1.split('_')[0]
            dict_section_text = section_all[line_test_1:line_test_2]
            dict_section_text = clean_subsections_end(dict_section_text)
            dict_section_text = clean_subsections_start(dict_section_text)
            dict_section_text_2 = dict_section_text
            subsection_dict = text_to_subsection_dict(dict_section_text, sec, subsec_1)
            dict_test.update({subsec_1: subsection_dict})
            # dict_test.update({subsec_1: [dict_section_text_2]})
        dict_test_2.update({sec: dict_test})
    return dict_test_2


def file_to_dict_of_sections(path):
    section_all, file_name = file_to_section(Path)
    dividing_lines, dividing_lines_header = dividing_into_sections(section_all)
    sub_sections = determining_subsections_from_sections(section_all, dividing_lines)
    dict_test_2 = dividing_sections_into_subsections(section_all, sub_sections, dividing_lines_header)
    return dict_test_2, file_name


# Path = "C:/Users/hendr/Google Drive/Masterarbeit/AD_Data_Exchange/12 Softwares/TestProj-Hendrik/TempStab1_files/dp0/CFX/CFX"

# Dict_test_2, File_name = file_to_dict_of_sections(Path)
#
# with open(''.join(File_name) + ".json", "w") as out_file:
#     json.dump(Dict_test_2, out_file)

# Path = "C:/Users/hendr/OneDrive/Desktop/Für Hendrik"



# def file_to_section(path):
#     section_all = []
#     for file in os.listdir(path):
#         if (file.endswith('.out')):
#             outfile = open(os.path.join(path, file))
#     with outfile as f_all:
#         for line_all in f_all:
#             t_line_all = str(line_all).rstrip('\n')
#             section_all.append(t_line_all)
#         file_out = file.split('.')[0]
#     return section_all, file_out


# def search_out_file_in_path(path):
#     list_of_files = []
#     for file in os.listdir(path):
#         if file.endswith('.out'):
#             list_of_files.append(tuple(file, path))
#         elif path.join('/' + file).isdir():
#             print(file)


def clean_section_text(section):
    over_hanging_lines = []
    for iterator, line in enumerate(section):
        if line.strip():
            if '\\' in line.strip()[-1]:
                over_hanging_lines.append(iterator)
    # print(over_hanging_lines)
    for lines in reversed(over_hanging_lines):
        # print(section[lines].strip())
        # print(section[lines + 1])
        # print(''.join((section[lines].rstrip().rstrip('\\'), section[lines + 1].strip())))
        section[lines] = ''.join((section[lines].rstrip().rstrip('\\'), section[lines + 1].strip()))
        section.pop(lines + 1)
    cleaned_section = section
    return cleaned_section


def file_to_section_3(file_path, file_name):
    section_all = []
    outfile = open(os.path.join(file_path, file_name))
    with outfile as f_all:
        for line_all in f_all:
            t_line_all = str(line_all).rstrip('\n')
            section_all.append(t_line_all)
    return section_all


def file_to_dict_of_sections_2(path):
    section_all = file_to_section_3(path[0], path[1])
    section_all_cleaned = clean_section_text(section_all)
    dividing_lines, dividing_lines_header = dividing_into_sections(section_all_cleaned)
    sub_sections = determining_subsections_from_sections(section_all_cleaned, dividing_lines)
    dict_test_2 = dividing_sections_into_subsections(section_all_cleaned, sub_sections, dividing_lines_header)
    return dict_test_2, path[2]


def folder_to_file_list(path):
    file_list_1 = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith((".out")):
                file_name = os.path.normpath(root.split(path)[1] + name.split('.out')[0])
                file_name = file_name[1:].replace('\\', '_')
                file_list_1.append([root, name, file_name])
    return file_list_1


def dump_files_to_json(read_path, write_path='', dump=True):
    f_2 = folder_to_file_list(read_path)
    f_3 = OrderedDict()
    for i in f_2:
        f_4, f_5 = file_to_dict_of_sections_2(i)
        filename_with_dict = {f_5: f_4}
        f_3.update(filename_with_dict)
    if dump:
        for i_1, i_2 in f_3.items():
            with open(''.join(write_path) + ''.join(i_1) + ".json", "w") as out_file:
                json.dump(i_2, out_file)
    return f_3

start = time.process_time()
# H:/NicksDaten/05 Simulationen
# C:/Users/hendr/Desktop/Für Hendrik
Path = 'C:/Users/hendr/Desktop/Für Hendrik'
if __name__ == '__main__':
    Write_Path = './Json_Dict_unmodified/'
    try:
        os.makedirs(Write_Path)
    except:
        pass
    dict_1 = dump_files_to_json(Path, Write_Path)

print('Finished')
print(time.process_time()-start)

# f_3 = []
# for i in f_2:
#     f_3.append([file_to_section_3(i[0], i[1])])
#
# f_4 = f_3[1]
#
# f_5 = clean_section_text(f_4[0])
# Dict_test_2, File_name = file_to_dict_of_sections(Path)
#
# with open(''.join(File_name) + ".json", "w") as out_file:
#     json.dump(Dict_test_2, out_file)
# print([os.path.normcase((f_2[0][0]).split(Path)[1])])
# normal_case_files = []
# for iterator_1 in Files:
#     normal_case_files.append(os.path.normcase(iterator_1))
#
# a, b = file_to_section_2(normal_case_files)

#
# section_all_test = []
# out_file_test = open(normal_case_files[0])
# with out_file_test as f_all_test:
#     for line_all_test in f_all_test:
#         t_line_all_test = str(line_all_test).rstrip('\n')
#         section_all_test.append(t_line_all_test)

#
# Dicts = []
# for file_1 in Files:
#     Dict, File_name = file_to_dict_of_sections(Path)
#     Dicts.append(zip(file_1, Dict))

    # with open(''.join(File_name) + ".json", "w") as out_file:
    #     json.dump(Dict_test_2, out_file)

# search_out_file_in_path(Path)

# def iterate_through_section_dict(section_dict):
#     list_internal = []
#     for k, v in section_dict.items():
#         list_internal.append(k)
#         if isinstance(v, dict):
#             list_internal.append(iterate_through_section_dict(v))
#     return list_internal


# a = iterate_through_section_dict(Dict_test_2)

# def clean_through_section_dict(section_dict):
#     for v in list(section_dict.items())[:]:
#         print(v)
#         # if isinstance(v, dict):
#         #     clean_through_section_dict(v)
#         #     k = []
#         # if k:
#         #     for section in section_dict[k]:
#         #         for line in section[-2:]:
#         #             if bool(line != '') & (bool(line.strip().strip('|').strip() == '') or bool(line.strip().strip('+').strip('-') == '')):
#         #                 print(k)
#     return section_dict



# def convergence_list_to_position_numbers(list_of_convergence_segments):
#     pos_number = []
#     for line in range(len(list_of_convergence_segments)):
#         if 'Timescale' in list_of_convergence_segments[line]:
#             pos_number.append(line-len(pos_number))
#     return pos_number
#
#
# convergence_list_to_position_numbers(list_of_convergence_segments)

# Section_dict = clean_through_section_dict(Dict_test_2)

# a = Dict_test_2['Partitioning']['Iso-Partition Connection Statistics'][0][1]
# b = Dict_test_2['Partitioning']['Iso-Partition Connection Statistics'][0][2]
#
# m = re.search("([+]|[-])+", a)
#
# f = a.split(m.group())



