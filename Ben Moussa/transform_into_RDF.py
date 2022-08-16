from rdflib import Graph, URIRef, Literal, BNode
import subprocess
from rdflib.namespace import FOAF, RDF, SDO, XSD, DCTERMS, RDFS
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from rdflib import Namespace
import networkx as nx
import pickle
import os, ssl

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
def u_string(string,d_r="http://Mazen_Ben_Moussa_Bachelor_Arbeit.org/Katalyse_Ontologie/",ns="URIRef"):
    # if type(string) == tuple:
    #     new_t = (u(validate(string[0]),d_r),u(validate(string[1]),d_r,ns),u(validate(string[2]),d_r))
    #     return new_t
    if type(string) != str:
        return string
    else:
        string = validate(string).replace(" ","_")        
    if ns != "URIRef":
        return ns[string]
    string = d_r + string
    return URIRef(string)
    
def validate(string):
    if (type(string) == str) and (len(string) > 0) :
        while (len(string)>=1) and (string[0] == " "):
            string = string[1:]
        while (len(string)>=1) and (string[-1] == " "):
            string = string[:-1]
        while (len(string)>=1) and ("  " in string):
            string = string.replace("  "," ")        
        while (len(string)>=1) and (",,,@" in string):
            string = string.replace(",,,@","@")
        if string[-3:] == ",,,":
            string = string[:-3]
    return string



def PageRank(terms,glossary=pickle.load(open("glossary.dat","rb"))):
    if type(glossary) == str:
         glossary = pickle.load(open("{}".format(glossary),"rb"))   
    else:
        glossary=pickle.load(open("glossary.dat","rb"))
    
    invalide_terms = ["it","he","she","they","their","his","him","its","her",
                      "you","your","me","my","himself","herself","itself","themselves"
                      ,"yourself","his","so",".",",",";",":",")","(","þ","%","y::","!","{","}","[","]","^","^^",
                      "|","-","_","?","!","::","[::","::]","*","<",">","&","²","'",'"',"è","¨","§","%","ù""#","~"
                      ,"é","°"]
    irrelevant_terms = [" ","Semantic_Specification","has_property","Object_Property","Semantic_Property","Complex_Semantic_Property_(verbs)"]
    
    for t in terms:
        if type(t) == str:
            if (t.lower() not in invalide_terms) and (t not in irrelevant_terms):
                if t not in glossary.keys():
                    glossary[t] = 1
                else:
                    glossary[t] += 1
    pickle.dump(glossary,open("glossary.dat","wb"))
    


# Validate each part of the tuple, appends the tuple to the graph in the right form,
# and update the weights of each mensioned term (through PageRank function)
def u_tuple(tupel,g_ba=Graph(),n=None,glossary=-1,chebi_tuple=False):
    preps = {"about":"about","above":"above","across":"across","after":"after","against":"against",
         "along":"along","among":"among","around":"around","at":"at","before":"before",
         "behind":"","between":"between","beyond":"beyond","but":"in contrast to","by":"by",
         "concerning":"concerning","despite":"despite","down":"down","during":"during",
         "except":"","following":"","for":"","from":"has origin","in":"in",
         "including":"including","into":"into","like":"similar to !!!!","near":"near","of":"related to","off":"off",
         "on":"on","onto":"onto","out":"out","over":"over","past":"past","plus":"plus",
         "since":"since","throughout":"throughout","to":"to","towards":"towards","under":"under",
         "until":"until","up":"up","upon":"upon","up to":"up to","with":"in company of / including",
         "within":"within","without":"in absence of","as":"as"} 
    
    chebi_classes = ["Complex_Semantic_Property_(verbs)","Complex_Semantic_Specification_(verbs)","Numerical_Value_With_Unit","Chemical_Entity","CHEBI_identifier","Formal_Charge","Molar_Mass","Chemical_Formula","CHEBI_Chemical_Entity","Numerical_value"]
    pickle.load(open("introducer_to_predicate.dat","rb"))
    a = tupel[0]
    b = tupel[1]
    c = tupel[2]
    if type(a) == str:
        a = validate(a).replace(" ","_")
        if ( not chebi_tuple) and (a not in chebi_classes):
            a = a.lower()
        g_ba.add( (n[a],RDF.type,RDFS.Class) )
    if type(b) == str:
        b = validate(b).replace(" ","_").lower()
    if type(c) == str:
        c = validate(c).replace(" ","_")
        if (not chebi_tuple) and (c not in chebi_classes):
            c = c.lower()
    PageRank((a,c),glossary)
    if type(b) == str:
        prpt = n[a +"/"+ b]
        g_ba.add( (prpt,RDF.type,RDF.Property) ) 
        g_ba.add( (prpt,RDFS.subPropertyOf,n["Object_Property"]) )
        g_ba.add( (prpt,RDFS.range,n[c]) )
        g_ba.add( (prpt,RDFS.domain,n[a]) )
        if b == "has_property":
            g_ba.add( (n[c],RDF.type,RDFS.Class) )
            g_ba.add( (n[c],RDFS.subClassOf,n["Semantic_Property"]) )
        elif b == "has_specification":
            g_ba.add( (n[c],RDFS.subClassOf,n["Semantic_Specification"]) )
            # g_ba.add( (n[c],RDFS.subClassOf,n["Complex_Semantic_Property_(verbs)"]) )
    else:
        g_ba.add( (n[c],RDF.type,RDFS.Class) )
        g_ba.add( (n[a],b,n[c]) )
        
    

    
def generate_protege_graph(tuples=-1,show_graph=True,return_tuples=False,return_graph=False,graph_path=-1):
    if not isinstance(graph_path,(str)):
        graph_path = "probe.n3"
    elif graph_path[-3:] != ".n3":
        graph_path += ".n3"
        
#    n = Namespace("http://example.org/Bachelor_Arbeit/")
    n = Namespace("http://TU-Dortmund.org/BCI/Apparatedesign/Bachelor_Arbeit/")
    
    if tuples == -1:
        tuples = pickle.load(open("tuples.dat","rb"))
    g_ba = []
    g_ba = Graph()
    
    g_ba = Graph()
    
    g_ba.add( (n["Semantic_Specification"],RDF.type,RDFS.Class) )
    g_ba.add( (n["Complex_Semantic_Property_(verbs)"],RDF.type,RDFS.Class) )
    g_ba.add( (n["Complex_Semantic_Specification_(verbs)"],RDF.type,RDFS.Class) )
    g_ba.add( (n["Semantic_Property"],RDF.type,RDF.Property) )
    g_ba.add( (n["Object_Property"],RDF.type,RDF.Property) )
    g_ba.add( (n["Chemical_Entity"],RDF.type,RDFS.Class))
    g_ba.add( (n["CHEBI_identifier"],RDF.type,RDFS.Class))
    g_ba.add( (n["Formal_Charge"],RDF.type,RDFS.Class))
    g_ba.add( (n["Molar_Mass"],RDF.type,RDFS.Class))
    g_ba.add( (n["Chemical_Formula"],RDF.type,RDFS.Class))
    g_ba.add( (n["CHEBI_Chemical_Entity"],RDF.type,RDFS.Class))
    g_ba.add( (n["Numerical_value"],RDF.type,RDFS.Class))
    g_ba.add( (n["Numerical_Value_With_Unit"],RDF.type,RDFS.Class))
    
    
    
    
    
    for t in tuples:
#        PageRank(t,glossary)
        u_tuple(t,g_ba,n)
    
    g_ba_list  = list(g_ba)
    
    subprocess.run(['del', "{}".format(graph_path)], shell = True, capture_output = True)
    g_ba.serialize(destination="{}".format(graph_path),format="n3")
#    g_ba = Graph()
    pc_name = subprocess.getoutput("whoami")
    own_pc = False
    if "desktop_lnpa0sp" in pc_name:
        own_pc = True
        
    if (show_graph == True) and (graph_path == "probe.n3"):
        if not own_pc:
            subprocess.run(["call",".\\CallProtege.bat"],shell=True,capture_output=True)
        else:
            subprocess.getoutput("start probe.n3  C:\\Users\\user\\Downloads\\Protege-5.5.0-win\\Protege-5.5.0\\Protege.exe")
    elif show_graph == True:
        if not own_pc:
            subprocess.run(["start","{}".format(graph_path),"C:\\Users\\smmnbenm\\Downloads\\Protege-5.5.0-win(1)\\Protege-5.5.0"],shell=True,capture_output=True)
        else:
            subprocess.getoutput("start {} C:\\Users\\user\\Downloads\\Protege-5.5.0-win\\Protege-5.5.0\\Protege.exe".format(graph_path) )
        
    if (return_tuples and return_graph) == True:
      return tuples, g_ba  
    
    elif return_tuples == True:
        return tuples
