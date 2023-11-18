# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 09:30:56 2023

@author: smmcvoel
"""

import sys
import Query

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("querys.ui", self)
        
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
        self.Q1_Downstream = self.findChild(QtWidgets.QComboBox, "Q1comboBox")
        
        temp_1 = self.Q1_T_input.text()
        pres_1 = self.Q1_P_input.text()
        velo_1 = self.Q1_V_input.text()
        
        if self.Q1_Downstream.currentText() == "With Downstream":
            down_1 = "'Yes'"
        elif self.Q1_Downstream.currentText() == "Without Downstream":
            down_1 = "'No'"
        else:
            down_1 = None
            
        results = Query.query_3(temperature=temp_1, pressure=pres_1, velocity=velo_1, downstream=down_1)
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
        
        
    def run_Q3(self):
        print("Query 3 started...")


    def openUrl(self, item):
        # get url from ListObject
        url = ""
        if " - Simulation-File: " in item.text():
            print(item.text())
            url = item.text().split(" - Simulation-File: ")[1]
        elif " - Data-File: " in item.text():
            url = item.text().split(" - Data-File: ")[1]
        else:
            print("Item got no url, select simulation- or data-file!")

        try:
            QDesktopServices.openUrl(QUrl(url))
        except: UnboundLocalError
        

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()