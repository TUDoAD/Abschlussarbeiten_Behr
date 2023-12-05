# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 09:11:35 2023

@author: smmcvoel
"""
import sys
import yaml
import math
import pandas as pd
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


def createReaction(data, substances):
    ## Adding METH_CO2
    for i in range(len(data)):
        if "ChemicalReaction" in data[i]:
            mechanism = data[i]["ChemicalReaction"]
    
    comps = Dictionary[str, float]()
    dorders = Dictionary[str, float]()
    rorders = Dictionary[str, float]()
    
    reaction_name = "METH_CO2"
    
    equation = mechanism[0][0]["reactions"][0]["reaction_equation"]
    
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
    
    # adding educts
    for compound in educts:
        for j in range(len(substances)):
            if compound[0]  == substances[j][0]:
                key = substances[j][1]
                coefficient = compound[1]
                comps.Add(key, float(coefficient))
                dorders.Add(key, 0)
                rorders.Add(key, 0)
    
    # adding product
    for compound in products:
        for j in range(len(substances)):
            if compound[0]  == substances[j][0]:
                key = substances[j][1]
                coefficient = compound[1]
                comps.Add(key, float(coefficient))
                dorders.Add(key, 0)
                rorders.Add(key, 0)
    
    # adding CO as "inert"
    key = "Carbon monoxide"
    coefficient = 0
    comps.Add(key, float(coefficient))
    dorders.Add(key, 0)
    rorders.Add(key, 0)
    
    num = "1.14*10^8*exp(-110000/(8.314*(T))) * 6.12*10^(-9)*exp(82900/(8.314*(T))) * 5*10^(-5)*exp(70000/(8.314*(T))) * R2 * R1 * (1- (P1 * P2^2)/(R2^4 * R1) * 1/exp(34.218 - 31266/(T)))"
    den = "(1+5*10^(-5)*exp(70000/(8.314*(T))) * R1 + 6.12*10^(-9)*exp(82900/(8.314*(T)))*R2 + 1.77*10^(5)*exp(-88600/(8.314*(T)))*P2 + 8.23*10^(-5) *exp(70650/(8.314*(T))) * N1)^2"
    # create reaction, set numerator and denominator to 1, because it get overwritten with own kintic skript
    reaction = sim.CreateHetCatReaction(reaction_name, "This reaction is created automatically!", comps, base_key, "Vapor",
                                        "Partial Pressure", "Pa", "mol/[kg.s]", num, den)
    
    sim.AddReaction(reaction)
    sim.AddReactionToSet(reaction.ID, "DefaultSet", True, 0)
    
    ## Adding RWGS
    comps = Dictionary[str, float]()
    dorders = Dictionary[str, float]()
    rorders = Dictionary[str, float]()
    
    reaction_name = "RWGS"
    
    equation = "CO2+H2>CO+H2O"
    
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
    
    # adding educts
    for compound in educts:
        for j in range(len(substances)):
            if compound[0]  == substances[j][0]:
                key = substances[j][1]
                coefficient = compound[1]
                comps.Add(key, float(coefficient))
                dorders.Add(key, 0)
                rorders.Add(key, 0)
    
    # adding product
    for compound in products:
        for j in range(len(substances)):
            if compound[0]  == substances[j][0]:
                key = substances[j][1]
                coefficient = compound[1]
                comps.Add(key, float(coefficient))
                dorders.Add(key, 0)
                rorders.Add(key, 0)
                
    # adding CH4 as "inert"
    key = "Methane"
    coefficient = 0
    comps.Add(key, float(coefficient))
    dorders.Add(key, 0)
    rorders.Add(key, 0)
    
    num = "1.78*10^6*exp(-97100/(8.314*(T))) * 5*10^(-5)*exp(70000/(8.314*(T)))*R1 * (1- (P1 * P2)/(R2 * R1)*1/exp(-3.798 + 4160/(T)))"
    den = "1+5*10^(-5)*exp(70000/(8.314*(T))) * R1 + 6.12*10^(-9)*exp(82900/(8.314*(T)))*R2 + 1.77*10^(5)*exp(-88600/(8.314*(T)))*P1 + 8.23*10^(-5) *exp(70650/(8.314*(T))) * P2"
    # create reaction, set numerator and denominator to 1, because it get overwritten with own kintic skript
    reaction = sim.CreateHetCatReaction(reaction_name, "This reaction is created automatically!", comps, base_key, "Vapor",
                                        "Partial Pressure", "Pa", "mol/[kg.s]", num, den)
    
    sim.AddReaction(reaction)
    sim.AddReactionToSet(reaction.ID, "DefaultSet", True, 0)
    
    
    ## Adding METH_CO
    comps = Dictionary[str, float]()
    dorders = Dictionary[str, float]()
    rorders = Dictionary[str, float]()
    
    reaction_name = "METH_CO"
    
    equation = "CO+3H2>CH4+H2O"
    
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
    
    # adding educts
    for compound in educts:
        for j in range(len(substances)):
            if compound[0]  == substances[j][0]:
                key = substances[j][1]
                coefficient = compound[1]
                comps.Add(key, float(coefficient))
                dorders.Add(key, 0)
                rorders.Add(key, 0)
    
    # adding product
    for compound in products:
        for j in range(len(substances)):
            if compound[0]  == substances[j][0]:
                key = substances[j][1]
                coefficient = compound[1]
                comps.Add(key, float(coefficient))
                dorders.Add(key, 0)
                rorders.Add(key, 0)
                
    # adding CO2 as "inert"
    key = "Carbon dioxide"
    coefficient = 0
    comps.Add(key, float(coefficient))
    dorders.Add(key, 0)
    rorders.Add(key, 0)
    
    num = "2.2*10^8*exp(-97300/(8.314*(T))) * 6.12*10^(-9)*exp(82900/(8.314*(T))) * 8.23*10^(-5)*exp(70650/(8.314*(T)))*R1*R2 * (1- (P1*P2)/(R1^3 * R2) * 1/exp(30.42-27106/(T)))"
    den = "(1+5*10^(-5)*exp(70000/(8.314*(T))) * N1 + 6.12*10^(-9)*exp(82900/(8.314*(T)))*R1 + 1.77*10^(5)*exp(-88600/(8.314*(T)))*P2 + 8.23*10^(-5) *exp(70650/(8.314*(T))) * R2)^2"
    
    # create reaction, set numerator and denominator to 1, because it get overwritten with own kintic skript
    reaction = sim.CreateHetCatReaction(reaction_name, "This reaction is created automatically!", comps, base_key, "Vapor",
                                        "Partial Pressure", "Pa", "mol/[kg.s]", num, den)
    
    sim.AddReaction(reaction)
    sim.AddReactionToSet(reaction.ID, "DefaultSet", True, 0)
                    

def simulation(name_sim, path, data, combination):
    ## create flowsheet and run simulation
    temperature_outlet, pressure, res_t = combination
    
    # set variable parameter for the new linkML-file
    for i in range(len(data)):
        if "Mixture" in data[i]:
            temperature_inlet = data[i]["Mixture"][0]["temperature"][0]["feed"]
            data[i]["Mixture"][0]["temperature"][0]["outlet"] = temperature_outlet
            data[i]["Mixture"][0]["pressure"] = pressure
            #data[i]["Mixture"][0]["velocity"] = veloc 
            data[i]["Mixture"][0]["residence time"] = res_t
            
            substances = data[i]["Mixture"][0]["substances"]
            mole_fraction = data[i]["Mixture"][0]["mole_fraction"]
    
    # get compound from DWSIM and add them to the simulation
    print("Adding substances to Simulation...")
    
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
                        compound = sim.AvailableCompounds[key]
                        sim.SelectedCompounds.Add(compound.Name, compound)
                        index = substances.index(sub)
                        substances[index] = [sub, key]
                    else:
                        key = key.capitalize()
                        compound = sim.AvailableCompounds[key]
                        sim.SelectedCompounds.Add(compound.Name, compound)
                        index = substances.index(sub)
                        substances[index] = [sub, key]
        except: ArgumentException
    print("Done!")
        
    # material
    m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "feed")
    m2 = sim.AddObject(ObjectType.MaterialStream, 200, 50, "outlet")
    m3 = sim.AddObject(ObjectType.MaterialStream, 325, 50, "expanded")
    m4 = sim.AddObject(ObjectType.MaterialStream, 450, 50, "cooled")
    m5 = sim.AddObject(ObjectType.MaterialStream, 600, 50, "sep_gas")
    m6 = sim.AddObject(ObjectType.MaterialStream, 600, 100, "sep_liquid")
    
    # energy
    e1 = sim.AddObject(ObjectType.EnergyStream, 50, 125, "E1")
    e2 = sim.AddObject(ObjectType.EnergyStream, 325, 125, "E2")
    
    # device
    r1 = sim.AddObject(ObjectType.RCT_PFR, 100, 75, "reactor")
    v1 = sim.AddObject(ObjectType.Valve, 250, 75, "valve")
    h1 = sim.AddObject(ObjectType.Heater, 375, 75, "cooler")
    s1 = sim.AddObject(ObjectType.Vessel, 500, 75, "separator")
    
    # get flowsheet objects as object
    m1 = m1.GetAsObject()
    m2 = m2.GetAsObject()
    m3 = m3.GetAsObject()
    m4 = m4.GetAsObject()
    m5 = m5.GetAsObject()
    m6 = m6.GetAsObject()
    e1 = e1.GetAsObject()
    e2 = e2.GetAsObject()
    
    r1 = r1.GetAsObject()
    v1 = v1.GetAsObject()
    h1 = h1.GetAsObject()
    s1 = s1.GetAsObject()
    
    # connect Objects
    r1.dV = 0.01
    r1.ConnectFeedMaterialStream(m1,0)
    r1.ConnectProductMaterialStream(m2,0)
    r1.ConnectFeedEnergyStream(e1,1)
    sim.ConnectObjects(m2.GraphicObject, v1.GraphicObject, -1, -1) # outlet -> valve
    sim.ConnectObjects(v1.GraphicObject, m3.GraphicObject, -1, -1) # valve -> expanded
    sim.ConnectObjects(m3.GraphicObject, h1.GraphicObject, -1, -1) # expanded -> heater
    sim.ConnectObjects(e2.GraphicObject, h1.GraphicObject, -1, -1) # E2 -> heater
    sim.ConnectObjects(h1.GraphicObject, m4.GraphicObject, -1, -1) # heater -> cooled
    sim.ConnectObjects(m4.GraphicObject, s1.GraphicObject, -1, -1) # cooled -> separator
    sim.ConnectObjects(s1.GraphicObject, m5.GraphicObject, -1, -1) # separator -> sep_gas
    sim.ConnectObjects(s1.GraphicObject, m6.GraphicObject, -1, -1) # separator -> sep_liquid
    
    # add property package
    sim.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
    #sim.CreateAndAddPropertyPackage("Soave-Redlich-Kwong (SRK)")
    
    # specify material parameter
    print("Set mole fractions...")

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
    
    m1.SetTemperature(temperature_outlet)
    m1.SetPressure(pressure)
    #velocity = float(veloc)
    # specify reactor parameter; doesnt make a difference if diameter or length is choosen
    for i in range(len(data)):
        if "Reactor" in data[i]:
            radius = float(data[i]["Reactor"][0]["tube_diameter"])/2
            r1.Volume = data[i]["Reactor"][0]["reactive_volume"]
            V_reac = data[i]["Reactor"][0]["reactive_volume"]
            r1.Length = float(data[i]["Reactor"][0]["tube_length"])
            r1.NumberOfTubes = data[i]["Reactor"][0]["num_tubes"]
            
            if data[i]["Reactor"][0]["calculation_mode"] == "isothermal":
                r1.ReactorOperationMode = Reactors.OperationMode.Isothermic
            elif data[i]["Reactor"][0]["calculation_mode"] == "adiabatic":
                r1.ReactorOperationMode = Reactors.OperationMode.Adiabatic
            else:
                print("Error accured while setting the ReactorOperationMode!")
            """
            r1.ReactorOperationMode = Reactors.OperationMode.OutletTemperature
            r1.OutletTemperature = temperature_outlet
            """  
            # specify catalyst parameter
            r1.CatalystLoading = data[i]['Reactor'][0]["catalyst_loading"]
            r1.CatalystVoidFraction = data[i]['Reactor'][0]["catalyst_void_fraction"]
            r1.CatalystParticleDiameter = data[i]['Reactor'][0]["catalyst_particle_diameter"]
            
    V_flow = V_reac / res_t
    m1.SetVolumetricFlow(V_flow)    
    r1.UseUserDefinedPressureDrop = True

    # specifiy other devices (valve, cooler, separator)
    v1.CalcMode = UnitOperations.Valve.CalculationMode.OutletPressure
    v1.set_OutletPressure(100000) # Pa: 1 bar [NormPressure]
    
    h1.CalcMode  = UnitOperations.Heater.CalculationMode.OutletTemperature
    h1.OutletTemperature = 293.15 # K: 25°C [NormTemperature]
    
    # create reaction
    print("Create reactions and kinetic scripts...")
    createReaction(data, substances)
    print("Done!")

    # set Solver Mode
    Settings.SolveMode = 0
    errors = interf.CalculateFlowsheet2(sim)
    
    ##SAVE RESULTS
    # get moleflows for evaluation
    mol_flow_in = m1.GetMolarFlow()
    mol_flow_in_comp = []
    
    for i in range(len(substances)):
        temp_1 = m1.GetCompoundMolarFlow(substances[i][1])
        mol_flow_in_comp.append([substances[i][0], temp_1])
  
    mol_flow_out = m2.GetMolarFlow()
    mol_flow_out_comp = []
    
    for i in range(len(substances)):
        temp_2 = m2.GetCompoundMolarFlow(substances[i][1])
        mol_flow_out_comp.append([substances[i][0], temp_2])
        
    data.append({"Inlet": [{"MolarFlow_In": mol_flow_in, "Comp_MolarFlow_In": mol_flow_in_comp}]})       
    data.append({"Outlet": [{"MolarFlow_Out": mol_flow_out, "Comp_MolarFlow_Out": mol_flow_out_comp}]})
    
    # getting outlet composition of sep_gas
    outlet_gas = list(m5.GetOverallComposition())
    outlet_gas_composition = []
    for i in range(len(substances)):
        outlet_gas_composition.append([substances[i][0], outlet_gas[i]])
    data.append({"Sep_Gas Composition": outlet_gas_composition})
    
    outlet_liq = list(m6.GetOverallComposition())
    outlet_liq_composition = []
    for i in range(len(substances)):
        outlet_liq_composition.append([substances[i][0], outlet_liq[i]])
    data.append({"Sep_Liquid Composition": outlet_liq_composition})
    
    # yaml-file
    coordinates = []
    for p in r1.points:
        coordinates.append(p[0])

    values = []
    for i in range(1, r1.ComponentConversions.Count + 3):
        list1=[]
        for p in r1.points:
            list1.append(p[i])
        values.append(list1)

    names = []
    for k in r1.ComponentConversions.Keys:
        names.append(k)
    names.append("Temperature")
    names.append("Pressure")
    
    data.append({"Coordinates": coordinates})
    for names_, values in zip(names, values):
        data.append({names_: values})    
    
    data.append({"hasDownstream": "Yes"})

    yaml_name = path + name_sim + ".yaml"
    with open(yaml_name, 'w') as new_yaml_file:
        yaml.dump(data, new_yaml_file, default_flow_style=False)
        
    # dwxmz-file
    fileName_dwsim = name_sim + ".dwxmz"
    fileNameToSave = Path.Combine(path, fileName_dwsim)
    
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
    fileName_pic = name_sim + ".png"
    
    bmp = SKBitmap(1024, 768)
    canvas = SKCanvas(bmp)
    canvas.Scale(1.0)
    PFDSurface.UpdateCanvas(canvas)
    d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
    stri = MemoryStream()
    d.SaveTo(stri)
    image = Image.FromStream(stri)
    imgPath = Path.Combine(path, fileName_pic)
    #image.Save(imgPath, ImageFormat.Png)
    stri.Dispose()
    canvas.Dispose()
    bmp.Dispose()
    #from PIL import Image
    #im = Image.open(imgPath)
    #im.show()
    

def run():  
    name_sim = sys.argv[1]
    temperature = sys.argv[2]
    pressure = sys.argv[3]
    res_t = sys.argv[4]
    path = sys.argv[5]
    data_path = sys.argv[6]
    combination = (float(temperature), float(pressure), float(res_t))
        
    with open(data_path, "r") as file:
        data = yaml.safe_load(file)
        
    simulation(name_sim, path, data, combination)
run()