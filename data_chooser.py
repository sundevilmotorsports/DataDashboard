from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from session import Session
import session_handler as handler

class DataChooser(QDialog):
    def __init__(self):
        super().__init__()

        self.session_arr = handler.get_active_sessions()
        
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Choose Your Data")
        self.setWindowIcon(QIcon("90129757.jpg"))

        self.session_chooser = QComboBox()
        self.session_chooser.addItems(handler.get_names())

        self.title = QLabel("Choose the session that you want to analyze")

        self.accept_button = QPushButton("Accept")
        self.accept_button.clicked.connect(self.clicked_accept)


        self.layout.addWidget(self.title)
        self.layout.addWidget(self.session_chooser)
        self.layout.addWidget(self.accept_button)

        self.dataReady = False
        self.current_session = None   

    def getDataFromSessionArr(self):
        return self.session_chooser.currentData()

    def getSessionComboBox(self):
        return self.session_chooser

    def clicked_accept(self):  
        self.done(1)
        self.current_session = self.session_arr[self.session_chooser.currentIndex()]
        self.dataReady = True
    
    def isDataReady(self):
        return self.dataReady

    def getCurrentSession(self) -> Session:
        return self.current_session

    


