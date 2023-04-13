# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 11:19:23 2023

@author: 49157
"""

from owlready2 import *

def class_creation(substance_list, onto):
    # Durchiterieren durch substance_list, um enthaltene Strings als Klassen 
    # in Ontologie onto einzusetzen
    for substance in test_substances:
        # codestring aufsetzen, .format(substance,substance) am Ende ersetzt 
        # jeden {}-Teil des Strings mit Inhalt der Variablen substance
        codestring = """with onto:
            class {}(Thing):
                label = '{}'
                pass
            """.format(substance,substance)
        
        # ABTSox und ABTSred der Klasse ABTS unterordnen
        if substance == "ABTSox" or substance == "ABTSred":
            codestring = """with onto:
            class {}({}):
                label = '{}'
                pass
            """.format(substance,"ABTSTest",substance)
        
        # Code, der im codestring enthalten ist compilieren
        code = compile(codestring, "<string>","exec")
        
        # Code ausführen
        exec(code)

def dataProp_creation(dataProp_dict, onto):
    # Benötigte Relationen bestimmen via set() -> auch bei Mehrfachnennung
    # ist jede Relation aus Dictionary nur max. 1x enthalten in relation_list
    relation_set = set()
    for i in list(dataProp_dict.keys()):
        relation_set.update(set(dataProp_dict[i].keys()))
    
    # Definieren jeder Relation in der Ontologie via codestring und exec:
    for rel in relation_set:
        codestring = """with onto:
            class {}(DataProperty):
                label = '{}'
                pass
            """.format(rel,rel)
        
        # Code, der im codestring enthalten ist compilieren
        code = compile(codestring, "<string>","exec")
        
        # Code ausführen
        exec(code)
    
    
def set_relations(dataProp_dict, onto):
    # Wieder aufsetzen des Codestrings, diesmal anhand eines Dictionaries
    
    for class_name in list(dataProp_dict.keys()):
        # Klasse in Ontologie raussuchen, die zum Dictionary-key passt
        onto_class = onto.search_one(label=class_name)
        
        for entry in dataProp_dict[class_name]:
            
            data_prop_type = type(dataProp_dict[class_name][entry])
            if (data_prop_type == int) or (data_prop_type == float):
                codestring = "{}.{} = {}".format(str(onto_class),str(entry), dataProp_dict[class_name][entry])                
                print(dataProp_dict[class_name][entry])
           
            else:
                codestring = "{}.{} = '{}'".format(str(onto_class),str(entry), str(dataProp_dict[class_name][entry]))                
            
            # Code, der im codestring enthalten ist compilieren
            code = compile(codestring, "<string>","exec")
            # Code ausführen
            exec(code)
            
        
# Create an empty ontology
onto = get_ontology("http://test.org/onto.owl")

test_substances = ["LaccaseTest", "ABTSTest", "ABTSoxTest", "ABTSredTest", "Oxygen", "Water"]

test_dict = {"LaccaseTest": {"has_relative_densities": 1000.0/1000.0,
                         "nbps": 55 + 273.15,
                         "has_stoichiometric_coefficient": -7.5219E-05,
                         "has_direct_order_coefficient": 0.0,
                         "has_reverse_order_coefficient": 0.0},
             "ABTSoxTest":{"has_relative_densities": 1370.0/1000.0,
                           "nbps": 100 + 273.15,
                           "has_stoichiometric_coefficient": 4,
                           "has_direct_order_coefficient": 0.0,
                           "has_reverse_order_coefficient": 0.0},
             "ABTSredTest":{"has_relative_densities": 1372.0/1000.0,
                            "nbps": 101 + 273.15,
                            "has_stoichiometric_coefficient": -4,
                            "has_direct_order_coefficient": 1.0,
                            "has_reverse_order_coefficient": 0.0},
             "Oxygen": {"has_stoichiometric_coefficient": -1,
                        "has_direct_order_coefficient": 0.0,
                        "has_reverse_order_coefficient": 0.0},
             "Water": {"has_stoichiometric_coefficient": 2,
                       "has_direct_order_coefficient": 0.0,
                       "has_reverse_order_coefficient": 0.0}
             }

# Aufrufen von Funktion class_creation(), um alle Strings aus Liste test_substances
# in Ontologie einzubauen
class_creation(test_substances, onto)

dataProp_creation(test_dict, onto)

set_relations(test_dict, onto)

# Save the ontology
onto.save(file="00test-onto.owl", format="rdfxml")

# save values to be able to store components as Json files
# relative desntities and normal boiling points
# the rest will be estimated
Laccase_dens = onto.LaccaseTest.has_relative_densities[0]
ABTSoxTest_dens = onto.ABTSoxTest.has_relative_densities[0]
ABTSredTest_dens = onto.ABTSredTest.has_relative_densities[0]

Laccase_nbps = onto.LaccaseTest.nbps[0]
ABTSoxTest_nbps = onto.ABTSoxTest.nbps[0]
ABTSredTest_nbps = onto.ABTSredTest.nbps[0]

import os

import pythoncom
pythoncom.CoInitialize()
import clr
import System

from System.IO import Directory, Path, File
from System import String, Environment
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\49157\\AppData\\Local\\DWSIM8\\"

clr.AddReference(dwsimpath + "DWSIM")
clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")
clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "System.Buffers.dll")

clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
clr.AddReference(dwsimpath + "Newtonsoft.Json")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

from System import *
from System.Linq import *
from DWSIM import *
from DWSIM import FormPCBulk
 
from DWSIM.Interfaces import *
from DWSIM.Interfaces.Enums import*
from DWSIM.Interfaces.Enums.GraphicObjects import *
from Newtonsoft.Json import JsonConvert, Formatting

from DWSIM.Thermodynamics import*
from DWSIM.Thermodynamics.BaseClasses import *
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import *
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization import GenerateCompounds
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization.Methods import *

Directory.SetCurrentDirectory(dwsimpath)

# Create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

# assay data from spreadsheet
names = [test_substances[0], test_substances[2], test_substances[3]]
relative_densities = [Laccase_dens, ABTSoxTest_dens, ABTSredTest_dens] # relative
nbps = [Laccase_nbps, ABTSoxTest_nbps, ABTSredTest_nbps] # K
 
n = 3

# bulk c7+ pseudocompound creator setting 
Tccorr = "Riazi-Daubert (1985)"
Pccorr = "Riazi-Daubert (1985)"
AFcorr = "Lee-Kesler (1976)"
MWcorr = "Winn (1956)"
adjustZR = True
adjustAf = True
 
# initial values for MW, SG and NBP 
mw0 = 65
sg0 = 0.65
nbp0 = 320

# pseudocompound generator 
comps = GenerateCompounds()
 
for i in range(0, n):
    
    # Will generate only 1 pseudocompound for each item on the list of assay data.
    # Normally we generate from 7 to 10 pseudocompounds for each set of assay data (MW, SG and NBP)
 
    comp_results = comps.GenerateCompounds(names[i], 1, Tccorr, Pccorr, AFcorr, 
                                           MWcorr, adjustAf, adjustZR, None, 
                                           relative_densities[i], nbps[i], None, 
                                           None, None, None, mw0, sg0, nbp0)
 
    comp_values = list(comp_results.Values)
    comp_values[0].Name = names[i]
    comp_values[0].ConstantProperties.Name = names[i]
    comp_values[0].ComponentName = names[i]
    
    # save the compound to a JSON file, which can be loaded back on any simulation
    # IMPORTANT: Save JSON file into "addcomps" file to be able to import the compound into simulation
 
    System.IO.File.WriteAllText("C:\\Users\\49157\\AppData\\Local\\DWSIM8\\addcomps\\"
                                + str(names[i]) + ".json", 
                                JsonConvert.SerializeObject(comp_values[0].ConstantProperties, 
                                                            Formatting.Indented))

# Save values that are needed for the simulation
# Stoichiometric coefficients, Direct order coefficients, Reverse order coefficients
# Laccase
stoichC_L = onto.LaccaseTest.has_stoichiometric_coefficient[0]
dorder_L = onto.LaccaseTest.has_direct_order_coefficient[0]
rorder_L = onto.LaccaseTest.has_reverse_order_coefficient[0]

# ABTSox
stoichC_Aox = onto.ABTSoxTest.has_stoichiometric_coefficient[0]
dorder_Aox = onto.ABTSoxTest.has_direct_order_coefficient[0]
rorder_Aox = onto.ABTSoxTest.has_reverse_order_coefficient[0]

# ABTSred
stoichC_Ared = onto.ABTSredTest.has_stoichiometric_coefficient[0]
dorder_Ared = onto.ABTSredTest.has_direct_order_coefficient[0]
rorder_Ared = onto.ABTSredTest.has_reverse_order_coefficient[0]

# Oxygen
stoichC_O = onto.Oxygen.has_stoichiometric_coefficient[0]
dorder_O = onto.Oxygen.has_direct_order_coefficient[0]
rorder_O = onto.Oxygen.has_reverse_order_coefficient[0]

# Oxygen
stoichC_W = onto.Water.has_stoichiometric_coefficient[0]
dorder_W = onto.Water.has_direct_order_coefficient[0]
rorder_W = onto.Water.has_reverse_order_coefficient[0]

# Add compounds 
sim.AddCompound(test_substances[0]) # Laccase
sim.AddCompound(test_substances[2]) # ABTSoxTest
sim.AddCompound(test_substances[3]) # ABTSredTest
sim.AddCompound(test_substances[4]) # Oxygen
sim.AddCompound(test_substances[5]) # Water

# Stoichiometric coefficients
comps = Dictionary[str, float]()
comps.Add(test_substances[0], stoichC_L);
comps.Add(test_substances[2], stoichC_Aox);
comps.Add(test_substances[3], stoichC_Ared);
comps.Add(test_substances[4], stoichC_O);
comps.Add(test_substances[5], stoichC_W);

# Direct order coefficients
dorders = Dictionary[str, float]()
dorders.Add(test_substances[0], dorder_L);
dorders.Add(test_substances[2], dorder_Aox);
dorders.Add(test_substances[3], dorder_Ared);
dorders.Add(test_substances[4], dorder_O);
dorders.Add(test_substances[5], dorder_W);

# Reverse order coefficients
rorders = Dictionary[str, float]()
rorders.Add(test_substances[0], rorder_L);
rorders.Add(test_substances[2], rorder_Aox);
rorders.Add(test_substances[3], rorder_Ared);
rorders.Add(test_substances[4], rorder_O);
rorders.Add(test_substances[5], rorder_W);

kr1 = sim.CreateKineticReaction("ABTS Oxidation", "ABTS Oxidation using Laccase", 
        comps, dorders, rorders, test_substances[3], "Mixture", "Molar Concentration", 
        "kmol/m3", "kmol/[m3.h]", 0.5, 0.0, 0.0, 0.0, "", "")

# Add all objects
m1 = sim.AddObject(ObjectType.MaterialStream, 0, 10, test_substances[5])
m2 = sim.AddObject(ObjectType.MaterialStream, 0, 60, test_substances[3])
m3 = sim.AddObject(ObjectType.MaterialStream, 100, 50, "Mixture")
m4 = sim.AddObject(ObjectType.MaterialStream, 250, 50, test_substances[2])
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 90, "Heat")
pfr = sim.AddObject(ObjectType.RCT_PFR, 150, 50, "PFR")
MIX1 = sim.AddObject(ObjectType.Mixer, 50, 50, "Mixer")
 
m1 = m1.GetAsObject()
m2 = m2.GetAsObject()
m3 = m3.GetAsObject()
m4 = m4.GetAsObject()
e1 = e1.GetAsObject()
MIX1 = MIX1.GetAsObject()
pfr = pfr.GetAsObject()

# Connect the inlet streams
sim.ConnectObjects(m1.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(m2.GraphicObject, MIX1.GraphicObject, -1, -1)
sim.ConnectObjects(MIX1.GraphicObject, m3.GraphicObject, -1, -1)

pfr.ConnectFeedMaterialStream(m3, 0)
pfr.ConnectProductMaterialStream(m4, 0)
pfr.ConnectFeedEnergyStream(e1, 1)

# PFR properties (fix pressure drop inside reactor)
pfr.ReactorOperationMode = Reactors.OperationMode.Isothermic
pfr.ReactorSizingType = Reactors.Reactor_PFR.SizingType.Length
pfr.Volume = 0.000008; # m3
pfr.Length = 0.0001; # m

# Set Property Package
sim.CreateAndAddPropertyPackage("Raoult's Law")

m1.SetTemperature(311.15) # Kelvin
m2.SetTemperature(311.15) # Kelvin
m3.SetTemperature(311.15) # Kelvin
m4.SetTemperature(311.15) # Kelvin

m1.SetMolarFlow(0.0) # will set by compound

m1.SetOverallCompoundMolarFlow(test_substances[5], 1.0) # mol/s
m1.SetOverallCompoundMolarFlow(test_substances[3], 0.0)  # mol/

m2.SetOverallCompoundMolarFlow(test_substances[5], 0.0) # mol/s
m2.SetOverallCompoundMolarFlow(test_substances[3], 1.0)  # mol/s

sim.AddReaction(kr1)
sim.AddReactionToSet(kr1.ID, "DefaultSet", True, 0)

# request a calculation

errors = interf.CalculateFlowsheet4(sim);

print("Reactor Heat Load: {0:.4g} kW".format(pfr.DeltaQ))
for c in pfr.ComponentConversions:
    if (c.Value > 0): print("{0} conversion: {1:.4g}%".format(c.Key, c.Value * 100.0))

if (len(errors) > 0):
    for e in errors:
        print("Error: " + e.ToString())

# reactor profiles (temperature, pressure and concentration)
coordinates = [] # volume coordinate in m3
names = [] # compound names
values = [] # concentrations in mol/m3 (0 to j, j = number of compounds - 1), temperature in K (j+1), pressure in Pa (j+2)

for p in pfr.points:
    coordinates.append(p[0])

for j in range(1, pfr.ComponentConversions.Count + 3):
    list1 = []
    for p in pfr.points:
        list1.append(p[j])
    values.append(list1)

for k in pfr.ComponentConversions.Keys:
    names.append(k)


# save file
fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), 
                              "test dynamic classes and DWSIM.dwxmz")
interf.SaveFlowsheet(sim, fileNameToSave, True)

# save the pfd to an image and display it
clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

PFDSurface = sim.GetSurface()
bmp = SKBitmap(1000, 600)
canvas = SKCanvas(bmp)
canvas.Scale(0.5)
PFDSurface.ZoomAll(bmp.Width, bmp.Height)
PFDSurface.UpdateCanvas(canvas)
d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
str = MemoryStream()
d.SaveTo(str)
image = Image.FromStream(str)
imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "TEST100.png")
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image
im = Image.open(imgPath)
im.show()