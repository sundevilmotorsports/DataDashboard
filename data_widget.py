from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import pandas as pd
import session_handler as handler

active_sessions = [[]]
index = 0
class DataWidget():
    def __init__(self, parent, plot, alignment = Qt.AlignCenter, alignment2 = Qt.AlignCenter):
        #Creating dropdowns
        # - Need to set ignore to false so .connects dont call functions when constructed
        self.ignore = True
        self.index = index
        self.sidebox = QVBoxLayout()
        self.sidebox2 = QVBoxLayout()
        self.sidebox.setAlignment(alignment) 
        self.sidebox2.setAlignment(alignment2)
        self.plot_widget = plot

        self.x_combo = QComboBox(parent)
        self.y_combo = QComboBox(parent)
        self.x_combo.currentIndexChanged.connect(self.graph_constructor)
        self.y_combo.currentIndexChanged.connect(self.graph_constructor)

        self.x_set = QComboBox(parent)
        self.y_set = QComboBox(parent)
        self.x_set.currentIndexChanged.connect(self.set_active_data)
        self.y_set.currentIndexChanged.connect(self.set_active_data)
        self.ignore = False

        self.sidebox.addWidget(QLabel("Select First Dataset:"))
        self.sidebox.addWidget(self.x_set)
        self.sidebox.addWidget(QLabel("Select X Axis Column:"))
        self.sidebox.addWidget(self.x_combo)

        self.sidebox.addWidget(QLabel("\n"))
        self.sidebox.addWidget(QLabel("Select Second Dataset:"))
        self.sidebox.addWidget(self.y_set)
        self.sidebox.addWidget(QLabel("Select Y Axis Column:"))
        self.sidebox.addWidget(self.y_combo)

        self.x_set.addItems(handler.get_names())
        self.y_set.addItems(handler.get_names())

        #Need to implement updating labels, plan on making inital widget here then using setText to change the label
        #Rather than creating a new QVBoxLayout every time, might change
        self.dataX = handler.get_active_sessions()[self.x_set.currentIndex()].get_metadata()
        self.dataY = handler.get_active_sessions()[self.x_set.currentIndex()].get_metadata()
        self.sidebox2.addWidget(QLabel("Name: " + self.dataX["Name"]))
        self.sidebox2.addWidget(QLabel("Date: " + self.dataX["Date"]))
        self.sidebox2.addWidget(QLabel("Driver: " + self.dataX["Driver"]))
        self.sidebox2.addWidget(QLabel("Car: " + self.dataX["Car"]))
        self.sidebox2.addWidget(QLabel("Track: " + self.dataX["Track"]))
        self.sidebox2.addWidget(QLabel(""))
        self.sidebox2.addWidget(QLabel("Name: " + self.dataY["Name"]))
        self.sidebox2.addWidget(QLabel("Date: " + self.dataY["Date"]))
        self.sidebox2.addWidget(QLabel("Driver: " + self.dataY["Driver"]))
        self.sidebox2.addWidget(QLabel("Car: " + self.dataY["Car"]))
        self.sidebox2.addWidget(QLabel("Track: " + self.dataY["Track"]))

    #Breaks when replacing graph_constructor with plot_graph, unknown why
    def graph_constructor(self):
        self.plot_graph()

    #Clears graph and plots every datapoint in given data's array
    #Changes color as each line is drawn, following pen_dict
    def plot_graph(self, pen:str = 'b'):
        pen_dict = {
            'r' : 'g', 
            'g' : 'b', 
            'b' : 'c', 
            'c' : 'm', 
            'm' : 'y',
            'y' : 'k',
            'k' : 'w', 
            'w' : 'r'
        }
        self.selected_x = self.x_combo.currentText()
        self.selected_y = self.y_combo.currentText()

        self.x_data = self.active_dataX[self.selected_x][:min(len(self.active_dataX), len(self.active_dataY))]
        self.y_data = self.active_dataY[self.selected_y][:min(len(self.active_dataX), len(self.active_dataY))]


        self.plot_widget.clear()
        for i in active_sessions[self.index]:
            self.plot_widget.plot(i.x_data, i.y_data, pen=pen)
            pen = pen_dict[pen]

    def set_active_data(self):
        self.x_combo.clear()
        self.y_combo.clear()
        self.active_dataX = handler.get_active_sessions()[self.x_set.currentIndex()].get_dataframe()
        self.active_dataY = handler.get_active_sessions()[self.y_set.currentIndex()].get_dataframe()
        self.x_combo.addItems(self.active_dataX.columns.tolist())
        self.y_combo.addItems(self.active_dataY.columns.tolist())
        self.graph_constructor()
        self.display_info()

    #Displays metadata of current dataset
    def display_info(self):
        self.dataX = handler.get_active_sessions()[self.x_set.currentIndex()].get_metadata()
        self.dataY = handler.get_active_sessions()[self.x_set.currentIndex()].get_metadata()
        """self.sidebox2.addWidget(QLabel("Name: " + self.dataX["Name"]))
        self.sidebox2.addWidget(QLabel("Date: " + self.dataX["Date"]))
        self.sidebox2.addWidget(QLabel("Driver: " + self.dataX["Driver"]))
        self.sidebox2.addWidget(QLabel("Car: " + self.dataX["Car"]))
        self.sidebox2.addWidget(QLabel("Track: " + self.dataX["Track"]))
        self.sidebox2.addWidget(QLabel(""))
        self.sidebox2.addWidget(QLabel("Name: " + self.dataY["Name"]))
        self.sidebox2.addWidget(QLabel("Date: " + self.dataY["Date"]))
        self.sidebox2.addWidget(QLabel("Driver: " + self.dataY["Driver"]))
        self.sidebox2.addWidget(QLabel("Car: " + self.dataY["Car"]))
        self.sidebox2.addWidget(QLabel("Track: " + self.dataY["Track"]))"""

    def add_session(session):
        try:
            active_sessions[session.index].append(session)
        except IndexError:
            active_sessions.append([session])
            

    def get_sessions():
        return active_sessions
    
    def increment_index():
        global index
        index += 1
    #Updated to set_active_data
    """def setComboBoxes(self, active_data:pd.DataFrame):
        self.test.x_set.addItems(handler.get_names())
        self.test.y_set.addItems(handler.get_names())
        self.test.x_combo.clear()
        self.test.y_combo.clear()
        self.test.x_combo.addItems(active_data.columns.tolist())
        self.test.y_combo.addItems(active_data.columns.tolist())"""