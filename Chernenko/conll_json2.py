import json
import glob
import os 
import sys
import jsonlines
#usage command line: python json_conll.py input_folder

def get_paths(input_folder):
    """
    Stores all .txt files in a list
    Returns a list of strings of filepaths from the Text (volumes) folder
    :param inputfolder: inputfolder used in main
    """
    list_files = []
    conll_folder = glob.glob(input_folder + '/*.conll')
    
    for filename in conll_folder:
        list_files.append(filename)

    return list_files

def load_text(txt_path):
    """
    Opens the container en reads the elements(strings)
    Returns a string
    :param txt path: list with filepaths
    """
    with open(txt_path, mode='rt', encoding="utf-8") as infile:
        content = infile.readlines()
        
    return content

def process_all_txt_files(paths):
    """
    given a list of txt_paths
    -process each
    :param paths: list of content volume
    :return: list of dicts
    """
    list_dicts = []
    list_sents = []
    #strip newline, split on space char and make components for the dictionary
    for line in paths:
        components = line.rstrip('\n').split()
        if len(components) > 0 and components[0] == '-DOCSTART-':
            continue
        elif len(components) > 0:
            if '.' in components[0]:
                word = components[0].rstrip('.')
                ner = components[3]
                feature_dict = {'text':word,
                                'label': ner,
                                }
                list_dicts.append(feature_dict)
                word = '.'
                ner = 'O'
                feature_dict = {'text':word,
                                'label': ner,
                                }
                list_dicts.append(feature_dict)
                list_sents.append(list_dicts)
                list_dicts = []
            else:
                word = components[0]
                ner = components[3]
                feature_dict = {'text':word,
                                'label': ner,
                                }
                list_dicts.append(feature_dict)
    return list_sents

def write_file(list_sents, input_folder, text):
    """
    write volumes to new directory
    :param list_dicts: list_of dicts
    :param input_folder: folder with CONLL files
    :param text: pathname of CONLL file
    """
    directory = "json-dir"
    
    #check if directoy exists, if not make it
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    #get basename of the path and change extension to json
    base = os.path.basename(text)[:-6]
    json_str = '.jsonl'
    basename = base + json_str
    
    #put in the new directory
    path = os.path.join (input_folder, directory)
    completeName = os.path.join(path, basename)
    
    #write file to json format
    #jsondumps = json.dumps(list_dicts)
    #jsonfile = open(completeName, "w")
    #jsonfile.write(jsondumps)
    #jsonfile.close()
    with jsonlines.open(completeName, 'w') as writer: 
        writer.write_all(list_sents)
        writer.close()
        
def main():
    
    input_folder = sys.argv[1]
    
    #loop over every pathname and call functions for each path separately
    txt_path = get_paths(input_folder)
    for text in txt_path:
        paths = load_text(text)
        list_sents = process_all_txt_files(paths)
        write_file(list_sents, input_folder, text)

if __name__ == "__main__":
    main()
