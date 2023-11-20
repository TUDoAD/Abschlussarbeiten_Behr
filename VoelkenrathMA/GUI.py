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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("querys.ui", self)
        
        with open("parameter.json") as json_file:
            self.para = json.load(json_file)
            
        self.list_temp = self.para["temperature"] # K
        self.list_pres = self.para["pressure"] # Pa
        self.list_velo = self.para["velocity"] # m/s
        
        self.Q1button = self.findChild(QtWidgets.QPushButton, "Q1Button")
        self.Q1button.clicked.connect(self.run_Q1)
        
        self.Q2button = self.findChild(QtWidgets.QPushButton, "Q2Button")
        self.Q2button.clicked.connect(self.run_Q2)
        
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
            
        results = Query.query_3(molefrac_co2=mole_1, temperature=self.Q1_temp_1, pressure=self.Q1_pres_1, velocity=self.Q1_velo_1, downstream=down_1)
        print("Results are stored in GUI_Q1_results.xlsx")
        
        # display results in GUI
        self.Q1_list = self.findChild(QtWidgets.QListWidget, "Q1List")
        self.Q1_list.clear()
        
        # disconnet previous connections, necessary if query is called more than one time per session
        try:
            self.Q1_list.itemClicked.disconnect(self.openUrl)
        except: TypeError
        
        for i in range(len(results)):
            individual_1 = QtWidgets.QListWidgetItem(str(results[i][0]).split("inferred.")[1], self.Q1_list)
            simulation_1 = QtWidgets.QListWidgetItem((" - Simulation-File: " + str(results[i][1])), self.Q1_list)
            data_1 =QtWidgets.QListWidgetItem((" - Data-File: "+ str(results[i][2])), self.Q1_list)
            
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
            
        self.results = Query.query_5(molefrac_co2=mole_1, temperature=[self.Q2_temp_1, self.Q2_temp_2],
                                pressure=[self.Q2_pres_1, self.Q2_pres_2], velocity=[self.Q2_velo_1, self.Q2_velo_2], downstream=down_1)
        
        self.createQ2Plots()
        
        
        
    def run_Q3(self):
        print("Query 3 started...")


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
        
        ## Plot_1 x,T (v=constants)
        #plot_1
        temp_1 = []
        for result in self.results:
            temp_1.append(result[5])
        self.min_velo_1 = min(temp_1)
        
        filtered_results_1 = [result for result in self.results if str(result[5]) == str(float(self.min_velo_1))]
        pressure_groups_1 = {}
        #print(pressure_groups_1)
        for result in filtered_results_1:
            pressure = result[4]
            if pressure not in pressure_groups_1:
                pressure_groups_1[pressure] = {"temperature": [], "turnover": []}
            pressure_groups_1[pressure]["temperature"].append(result[3])
            pressure_groups_1[pressure]["turnover"].append(result[6])
               
        self.Q2W1 = self.findChild(QtWidgets.QWidget, "Q2widget1")
        """
        if not hasattr(self, 'Q2_figure_1'):
            self.Q2_figure_1, self.Q2_1_ax = plt.subplots()
            self.canvas_Q2_1 = FigureCanvas(self.Q2_figure_1)
            self.canvas_Q2_1.setGeometry(self.Q2W1.geometry())
            self.QW2_figure_1_layout = QtWidgets.QVBoxLayout(self.Q2W1)
            self.QW2_figure_1_layout.addWidget(self.canvas_Q2_1)
        else:
            self.Q2_1_ax.clear()
            self.canvas_Q2_1.draw_idle()
        
        for pressure, data in pressure_groups_1.items():
            self.Q2_1_ax.plot(data['temperature'], data['turnover'], label=f'Pressure: {pressure} Pa')

        self.Q2_1_ax.grid(True)
        self.Q2_figure_1.tight_layout()
        self.canvas_Q2_1.draw()
        """
        # plot_2
        temp_2 = []
        for result in self.results:
            temp_2.append(result[4])
        self.min_pres_1 = min(temp_2)
        
        filtered_results_2 = [result for result in self.results if str(result[4]) == str(float(self.min_pres_1))]
        #print(filtered_results_2)
        velo_groups_1 = {}
        for result in filtered_results_2:
            velo = result[5]
            if velo not in velo_groups_1:
                velo_groups_1[velo] = {"temperature": [], "turnover": []}
            velo_groups_1[velo]["temperature"].append(result[3])
            velo_groups_1[velo]["turnover"].append(result[6])
        
        self.Q2W2 = self.findChild(QtWidgets.QWidget, "Q2widget2")
        #print(velo_groups_1)
        """
        if not hasattr(self, 'Q2_figure_2'):
            self.Q2_figure_2, self.Q2_2_ax = plt.subplots()
            self.canvas_Q2_2 = FigureCanvas(self.Q2_figure_2)
            self.canvas_Q2_2.setGeometry(self.Q2W2.geometry())
            self.QW2_figure_2_layout = QtWidgets.QVBoxLayout(self.Q2W2)
            self.QW2_figure_2_layout.addWidget(self.canvas_Q2_2)
        else:
            self.Q2_2_ax.clear()
            self.canvas_Q2_2.draw_idle()
        
        for velo, data in velo_groups_1.items():
            print(velo, data)
            self.Q2_2_ax.plot(data['temperature'], data['turnover'], label=f'Velocity: {velo} ms')

        self.Q2_2_ax.grid(True)
        self.Q2_figure_2.tight_layout()
        self.canvas_Q2_2.draw()
        """
        # Liste von Plot-Widgets
        plot_widgets = [
            {"result_filter": lambda result: str(result[5]) == str(self.Q2_velo_1), "groups": pressure_groups_1, "widget": self.Q2W1},
            {"result_filter": lambda result: str(result[4]) == str(self.Q2_pres_1), "groups": velo_groups_1, "widget": self.Q2W2}
        ]
        
        for plot_info in plot_widgets:
            result_filter = plot_info["result_filter"]
            groups = plot_info["groups"]
            widget = plot_info["widget"]
        
            if not hasattr(self, f'{widget.objectName()}_figure'):
                figure, ax = plt.subplots()
                canvas = FigureCanvas(figure)
                canvas.setMouseTracking(True)
                canvas.setGeometry(widget.geometry())
                layout = QtWidgets.QVBoxLayout(widget)
                layout.addWidget(canvas)
        
                setattr(self, f'{widget.objectName()}_figure', figure)
                setattr(self, f'{widget.objectName()}_ax', ax)
                setattr(self, f'{widget.objectName()}_canvas', canvas)
            else:
                ax = getattr(self, f'{widget.objectName()}_ax')
                ax.clear()
                getattr(self, f'{widget.objectName()}_canvas').draw_idle()
        
            for key, data in groups.items():
                print(key)
                print(data)
                ax.plot(data['temperature'], data['turnover'], label=f'{key}')
        
            ax.grid(True)
            getattr(self, f'{widget.objectName()}_figure').tight_layout()
            getattr(self, f'{widget.objectName()}_canvas').draw()
            
    def canvas_press_event(self, event):
        canvas_name = event.inaxes.figure.canvas.get_name()

        if canvas_name == 'Q2W1_canvas':
            self.Q2_1_canvas_clicked(event)
        elif canvas_name == 'Q2W2_canvas':
            self.Q2_2_canvas_clicked(event)      
        
    
    def Q2_1_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_1 = NewWindow_Q2_1(self.results, self.Q2_velo_1)
        self.new_window_1.show()
        

    def Q2_2_canvas_clicked(self, event):
        print("canvas clicked")
        self.new_window_2 = NewWindow_Q2_2(self.results, self.Q2_pres_1)
        self.new_window_2.show()
        

class NewWindow_Q2_1(QtWidgets.QMainWindow):
    def __init__(self, results, Q2_velo_1):
        super(NewWindow_Q2_1, self).__init__()
        
        self.results = results
        self.Q2_velo_1 = Q2_velo_1
        
        self.setWindowTitle("Q2_P1")
        self.create_plot()
        
        
    def create_plot(self):
        filtered_results_1 = [result for result in self.results if str(result[5]) == str(self.Q2_velo_1)]
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
        filtered_results_2 = [result for result in self.results if str(result[4]) == str(self.Q2_pres_1)]
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
            
        self.Q2_Figure_2.tight_layout()
        self.Q2_P2_ax.grid(True)
        self.Q2_P2_ax.legend()
        self.canvas_Q2_P2.draw()
        
        
        
        
        
app = QtWidgets.QApplication(sys.argv)
qdarktheme.setup_theme(theme="light", custom_colors={"[light]":{"primary":"#84BC34"}})
window = Ui()
app.exec_()