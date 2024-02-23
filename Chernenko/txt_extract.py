# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:36:09 2023

@author: smdicher
"""
"""
from owlready2 import *
def
new_world = owlready2.World()
onto_test = new_world.get_ontology("./ontology_sniplet/{}_classes.owl".format(onto_name)).load()
new_world2= owlready2.World()
onto =new_world2.get_ontology("./ontologies/{}.owl".format(onto_name)).load()
a = list(onto_test.classes().label)
"""
"""

cr = Crossref()

result = cr.works(query = 'Vapour phase propene hydroformylation catalyzed by the Rh/Al system on silica')

print(result['message']['items'][0]['DOI'])
"""
"""
Limitations:
    - No processing of CID keyed fonts. PDFMiner seems to decode them
    in some methods (e.g. PDFTextDevice.render_string()).
    - Some `LTTextLine` elements report incorrect height, leading to some
    blocks of text being consider bigger than title text.
    - Heuristics are used to judge invalid titles, implying the possibility of
    false positives.
    https://gist.github.com/Zeqiang-Lai/576940bcffd5816d695c65b4b6c13e98
    """
import glob
from pdfdataextractor import Reader
import os
import re
import string
import subprocess
import unidecode
from pybliometrics.scopus import AbstractRetrieval
from pypdf import PdfReader
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser 
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTChar, LTFigure, LTTextBox, LTTextLine
from habanero import Crossref
from bs4 import BeautifulSoup
__all__ = ['pdf_title']

def make_parsing_state(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('ParsingState', (), enums)
CHAR_PARSING_STATE = make_parsing_state('INIT_X', 'INIT_D', 'INSIDE_WORD')

def log(text):
    if IS_LOG_ON:
        print('--- ' + text)
IS_LOG_ON = False

MIN_CHARS = 6
MAX_WORDS = 20
MAX_CHARS = MAX_WORDS * 10
TOLERANCE = 1e-06

def sanitize(filename):
    """Turn string into a valid file name.
    """
    # If the title was picked up from text, it may be too large.
    # Preserve a certain number of words and characters
    words = filename.split(' ')
    filename = ' '.join(words[0:MAX_WORDS])
    if len(filename) > MAX_CHARS:
        filename = filename[0:MAX_CHARS]

    # Preserve letters with diacritics
    try:
        filename = unidecode.unidecode(filename.encode('utf-8').decode('utf-8'))
    except UnicodeDecodeError:
        print("*** Skipping invalid title decoding for file %s! ***" % filename)

    # Preserve subtitle and itemization separators
    filename = re.sub(r',', ' ', filename)
    filename = re.sub(r': ', ' - ', filename)

    # Strip repetitions
    filename = re.sub(r'\.pdf(\.pdf)*$', '', filename)
    filename = re.sub(r'[ \t][ \t]*', ' ', filename)

    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join([c for c in filename if c in valid_chars])

def meta_title(filename):
    """Title from pdf metadata. 
    """
    docinfo = PdfReader(open(filename, 'rb')).metadata
    if docinfo is None:
        return ''
    return docinfo.title if docinfo.title else ''

def junk_line(line):
    """Judge if a line is not appropriate for a title.
    """
    too_small = len(line.strip()) < MIN_CHARS
    is_placeholder_text = bool(re.search(r'^[0-9 \t-]+(abstract|introduction)?\s+$|^(abstract|unknown|title|untitled):?$', line.strip().lower()))
    is_copyright_info = bool(re.search(r'paper\s+title|technical\s+report|proceedings|preprint|to\s+appear|submission|(integrated|international).*conference|transactions\s+on|symposium\s+on|downloaded\s+from\s+http', line.lower()))

    # NOTE: Titles which only contain a number will be discarded
    stripped_to_ascii = ''.join([c for c in line.strip() if c in string.ascii_letters])
    ascii_length = len(stripped_to_ascii)
    stripped_to_chars = re.sub(r'[ \t\n]', '', line.strip())
    chars_length = len(stripped_to_chars)
    is_serial_number = ascii_length < chars_length / 2

    return too_small or is_placeholder_text or is_copyright_info or is_serial_number

def empty_str(s):
    return len(s.strip()) == 0

def is_close(a, b, relative_tolerance=TOLERANCE):
    return abs(a-b) <= relative_tolerance * max(abs(a), abs(b))

def update_largest_text(line, y0, size, largest_text):
    log('update size: ' + str(size))
    log('largest_text size: ' + str(largest_text['size']))

    # Sometimes font size is not correctly read, so we
    # fallback to text y0 (not even height may be calculated).
    # In this case, we consider the first line of text to be a title.
    if ((size == largest_text['size'] == 0) and (y0 - largest_text['y0'] < -TOLERANCE)):
        return largest_text

    # If it is a split line, it may contain a new line at the end
    line = re.sub(r'\n$', ' ', line)

    if (size - largest_text['size'] > TOLERANCE):
        largest_text = {
            'contents': line,
            'y0': y0,
            'size': size
        }
    # Title spans multiple lines
    elif is_close(size, largest_text['size']):
        largest_text['contents'] = largest_text['contents'] + line
        largest_text['y0'] = y0

    return largest_text

def extract_largest_text(obj, largest_text):
    # Skip first letter of line when calculating size, as articles
    # may enlarge it enough to be bigger then the title size.
    # Also skip other elements such as `LTAnno`.
    for i, child in enumerate(obj):
        if isinstance(child, LTTextLine):
            log('lt_obj child line: ' + str(child))
            for j, child2 in enumerate(child):
                if j > 1 and isinstance(child2, LTChar):
                    largest_text = update_largest_text(child.get_text(), child2.y0, child2.size, largest_text)
                    # Only need to parse size of one char
                    break
        elif i > 1 and isinstance(child, LTChar):
            log('lt_obj child char: ' + str(child))
            largest_text = update_largest_text(obj.get_text(), child.y0, child.size, largest_text)
            # Only need to parse size of one char
            break
    return largest_text

def extract_figure_text(lt_obj, largest_text):
    """
    Extract text contained in a `LTFigure`.
    Since text is encoded in `LTChar` elements, we detect separate lines
    by keeping track of changes in font size.
    """
    text = ''
    line = ''
    y0 = 0
    size = 0
    char_distance = 0
    char_previous_x1 = 0
    state = CHAR_PARSING_STATE.INIT_X
    for child in lt_obj:
        log('child: ' + str(child))

        # Ignore other elements
        if not isinstance (child, LTChar):
            continue

        char_y0 = child.y0
        char_size = child.size
        char_text = child.get_text()
        decoded_char_text = unidecode.unidecode(char_text.encode('utf-8').decode('utf-8'))
        log('char: ' + str(char_size) + ' ' + str(decoded_char_text))

        # A new line was detected
        if char_size != size:
            log('new line')
            largest_text = update_largest_text(line, y0, size, largest_text)
            text += line + '\n'
            line = char_text
            y0 = char_y0
            size = char_size

            char_previous_x1 = child.x1
            state = CHAR_PARSING_STATE.INIT_D
        else:
            # Spaces may not be present as `LTChar` elements,
            # so we manually add them.
            # NOTE: A word starting with lowercase can't be
            # distinguished from the current word.
            char_current_distance = abs(child.x0 - char_previous_x1)
            log('char_current_distance: ' + str(char_current_distance))
            log('char_distance: ' + str(char_distance))
            log('state: ' + str(state))

            # Initialization
            if state == CHAR_PARSING_STATE.INIT_X:
                char_previous_x1 = child.x1
                state = CHAR_PARSING_STATE.INIT_D
            elif state == CHAR_PARSING_STATE.INIT_D:
                # Update distance only if no space is detected
                if (char_distance > 0) and (char_current_distance < char_distance * 2.5):
                    char_distance = char_current_distance
                if (char_distance < 0.1):
                    char_distance = 0.1
                state = CHAR_PARSING_STATE.INSIDE_WORD
            # If the x-position decreased, then it's a new line
            if (state == CHAR_PARSING_STATE.INSIDE_WORD) and (child.x1 < char_previous_x1):
                log('x-position decreased')
                line += ' '
                char_previous_x1 = child.x1
                state = CHAR_PARSING_STATE.INIT_D
            # Large enough distance: it's a space
            elif (state == CHAR_PARSING_STATE.INSIDE_WORD) and (char_current_distance > char_distance * 8.5):
                log('space detected')
                log('char_current_distance: ' + str(char_current_distance))
                log('char_distance: ' + str(char_distance))
                line += ' '
                char_previous_x1 = child.x1
            # When larger distance is detected between chars, use it to
            # improve our heuristic
            elif (state == CHAR_PARSING_STATE.INSIDE_WORD) and (char_current_distance > char_distance) and (char_current_distance < char_distance * 2.5):
                char_distance = char_current_distance
                char_previous_x1 = child.x1
            # Chars are sequential
            else:
                char_previous_x1 = child.x1
            child_text = child.get_text()
            if not empty_str(child_text):
                line += child_text
    return (largest_text, text)

def pdf_text(filename):
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser, '')
    parser.set_document(doc)
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    text = ''
    largest_text = {
        'contents': '',
        'y0': 0,
        'size': 0
    }
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            log('lt_obj: ' + str(lt_obj))
            if isinstance(lt_obj, LTFigure):
                (largest_text, figure_text) = extract_figure_text(lt_obj, largest_text)
                text += figure_text
            elif isinstance(lt_obj, (LTTextBox, LTTextLine)):
                # Ignore body text blocks
                stripped_to_chars = re.sub(r'[ \t\n]', '', lt_obj.get_text().strip())
                if (len(stripped_to_chars) > MAX_CHARS * 2):
                    continue

                largest_text = extract_largest_text(lt_obj, largest_text)
                text += lt_obj.get_text() + '\n'

        # Remove unprocessed CID text
        largest_text['contents'] = re.sub(r'(\(cid:[0-9 \t-]*\))*', '', largest_text['contents'])

        # Only parse the first page
        return (largest_text, text)

def title_start(lines):
    for i, line in enumerate(lines):
        if not empty_str(line) and not junk_line(line):
            return i
    return 0

def title_end(lines, start, max_lines=2):
    for i, line in enumerate(lines[start+1:start+max_lines+1], start+1):
        if empty_str(line):
            return i
    return start + 1

def text_title(filename):
    """Extract title from PDF's text.
    """
    (largest_text, lines_joined) = pdf_text(filename)

    if empty_str(largest_text['contents']):
        lines = lines_joined.strip().split('\n')
        i = title_start(lines)
        j = title_end(lines, i)
        text = ' '.join(line.strip() for line in lines[i:j])
    else:
        text = largest_text['contents'].strip()

    # Strip dots, which conflict with os.path's splittext()
    text = re.sub(r'\.', '', text)

    # Strip extra whitespace
    text = re.sub(r'[\t\n]', '', text)

    return text

def pdftotext_title(filename):
    """Extract title using `pdftotext`
    """
    command = 'pdftotext {} -'.format(re.sub(' ', '\\ ', filename))
    process = subprocess.Popen([command], \
            shell=True, \
            stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
    out, err = process.communicate()
    lines = out.strip().split('\n')

    i = title_start(lines)
    j = title_end(lines, i)
    text = ' '.join(line.strip() for line in lines[i:j])

    # Strip dots, which conflict with os.path's splittext()
    text = re.sub(r'\.', '', text)

    # Strip extra whitespace
    text = re.sub(r'[\t\n]', '', text)

    return text

def valid_title(title):
    return not empty_str(title) and not junk_line(title) and empty_str(os.path.splitext(title)[1])

def pdf_title(filename):
    """Extract title using one of multiple strategies.
    """
    try:
        title = meta_title(filename)
        if valid_title(title):
            return title
    except Exception as e:
        print("*** Skipping invalid metadata for file %s! ***" % filename)
        print(e)

    try:
        title = text_title(filename)
        if valid_title(title):
            return title
    except Exception as e:
        print("*** Skipping invalid parsing for file %s! ***" % filename)
        print(e)

    title = pdftotext_title(filename)
    if valid_title(title):
        return title
    return os.path.basename(os.path.splitext(filename)[0])

def get_abstract(path, doi, publisher):                                    
    

     
    if ('ACS' or 'American Chemical Society') in publisher:
        file= Reader()
        pdf= file.read_file(path)
        abstract=pdf.abstract()
    elif publisher:
        ab = AbstractRetrieval(doi)
        abstract=ab.abstract
        #keywords=ab.authkeywords
        if not abstract:
            abstract=ab.description
    else:
        return None
    if abstract:
        abstract=re.sub(r'A[Bb][Ss][Tt][Rr][Aa][Cc][Tt][:]?','',abstract)
        if abstract[0]==':':
                abstract=abstract[1:]
    
    #if re.search(r'K[Ee][Yy][Ww][Oo][Rr][Dd][Ss][:]?', abstract):
        #keywords=abstract[re.search(r'K[Ee][Yy][Ww][Oo][Rr][Dd][Ss][:]?', abstract).end():]
        #abstract=abstract[re.search(:r'K[Ee][Yy][Ww][Oo][Rr][Dd][Ss][:]?', abstract).start()]
        #keywords = re.findall(r'[a-zA-Z]\w+',text)
    return abstract

def is_majority_included(list1, list2, threshold=0.8):
    # Count how many items from list1 are in list2
    count = sum(1 for item in list1 if item in list2)

    # Calculate the percentage
    percentage = count / len(list1)

    # Check if the percentage is above the threshold
    return percentage >= threshold   

def get_metadata(filename):
    file= Reader()
    pdf= file.read_file(filename)
    manual_prep= False
    try:
        title=pdf.title()
    except:
        #print('empty title')
        title = pdf_title(filename)
        title = sanitize(' '.join(title.split()))
    if not re.search(r'[\w]+',title):
        #print('empty title')
        title = pdf_title(filename)
        title = sanitize(' '.join(title.split()))
        manual_prep=True
    cr = Crossref()
    if re.search("[Jj]ournal|[Nn]ews",title):
        doi=search_doi_text(filename)
        if doi != None:
            result = cr.works(ids = doi)
            title=result['message']['title'][0]
            publisher = result['message']['publisher']
            return title, doi, publisher
        else:
            print('no title found for '+filename)
            return None,None,None
    result = cr.works(query = title)
    for i in range(len(result['message']['items'])):    
        try:
            result['message']['items'][i]['title'][0]
        except:
            continue
        else:
            if is_majority_included(title.split(), result['message']['items'][i]['title'][0].split(), threshold=0.8):
                doi=result['message']['items'][i]['DOI']
                title, publisher = crossref_search(result,i)
                return title, doi, publisher

            elif i== len(result['message']['items'])-1: 
                if manual_prep==False:
                    title = pdf_title(filename)
                    title = sanitize(' '.join(title.split()))
                    cr = Crossref()
                    result = cr.works(query = title)
                    for k in range(len(result['message']['items'])):
                        try:
                            result['message']['items'][k]['title'][0]
                        except:
                            continue
                        else:
                            if is_majority_included(title.split(), result['message']['items'][k]['title'][0].split(), threshold=0.8):
                                doi=result['message']['items'][k]['DOI']
                                title, publisher = crossref_search(result,k)
                                return title, doi, publisher
                            elif k == len(result['message']['items'])-1:
                                doi = search_doi_text(filename)
                                if doi != None:
                                    try:
                                        result = cr.works(ids = doi)
                                        title=result['message']['title'][0]
                                        publisher = result['message']['publisher']
                                    except:
                                        print('no title found for '+filename)
                                        return None,None,None
                                    return title, doi, publisher
                                else:
                                    print('no title found for '+filename)
                                    return None,None,None
                else:
                    print('no title found for '+filename)
                    return None,None,None

def search_doi_text(filename):
    reader = PdfReader(filename)
    page = reader.pages[0]
    text= page.extract_text()
    pattern= r"\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'<>])\S)+)\b"
    m=re.search(pattern, text)
    if m:
        doi=m[0]
    else:
        doi=None
    return doi
def crossref_search(result,k):
    title=result['message']['items'][k]['title'][0]
    soup = BeautifulSoup(title, 'html.parser')
    title = soup.get_text()
    publisher=result['message']['items'][k]['publisher']
    return title,publisher
''' 
#abstract_all=''
path=r'.\Methanisierung\*.pdf'
for i in glob.iglob(path):
    title,doi,publisher = get_metadata(i)
    if doi==None:
        continue
    print(title+' : '+doi)
    abstract = get_abstract(i, doi, publisher)
    if abstract==None or not abstract:
        print('no abstract found')
    #if abstract!=None and abstract:
    #    print("Abstract:"+abstract)
    #else:
    #    print('no abstract found')
'''        
"""
    import json
    def set_config_key(key, value):
             globals()[key] = value
             
    with open("config.json") as json_config:
             for key, value in json.load(json_config).items():
                 set_config_key(key, value)
    for i in glob.iglob(path):

                     title,doi,publisher= get_metadata(i)
                     print(title)
                     print(doi)

"""




