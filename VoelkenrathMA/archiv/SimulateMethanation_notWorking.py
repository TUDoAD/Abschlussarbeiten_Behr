# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 09:11:35 2023

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


Directory.SetCurrentDirectory(dwsimpath)

# create automation manager
interf = Automation3()
sim = interf.CreateFlowsheet()


def createReaction(data, substances):
    mechanism = data[2]["ChemicalReaction"][0]
    
    i = 0
    while i <= (len(mechanism)-1):
        comps = Dictionary[str, float]()
        dorders = Dictionary[str, float]()
        rorders = Dictionary[str, float]()
        
        reaction_name = "ID_" + str(i)
        
        br = mechanism[i]["reactions"][0]["br"]
        K_1 = mechanism[i]["reactions"][0]["K_1"]
        K_2 = mechanism[i]["reactions"][0]["K_2"]
        K_3 = mechanism[i]["reactions"][0]["K_3"]
        
        equation = mechanism[i]["reactions"][0]["reaction_equation"]
        
        educts_ = equation.split(">")[0].split("+")
        educts = []
        for educt in educts_:
            if educt[0].isdigit():
                educts.append([educt[1:], -int(educt[0])])
            else: 
                educts.append([educt, -1])
                
        products_ = equation.split(">")[1].split("+")
        products = []
        for product in products_:
            if product[0].isdigit():
                products.append([product[1:], int(product[0])])
            else: 
                products.append([product, 1])
        
        # set base compound
        base_formula = educts[0][0]
        for j in range(len(substances)):
            if base_formula == substances[j][0]:
                base_key = substances[j][1]
                print("Base: " + str(base_key))
                
        for compound in educts:
            for j in range(len(substances)):
                if compound[0]  == substances[j][0]:
                    key = substances[j][1]
                    coefficient = compound[1]
                    print("Educt: " + str(key) + " " + str(coefficient))
                    comps.Add(key, float(coefficient))
                    dorders.Add(key, 0)
                    rorders.Add(key, 0)

        for compound in products:
            for j in range(len(substances)):
                if compound[0]  == substances[j][0]:
                    key = substances[j][1]
                    coefficient = compound[1]
                    print("Product: " + str(key) + " " + str(coefficient))
                    comps.Add(key, float(coefficient))
                    dorders.Add(key, 0)
                    rorders.Add(key, 0)
        
        # create reaction, set numerator and denominator to 1, because it get overwritten with own kintic skript
        reaction = sim.CreateHetCatReaction(reaction_name, "This reaction is created automatically!", comps, base_key, "Mixture", 
                                            "Fugacities", "Pa", "mol/[kg.s]", "1", "1" )
        
        sim.AddReaction(reaction)
        sim.AddReactionToSet(reaction.ID, "DefaultSet", True, 0)
        
        # add kinetic script
        sim.Scripts.Add(reaction_name, FlowsheetSolver.Script())
        myscripttitle = reaction_name
        
        myscript = sim.Scripts[myscripttitle]
        myscript.Title = myscripttitle
        myscript.ID = str(i)
        myscript.ScriptText = str(f"""import math
from System import Array
from DWSIM.Thermodynamics import *

import clr
clr.AddReference('DWSIM.MathOps.DotNumerics')                                                                 
from DotNumerics.ODE import *

K_0 = {br}
K_1 = {K_1}
K_2 = {K_2}
K_3 = {K_3}

r=(K_0 * R2 * math.pow(R1, 1/3))/(1 + K_1 * R2 + K_2 * R1 + K_3 * P2)""")
        myreaction = sim.GetReaction(reaction_name)
        myreaction.ReactionKinetics = ReactionKinetics(1)
        myreaction.ScriptTitle = myscripttitle
        
        i+=1
                    

def simulation(name, data, combination):
    interf = Automation3()
    sim = interf.CreateFlowsheet()
    
    path_storage = "C:\\Users\\smmcvoel\\Desktop\\Temporäre Ablage\\dice_01"
    temperature, pressure, loading = combination
    
    ## create flowsheet and run simulation
    # get compound from DWSIM and add them to the simulation
    print("Adding substances to Simulation...")
    substances = data[0]["Mixture"][0]["substances"]
    for sub in substances:
        try:
            if "-Ni" not in sub:
                # water is a special case, because it is as water in DWSIM instead with its iupac-name "oxidane"
                if sub == "H2O":
                    key = "Water"
                    compound = sim.AvailableCompounds[key]
                    sim.SelectedCompounds.Add(compound.Name, compound)
                    index = substances.index(sub)    
                    substances[index] = [sub, key]
                # CO2 is a special case, because pubchempy has no iupac-name for it
                elif sub == "CO2":
                    key = "Carbon dioxide"
                    compound = sim.AvailableCompounds[key]
                    sim.SelectedCompounds.Add(compound.Name, compound)
                    index = substances.index(sub)
                    substances[index] = [sub, key]
                else:
                    key = pcp.get_compounds(sub,"formula")[0].iupac_name
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
        except: ArgumentException
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
    
    # specify material parameter
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
    
    m1.SetTemperature(420) #temperature)
    m1.SetPressure(100000) #pressure)
    
    V_flow = math.pi * (data[1]["Reactor"][0]["tube_diameter"]/2) ** 2 * data[0]["Mixture"][0]["velocity"]
    m1.SetVolumetricFlow(V_flow)
    
    
    # specify reactor parameter; doesnt make a difference if diameter or length is choosen
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
        
    # specify catalyst parameter
    r1.CatalystLoading = 1000 #loading
    r1.CatalystVoidFraction = data[1]['Reactor'][0]["catalyst_void_fraction"]
    #cat_diameter = data[1]['Reactor'][0]["catalyst_particle_diameter"] #m
    r1.CatalystParticleDiameter = data[1]['Reactor'][0]["catalyst_particle_diameter"]
    
    print("Create reactions and kinetic scripts...")
    createReaction(data, substances)
    print("Done!")

    # set Solver Mode
    Settings.SolveMode = 0
    
    errors = interf.CalculateFlowsheet2(sim)
    
    # save file as dwxmz
    fileName_dwsim = name + ".dwxmz"
    fileNameToSave = Path.Combine(path_storage, fileName_dwsim)
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
    imgPath = Path.Combine(path_storage, fileName_pic)
    #imgPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), fileName_pic)
    image.Save(imgPath, ImageFormat.Png)
    stri.Dispose()
    canvas.Dispose()
    bmp.Dispose()
    
    from PIL import Image
    
    im = Image.open(imgPath)
    #im.show()
