from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import session_handler as handler

matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class DatasetChooser(QWidget):
    def __init__(self, central_widget: QWidget, plot: MplCanvas):
        super().__init__()
        self.central_widget = central_widget
        self.plot_widget = plot

        self.sidebox = QVBoxLayout()
        self.sidebox2 = QVBoxLayout()

        self._plot_ref = None
        self.sidebox.setAlignment(Qt.AlignTop)

        self.x_combo = QComboBox(self.central_widget)
        self.y_combo = QComboBox(self.central_widget)
        self.x_combo.currentIndexChanged.connect(self.plot_graph)
        self.y_combo.currentIndexChanged.connect(self.plot_graph)

        #creating dropdowns and updating dataset when changed
        self.x_set = QComboBox(self.central_widget)
        self.x_set.showEvent = lambda _: self.init_metadata()
        self.x_set.currentIndexChanged.connect(self.set_active_data)
        self.set_combo_box()
        self.sidebox.addWidget(QLabel("Select Dataset:"))
        self.sidebox.addWidget(self.x_set)
        #self.sidebox.addWidget(QLabel("")
        self.sidebox.addWidget(QLabel("Select X Axis Column:"))
        self.sidebox.addWidget(self.x_combo)
        #self.sidebox.addWidget(QLabel(""))
        self.sidebox.addWidget(QLabel("Select Y Axis Column:"))
        self.sidebox.addWidget(self.y_combo)

        #No longer needed, auto ploting
        #self.central_widget

        self.sidebox2.setAlignment(Qt.AlignTop)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def set_combo_box(self):
        try:
            self.x_set.addItems(handler.get_names())
            self.x_combo.clear()
            self.y_combo.clear()
            self.active_dataX = handler.get_active_sessions(
            )[0].get_dataframe()
            self.x_combo.addItems(self.active_dataX.columns.tolist())
            self.y_combo.addItems(self.active_dataX.columns.tolist())
        except:
            print("Error setting combo box")
            
        '''
        IMPORTANT: Not all CSVs contain the same data, meaning we need to find/make a parser/organizer to recover the columns/rows from 
        a csv and be able to show them. One of the issues with this is that some stats in the data frame may not be numerical, so problematic

        One of 
        '''

    def init_combobox(self, xSet, xSelect, ySelect):
        self.x_set.setCurrentText(xSet)
        self.x_combo.setCurrentText(xSelect)
        self.y_combo.setCurrentText(ySelect)

    def get_scroll_areas(self):
        return self.sidebox, self.sidebox2

    def set_active_data(self):
        self.x_combo.clear()
        self.y_combo.clear()

        self.init_metadata()

        self.active_dataX = handler.get_active_sessions(
        )[self.x_set.currentIndex()].get_dataframe()
        self.x_combo.addItems(self.active_dataX.columns.tolist())
        self.y_combo.addItems(self.active_dataX.columns.tolist())
        self.plot_graph()

    def init_metadata(self):
        try:
            self.clear_layout(self.sidebox2)
            self.dataX = handler.get_active_sessions(
            )[self.x_set.currentIndex()].get_metadata()
            self.dataY = handler.get_active_sessions(
            )[self.x_set.currentIndex()].get_metadata()

            self.sidebox2.addWidget(QLabel("Name: " + self.dataX["Name"]))
            self.sidebox2.addWidget(QLabel("Date: " + self.dataX["Date"]))
            self.sidebox2.addWidget(QLabel("Driver: " + self.dataX["Driver"]))
            self.sidebox2.addWidget(QLabel("Car: " + self.dataX["Car"]))
            self.sidebox2.addWidget(QLabel("Track: " + self.dataX["Track"]))
        except:
            print("Error initializing metadata")

    def plot_graph(self):
        try:
            self.selected_x = self.x_combo.currentText()
            self.selected_y = self.y_combo.currentText()
            self.x_data = self.active_dataX[self.selected_x]
            self.y_data = self.active_dataX[self.selected_y]
            if self._plot_ref is None:
                plotrefs = self.plot_widget.axes.plot(
                    self.x_data, self.y_data, label=self.x_set.currentText())
                self._plot_ref = plotrefs[0]

            else:
                self._plot_ref.set_data(self.x_data, self.y_data)
                self._plot_ref.set_label(self.x_set.currentText())
                self.plot_widget.axes.relim()
                self.plot_widget.axes.autoscale()
                self.plot_widget.axes.autoscale()
            self.plot_widget.axes.set_xlabel(self.selected_x)
            self.plot_widget.axes.set_ylabel(self.selected_y)
            self.plot_widget.axes.set_title(
                self.selected_x + " vs " + self.selected_y)
            self.plot_widget.axes.grid()
            self.plot_widget.axes.legend()
            self.plot_widget.draw()
        except:
            print("Error plotting graph")
    
    def get_info(self):
        return self.x_set.currentText(), self.selected_x, self.selected_y


class GraphModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_set = []
        self.setWindowTitle("Module")
        self.setGeometry(100, 100, 300, 200)
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet(
            'background-color: #333; color: white; font-size: 14px;')
        self.menubar.setStyleSheet(
            'QMenu::item:selected { background-color: #555; }')
        self.menubar.setStyleSheet(
            'QMenu::item:pressed { background-color: #777; }')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)
        sideBoxLayout = QVBoxLayout()

        graph_widget = QWidget()
        self.plot_widget = MplCanvas()

        toolbar = NavigationToolbar(self.plot_widget, self)

        plot_layout = QVBoxLayout(graph_widget)
        plot_layout.addWidget(toolbar)
        plot_layout.addWidget(self.plot_widget)
        self.layout.addWidget(graph_widget)

        setChooser = DatasetChooser(self.central_widget, self.plot_widget)
        sidebox, sidebox1 = setChooser.get_scroll_areas()
        self.data_set.append(setChooser)
        sideBoxLayout.addLayout(sidebox)
        sideBoxLayout.addLayout(sidebox1)
        self.add_dataset_button = QPushButton(
            "Add Dataset", self.central_widget)
        self.add_dataset_button.clicked.connect(self.add_dataset)
        sideBoxLayout.addWidget(self.add_dataset_button)
        self.layout.addLayout(sideBoxLayout)


        #self.plot_button.clicked.connect(self.plot_graph)

    def add_dataset(self):
        setChooser = DatasetChooser(self.central_widget, self.plot_widget)
        self.data_set.append(setChooser)
        sideBoxLayout = QVBoxLayout()
        sidebox, sidebox1 = setChooser.get_scroll_areas()

        sideBoxLayout.addLayout(sidebox)
        sideBoxLayout.addLayout(sidebox1)
        sideBoxLayout.insertWidget(-1,self.add_dataset_button)
        self.layout.addLayout(sideBoxLayout)
    
    def get_info(self):
        info = []
        for i in self.data_set:
            info.append(i.get_info())
        
        return info

    def init_combobox(self, xSet, xSelect, ySelect):
        self.data_set[0].init_combobox(xSet, xSelect, ySelect)
    
        
