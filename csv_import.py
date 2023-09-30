from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from datetime import date
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
        self.setWindowIcon(QIcon("90129757.jpg"))

        # get headers
        col_select_layout: QGridLayout = QGridLayout()
        self.combo_time = QComboBox()
        self.combo_lap = QComboBox()
        self.combo_lat = QComboBox()
        self.combo_lon = QComboBox()        

        # session details
        session_details_layout: QVBoxLayout = QVBoxLayout()
        self.edit_name = QLineEdit(filename[filename.rfind("/") + 1:filename.rfind(".")])
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
        #print("Is checked: " + str(self.live.isChecked()))
        new_session = Session.set_session(self.df, time_idx, lap_idx, lat_idx, lon_idx, name, date, driver, car, track, find_gps_fix())
        handler.add_session(new_session, self.live.isChecked())


        self.done(1)
        self.hide()


    def find_gps_fix():
        ts = 0
        for index, row in self.df.iterrows():
            if (row["longitude"] != 0):
                ts = row["timestamp (s)"]
                break
        return ts



        '''
        gps = []
        useful = []
        sus = []
        lat = []

        for i in range(2, 22):
            if i in (196, 198):
                continue
            #with open(f'raw/run{i}-data.csv', 'r') as file:
            with open(self.df) as file:
                rows = file.read().split('\n')
            
            min_long_accel = 99999
            max_long_accel = -99999
            max_lateral_accel = -99999
            max_gps_speed = -99999
            ts = 0
            run_length = 0
            min_damper = 99999
            max_damper = -999
            max_temp = -99999
            max_sg = -99
            min_sg = 9999999

            print(f"run {i}:")

            for row in rows[1:-1]:
                data = row.split(',')
                long_accel = float(data[1])
                lat_accel = abs(float(data[2]))
                speed = float(data[17])
                damper = float(data[13])
                temp = float(data[10])
                fr_sg = float(data[11])

                min_long_accel = min(min_long_accel, long_accel)
                max_long_accel = max(max_long_accel, long_accel)
                max_lateral_accel = max(max_lateral_accel, lat_accel)
                max_gps_speed = max(max_gps_speed, speed)
                max_damper = max(max_damper, damper)
                min_damper = min(min_damper, damper)
                max_temp = max(max_temp, temp)
                max_sg = max(max_sg, fr_sg)
                min_sg = min(min_sg, fr_sg)

                if ts == 0 and speed > 0:
                    ts = float(data[0])

                if row == rows[-10]:
                    run_length = float(data[0])

            if ts > 0:
                gps.append(i)
            if run_length > 120:
                useful.append(i)
            if max_damper - min_damper > 5:
                sus.append(i)
            if max_lateral_accel > 100:
                lat.append(i)


        
            print(f"max accel (mG): {abs(max_long_accel)}")
            print(f"max braking (mG): {min_long_accel}")
            print(f"max lateral accel (mG): {max_lateral_accel}")
            print(f"max gps speed (knots): {max_gps_speed}")
            print(f"max rotor temp (C): {max_temp}")
            print(f"rl damper range (mm): {max_damper - min_damper}")
            print(f"fr sg range (adcval): {max_sg - min_sg}")
            print(f"gps fix acquired at: {ts} seconds")
            print(f"run length (s): {run_length}\n")
        
        print("runs with gps:")
        print(gps)

        print("\nruns longer than 2 minutes:")
        print(useful)

        print("\nruns with damper travel > 5mm:")
        print(sus)

        print("\nruns with lat accel > 100 mG:")
        print(lat)
        '''







