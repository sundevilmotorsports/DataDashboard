from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import pandas as pd
import session as Session
import session_handler as handler


class CSVImport(QDialog):
    def __init__(self, filename: str):
        super().__init__()

        self.df : pd.DataFrame = pd.read_csv(filename)

        columns = list(self.df.columns)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Import CSV file")
        self.setWindowIcon(QIcon("Downloads/90129757.jpg"))

        # get headers
        col_select_layout: QGridLayout = QGridLayout()
        self.combo_time = QComboBox()
        self.combo_lap = QComboBox()
        self.combo_lat = QComboBox()
        self.combo_lon = QComboBox()        

        # session details
        session_details_layout: QVBoxLayout = QVBoxLayout()
        self.edit_name = QLineEdit(filename[filename.rfind("/") + 1:filename.rfind(".")])
        self.edit_date = QLineEdit("Session Date")
        self.edit_driver = QLineEdit("Driver")
        self.edit_car = QLineEdit("Car")
        self.edit_track = QLineEdit("Track Name")
        session_details_layout.addWidget(self.edit_name)
        session_details_layout.addWidget(self.edit_date)
        session_details_layout.addWidget(self.edit_driver)
        session_details_layout.addWidget(self.edit_car)
        session_details_layout.addWidget(self.edit_track)

        # dialog management
        mgmt_layout: QHBoxLayout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_import = QPushButton("Import")
        self.btn_import.setDefault(True)
        self.btn_import.clicked.connect(self.accept)
        mgmt_layout.addWidget(self.btn_cancel)
        mgmt_layout.addWidget(self.btn_import)

        #self.layout.addLayout(col_select_layout)
        self.layout.addLayout(session_details_layout)
        self.layout.addLayout(mgmt_layout)

    def cancel(self):
        self.done(0)

    def accept(self):
        time_idx = self.combo_time.currentText()
        lap_idx = self.combo_lap.currentText()
        lat_idx = self.combo_lat.currentText()
        lon_idx = self.combo_lon.currentText()

        name = self.edit_name.text()
        date = self.edit_date.text()
        driver = self.edit_driver.text()
        car = self.edit_car.text()
        track = self.edit_track.text()

        new_session = Session.set_session(self.df, time_idx, lap_idx, lat_idx, lon_idx, name, date, driver, car, track)
        handler.add_session(new_session)


        self.done(1)
        self.hide()






