import sys
import numpy as np
import pandas as pd
#from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QMdiArea, QMdiSubWindow, QWidget
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import session as Session
from csv_import import CSVImport
from data_chooser import DataChooser
import session_handler as handler

class GraphModule(QMainWindow):
    def __init__(self, data_frame:pd.DataFrame):
        super().__init__()

        self.setWindowTitle("Module")
        self.setGeometry(100, 100, 300, 200)
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet('background-color: #333; color: white; font-size: 14px;')
        self.menubar.setStyleSheet('QMenu::item:selected { background-color: #555; }')
        self.menubar.setStyleSheet('QMenu::item:pressed { background-color: #777; }')

        self.dataframe = data_frame

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        self.sidewidget = QWidget()
        self.sidebox = QVBoxLayout()

        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.x_set = QComboBox(self.central_widget)
        self.x_combo = QComboBox(self.central_widget)
        self.y_set = QComboBox(self.central_widget)
        self.y_combo = QComboBox(self.central_widget)

        self.sidebox.addWidget(QLabel("Select First Dataset:"))
        self.sidebox.addWidget(self.x_set)
        self.sidebox.addWidget(QLabel("Select X Axis Column:"))
        self.sidebox.addWidget(self.x_combo)

        self.sidebox.addWidget(QLabel("Select Second Dataset:"))
        self.sidebox.addWidget(self.y_set)
        self.sidebox.addWidget(QLabel("Select Y Axis Column:"))
        self.sidebox.addWidget(self.y_combo)

        self.plot_button = QPushButton("Plot Graph", self.central_widget)
        self.sidebox.addWidget(self.plot_button)
        

        self.layout.addLayout(self.sidebox)

        self.plot_button.clicked.connect(self.plot_graph)

    def plot_graph(self):
        self.selected_x = self.x_combo.currentText()
        self.selected_y = self.y_combo.currentText()

        self.x_data = self.dataframe[self.selected_x]
        self.y_data = self.dataframe[self.selected_y]

        self.plot_widget.clear()    
        self.plot_widget.plot(self.x_data, self.y_data, pen='b')

      
   

    def setComboBoxes(self, active_data:pd.DataFrame):
        print(handler.get_names())
        self.x_set.addItems(handler.get_names())
        self.y_set.addItems(handler.get_names())
        self.x_combo.addItems(active_data.columns.tolist())
        self.y_combo.addItems(active_data.columns.tolist())
        self.dataframe = active_data
        
        '''
        IMPORTANT: Not all CSVs contain the same data, meaning we need to find/make a parser/organizer to recover the columns/rows from 
        a csv and be able to show them. One of the issues with this is that some stats in the data frame may not be numerical, so problematic

        One of 
        '''
        

class CustomDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sun Devil Motorsports Data Dashboard")
        self.setWindowIcon(QIcon("90129757.jpg"))
        self.setGeometry(100, 100, 1800, 900)

        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        self.layout = QVBoxLayout()
        self.toolbar = QHBoxLayout()
        self.layout.addLayout(self.toolbar)

        self.camera_module_button = QPushButton("Add Camera", self)
        self.camera_module_button.setMaximumWidth(200)
        self.camera_module_button.clicked.connect(self.create_camera_module)

        self.velocity_module_button = QPushButton("Add Velocity vs Time")
        self.velocity_module_button.setMaximumWidth(200)
        self.velocity_module_button.clicked.connect(self.create_velocity_module)

        self.add_csv_button = QPushButton("Add CSV File")
        self.add_csv_button.setMaximumWidth(200)
        self.add_csv_button.clicked.connect(self.introduce_csv_importer)

        """self.update_session_button = QPushButton("Update Session")
        self.update_session_button.setMaximumWidth(200)
        self.update_session_button.clicked.connect(self.updateSession)"""

                

        self.toolbar.addWidget(self.camera_module_button)
        self.toolbar.addWidget(self.velocity_module_button)
        self.toolbar.addWidget(self.add_csv_button)
        #self.toolbar.addWidget(self.update_session_button)
        self.toolbar.addStretch(1)
        self.layout.addWidget(self.mdi_area)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.data_chooser = DataChooser()
        if (self.data_chooser.isDataReady()):
            self.active_data = self.data_chooser.getCurrentSession().get_dataframe()

    def create_new_module(self):
        sub_window = QMdiSubWindow()
        graph_module = GraphModule(self.active_data)
        self.graph_module.setWindowIcon(QIcon("90129757.jpg"))
        sub_window.setWidget(graph_module)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def create_camera_module():
        #create camera module
        pass

    def create_velocity_module(self):
        #create velo module
        sub_window = QMdiSubWindow()
        graph_module = GraphModule(self.active_data)
        graph_module.setComboBoxes(self.active_data)
        sub_window.setWidget(graph_module)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def introduce_csv_importer(self):
        filename = QFileDialog.getOpenFileName()
        if filename[0] == "":
            return
        importer = CSVImport(filename[0])
        importer.exec()
        self.active_data = handler.get_active_sessions()[0].get_dataframe()

    #Obsolite, initiated with intorduce_csv_importer
    """def updateSession(self):
        #implement updating all modules with new data
        self.data_chooser = DataChooser()
        self.data_chooser.exec()
        if (self.data_chooser.isDataReady()):
            self.active_data = self.data_chooser.getCurrentSession().get_dataframe()"""
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomDashboard()
    window.show()
    sys.exit(app.exec_())
