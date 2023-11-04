from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from datetime import date
import pandas as pd
import session as Session
import session_handler as handler

# ------------------------------
# Custom class named CSVImport. This opens a new window which features a set of comboboxes and textboxes where the user can predefine
# the metadata that will be associated with the CSV that they are importing.
# ------------------------------

class CSVImport(QDialog):
    def __init__(self, filename: str):
        super().__init__()

        self.df: pd.DataFrame = pd.read_csv(filename)

        columns = list(self.df.columns)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Import CSV file")
        self.setWindowIcon(QIcon("90129757.jpg"))

        # get headers
        col_select_layout: QGridLayout = QGridLayout()
        self.combo_time = QComboBox()
        self.combo_lap = QComboBox()
        self.combo_lat = QComboBox()
        self.combo_lon = QComboBox()

        # session details
        session_details_layout: QVBoxLayout = QVBoxLayout()
        self.edit_name = QLineEdit(
            filename[filename.rfind("/") + 1 : filename.rfind(".")]
        )
        self.edit_date = QLineEdit(str(date.today()))
        self.edit_driver = QLineEdit("Driver")
        self.edit_car = QLineEdit("Car")
        self.edit_track = QLineEdit("Track Name")
        self.live = QCheckBox("Live")
        session_details_layout.addWidget(self.edit_name)
        session_details_layout.addWidget(self.edit_date)
        session_details_layout.addWidget(self.edit_driver)
        session_details_layout.addWidget(self.edit_car)
        session_details_layout.addWidget(self.edit_track)
        session_details_layout.addWidget(self.live)

        # dialog management
        mgmt_layout: QHBoxLayout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_import = QPushButton("Import")
        self.btn_import.setDefault(True)
        self.btn_import.clicked.connect(self.accept)
        mgmt_layout.addWidget(self.btn_cancel)
        mgmt_layout.addWidget(self.btn_import)

        # self.layout.addLayout(col_select_layout)
        self.layout.addLayout(session_details_layout)
        self.layout.addLayout(mgmt_layout)

    def cancel(self):
        self.done(0)

    def find_gps_fix(self):

        ts = 0
        return ts

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
        # print("Is checked: " + str(self.live.isChecked()))
        new_session = Session.set_session(
            self.df,
            time_idx,
            lap_idx,
            lat_idx,
            lon_idx,
            name,
            date,
            driver,
            car,
            track,
            self.find_gps_fix(),
        )
        handler.add_session(new_session, self.live.isChecked())

        self.done(1)
        self.hide()