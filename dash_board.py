
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from csv_import import CSVImport
from data_chooser import DataChooser
import session_handler as handler
from graph_module import GraphModule
import glob
import pickle 
from datetime import datetime
from PyQt5.QtCore import Qt
class CustomDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sessions = []
        sessions = glob.glob(f"sessions/*.pkl")
        data = glob.glob(f"data/*.pkl")
        for file in sessions:
            session = pickle.load(open(file, "rb"))
            self.sessions.append(session)

        for file in data:
            data = pickle.load(open(file, "rb"))
            handler.add_session(data)


        self.setWindowTitle("Sun Devil Motorsports Data Dashboard")
        self.setWindowIcon(QIcon("90129757.jpg"))
        self.setGeometry(100, 100, 1800, 900)
        handler.get_sessions_from_csv()
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setTabsClosable(True)

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

        self.save_dashboard_button = QPushButton("Save Dashboard")
        self.save_dashboard_button.setMaximumWidth(200)
        self.save_dashboard_button.clicked.connect(self.save_dashboard)

        self.select_session_button = QComboBox()
        self.select_session_button.setMaximumWidth(200)
        self.select_session_button.setPlaceholderText("Select Session")
        self.select_session_button.currentIndexChanged.connect(self.update_session)
        
        for session in self.sessions:
            self.select_session_button.addItem(session["time"].strftime("%m/%d/%Y, %H:%M:%S"))


        self.toolbar.addWidget(self.camera_module_button)
        self.toolbar.addWidget(self.velocity_module_button)
        self.toolbar.addWidget(self.add_csv_button)
        self.toolbar.addWidget(self.save_dashboard_button)
        self.toolbar.addWidget(self.select_session_button)
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
        graph_module = GraphModule()
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
        graph_module = GraphModule()
        sub_window.setWidget(graph_module)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def introduce_csv_importer(self):
        filename = QFileDialog.getOpenFileName(filter = "CSV Files(*.csv)")
        if filename[0] == "":
            return
        importer = CSVImport(filename[0])
        importer.exec()
        self.select_session_button.clear()
        self.active_data = handler.get_active_sessions()[0].get_dataframe()

    def save_dashboard(self):
        data = {"pos": [], "size": [], "metadata": [], "csv": handler.get_names(), "time": datetime.now()}
        for tab in self.mdi_area.subWindowList():
            data["pos"].append((tab.pos().x(), tab.pos().y()))
            data["size"].append((tab.size().width(), tab.size().height()))
            data["metadata"].append(tab.widget().get_info())
        pickle.dump(data, open(f"sessions/{datetime.now()}.pkl", "wb"))
        self.select_session_button.addItem(data["time"].strftime("%m/%d/%Y, %H:%M:%S"))
        self.sessions.append(data)

    def update_session(self):
        active_session = self.sessions[self.select_session_button.currentIndex()]
        tab_amt = len(active_session["pos"])
        print(active_session)
        for window in self.mdi_area.subWindowList():
            self.mdi_area.removeSubWindow(window)
        print(len(self.mdi_area.subWindowList()))
        for tab in range(tab_amt):
            self.create_velocity_module()
        for i, tab in enumerate(self.mdi_area.subWindowList()):
            tab.move(active_session["pos"][i][0], active_session["pos"][i][1])
            tab.resize(active_session["size"][i][0], active_session["size"][i][1])
            tab.widget().init_combobox(
                active_session["metadata"][i][0][0], active_session["metadata"][i][0][1], active_session["metadata"][i][0][2])
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomDashboard()
    window.show()
    sys.exit(app.exec_())
