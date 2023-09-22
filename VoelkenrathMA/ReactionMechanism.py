# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 09:19:16 2023

@author: smmcvoel
"""
import yaml
import math
import pubchempy as pcp
from collections import Counter
#import owlready2

## Import all necessary DWSIM packages
import os
import uuid
import clr

import pythoncom
import System
pythoncom.CoInitialize()

from System import String, Environment, Array
from System.IO import Directory, Path, File
from System.Collections.Generic import Dictionary

dwsimpath = "C:\\Users\\smmcvoel\\AppData\\Local\\DWSIM7\\"

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
#clr.AddReference(dwsimpath + "TcpComm.dll")
#clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")
clr.AddReference(dwsimpath + "DWSIM.FlowsheetSolver.dll")
clr.AddReference("System.Core")
clr.AddReference("System.Windows.Forms")
clr.AddReference(dwsimpath + "Newtonsoft.Json")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations, Reactors
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

from enum import Enum
from DWSIM import FlowsheetSolver
from DWSIM import Interfaces
from System import *

from System.Linq import *
from DWSIM import *
from DWSIM import FormPCBulk
from DWSIM.Interfaces import *
from DWSIM.Interfaces.Enums import *

from DWSIM.Interfaces.Enums.GraphicObjects import *

from Newtonsoft.Json import JsonConvert, Formatting

from DWSIM.Thermodynamics import *
from DWSIM.Thermodynamics.BaseClasses import *
from DWSIM.Thermodynamics.PropertyPackages.Auxiliary import *

from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization import GenerateCompounds
from DWSIM.Thermodynamics.Utilities.PetroleumCharacterization.Methods import *


#Directory.SetCurrentDirectory(dwsimpath)

# create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()

def createReactionScript(obj_name):
    GUID = obj_name
    sim.Scripts.Add(GUID, FlowsheetSolver.Script())
    sim.Scripts.TryGetValue(GUID)[1].Linked = True
    sim.Scripts.TryGetValue(GUID)[1].LinkedEventType = Interfaces.Enums.Scripts.EventType.ObjectCalculationStarted
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectName = obj_name
    sim.Scripts.TryGetValue(GUID)[1].LinkedObjectType = Interfaces.Enums.Scripts.ObjectType.FlowsheetObject
    sim.Scripts.TryGetValue(GUID)[1].PythonInterpreter = Interfaces.Enums.Scripts.Interpreter.IronPython
    sim.Scripts.TryGetValue(GUID)[1].Title = obj_name
    sim.Scripts.TryGetValue(GUID)[1].ScriptText = str()


def createReaction(data, substances):
    # add reaction (Evtl. muss der ganze folgende Abschnitt variabel gestaltet werden)
    # ACHTUNG: Definieren den Reaktionname z.b. als ID_1&2 und übergebe diesen an createReactionScript, sonst wird das Skript nicht verknüpft.
    mechanism = data[2]["ChemicalReaction"][0]
    
    i = 0
    while i <= len(mechanism):
        comps = Dictionary[str, float]()
        dorders = Dictionary[str, float]()
        rorders = Dictionary[str, float]()
        
        reaction_name = "ID_" + str(mechanism[i]["id"]) + "&" + str(mechanism[i+1]["id"])
        
        EA_1 = mechanism[i]["reactions"][0]["EA"]
        beta_1 = mechanism[i]["reactions"][0]["beta"]
        
        if "S0" in mechanism[i]["reactions"][0]:
            A_1 = mechanism[i]["reactions"][0]["S0"]
        elif "A_cm_units" in mechanism[i]["reactions"][0]:
            A_1 = mechanism[i]["reactions"][0]["A_cm_units"]
        else:
            print("Some unexpected error accured while setting kinetic parameters...")
            
        EA_2  = mechanism[i+1]["reactions"][0]["EA"]
        beta_2  = mechanism[i+1]["reactions"][0]["beta"]
        
        if "S0" in mechanism[i+1]["reactions"][0]:
            A_2 = mechanism[i+1]["reactions"][0]["S0"]
        elif "A_cm_units" in mechanism[i+1]["reactions"][0]:
            A_2 = mechanism[i+1]["reactions"][0]["A_cm_units"]
        else:
            print("Some unexpected error accured while setting kinetic parameters...")
            
        equation = mechanism[i]["reactions"][0]["reaction_equation"]
        educts_ = equation.split(">")[0].split("+")
        educts_count = Counter(educts_)
        products_ = equation.split(">")[1].split("+")
        products_count = Counter(products_)
        
        # set base compound as the first compound in equation
        base = educts_[0]
        
        for compound in educts_count:
            for j in range(len(substances)):
                if compound == substances[j][0]:
                    key = substances[j][1]
                    coefficient = educts_count[compound] * -1 # educts has a negative stochiometric coefficient
                    
                    comps.Add(key, coefficient)
                    dorders.Add(key, 0) # can be set to zero for every component, because it isn't used with "user defined" kinetic scripts
                    rorders.Add(key, 0) # can be set to zero for every component, because it isn't used with "user defined" kinetic scripts
                    
        for compound in products_count:
            for j in range(len(substances)):
                if compound == substances[j][0]:
                    key = substances[j][1]
                    coefficient = products_count[compound] # products has a positive stochiometric coefficient

                    comps.Add(key, coefficient)
                    dorders.Add(key, 0) # can be set to zero for every component, because it isn't used with "user defined" kinetic scripts
                    rorders.Add(key, 0) # can be set to zero for every component, because it isn't used with "user defined" kinetic scripts
               
        # values for A & EA is set to "1" for forward and backward reaction, because it isnt used with "user defined" but has to be given
        reaction_kinetic = sim.CreateKineticReaction(reaction_name,"This reaction is created fully automatic", comps, dorders, rorders,
                                                     base, "Mixture", "Fugacities", "Pa", "mol/[m3.s]",
                                                     1.0, 1.0, 1.0, 1.0, "", "")
        sim.AddReaction(reaction_kinetic)
        sim.AddReactionToSet(reaction_kinetic.ID, "DefaultSet", True, 0)
    
        createReactionScript(reaction_name)
        myreaction = sim.GetReaction(reaction_name)
        myscripttitle = reaction_name
        myscript = sim.Scripts[myscripttitle]

        # indention is stupid but necessary, because script isnt running in DWSIM with the "right" python indention
        myscript.ScriptText = str(f"""import math                              
from System import Array
from DWSIM.Thermodynamics import *

import clr
clr.AddReference('DWSIM.MathOps.DotNumerics')
from DotNumerics.ODE import *

R = 8.314

A_1 = {A_1}
b_1 = {beta_1}
EA_1 = {EA_1}

A_2 = {A_2}
b_2 = {beta_2}
EA_2 = {EA_2}

k_1 = A_1 * math.pow(T, b_1) * math.exp(-EA_1/(R*T))
k_2 = A_2 * math.pow(T, b_2) * math.exp(-EA_2/(R*T))

r = (k_1 * R1 * R2) - (k_2 * P1 * P2)""")
                              
        myreaction.ReactionKinetics = ReactionKinetics(1)
        myreaction.ScriptTitle = myscripttitle
        
        i+=2
        
    return reaction_kinetic    
    

def simulation(name, data):
    # get compounds from DWISM and add them to Simulation
    print("Adding substances to Simulation...")
    substances = data[0]["Mixture"][0]["substances"]
    for sub in substances:
        # adding every "real" compound
        if "-Ni" not in sub:
            # water is a special case, because it is as Water in DWSIM instead with its iupac-name "oxidane"
            if sub == "H2O":
                key = "Water"
                #sim.AddCompound(key)
                compound = sim.AvailableCompounds[key]
                sim.SelectedCompounds.Add(compound.Name, compound)
                index = substances.index(sub)
                substances[index] = [sub, key]
            # CO2 is a special case, because pubchempy has no iupac_name for it
            elif sub == "CO2":
                key = "Carbon dioxide"
                #sim.AddCompound(key)
                compound = sim.AvailableCompounds[key]
                sim.SelectedCompounds.Add(compound.Name, compound)
                index = substances.index(sub)
                substances[index] = [sub, key]
            else:
                key = pcp.get_compounds(sub,"formula")[0].iupac_name
                # check if "molecular" is in iupac_name and split string if it is, because compounds are in DWSIM without the prefix "molecular"
                if "molecular" in key:
                    key = key.split("molecular ")[1].capitalize()
                    #sim.AddCompound(key)
                    compound = sim.AvailableCompounds[key]
                    sim.SelectedCompounds.Add(compound.Name, compound)
                    index = substances.index(sub)
                    substances[index] = [sub, key]
                else:
                    key = key.capitalize()
                    #sim.AddCompound(key)
                    compound = sim.AvailableCompounds[key]
                    sim.SelectedCompounds.Add(compound.Name, compound)
                    index = substances.index(sub)
                    substances[index] = [sub, key]
        # adding every pseudocompound
        else:
            key = sub
            #sim.AddCompound(key)
            compound = sim.AvailableCompounds[key]
            sim.SelectedCompounds.Add(compound.Name, compound)
            index = substances.index(sub)
            substances[index] = [sub, key]
    print("Done!")

    # material
    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "feed")
    m2 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "outlet")
    
    # energy
    e1 = sim.AddObject(ObjectType.EnergyStream, 50, 100, "power")
    
    # device
    r1 = sim.AddObject(ObjectType.RCT_PFR, 100, 75, "reactor")
    
    # get flowsheet objects as object
    m1 = m1.GetAsObject()
    m2 = m2.GetAsObject()
    e1 = e1.GetAsObject()
    r1 = r1.GetAsObject()
    
    # connect Objects
    r1.ConnectFeedMaterialStream(m1,0)
    r1.ConnectProductMaterialStream(m2,0)
    r1.ConnectFeedEnergyStream(e1,1)
    
    # add property package
    sim.CreateAndAddPropertyPackage("NRTL")
    
    # specify parameter (material)
    print("Set mole fractions...")
    mole_fraction = data[0]["Mixture"][0]["mole_fraction"]
    composition = [0.0] * len(substances)
    for entry in mole_fraction:
        sub, value = entry
        for i in range(len(substances)):
            if sub in substances[i]:
                index = i #substances.index(sub)
                composition[index] = value
    composition = tuple(composition)
    composition = Array[float](composition)
    m1.SetOverallComposition(composition)
    print("Done!")
    
    m1.SetTemperature(data[0]["Mixture"][0]["temperature"])
    V_flow = math.pi * (data[1]["Reactor"][0]["tube_diameter"]/2) ** 2 * data[0]["Mixture"][0]["velocity"]
    m1.SetVolumetricFlow(V_flow)
    
    # specify parameter (reactor); doesnt make a difference if diameter or length is choosen
    r1.Volume = data[1]["Reactor"][0]["reactive_volume"]
    r1.Length = data[1]["Reactor"][0]["tube_length"]
    #r1.Diameter = data[1]["Reactor"][0]["tube_diameter"]
    r1.NumberOfTubes = data[1]["Reactor"][0]["num_tubes"]
    
    if data[1]["Reactor"][0]["calculation_mode"] == "isothermal":
        r1.ReactorOperationMode = Reactors.OperationMode.Isothermic
    elif data[1]["Reactor"][0]["calculation_mode"] == "adiabatic":
        r1.ReactorOperationMode = Reactors.OperationMode.Adiabatic
    else:
        print("Error accured while setting the ReactorOperationMode!")
    
    print("Create reactions and kinetic scripts...")
    reaction_system = createReaction(data, substances)
    print("Done!")
    
    # set Solver Mode
    Settings.SolveMode = 0
    
    errors = interf.CalculateFlowsheet2(sim)
    
    # save file as dwxmz
    fileName_dwsim = name + ".dwxmz"
    fileNameToSave = Path.Combine("C:\\Users\\smmcvoel\\Desktop\\Temporäre Ablage", fileName_dwsim)
    #fileNameToSave = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), fileName_dwsim)
    
    interf.SaveFlowsheet(sim, fileNameToSave, True)
    
    # packages to draw and save the pdf to an image and display it
    clr.AddReference(dwsimpath + "SkiaSharp.dll")
    clr.AddReference("System.Drawing")
    
    from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
    from System.IO import MemoryStream
    from System.Drawing import Image
    from System.Drawing.Imaging import ImageFormat
        
    # save the pdf to an image and display it
    PFDSurface = sim.GetSurface()
    
    fileName_pic = name + ".png"
    
    bmp = SKBitmap(1024, 768)
    canvas = SKCanvas(bmp)
    canvas.Scale(1.0)
    PFDSurface.UpdateCanvas(canvas)
    d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
    stri = MemoryStream()
    d.SaveTo(stri)
    image = Image.FromStream(stri)
    imgPath = Path.Combine("C:\\Users\\smmcvoel\\Desktop\\Temporäre Ablage", fileName_pic)
    #imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), fileName_pic)
    image.Save(imgPath, ImageFormat.Png)
    stri.Dispose()
    canvas.Dispose()
    bmp.Dispose()
    
    from PIL import Image
    
    im = Image.open(imgPath)
    im.show()
    
    
def run(name):
    # load yaml-datafile
    # ACHTUNG: Übergabe des yaml-file zum Ende hin Variabel gestalten, sodass gesamter Workflow
    # mit einem einzigen Befehl ausgeführt werden kann
    # ACHTUNG: Onto-Klassen sind voerst im DataSheet auskommentiert, da sie Probleme beim Import gemacht haben
    # --> Lösung sollte allgemeingültig sein, d.h. die Klassen vorher zu definieren klappt nur wenn es automatisiert geht
    
    with open("linkml/Methanation_PFR_DataSheet.yaml", "r") as file:
        data = yaml.safe_load(file)
        
    simulation(name, data)


   