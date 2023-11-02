import time
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import session_handler as handler
from collapsible_module import Collapsible
from timestamper import TimeStamper


matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    activeXY = [[],[]]
    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class DatasetChooser(QWidget):
    def __init__(
        self,
        central_widget: QWidget,
        plot: MplCanvas,
        timestamper: TimeStamper,
        live=False,
    ):
        super().__init__()

        self.central_widget = central_widget
        self.plot_widget = plot
        self.live = live
        self.sidebox = QVBoxLayout()
        self.sidebox2 = QVBoxLayout()

        timestamper.bind_to(self.redraw_graph)

        self.plot_widget.fig.canvas.mpl_connect("button_press_event", self.on_click)

        self._plot_ref = None
        self.left = False

        self.sidebox.setAlignment(Qt.AlignTop)
        self.x_combo = QComboBox(self.central_widget)
        self.y_combo = QComboBox(self.central_widget)
        self.x_combo.currentIndexChanged.connect(self.plot_graph)
        self.y_combo.currentIndexChanged.connect(self.plot_graph)

        # creating dropdowns and updating dataset when changed
        self.x_set = QComboBox(self.central_widget)
        self.x_set.showEvent = lambda _: self.init_metadata()
        self.x_set.currentIndexChanged.connect(self.set_active_data)

        trim_layout = QHBoxLayout()
        self.autofit_widget = QCheckBox("Autofit")
        self.autofit_widget.stateChanged.connect(self.trim_graph)
        trim_layout.addWidget(self.autofit_widget)
        trim_layout.addWidget(QLabel("Trim:"))
        self.begin_widget = QLineEdit()
        self.begin_widget.setFixedWidth(50)
        self.begin_widget.textChanged.connect(self.trim_graph)
        trim_layout.addWidget(self.begin_widget)
        trim_layout.addWidget(QLabel("≤ x ≤"))
        self.end_widget = QLineEdit()
        self.end_widget.setFixedWidth(50)
        self.end_widget.textChanged.connect(self.trim_graph)
        trim_layout.addWidget(self.end_widget)

        self.set_combo_box()
        self.sidebox.addWidget(QLabel("Select Dataset:"))
        self.sidebox.addWidget(self.x_set)
        # self.sidebox.addWidget(QLabel("")
        self.sidebox.addWidget(QLabel("Select X Axis Column:"))
        self.sidebox.addWidget(self.x_combo)
        # self.sidebox.addWidget(QLabel(""))
        self.sidebox.addWidget(QLabel("Select Y Axis Column:"))
        self.sidebox.addWidget(self.y_combo)
        self.sidebox.addLayout(trim_layout)
        # No longer needed, auto ploting
        # self.central_widget

        self.sidebox2.setAlignment(Qt.AlignTop)

    def on_click(self, event):
        if event.dblclick:
            if event.button is MouseButton.LEFT:
                self.left = True
            self.click_trim()
            self.left = False

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def set_combo_box(self):
        try:
            if self.live:
                names = handler.get_live_names()
                data = handler.get_live_sessions()
            else:
                names = handler.get_names()
                data = handler.get_active_sessions()
            self.x_set.addItems(names)
            self.x_combo.clear()
            self.y_combo.clear()
            self.active_dataX = data[0].get_dataframe()
            self.x_combo.addItems(self.active_dataX.columns.tolist())
            self.y_combo.addItems(self.active_dataX.columns.tolist())
        except:
            print("Error setting combo box")

        """
        IMPORTANT: Not all CSVs contain the same data, meaning we need to find/make a parser/organizer to recover the columns/rows from 
        a csv and be able to show them. One of the issues with this is that some stats in the data frame may not be numerical, so problematic

        One of 
        """

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

        self.active_dataX = handler.get_active_sessions()[
            self.x_set.currentIndex()
        ].get_dataframe()
        self.x_combo.addItems(self.active_dataX.columns.tolist())
        self.y_combo.addItems(self.active_dataX.columns.tolist())
        self.begin_widget.setText(str(self.active_dataX[self.selected_x].iloc[0]))
        self.end_widget.setText(str(self.active_dataX[self.selected_x].iloc[-1]))
        self.trim_graph()
        self.plot_graph()

    def init_metadata(self):
        try:
            self.clear_layout(self.sidebox2)
            self.dataX = handler.get_active_sessions()[
                self.x_set.currentIndex()
            ].get_metadata()
            self.dataY = handler.get_active_sessions()[
                self.x_set.currentIndex()
            ].get_metadata()

            self.sidebox2.addWidget(QLabel("Name: " + self.dataX["Name"]))
            self.sidebox2.addWidget(QLabel("Date: " + self.dataX["Date"]))
            self.sidebox2.addWidget(QLabel("Driver: " + self.dataX["Driver"]))
            self.sidebox2.addWidget(QLabel("Car: " + self.dataX["Car"]))
            self.sidebox2.addWidget(QLabel("Track: " + self.dataX["Track"]))
        except:
            print("Error initializing metadata")

    def trim_graph(self):
        if self.begin_widget.text() == "" or self.end_widget.text() == "":
            return
        if self.autofit_widget.isChecked():
            self.begin = self.active_dataX[self.selected_x].iloc[0]
            self.end = self.active_dataX[self.selected_x].iloc[-1]
            self.begin_widget.setDisabled(True)
            self.end_widget.setDisabled(True)
        else:
            self.begin = float(self.begin_widget.text())
            self.end = float(self.end_widget.text())
            self.begin_widget.setEnabled(True)
            self.end_widget.setEnabled(True)

        self.begin_widget.setText(str(int(self.begin)))
        self.end_widget.setText(str(int(self.end)))
        self._plot_ref.axes.set_xlim(self.begin, self.end)
        self.plot_widget.draw()

    def click_trim(self):
        if (
            self.begin_widget.text() == ""
            or self.end_widget.text() == ""
            or self.autofit_widget.isChecked()
        ):
            return

        if self.left:
            adjustment = round(int(self.end_widget.text()) * 0.1)
        else:
            adjustment = round(int(self.end_widget.text()) * 0.1) * -1

        if (
            not int(self.begin_widget.text()) + adjustment
            >= int(self.end_widget.text()) - adjustment
        ):
            self.begin_widget.setText(str(int(self.begin_widget.text()) + adjustment))
            self.end_widget.setText(str(int(self.end_widget.text()) - adjustment))

        self._plot_ref.axes.set_xlim(
            float(self.begin_widget.text()), float(self.end_widget.text())
        )
        self.plot_widget.draw()

    def plot_graph(self):
        try:
            self.selected_x = self.x_combo.currentText()
            self.selected_y = self.y_combo.currentText()
            self.x_data = self.active_dataX[self.selected_x]
            self.y_data = self.active_dataX[self.selected_y]
            if self._plot_ref is None:
                plotrefs = self.plot_widget.ax1.plot(
                    self.x_data, self.y_data, label=self.x_set.currentText()
                )
                self._plot_ref = plotrefs[0]

            else:
                self._plot_ref.set_data(self.x_data, self.y_data)
                self._plot_ref.set_label(self.x_set.currentText())
                self.plot_widget.ax1.relim()
                self.plot_widget.ax1.autoscale()
                self.plot_widget.ax1.autoscale()
            self.plot_widget.ax1.set_xlabel(self.selected_x)
            self.plot_widget.ax1.set_ylabel(self.selected_y)
            self.plot_widget.ax1.set_title(self.selected_x + " vs " + self.selected_y)
            self.plot_widget.ax1.grid()
            self.plot_widget.ax1.legend()
            self.plot_widget.ax1.set_xlim(self.begin, self.end)
            self.trim_graph()
            self.plot_widget.draw()
        except Exception as e:
            print("Error plotting graph: " + str(e))

    def redraw_graph(self, timestamp=614):
        try:
            activeXY = self.active_dataX[(self.active_dataX["Time (s)"] >= 0) & (self.active_dataX["Time (s)"] >= timestamp)][[self.selected_x, self.selected_y]].to_numpy()
            ani = animation.FuncAnimation(self.plot_widget.fig, self.animate, frames = activeXY, interval = 10, repeat = False)
            self.plot_widget.draw()
            
        except Exception as e:
            print("Error re-drawing graph: " + str(e))

    def animate(self, cords):
        self.plot_widget.activeXY[0].append(cords[0])
        self.plot_widget.activeXY[1].append(cords[1])
        print(len(self.plot_widget.activeXY[0]))
        self.plot_widget.ax1.clear()
        self.plot_widget.ax1.plot(self.plot_widget.activeXY[0], self.plot_widget.activeXY[1]) 
        self.plot_widget.ax1.set_xlabel(self.selected_x)
        self.plot_widget.ax1.set_ylabel(self.selected_y)
        self.plot_widget.ax1.set_title(self.selected_x + " vs " + self.selected_y)
        self.plot_widget.ax1.grid()      


    def get_info(self):
        return self.x_set.currentText(), self.selected_x, self.selected_y


class GraphModule(QMainWindow):
    def __init__(self, live=False, timestamper=None):
        super().__init__()
        self.live = live
        self.data_set = []
        self.setWindowTitle("Module")
        self.setGeometry(100, 100, 300, 200)
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet(
            "background-color: #333; color: white; font-size: 14px;"
        )
        self.menubar.setStyleSheet("QMenu::item:selected { background-color: #555; }")
        self.menubar.setStyleSheet("QMenu::item:pressed { background-color: #777; }")

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

        setChooser = DatasetChooser(
            self.central_widget, self.plot_widget, timestamper, self.live
        )
        sidebox, sidebox1 = setChooser.get_scroll_areas()
        self.data_set.append(setChooser)
        sideBoxLayout.addLayout(sidebox)
        sideBoxLayout.addLayout(sidebox1)

        self.add_dataset_button = QPushButton("Add Dataset", self.central_widget)
        self.add_dataset_button.clicked.connect(self.add_dataset)
        sideBoxLayout.addWidget(self.add_dataset_button)

        collapsible_container = Collapsible()
        collapsible_container.setContentLayout(sideBoxLayout)
        self.layout.addWidget(collapsible_container)
        # self.layout.addLayout(sideBoxLayout)

        # self.plot_button.clicked.connect(self.plot_graph)

    def add_dataset(self):
        setChooser = DatasetChooser(self.central_widget, self.plot_widget)
        self.data_set.append(setChooser)
        sideBoxLayout = QVBoxLayout()
        sidebox, sidebox1 = setChooser.get_scroll_areas()

        sideBoxLayout.addLayout(sidebox)
        sideBoxLayout.addLayout(sidebox1)
        sideBoxLayout.insertWidget(-1, self.add_dataset_button)
        # self.layout.addLayout(sideBoxLayout)
        collapsible_container = Collapsible()
        collapsible_container.setContentLayout(sideBoxLayout)
        self.layout.addWidget(collapsible_container)

    def get_info(self):
        info = []
        for i in self.data_set:
            info.append(i.get_info())

        return info

    def init_combobox(self, xSet, xSelect, ySelect):
        self.data_set[0].init_combobox(xSet, xSelect, ySelect)
