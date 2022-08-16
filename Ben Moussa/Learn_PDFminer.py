from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from io import StringIO
from pdfminer.pdfpage import PDFPage
from BA_main_function_copy import*
import spacy
import transform_into_RDF
from clear_glossary import* 
import libchebipy
from libchebipy import ChebiEntity
import time
from time import time
# import pdfplumber
from os.path import exists

def add_to_saved_list(liste,path):
    if not exists(path):
        pickle.dump(liste,open(path,"wb"))
        del liste
    else:
        saved_list = pickle.load(open(path,"rb"))
        if type(saved_list) == dict:
            saved_list = list(saved_list.values())
        saved_list.append(liste)
        pickle.dump(saved_list,open(path,"wb"))
        del saved_list
        del liste
    
    
def add_to_data_base(semantic_tuples,sent=-1,path=-1,fortfahren="unknown"):
    if not isinstance(path,(str)):
        path = "semantic_tuples.dat"
    elif not exists(path):
        pickle.dump(set(),open(path,"wb"))
        
    if isinstance(sent,(float,int)):
        sentence = "the processed sentences"
    elif not isinstance(sent,(str)):
        sentence = '"'+str(sent)+'"'
    elif isinstance(sent,(str)):
        sentence = '"'+sent+'"'

    while fortfahren.lower() not in ["no","yes"]:
        fortfahren = input('Is {}\nrelevant for the data base ?\n'.format(sentence))
    if fortfahren == True or fortfahren.lower() == "yes":
        saved_semantic_tuples = set(pickle.load(open("{}".format(path),"rb")))
        for tupel in semantic_tuples:
            saved_semantic_tuples.add(tupel)
        pickle.dump(saved_semantic_tuples,open("{}".format(path),"wb"))
        
        
def get_pdf_file_content(path_to_pdf,page_list,maxpages=400):
    resource_manager = PDFResourceManager(caching=True)
    out_text = StringIO()
    codec = 'utf-8'
    laParams = LAParams()
    text_converter = TextConverter(resource_manager, out_text, laparams=laParams)
    fp = open(path_to_pdf, 'rb')
    interpreter = PDFPageInterpreter(resource_manager, text_converter)
    for page in PDFPage.get_pages(fp, pagenos=set(page_list), maxpages=maxpages, password="", caching=True, check_extractable=True):
        interpreter.process_page(page)
    text = out_text.getvalue()
    fp.close()
    text_converter.close()
    out_text.close()
    return text


if input("Remainder!\nDid you change the names of the following file paths and variables?\n\n'path_to_pdf',\n'glossary.dat',\n'valid_sents_file',\n'error_sents_file',\n'processing_time_file',\n'saving_path',\n'graph_saving_path','\nfinish and start page'\n\n").lower() not in ["yes","ja","y","ye","j"]:
    raise Exception("Than change them !")
    
#path_to_pdf = ".\\Data_Base\\processing_PDFS\\OrganicChemistry0.pdf"
path_to_pdf = ".\\Data_Base\\processing_PDFS\\IndustrialCatalysis0.pdf"
#path_to_pdf = "./processing_PDFS/OrganicChemistry2.pdf"
valid_sents_file = "./Data_Base/ValidSents/valid_sents_MardiALex.dat"
error_sents_file = "./Data_Base/ErrorSents/error_sents_MardiALex.dat"
processing_time_file = "./Data_Base/processing_time.dat"
saving_path = "./Data_Base/saved_tuples/MardiALex.dat"
graph_saving_path = "./Data_Base/RDF-Dateien/MardiALex.n3"
i0 = 0
i_end = 2

PDF_text = get_pdf_file_content(path_to_pdf,list(range(0,484)),500)
#f = open("./Data_Base/processing_PDFS/text.txt","r")
#PDF_text =  f.read()
#f.close()
formula_dic = pickle.load(open("formula_dic.dat","rb"))
chebi_dic = pickle.load(open("chebi_dic.dat","rb"))

t00 = time()

# for i in range(i0,i_end):
for i in range(i_end):  
    t0 = time()
    print("\n\n Round number {}\n".format(i))
    if i>i0:
        del semantic_tuples
        del PDF_text, primary_sentences, str_sentences
        del valid_sents
        del error_sents
        
    page_end = i*10
    page_start = (i-1)*10
    PDF_text_raw = get_pdf_file_content(path_to_pdf,list(range(page_start,page_end))).split("\n\n")
#    f = open()
    PDF_text = [preprocessing(part) for part in PDF_text_raw]
    
    
    
    if i == i0:
        nlp = spacy.load("en_core_web_md")
    primary_sentences = []
    for pdf_part in PDF_text:
        primary_sentences += [preprocessing(sent.text) for sent in list(nlp(pdf_part).sents)]
    str_sentences = []
    for pr_sent in primary_sentences:
        if len(pr_sent)<1000:
            for nlp_sent in list(nlp(pr_sent).sents):
                str_sentences.append(nlp_sent.text)
    sentences = [nlp(sentence) for sentence in str_sentences]
    sent_number = len(sentences)
    print("\nThere are {} sentences\n".format(len(sentences)))
    semantic_tuples = []
    error_num = 0
    error_sents = []
    valid_sents = []
    for s_num, s in enumerate(sentences):
        try:
            new_tuples = tuples_from_text(s,nlp,show_graph=False,formula_dic=formula_dic,chebi_dic=chebi_dic)
            semantic_tuples += new_tuples
        except:
            error_num += 1
            print("Error {} at sentence number {} !".format(error_num,s_num),sep='\n')
            error_sents.append(s.text)
        else:
            valid_sents.append(s.text)
    
#    transform_into_RDF.generate_protege_graph(semantic_tuples,show_graph=False,graph_path="./Data_Base/InoragnicChemistry0.n3")
    
    
        
#    glossary = pickle.load(open("glossary.dat","rb"))
    t1 = time()
    if sent_number != 0:
        print("\nProcessing time is {}\n".format(t1-t0))
        print("{} of {} was not processed\nEquals to {}%\n".format(error_num,len(sentences), 100*((error_num/sent_number)) ))
        print("{} of {} was processed\nEquals to {}%\n".format(sent_number-error_num,sent_number,100*(1-(error_num/sent_number)) ))    
    add_to_data_base(semantic_tuples,path=saving_path,fortfahren="yes")
    add_to_saved_list(valid_sents,valid_sents_file)
    add_to_saved_list(error_sents,error_sents_file)
    #clear_glossary("glossary.dat")

tf = time()
print("\nProcessing time of the hole book is {}\n".format(tf-t00))
processing_time = pickle.load(open(processing_time_file,"rb"))
processing_time[saving_path] = tf-t00
pickle.dump(processing_time,open(processing_time_file,"wb"))
transform_into_RDF.generate_protege_graph(tuples=pickle.load(open(saving_path,"rb")),show_graph=True,return_tuples=False,return_graph=False,graph_path=graph_saving_path)





#def extract_pdf(pdf_path):
#    all_text = ''
#    with pdfplumber.open(pdf_path) as pdf:
#        for pdf_page in pdf.pages:
#            single_page_text = pdf_page.extract_text()
#            all_text = all_text + '\n' + single_page_text
#    return all_text