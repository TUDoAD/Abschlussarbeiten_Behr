# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 09:30:56 2023

@author: smmcvoel
"""

import sys
import json
import Query
import qdarktheme
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from pyDataverse.models import Dataset, Datafile
from pyDataverse.api import NativeApi, DataAccessApi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("querys.ui", self)
        
        with open("parameter.json") as json_file:
            self.para = json.load(json_file)
            
        self.list_temp = self.para["temperature"] # K
        self.list_pres = self.para["pressure"] # Pa
        self.list_velo = self.para["res_t"] # s
        
        # call query 1
        self.Q1button = self.findChild(QtWidgets.QPushButton, "Q1Button")
        self.Q1button.clicked.connect(self.run_Q1)
        
        # call query 2
        self.Q2button = self.findChild(QtWidgets.QPushButton, "Q2Button")
        self.Q2button.clicked.connect(self.run_Q2)
        
        # call dataverse API an set parameter
        self.Q3xml_file = self.findChild(QtWidgets.QComboBox, "Q3comboBox1")
        
        base_url = "https://repo4cat.hlrs.de/"
        api_token = "1e98ec1a-ddf0-4fbd-8348-d5ab86524e70"
        dataverse_alias = "tu-do-ad"
        api = NativeApi(base_url, api_token)
        data_api = DataAccessApi(base_url, api_token)
        DOI = "hdl:21.T11978/repo4cat-proto-1030&version=DRAFT"
        dataset = api.get_dataset(DOI)
        file_list = dataset.json()["data"]["latestVersion"]["files"]
        for file in file_list:
            file_name = file["label"]
            if ".xlsx" in file_name:
                self.Q3xml_file.addItem(file_name)

        self.Q3xml_file.currentIndexChanged.connect(self.update_labels)
        # call query 3
        self.Q3button = self.findChild(QtWidgets.QPushButton, "Q3Button")
        self.Q3button.clicked.connect(self.run_Q3)
        
        self.show()

    
    def run_Q1(self):
        print("Query 1 started...")
        # get parameter from GUI and call query
        self.Q1_T_input = self.findChild(QtWidgets.QLineEdit, "Q1Temp")
        self.Q1_P_input = self.findChild(QtWidgets.QLineEdit, "Q1Pres")
        self.Q1_V_input = self.findChild(QtWidgets.QLineEdit, "Q1Velo")
        self.Q1_MoleFrac = self.findChild(QtWidgets.QComboBox, "Q1comboBox1")
        self.Q1_Downstream = self.findChild(QtWidgets.QComboBox, "Q1comboBox2")
        
        self.Q1_temp_1 = self.Q1_T_input.text()
        self.Q1_pres_1 = self.Q1_P_input.text()
        self.Q1_velo_1 = self.Q1_V_input.text()
        
        if self.Q1_MoleFrac.currentText() == "0.04":
            mole_1 = 0.04
        elif self.Q1_MoleFrac.currentText() == "0.20":
            mole_1 = 0.2
        elif self.Q1_MoleFrac.currentText() == "0.50":
            mole_1 = 0.5
        else:
            mole_1 = None
            
        if self.Q1_Downstream.currentText() == "With Downstream":
            down_1 = "'Yes'"
        elif self.Q1_Downstream.currentText() == "Without Downstream":
            down_1 = "'No'"
        else:
            down_1 = None
            
        self.Q1_results = Query.query_3(molefrac_co2=mole_1, temperature=self.Q1_temp_1, pressure=self.Q1_pres_1,
                                        velocity=self.Q1_velo_1, downstream=down_1)
        print("Results are stored in GUI_Q1_results.xlsx")
        
        # display results in GUI
        self.Q1_list = self.findChild(QtWidgets.QListWidget, "Q1List")
        self.Q1_list.clear()
        
        # disconnet previous connections, necessary if query is called more than one time per session
        try:
            self.Q1_list.itemClicked.disconnect(self.openUrl)
        except: TypeError
        
        for i in range(len(self.Q1_results)):
            individual_1 = QtWidgets.QListWidgetItem(str(self.Q1_results[i][0]).split("inferred.")[1], self.Q1_list)
            simulation_1 = QtWidgets.QListWidgetItem((" - Simulation-File: " + str(self.Q1_results[i][1])), self.Q1_list)
            data_1 =QtWidgets.QListWidgetItem((" - Data-File: "+ str(self.Q1_results[i][2])), self.Q1_list)
            
            self.Q1_list.addItem(individual_1)
            self.Q1_list.addItem(simulation_1)
            self.Q1_list.addItem(data_1)
                
        self.Q1_list.itemClicked.connect(self.openUrl)


    def run_Q2(self):
        print("Query 2 started...")
        # get parameter from GUI and call query
        self.Q2_T_input_1 = self.findChild(QtWidgets.QLineEdit, "Q2Temp1")
        self.Q2_T_input_2 = self.findChild(QtWidgets.QLineEdit, "Q2Temp2")
        self.Q2_P_input_1 = self.findChild(QtWidgets.QLineEdit, "Q2Pres1")
        self.Q2_P_input_2 = self.findChild(QtWidgets.QLineEdit, "Q2Pres2")
        self.Q2_V_input_1 = self.findChild(QtWidgets.QLineEdit, "Q2Velo1")
        self.Q2_V_input_2 = self.findChild(QtWidgets.QLineEdit, "Q2Velo2")
        self.Q2_MoleFrac = self.findChild(QtWidgets.QComboBox, "Q2comboBox1")
        self.Q2_Downstream = self.findChild(QtWidgets.QComboBox, "Q2comboBox2")
        
        self.Q2_temp_1 = self.Q2_T_input_1.text()
        self.Q2_temp_2 = self.Q2_T_input_2.text()
        self.Q2_pres_1 = float(self.Q2_P_input_1.text())
        self.Q2_pres_2 = self.Q2_P_input_2.text()
        self.Q2_velo_1 = self.Q2_V_input_1.text()
        self.Q2_velo_2 = self.Q2_V_input_2.text()
        
        if self.Q2_MoleFrac.currentText() == "0.04":
            mole_1 = 0.04
        elif self.Q2_MoleFrac.currentText() == "0.20":
            mole_1 = 0.2
        elif self.Q2_MoleFrac.currentText() == "0.50":
            mole_1 = 0.5
        else:
            print("Some error occured while setting mole fraction...")
        
        if self.Q2_Downstream.currentText() == "With Downstream":
            down_1 = "'Yes'"
        elif self.Q2_Downstream.currentText() == "Without Downstream":
            down_1 = "'No'"
        else:
            print("Some error occured while setting the downstream option...")
            
        self.Q2_results = Query.query_5(molefrac_co2=mole_1, temperature=[self.Q2_temp_1, self.Q2_temp_2],
                                pressure=[self.Q2_pres_1, self.Q2_pres_2], velocity=[self.Q2_velo_1, self.Q2_velo_2],
                                downstream=down_1, result_name="GUI_Q2_results")
        
        self.createQ2Plots()
        
           
    def run_Q3(self):
        print("Query 3 started...")
        # getting parameter for query
        # parameter set in def_update_labels
        # T: self.Q3_xml_temperature
        # P: self.Q3_xml_pressure
        # V: self.Q3_xml_velocity
        # X: self.Q3_xml_molefrac # Molefraction of CO2
        self.Q3_Downstream = self.findChild(QtWidgets.QComboBox, "Q3comboBox2")
        
        if self.Q3_Downstream.currentText() == "With Downstream":
            down_3 = "'Yes'"
        elif self.Q3_Downstream.currentText() == "Without Downstream":
            down_3 = "'No'"
        else:
            print("Some error occured while setting the downstream option...")
        
        self.Q3_results = Query.query_5(molefrac_co2=float(self.Q3_xml_molefrac), temperature=[self.list_temp[0], self.list_temp[-1]],
                                        pressure=[self.list_pres[0], self.list_pres[-1]], velocity=[self.list_velo[0], self.list_velo[-1]],
                                        downstream=down_3, result_name="GUI_Q3_results")
        
        self.createQ3Plots()
        
        
    def update_labels(self):
        self.Q3xml_file_text = self.Q3xml_file.currentText()
        
        base_url = "https://repo4cat.hlrs.de/"
        api_token = "1e98ec1a-ddf0-4fbd-8348-d5ab86524e70"
        dataverse_alias = "tu-do-ad"
        api = NativeApi(base_url, api_token)
        data_api = DataAccessApi(base_url, api_token)
        DOI = "hdl:21.T11978/repo4cat-proto-1030&version=DRAFT"
        dataset = api.get_dataset(DOI)
        
        file_list = dataset.json()["data"]["latestVersion"]["files"]

        for file in file_list:
            file_name = file["label"]
            if file_name  == self.Q3xml_file_text:
                print("xml-file found...")
                file_id = file["dataFile"]["id"]
                
                response = data_api.get_datafile(file_id)
                with open(self.Q3xml_file_text, "wb") as f:
                    f.write(response.content)                    
                excel = pd.read_excel(file_name, sheet_name=[1,2,4])
                self.user_quest = excel[1]
                self.experi = excel[2]
                self.calc = excel[4]
                
        for i in range(len(self.user_quest)):
            if self.user_quest.at[i, "Unnamed: 2"] == "reactor inlet temperature":
                self.Q3_xml_temperature = self.user_quest.at[i, "Unnamed: 4"] # K
            if self.user_quest.at[i, "Unnamed: 2"] == "pressure":
                self.Q3_xml_pressure = self.user_quest.at[i, "Unnamed: 4"] * 100000 # bar -> Pa
            if self.user_quest.at[i, "Unnamed: 2"] ==  "CO2":
                self.Q3_xml_molefrac = self.user_quest.at[i, "Unnamed: 4"]
        
        for i in range(len(self.calc)):
            if self.calc.at[i, "Unnamed: 0"] == "linear velocity":
                self.Q3_xml_velocity = self.calc.at[i, "Unnamed: 1"]
    
        self.window_list = [self.Q3_xml_temperature, self.Q3_xml_pressure, self.Q3_xml_molefrac, self.Q3_xml_velocity]
                
        self.Q3_temp_1 = self.findChild(QtWidgets.QLabel, "Q3Temp")
        self.Q3_pres_1 = self.findChild(QtWidgets.QLabel, "Q3Pres")
        self.Q3_velo_1 = self.findChild(QtWidgets.QLabel, "Q3Velo")

        self.Q3_temp_1.setText(str(self.Q3_xml_temperature))
        self.Q3_pres_1.setText(str(self.Q3_xml_pressure))
        self.Q3_velo_1.setText(str(self.Q3_xml_velocity))
        

    def openUrl(self, item):
        # get url from ListObject
        url = ""
        if " - Simulation-File: " in item.text():
            url = item.text().split(" - Simulation-File: ")[1]
        elif " - Data-File: " in item.text():
            url = item.text().split(" - Data-File: ")[1]
        else:
            print("Item got no url, select simulation- or data-file!")

        try:
            QDesktopServices.openUrl(QUrl(url))
        except: UnboundLocalError
    
    
    def createQ2Plots(self):
        # get minimal values
        temp_1 = []
        for result in self.Q2_results:
            temp_1.append(result[5])
        self.min_velo_1 = min(temp_1)
        
        temp_2 = []
        for result in self.Q2_results:
            temp_2.append(result[4])
        self.min_pres_1 = min(temp_2)
        
        temp_3 = []
        for result in self.Q2_results:
            temp_3.append(result[3])
        self.min_temp_1 = min(temp_3)
        
        # data for plot 1 (x,T; v_const)
        filtered_results_1 = [result for result in self.Q2_results if str(result[5]) == str(float(self.min_velo_1))]
        pressure_groups_1 = {}
        for result in filtered_results_1:
            pressure = result[4]
            if pressure not in pressure_groups_1:
                pressure_groups_1[pressure] = {"temperature": [], "turnover": []}
            pressure_groups_1[pressure]["temperature"].append(result[3])
            pressure_groups_1[pressure]["turnover"].append(result[6])
               
        self.Q2W1 = self.findChild(QtWidgets.QWidget, "Q2widget1")

        # data for plot 2 (x,T; p_const)
        filtered_results_2 = [result for result in self.Q2_results if str(result[4]) == str(float(self.min_pres_1))]
        velo_groups_2 = {}
        for result in filtered_results_2:
            velo = result[5]
            if velo not in velo_groups_2:
                velo_groups_2[velo] = {"temperature": [], "turnover": []}
            velo_groups_2[velo]["temperature"].append(result[3])
            velo_groups_2[velo]["turnover"].append(result[6])
        
        self.Q2W2 = self.findChild(QtWidgets.QWidget, "Q2widget2")
        
        # data for plot 3 (x,p; v_const)
        filtered_results_3 = [result for result in self.Q2_results if str(result[5]) == str(float(self.min_velo_1))]
        temperature_groups_3 = {}
        for result in filtered_results_3:
            temperature = result[3]
            if temperature not in temperature_groups_3:
                temperature_groups_3[temperature] = {"pressure": [], "turnover": []}
            temperature_groups_3[temperature]["pressure"].append(result[4])
            temperature_groups_3[temperature]["pressure"] = sorted(temperature_groups_3[temperature]["pressure"])
            
            index = temperature_groups_3[temperature]["pressure"].index(result[4])
            temperature_groups_3[temperature]["turnover"].insert(index, result[6])
               
        self.Q2W3 = self.findChild(QtWidgets.QWidget, "Q2widget3")
        
        # data for plot 4 (x,p; T_const)
        filtered_results_4 = [result for result in self.Q2_results if str(result[3]) == str(float(self.min_temp_1))]
        velo_groups_4 = {}
        for result in filtered_results_4:
            velo = result[5]
            if velo not in velo_groups_4:
                velo_groups_4[velo] = {"pressure": [], "turnover": []}
            velo_groups_4[velo]["pressure"].append(result[4])
            velo_groups_4[velo]["pressure"] = sorted(velo_groups_4[velo]["pressure"])
            index = velo_groups_4[velo]["pressure"].index(result[4])
            velo_groups_4[velo]["turnover"].insert(index, result[6])

        self.Q2W4 = self.findChild(QtWidgets.QWidget, "Q2widget4")
        
        # data for plot 5 (x,v; p_const)
        filtered_results_5 = [result for result in self.Q2_results if str(result[4]) == str(float(self.min_pres_1))]
        temperature_groups_5 = {}
        for result in filtered_results_5:
            temperature = result[3]
            if temperature not in temperature_groups_5:
                temperature_groups_5[temperature] = {"velocity": [], "turnover": []}
            temperature_groups_5[temperature]["velocity"].append(result[5])
            temperature_groups_5[temperature]["turnover"].append(result[6])
               
        self.Q2W5 = self.findChild(QtWidgets.QWidget, "Q2widget5")
        
        # data for plot 6 (x,v; T_const)
        filtered_results_6 = [result for result in self.Q2_results if str(result[3]) == str(float(self.min_temp_1))]
        pressure_groups_6 = {}
        for result in filtered_results_6:
            pressure = result[4]
            if pressure not in pressure_groups_6:
                pressure_groups_6[pressure] = {"velocity": [], "turnover": []}
            pressure_groups_6[pressure]["velocity"].append(result[5])
            pressure_groups_6[pressure]["velocity"] = sorted(pressure_groups_6[pressure]["velocity"])
            index = pressure_groups_6[pressure]["velocity"].index(result[5])
            pressure_groups_6[pressure]["turnover"].insert(index, result[6])
               
        self.Q2W6 = self.findChild(QtWidgets.QWidget, "Q2widget6")


        # Liste von Plot-Widgets
        plot_widgets = [
            {"result_filter": lambda result: str(result[5]) == str(self.Q2_velo_1), "groups": pressure_groups_1, "widget": self.Q2W1, "identifier": "temperature"},
            {"result_filter": lambda result: str(result[4]) == str(self.Q2_pres_1), "groups": velo_groups_2, "widget": self.Q2W2, "identifier": "temperature"},
            {"result_filter": lambda result: str(result[5]) == str(self.Q2_velo_1), "groups": temperature_groups_3, "widget": self.Q2W3, "identifier": "pressure"},
            {"result_filter": lambda result: str(result[3]) == str(self.Q2_temp_1), "groups": velo_groups_4, "widget": self.Q2W4, "identifier": "pressure"},
            {"result_filter": lambda result: str(result[4]) == str(self.Q2_pres_1), "groups": temperature_groups_5, "widget": self.Q2W5, "identifier": "velocity"},
            {"result_filter": lambda result: str(result[3]) == str(self.Q2_temp_1), "groups": pressure_groups_6, "widget": self.Q2W6, "identifier": "velocity"},
        ]
        
        for plot_info in plot_widgets:
            result_filter = plot_info["result_filter"]
            groups = plot_info["groups"]
            widget = plot_info["widget"]
            identifier = plot_info["identifier"]
        
            if not hasattr(self, f'{widget.objectName()}_figure'):
                figure, ax = plt.subplots()
                canvas = FigureCanvas(figure)
                canvas.setMouseTracking(True)
                canvas.setGeometry(widget.geometry())
                layout = QtWidgets.QVBoxLayout(widget)
                layout.addWidget(canvas)
                
                canvas.mpl_connect('button_press_event', self.canvas_press_event)

                setattr(self, f'{widget.objectName()}_figure', figure)
                setattr(self, f'{widget.objectName()}_ax', ax)
                setattr(self, f'{widget.objectName()}_canvas', canvas)
                setattr(self, f'{widget.objectName()}', canvas)
            else:
                ax = getattr(self, f'{widget.objectName()}_ax')
                ax.clear()
                getattr(self, f'{widget.objectName()}_canvas').draw_idle()
        
            for key, data in groups.items():
                ax.plot(data[identifier], data['turnover'], label=f'{key}')
            
            if identifier == "temperature":
                ax.set_xlabel("T")
            elif identifier == "pressure":
                ax.set_xlabel("p")
            elif identifier == "velocity":
                ax.set_xlabel("u")
            ax.set_ylabel("X")
            ax.grid(True)
            getattr(self, f'{widget.objectName()}_figure').tight_layout()
            getattr(self, f'{widget.objectName()}_canvas').draw()
            
            
    def createQ3Plots(self):
        # get experimental data from df
        for column in self.experi.columns:
            if self.experi[column][1] == "T":
                self.exp_temp = list(self.experi[column][2:])
            if self.experi[column][1] == "CO2":
                self.exp_turnover = list(self.experi[column][2:])
        
        self.experi_list = [self.exp_temp, self.exp_turnover]
        
        # get minimal values
        temp_1 = []
        for result in self.Q3_results:
            temp_1.append(result[5])
        self.min_velo_1 = min(temp_1)
        
        temp_2 = []
        for result in self.Q3_results:
            temp_2.append(result[4])
        self.min_pres_1 = min(temp_2)
        
        temp_3 = []
        for result in self.Q3_results:
            temp_3.append(result[3])
        self.min_temp_1 = min(temp_3)
        
        # data for plot 1 (x,T; v_const)
        filtered_results_1 = [result for result in self.Q3_results if str(result[5]) == str(float(self.min_velo_1))]
        pressure_groups_1 = {}
        for result in filtered_results_1:
            pressure = result[4]
            if pressure not in pressure_groups_1:
                pressure_groups_1[pressure] = {"temperature": [], "turnover": []}
            pressure_groups_1[pressure]["temperature"].append(result[3])
            pressure_groups_1[pressure]["turnover"].append(result[6])
        
        # adding experimental data to plot 1     
        pressure_groups_1[f"Exp. {self.Q3_xml_pressure}"] = {"temperature": [], "turnover": []}
        pressure_groups_1[f"Exp. {self.Q3_xml_pressure}"]["temperature"] = self.exp_temp
        pressure_groups_1[f"Exp. {self.Q3_xml_pressure}"]["turnover"] = self.exp_turnover
     
        self.Q3W1 = self.findChild(QtWidgets.QWidget, "Q3widget1")
        
        # data for plot 2 (x,T; p_const)
        filtered_results_2 = [result for result in self.Q3_results if str(result[4]) == str(float(self.min_pres_1))]
        velo_groups_2 = {}
        for result in filtered_results_2:
            velo = result[5]
            if velo not in velo_groups_2:
                velo_groups_2[velo] = {"temperature": [], "turnover": []}
            velo_groups_2[velo]["temperature"].append(result[3])
            velo_groups_2[velo]["turnover"].append(result[6])
        
        # adding experimental data to plot 2
        velo_groups_2[f"Exp. {self.Q3_xml_velocity}"] = {"temperature": [], "turnover": []}
        velo_groups_2[f"Exp. {self.Q3_xml_velocity}"]["temperature"] = self.exp_temp
        velo_groups_2[f"Exp. {self.Q3_xml_velocity}"]["turnover"] = self.exp_turnover
        
        self.Q3W2 = self.findChild(QtWidgets.QWidget, "Q3widget2")
        
        # data for plot 3 (x,p; v_const)
        filtered_results_3 = [result for result in self.Q3_results if str(result[5]) == str(float(self.min_velo_1))]
        temperature_groups_3 = {}
        for result in filtered_results_3:
            temperature = result[3]
            if temperature not in temperature_groups_3:
                temperature_groups_3[temperature] = {"pressure": [], "turnover": []}
            temperature_groups_3[temperature]["pressure"].append(result[4])
            temperature_groups_3[temperature]["pressure"] = sorted(temperature_groups_3[temperature]["pressure"])
            
            index = temperature_groups_3[temperature]["pressure"].index(result[4])
            temperature_groups_3[temperature]["turnover"].insert(index, result[6])
       
        # adding experimental data to plot 3
        temperature_groups_3[f"Exp. {self.Q3_xml_temperature}"] = {"pressure": [], "turnover": []}
        temperature_groups_3[f"Exp. {self.Q3_xml_temperature}"]["pressure"] = [self.Q3_xml_pressure, self.Q3_xml_pressure*1.2]
        temperature_groups_3[f"Exp. {self.Q3_xml_temperature}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover

        self.Q3W3 = self.findChild(QtWidgets.QWidget, "Q3widget3")
        
        # data for plot 4 (x,p; T_const)
        filtered_results_4 = [result for result in self.Q3_results if str(result[3]) == str(float(self.min_temp_1))]
        velo_groups_4 = {}
        for result in filtered_results_4:
            velo = result[5]
            if velo not in velo_groups_4:
                velo_groups_4[velo] = {"pressure": [], "turnover": []}
            velo_groups_4[velo]["pressure"].append(result[4])
            velo_groups_4[velo]["pressure"] = sorted(velo_groups_4[velo]["pressure"])
            index = velo_groups_4[velo]["pressure"].index(result[4])
            velo_groups_4[velo]["turnover"].insert(index, result[6])

        # adding experimental data to plot 4
        velo_groups_4[f"Exp. {self.Q3_xml_velocity}"] = {"pressure": [], "turnover": []}
        velo_groups_4[f"Exp. {self.Q3_xml_velocity}"]["pressure"] = [self.Q3_xml_pressure, self.Q3_xml_pressure*1.2]
        velo_groups_4[f"Exp. {self.Q3_xml_velocity}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover
        
        self.Q3W4 = self.findChild(QtWidgets.QWidget, "Q3widget4")
        
        # data for plot 5 (x,v; p_const)
        filtered_results_5 = [result for result in self.Q3_results if str(result[4]) == str(float(self.min_pres_1))]
        temperature_groups_5 = {}
        for result in filtered_results_5:
            temperature = result[3]
            if temperature not in temperature_groups_5:
                temperature_groups_5[temperature] = {"velocity": [], "turnover": []}
            temperature_groups_5[temperature]["velocity"].append(result[5])
            temperature_groups_5[temperature]["turnover"].append(result[6])
        
        # adding experimental data to plot 5
        temperature_groups_5[f"Exp. {self.Q3_xml_temperature}"] = {"velocity": [], "turnover": []}
        temperature_groups_5[f"Exp. {self.Q3_xml_temperature}"]["velocity"] = [self.Q3_xml_velocity, self.Q3_xml_velocity*1.01]
        temperature_groups_5[f"Exp. {self.Q3_xml_temperature}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover
        
        self.Q3W5 = self.findChild(QtWidgets.QWidget, "Q3widget5")
        
        # data for plot 6 (x,v; T_const)
        filtered_results_6 = [result for result in self.Q3_results if str(result[3]) == str(float(self.min_temp_1))]
        pressure_groups_6 = {}
        for result in filtered_results_6:
            pressure = result[4]
            if pressure not in pressure_groups_6:
                pressure_groups_6[pressure] = {"velocity": [], "turnover": []}
            pressure_groups_6[pressure]["velocity"].append(result[5])
            pressure_groups_6[pressure]["velocity"] = sorted(pressure_groups_6[pressure]["velocity"])
            index = pressure_groups_6[pressure]["velocity"].index(result[5])
            pressure_groups_6[pressure]["turnover"].insert(index, result[6])
        
        # adding experimental data to plot 6
        pressure_groups_6[f"Exp. {self.Q3_xml_pressure}"] = {"velocity": [], "turnover": []}
        pressure_groups_6[f"Exp. {self.Q3_xml_pressure}"]["velocity"] = [self.Q3_xml_velocity, self.Q3_xml_velocity*1.01]
        pressure_groups_6[f"Exp. {self.Q3_xml_pressure}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover
               
        self.Q3W6 = self.findChild(QtWidgets.QWidget, "Q3widget6")
        
        # Liste von Plot-Widgets
        plot_widgets = [
            {"result_filter": lambda result: str(result[5]) == str(self.Q3_velo_1), "groups": pressure_groups_1, "widget": self.Q3W1, "identifier": "temperature"},
            {"result_filter": lambda result: str(result[4]) == str(self.Q3_pres_1), "groups": velo_groups_2, "widget": self.Q3W2, "identifier": "temperature"},
            {"result_filter": lambda result: str(result[5]) == str(self.Q3_velo_1), "groups": temperature_groups_3, "widget": self.Q3W3, "identifier": "pressure"},
            {"result_filter": lambda result: str(result[3]) == str(self.Q3_temp_1), "groups": velo_groups_4, "widget": self.Q3W4, "identifier": "pressure"},
            {"result_filter": lambda result: str(result[4]) == str(self.Q3_pres_1), "groups": temperature_groups_5, "widget": self.Q3W5, "identifier": "velocity"},
            {"result_filter": lambda result: str(result[3]) == str(self.Q3_temp_1), "groups": pressure_groups_6, "widget": self.Q3W6, "identifier": "velocity"},
        ]
        
        for plot_info in plot_widgets:
            result_filter = plot_info["result_filter"]
            groups = plot_info["groups"]
            widget = plot_info["widget"]
            identifier = plot_info["identifier"]
        
            if not hasattr(self, f'{widget.objectName()}_figure'):
                figure, ax = plt.subplots()
                canvas = FigureCanvas(figure)
                canvas.setMouseTracking(True)
                canvas.setGeometry(widget.geometry())
                layout = QtWidgets.QVBoxLayout(widget)
                layout.addWidget(canvas)
                
                canvas.mpl_connect('button_press_event', self.canvas_press_event)

                setattr(self, f'{widget.objectName()}_figure', figure)
                setattr(self, f'{widget.objectName()}_ax', ax)
                setattr(self, f'{widget.objectName()}_canvas', canvas)
                setattr(self, f'{widget.objectName()}', canvas)
            else:
                ax = getattr(self, f'{widget.objectName()}_ax')
                ax.clear()
                getattr(self, f'{widget.objectName()}_canvas').draw_idle()
        
            for key, data in groups.items():
                ax.plot(data[identifier], data['turnover'], label=f'{key}')
            
            if identifier == "temperature":
                ax.set_xlabel("T")
            elif identifier == "pressure":
                ax.set_xlabel("p")
            elif identifier == "velocity":
                ax.set_xlabel("u")
            ax.set_ylabel("X")
            ax.grid(True)
            getattr(self, f'{widget.objectName()}_figure').tight_layout()
            getattr(self, f'{widget.objectName()}_canvas').draw()
            
    
                
            
    def canvas_press_event(self, event):
        #canvas_name = event.inaxes.figure.canvas.get_name()
        canvas_widget = event.inaxes.figure.canvas

        if canvas_widget == self.Q2widget1:
            self.Q2_1_canvas_clicked(event)
        elif canvas_widget == self.Q2widget2:
            self.Q2_2_canvas_clicked(event)
        elif canvas_widget == self.Q2widget3:
            self.Q2_3_canvas_clicked(event)
        elif canvas_widget == self.Q2widget4:
            self.Q2_4_canvas_clicked(event)
        elif canvas_widget == self.Q2widget5:
            self.Q2_5_canvas_clicked(event)
        elif canvas_widget == self.Q2widget6:
            self.Q2_6_canvas_clicked(event)
        elif canvas_widget == self.Q3widget1:
            self.Q3_1_canvas_clicked(event)
        elif canvas_widget == self.Q3widget2:
            self.Q3_2_canvas_clicked(event)
        elif canvas_widget == self.Q3widget3:
            self.Q3_3_canvas_clicked(event)
        elif canvas_widget == self.Q3widget4:
            self.Q3_4_canvas_clicked(event)
        elif canvas_widget == self.Q3widget5:
            self.Q3_5_canvas_clicked(event)
        elif canvas_widget == self.Q3widget6:
            self.Q3_6_canvas_clicked(event)
        
    
    def Q2_1_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_1 = NewWindow_Q2_1(self.Q2_results, self.Q2_velo_1)
        self.new_window_1.show()
        

    def Q2_2_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_2 = NewWindow_Q2_2(self.Q2_results, self.Q2_pres_1)
        self.new_window_2.show()
        
        
    def Q2_3_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_3 = NewWindow_Q2_3(self.Q2_results, self.Q2_velo_1)
        self.new_window_3.show()
    
    
    def Q2_4_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_4 = NewWindow_Q2_4(self.Q2_results, self.Q2_temp_1)
        self.new_window_4.show()
    
    
    def Q2_5_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_5 = NewWindow_Q2_5(self.Q2_results, self.Q2_pres_1)
        self.new_window_5.show()
    
    
    def Q2_6_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_6 = NewWindow_Q2_6(self.Q2_results, self.Q2_temp_1)
        self.new_window_6.show()
        
        
    def Q3_1_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_7 = NewWindow_Q3_1(self.Q3_results, self.Q3_velo_1, self.window_list, self.experi_list)
        self.new_window_7.show()
        

    def Q3_2_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_8 = NewWindow_Q3_2(self.Q3_results, self.Q3_pres_1, self.window_list, self.experi_list)
        self.new_window_8.show()
        
        
    def Q3_3_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_9 = NewWindow_Q3_3(self.Q3_results, self.Q3_velo_1, self.window_list, self.experi_list)
        self.new_window_9.show()
    
    
    def Q3_4_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_10 = NewWindow_Q3_4(self.Q3_results, self.Q3_temp_1, self.window_list, self.experi_list)
        self.new_window_10.show()
    
    
    def Q3_5_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_11 = NewWindow_Q3_5(self.Q3_results, self.Q3_pres_1, self.window_list, self.experi_list)
        self.new_window_11.show()
    
    
    def Q3_6_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_12 = NewWindow_Q3_6(self.Q3_results, self.Q3_temp_1, self.window_list, self.experi_list)
        self.new_window_12.show()
        

class NewWindow_Q2_1(QtWidgets.QMainWindow):
    def __init__(self, results, Q2_velo_1):
        super(NewWindow_Q2_1, self).__init__()
        
        self.results = results
        self.Q2_velo_1 = Q2_velo_1
        
        self.setWindowTitle("Q2_P1")
        self.create_plot()
        
        
    def create_plot(self):
        temp_1 = []
        for result in self.results:
            temp_1.append(result[5])
        self.min_velo_1 = min(temp_1)
        
        filtered_results_1 = [result for result in self.results if str(result[5]) == str(float(self.min_velo_1))]
        pressure_groups_1 = {}
        for result in filtered_results_1:
            pressure = result[4]
            if pressure not in pressure_groups_1:
                pressure_groups_1[pressure] = {"temperature": [], "turnover": []}
            pressure_groups_1[pressure]["temperature"].append(result[3])
            pressure_groups_1[pressure]["turnover"].append(result[6])
        import matplotlib.pyplot as plt    
        self.Q2_Figure_1, self.Q2_P1_ax = plt.subplots()
        self.canvas_Q2_P1 = FigureCanvas(self.Q2_Figure_1)
        self.setCentralWidget(self.canvas_Q2_P1)
        
        for pressure, data in pressure_groups_1.items():
            plt.plot(data['temperature'], data['turnover'], label=f'Pressure: {pressure} Pa')
        
        self.Q2_P1_ax.set_xlabel('T [K]')
        self.Q2_P1_ax.set_ylabel('X_CO2 [-]')
        self.Q2_P1_ax.set_title("X_CO2 over T with constant velocity")
        self.Q2_Figure_1.tight_layout()
        self.Q2_P1_ax.grid(True)
        self.Q2_P1_ax.legend()
        self.canvas_Q2_P1.draw()
        

class NewWindow_Q2_2(QtWidgets.QMainWindow):
    def __init__(self, results, Q2_pres_1):
        super(NewWindow_Q2_2, self).__init__()
        
        self.results = results
        self.Q2_pres_1 = Q2_pres_1
        
        self.setWindowTitle("Q2_P2")
        self.create_plot()
        
        
    def create_plot(self):
        temp_2 = []
        for result in self.results:
            temp_2.append(result[4])
        self.min_pres_1 = min(temp_2)
        
        filtered_results_2 = [result for result in self.results if str(result[4]) == str(float(self.min_pres_1))]
        velo_groups_1 = {}
        for result in filtered_results_2:
            velo = result[5]
            if velo not in velo_groups_1:
                velo_groups_1[velo] = {"temperature": [], "turnover": []}
            velo_groups_1[velo]["temperature"].append(result[3])
            velo_groups_1[velo]["turnover"].append(result[6])
        import matplotlib.pyplot as plt    
        self.Q2_Figure_2, self.Q2_P2_ax = plt.subplots()
        self.canvas_Q2_P2 = FigureCanvas(self.Q2_Figure_2)
        self.setCentralWidget(self.canvas_Q2_P2)
        
        for velo, data in velo_groups_1.items():
            plt.plot(data['temperature'], data['turnover'], label=f'Velocity: {velo} m/s')
        
        self.Q2_P2_ax.set_xlabel('T [K]')
        self.Q2_P2_ax.set_ylabel('X_CO2 [-]')
        self.Q2_P2_ax.set_title("X_CO2 over T with constant pressure")
        self.Q2_Figure_2.tight_layout()
        self.Q2_P2_ax.grid(True)
        self.Q2_P2_ax.legend()
        self.canvas_Q2_P2.draw()
        
        
class NewWindow_Q2_3(QtWidgets.QMainWindow):
    def __init__(self, results, Q2_velo_1):
        super(NewWindow_Q2_3, self).__init__()
        
        self.results = results
        self.Q2_velo_1 = Q2_velo_1
        
        self.setWindowTitle("Q2_P3")
        self.create_plot()
        
        
    def create_plot(self):
        temp_3 = []
        for result in self.results:
            temp_3.append(result[5])
        self.min_velo_1 = min(temp_3)
        
        filtered_results_3 = [result for result in self.results if str(result[5]) == str(float(self.min_velo_1))]
        temperature_groups_3 = {}
        for result in filtered_results_3:
            temperature = result[3]
            if temperature not in temperature_groups_3:
                temperature_groups_3[temperature] = {"pressure": [], "turnover": []}
            temperature_groups_3[temperature]["pressure"].append(result[4])
            temperature_groups_3[temperature]["pressure"] = sorted(temperature_groups_3[temperature]["pressure"])
            
            index = temperature_groups_3[temperature]["pressure"].index(result[4])
            temperature_groups_3[temperature]["turnover"].insert(index, result[6])
        import matplotlib.pyplot as plt    
        self.Q2_Figure_3, self.Q2_P3_ax = plt.subplots()
        self.canvas_Q2_P3 = FigureCanvas(self.Q2_Figure_3)
        self.setCentralWidget(self.canvas_Q2_P3)
        
        for temp, data in temperature_groups_3.items():
            plt.plot(data['pressure'], data['turnover'], label=f'Temperature: {temp} K')
        
        self.Q2_P3_ax.set_xlabel('p [Pa]')
        self.Q2_P3_ax.set_ylabel('X_CO2 [-]')
        self.Q2_P3_ax.set_title("X_CO2 over p with constant Temperature")
        self.Q2_Figure_3.tight_layout()
        self.Q2_P3_ax.grid(True)
        self.Q2_P3_ax.legend()
        self.canvas_Q2_P3.draw()
        

class NewWindow_Q2_4(QtWidgets.QMainWindow):
    def __init__(self, results, Q2_temp_1):
        super(NewWindow_Q2_4, self).__init__()
        
        self.results = results
        self.Q2_temp_1 = Q2_temp_1
        
        self.setWindowTitle("Q2_P4")
        self.create_plot()
        
        
    def create_plot(self):
        temp_4 = []
        for result in self.results:
            temp_4.append(result[3])
        self.min_temp_1 = min(temp_4)
        
        filtered_results_4 = [result for result in self.results if str(result[3]) == str(float(self.min_temp_1))]
        velo_groups_4 = {}
        for result in filtered_results_4:
            velo = result[5]
            if velo not in velo_groups_4:
                velo_groups_4[velo] = {"pressure": [], "turnover": []}
            velo_groups_4[velo]["pressure"].append(result[4])
            velo_groups_4[velo]["pressure"] = sorted(velo_groups_4[velo]["pressure"])
            index = velo_groups_4[velo]["pressure"].index(result[4])
            velo_groups_4[velo]["turnover"].insert(index, result[6])
        import matplotlib.pyplot as plt    
        self.Q2_Figure_4, self.Q2_P4_ax = plt.subplots()
        self.canvas_Q2_P4 = FigureCanvas(self.Q2_Figure_4)
        self.setCentralWidget(self.canvas_Q2_P4)
        
        for velo, data in velo_groups_4.items():
            plt.plot(data['pressure'], data['turnover'], label=f'Velocity: {velo} ms')
        
        self.Q2_P4_ax.set_xlabel('p [Pa]')
        self.Q2_P4_ax.set_ylabel('X_CO2 [-]')
        self.Q2_P4_ax.set_title("X_CO2 over p with constant temperature")
        self.Q2_Figure_4.tight_layout()
        self.Q2_P4_ax.grid(True)
        self.Q2_P4_ax.legend()
        self.canvas_Q2_P4.draw()
        
        
class NewWindow_Q2_5(QtWidgets.QMainWindow):
    def __init__(self, results, Q2_pres_1):
        super(NewWindow_Q2_5, self).__init__()
        
        self.results = results
        self.Q2_pres_1 = Q2_pres_1
        
        self.setWindowTitle("Q2_P5")
        self.create_plot()
        
        
    def create_plot(self):
        temp_5 = []
        for result in self.results:
            temp_5.append(result[4])
        self.min_pres_1 = min(temp_5)
        
        filtered_results_5 = [result for result in self.results if str(result[4]) == str(float(self.min_pres_1))]
        temperature_groups_5 = {}
        for result in filtered_results_5:
            temperature = result[3]
            if temperature not in temperature_groups_5:
                temperature_groups_5[temperature] = {"velocity": [], "turnover": []}
            temperature_groups_5[temperature]["velocity"].append(result[5])
            temperature_groups_5[temperature]["turnover"].append(result[6])
        import matplotlib.pyplot as plt    
        self.Q2_Figure_5, self.Q2_P5_ax = plt.subplots()
        self.canvas_Q2_P5 = FigureCanvas(self.Q2_Figure_5)
        self.setCentralWidget(self.canvas_Q2_P5)
        
        for temp, data in temperature_groups_5.items():
            plt.plot(data['velocity'], data['turnover'], label=f'Temperature: {temp} K')
        
        self.Q2_P5_ax.set_xlabel('v [ms]')
        self.Q2_P5_ax.set_ylabel('X_CO2 [-]')
        self.Q2_P5_ax.set_title("X_CO2 over v with constant pressure")
        self.Q2_Figure_5.tight_layout()
        self.Q2_P5_ax.grid(True)
        self.Q2_P5_ax.legend()
        self.canvas_Q2_P5.draw()
        
        
class NewWindow_Q2_6(QtWidgets.QMainWindow):
    def __init__(self, results, Q2_temp_1):
        super(NewWindow_Q2_6, self).__init__()
        
        self.results = results
        self.Q2_temp_1 = Q2_temp_1
        
        self.setWindowTitle("Q2_P6")
        self.create_plot()
        
        
    def create_plot(self):
        temp_6 = []
        for result in self.results:
            temp_6.append(result[3])
        self.min_temp_1 = min(temp_6)
        
        filtered_results_6 = [result for result in self.results if str(result[3]) == str(float(self.min_temp_1))]
        pressure_groups_6 = {}
        for result in filtered_results_6:
            pressure = result[4]
            if pressure not in pressure_groups_6:
                pressure_groups_6[pressure] = {"velocity": [], "turnover": []}
            pressure_groups_6[pressure]["velocity"].append(result[5])
            pressure_groups_6[pressure]["velocity"] = sorted(pressure_groups_6[pressure]["velocity"])
            index = pressure_groups_6[pressure]["velocity"].index(result[5])
            pressure_groups_6[pressure]["turnover"].insert(index, result[6])
        import matplotlib.pyplot as plt    
        self.Q2_Figure_6, self.Q2_P6_ax = plt.subplots()
        self.canvas_Q2_P6 = FigureCanvas(self.Q2_Figure_6)
        self.setCentralWidget(self.canvas_Q2_P6)
        
        for pres, data in pressure_groups_6.items():
            plt.plot(data['velocity'], data['turnover'], label=f'Pressure: {pres} Pa')
        
        self.Q2_P6_ax.set_xlabel('v [ms]')
        self.Q2_P6_ax.set_ylabel('X_CO2 [-]')
        self.Q2_P6_ax.set_title("X_CO2 over v with constant temperature")
        self.Q2_Figure_6.tight_layout()
        self.Q2_P6_ax.grid(True)
        self.Q2_P6_ax.legend()
        self.canvas_Q2_P6.draw()
        
        
class NewWindow_Q3_1(QtWidgets.QMainWindow):
    def __init__(self, results, Q3_velo_1, window_list, experi_list):
        super(NewWindow_Q3_1, self).__init__()
        
        self.results = results
        self.Q3_velo_1 = Q3_velo_1
        
        self.Q3_xml_temperature, self.Q3_xml_pressure, self.Q3_xml_molefrac, self.Q3_xml_velocity = window_list
        self.exp_temp, self.exp_turnover = experi_list
        
        self.setWindowTitle("Q3_P1")
        self.create_plot()
        
        
    def create_plot(self):
        temp_1 = []
        for result in self.results:
            temp_1.append(result[5])
        self.min_velo_1 = min(temp_1)
        
        filtered_results_1 = [result for result in self.results if str(result[5]) == str(float(self.min_velo_1))]
        pressure_groups_1 = {}
        for result in filtered_results_1:
            pressure = result[4]
            if pressure not in pressure_groups_1:
                pressure_groups_1[pressure] = {"temperature": [], "turnover": []}
            pressure_groups_1[pressure]["temperature"].append(result[3])
            pressure_groups_1[pressure]["turnover"].append(result[6])
        
        # adding experimental data to plot 1     
        pressure_groups_1[f"Exp. {self.Q3_xml_pressure}"] = {"temperature": [], "turnover": []}
        pressure_groups_1[f"Exp. {self.Q3_xml_pressure}"]["temperature"] = self.exp_temp
        pressure_groups_1[f"Exp. {self.Q3_xml_pressure}"]["turnover"] = self.exp_turnover
        import matplotlib.pyplot as plt    
        self.Q3_Figure_1, self.Q3_P1_ax = plt.subplots()
        self.canvas_Q3_P1 = FigureCanvas(self.Q3_Figure_1)
        self.setCentralWidget(self.canvas_Q3_P1)
        
        for pressure, data in pressure_groups_1.items():
            plt.plot(data['temperature'], data['turnover'], label=f'Pressure: {pressure} Pa')
        
        self.Q3_P1_ax.set_xlabel('T [K]')
        self.Q3_P1_ax.set_ylabel('X_CO2 [-]')
        self.Q3_P1_ax.set_title("X_CO2 over T with constant velocity")
        self.Q3_Figure_1.tight_layout()
        self.Q3_P1_ax.grid(True)
        self.Q3_P1_ax.legend()
        self.canvas_Q3_P1.draw()
        

class NewWindow_Q3_2(QtWidgets.QMainWindow):
    def __init__(self, results, Q3_pres_1, window_list, experi_list):
        super(NewWindow_Q3_2, self).__init__()
        
        self.results = results
        self.Q3_pres_1 = Q3_pres_1
        
        self.Q3_xml_temperature, self.Q3_xml_pressure, self.Q3_xml_molefrac, self.Q3_xml_velocity = window_list
        self.exp_temp, self.exp_turnover = experi_list
        
        self.setWindowTitle("Q3_P2")
        self.create_plot()
        
        
    def create_plot(self):
        temp_2 = []
        for result in self.results:
            temp_2.append(result[4])
        self.min_pres_1 = min(temp_2)
        
        filtered_results_2 = [result for result in self.results if str(result[4]) == str(float(self.min_pres_1))]
        velo_groups_2 = {}
        for result in filtered_results_2:
            velo = result[5]
            if velo not in velo_groups_2:
                velo_groups_2[velo] = {"temperature": [], "turnover": []}
            velo_groups_2[velo]["temperature"].append(result[3])
            velo_groups_2[velo]["turnover"].append(result[6])
        
        # adding experimental data to plot 2
        velo_groups_2[f"Exp. {self.Q3_xml_velocity}"] = {"temperature": [], "turnover": []}
        velo_groups_2[f"Exp. {self.Q3_xml_velocity}"]["temperature"] = self.exp_temp
        velo_groups_2[f"Exp. {self.Q3_xml_velocity}"]["turnover"] = self.exp_turnover
        import matplotlib.pyplot as plt    
        self.Q3_Figure_2, self.Q3_P2_ax = plt.subplots()
        self.canvas_Q3_P2 = FigureCanvas(self.Q3_Figure_2)
        self.setCentralWidget(self.canvas_Q3_P2)
        
        for velo, data in velo_groups_2.items():
            plt.plot(data['temperature'], data['turnover'], label=f'Velocity: {velo} m/s')
        
        self.Q3_P2_ax.set_xlabel('T [K]')
        self.Q3_P2_ax.set_ylabel('X_CO2 [-]')
        self.Q3_P2_ax.set_title("X_CO2 over T with constant pressure")
        self.Q3_Figure_2.tight_layout()
        self.Q3_P2_ax.grid(True)
        self.Q3_P2_ax.legend()
        self.canvas_Q3_P2.draw()
        
        
class NewWindow_Q3_3(QtWidgets.QMainWindow):
    def __init__(self, results, Q3_velo_1, window_list, experi_list):
        super(NewWindow_Q3_3, self).__init__()
        
        self.results = results
        self.Q3_velo_1 = Q3_velo_1
        
        self.Q3_xml_temperature, self.Q3_xml_pressure, self.Q3_xml_molefrac, self.Q3_xml_velocity = window_list
        self.exp_temp, self.exp_turnover = experi_list
        
        self.setWindowTitle("Q3_P3")
        self.create_plot()
        
        
    def create_plot(self):
        temp_3 = []
        for result in self.results:
            temp_3.append(result[5])
        self.min_velo_1 = min(temp_3)
        
        # data for plot 3 (x,p; v_const)
        filtered_results_3 = [result for result in self.results if str(result[5]) == str(float(self.min_velo_1))]
        temperature_groups_3 = {}
        for result in filtered_results_3:
            temperature = result[3]
            if temperature not in temperature_groups_3:
                temperature_groups_3[temperature] = {"pressure": [], "turnover": []}
            temperature_groups_3[temperature]["pressure"].append(result[4])
            temperature_groups_3[temperature]["pressure"] = sorted(temperature_groups_3[temperature]["pressure"])
            
            index = temperature_groups_3[temperature]["pressure"].index(result[4])
            temperature_groups_3[temperature]["turnover"].insert(index, result[6])
        
        # adding experimental data to plot 3
        temperature_groups_3[f"Exp. {self.Q3_xml_temperature}"] = {"pressure": [], "turnover": []}
        temperature_groups_3[f"Exp. {self.Q3_xml_temperature}"]["pressure"] = [self.Q3_xml_pressure, self.Q3_xml_pressure * 1.2]
        temperature_groups_3[f"Exp. {self.Q3_xml_temperature}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover
        import matplotlib.pyplot as plt    
        self.Q3_Figure_3, self.Q3_P3_ax = plt.subplots()
        self.canvas_Q3_P3 = FigureCanvas(self.Q3_Figure_3)
        self.setCentralWidget(self.canvas_Q3_P3)
        
        for temp, data in temperature_groups_3.items():
            plt.plot(data['pressure'], data['turnover'], label=f'Temperature: {temp} K')
        
        self.Q3_P3_ax.set_xlabel('p [Pa]')
        self.Q3_P3_ax.set_ylabel('X_CO2 [-]')
        self.Q3_P3_ax.set_title("X_CO2 over p with constant Temperature")
        self.Q3_Figure_3.tight_layout()
        self.Q3_P3_ax.grid(True)
        self.Q3_P3_ax.legend()
        self.canvas_Q3_P3.draw()
        

class NewWindow_Q3_4(QtWidgets.QMainWindow):
    def __init__(self, results, Q3_temp_1, window_list, experi_list):
        super(NewWindow_Q3_4, self).__init__()
        
        self.results = results
        self.Q3_temp_1 = Q3_temp_1
        
        self.Q3_xml_temperature, self.Q3_xml_pressure, self.Q3_xml_molefrac, self.Q3_xml_velocity = window_list
        self.exp_temp, self.exp_turnover = experi_list
        
        self.setWindowTitle("Q3_P4")
        self.create_plot()
        
        
    def create_plot(self):
        temp_4 = []
        for result in self.results:
            temp_4.append(result[3])
        self.min_temp_1 = min(temp_4)
        
        # data for plot 4 (x,p; T_const)
        filtered_results_4 = [result for result in self.results if str(result[3]) == str(float(self.min_temp_1))]
        velo_groups_4 = {}
        for result in filtered_results_4:
            velo = result[5]
            if velo not in velo_groups_4:
                velo_groups_4[velo] = {"pressure": [], "turnover": []}
            velo_groups_4[velo]["pressure"].append(result[4])
            velo_groups_4[velo]["pressure"] = sorted(velo_groups_4[velo]["pressure"])
            index = velo_groups_4[velo]["pressure"].index(result[4])
            velo_groups_4[velo]["turnover"].insert(index, result[6])

        # adding experimental data to plot 4
        velo_groups_4[f"Exp. {self.Q3_xml_velocity}"] = {"pressure": [], "turnover": []}
        velo_groups_4[f"Exp. {self.Q3_xml_velocity}"]["pressure"] = [self.Q3_xml_pressure, self.Q3_xml_pressure * 1.2]
        velo_groups_4[f"Exp. {self.Q3_xml_velocity}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover
        import matplotlib.pyplot as plt    
        self.Q3_Figure_4, self.Q3_P4_ax = plt.subplots()
        self.canvas_Q3_P4 = FigureCanvas(self.Q3_Figure_4)
        self.setCentralWidget(self.canvas_Q3_P4)
        
        for velo, data in velo_groups_4.items():
            plt.plot(data['pressure'], data['turnover'], label=f'Velocity: {velo} ms')
        
        self.Q3_P4_ax.set_xlabel('p [Pa]')
        self.Q3_P4_ax.set_ylabel('X_CO2 [-]')
        self.Q3_P4_ax.set_title("X_CO2 over p with constant temperature")
        self.Q3_Figure_4.tight_layout()
        self.Q3_P4_ax.grid(True)
        self.Q3_P4_ax.legend()
        self.canvas_Q3_P4.draw()
        
        
class NewWindow_Q3_5(QtWidgets.QMainWindow):
    def __init__(self, results, Q3_pres_1, window_list, experi_list):
        super(NewWindow_Q3_5, self).__init__()
        
        self.results = results
        self.Q3_pres_1 = Q3_pres_1
        
        self.Q3_xml_temperature, self.Q3_xml_pressure, self.Q3_xml_molefrac, self.Q3_xml_velocity = window_list
        self.exp_temp, self.exp_turnover = experi_list
        
        self.setWindowTitle("Q3_P5")
        self.create_plot()
        
        
    def create_plot(self):
        temp_5 = []
        for result in self.results:
            temp_5.append(result[4])
        self.min_pres_1 = min(temp_5)
        
        # data for plot 5 (x,v; p_const)
        filtered_results_5 = [result for result in self.results if str(result[4]) == str(float(self.min_pres_1))]
        temperature_groups_5 = {}
        for result in filtered_results_5:
            temperature = result[3]
            if temperature not in temperature_groups_5:
                temperature_groups_5[temperature] = {"velocity": [], "turnover": []}
            temperature_groups_5[temperature]["velocity"].append(result[5])
            temperature_groups_5[temperature]["turnover"].append(result[6])
        
        # adding experimental data to plot 5
        temperature_groups_5[f"Exp. {self.Q3_xml_temperature}"] = {"velocity": [], "turnover": []}
        temperature_groups_5[f"Exp. {self.Q3_xml_temperature}"]["velocity"] = [self.Q3_xml_velocity, self.Q3_xml_velocity * 1.01]
        temperature_groups_5[f"Exp. {self.Q3_xml_temperature}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover
        import matplotlib.pyplot as plt    
        self.Q3_Figure_5, self.Q3_P5_ax = plt.subplots()
        self.canvas_Q3_P5 = FigureCanvas(self.Q3_Figure_5)
        self.setCentralWidget(self.canvas_Q3_P5)
        
        for temp, data in temperature_groups_5.items():
            plt.plot(data['velocity'], data['turnover'], label=f'Temperature: {temp} K')
        
        self.Q3_P5_ax.set_xlabel('v [ms]')
        self.Q3_P5_ax.set_ylabel('X_CO2 [-]')
        self.Q3_P5_ax.set_title("X_CO2 over v with constant pressure")
        self.Q3_Figure_5.tight_layout()
        self.Q3_P5_ax.grid(True)
        self.Q3_P5_ax.legend()
        self.canvas_Q3_P5.draw()
        
        
class NewWindow_Q3_6(QtWidgets.QMainWindow):
    def __init__(self, results, Q3_temp_1, window_list, experi_list):
        super(NewWindow_Q3_6, self).__init__()
        
        self.results = results
        self.Q3_temp_1 = Q3_temp_1
        
        self.Q3_xml_temperature, self.Q3_xml_pressure, self.Q3_xml_molefrac, self.Q3_xml_velocity = window_list
        self.exp_temp, self.exp_turnover = experi_list
        
        self.setWindowTitle("Q3_P6")
        self.create_plot()
        
        
    def create_plot(self):
        temp_6 = []
        for result in self.results:
            temp_6.append(result[3])
        self.min_temp_1 = min(temp_6)
        
        # data for plot 6 (x,v; T_const)
        filtered_results_6 = [result for result in self.results if str(result[3]) == str(float(self.min_temp_1))]
        pressure_groups_6 = {}
        for result in filtered_results_6:
            pressure = result[4]
            if pressure not in pressure_groups_6:
                pressure_groups_6[pressure] = {"velocity": [], "turnover": []}
            pressure_groups_6[pressure]["velocity"].append(result[5])
            pressure_groups_6[pressure]["velocity"] = sorted(pressure_groups_6[pressure]["velocity"])
            index = pressure_groups_6[pressure]["velocity"].index(result[5])
            pressure_groups_6[pressure]["turnover"].insert(index, result[6])
        
        # adding experimental data to plot 6
        pressure_groups_6[f"Exp. {self.Q3_xml_pressure}"] = {"velocity": [], "turnover": []}
        pressure_groups_6[f"Exp. {self.Q3_xml_pressure}"]["velocity"] = [self.Q3_xml_velocity, self.Q3_xml_velocity * 1.01]
        pressure_groups_6[f"Exp. {self.Q3_xml_pressure}"]["turnover"] = [sum(self.exp_turnover)/len(self.exp_turnover),sum(self.exp_turnover)/len(self.exp_turnover)] #average turnover
        import matplotlib.pyplot as plt    
        self.Q3_Figure_6, self.Q3_P6_ax = plt.subplots()
        self.canvas_Q3_P6 = FigureCanvas(self.Q3_Figure_6)
        self.setCentralWidget(self.canvas_Q3_P6)
        
        for pres, data in pressure_groups_6.items():
            plt.plot(data['velocity'], data['turnover'], label=f'Pressure: {pres} Pa')
        
        self.Q3_P6_ax.set_xlabel('v [ms]')
        self.Q3_P6_ax.set_ylabel('X_CO2 [-]')
        self.Q3_P6_ax.set_title("X_CO2 over v with constant temperature")
        self.Q3_Figure_6.tight_layout()
        self.Q3_P6_ax.grid(True)
        self.Q3_P6_ax.legend()
        self.canvas_Q3_P6.draw()
        
        
app = QtWidgets.QApplication(sys.argv)
qdarktheme.setup_theme(theme="light", custom_colors={"[light]":{"primary":"#84BC34"}})
window = Ui()
app.exec_()