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

# ------------------------------
# Custom Class for our GraphModule. By inheriting from it, we can create a custom canvas for Matplotlib within the PyQt application.
# Line outside the class tells the application that the backend for Matplotlib will use Qt5Agg,
# which is the backend that integrates Matplotlib with the PyQt5 framework. It tells Matplotlib
# to render plots using Qt for the graphical user interface.
# ------------------------------

matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    activeXY = [[], []]

    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


# ------------------------------
# Custom class named DatasetChooser. This is the sidebar that provides functionality to select datasets,
# customize data visualization settings, and update and animate graphs using Matplotlib.
# It connects various widgets and signals to provide an interactive data visualization experience.
# ------------------------------
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
        self.timestamper = timestamper

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

        # creates labels and textboxes for editing graph limits and trims
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

        # creates labels and adds comboboxes to select columns in the graph
        self.set_combo_box()
        self.sidebox.addWidget(QLabel("Select Dataset:"))
        self.sidebox.addWidget(self.x_set)
        self.sidebox.addWidget(QLabel("Select X Axis Column:"))
        self.sidebox.addWidget(self.x_combo)
        self.sidebox.addWidget(QLabel("Select Y Axis Column:"))
        self.sidebox.addWidget(self.y_combo)
        self.sidebox.addLayout(trim_layout)

        self.sidebox2.setAlignment(Qt.AlignTop)

    def on_click(self, event):
        """On click function is called during a click, decides if it is a left click, and calls click_trim() to zoom the graph in/out"""
        if event.dblclick:
            if event.button is MouseButton.LEFT:
                self.left = True
            self.click_trim()
            self.left = False

    def clear_layout(self, layout):
        """Removes all items from the given layout"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def set_combo_box(self):
        """Populates ComboBoxes with all different columns within the active data"""
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

    def init_combobox(self, xSet, xSelect, ySelect):
        """Sets the front-text of comboboxes within the sidebar to the currently selected column within the active dataset"""
        self.x_set.setCurrentText(xSet)
        self.x_combo.setCurrentText(xSelect)
        self.y_combo.setCurrentText(ySelect)

    def get_scroll_areas(self):
        """returns both sidebox layouts"""
        return self.sidebox, self.sidebox2

    def set_active_data(self):
        """Modifies self.active_dataX and sets it to the dataframe in which the "set x" value is. It then calls trim_graph() and plot_graph()."""
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
        """This function simply populates some of the labels with the metadata from the chosen metadata data frame"""
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
        """Function that when called, will edit the bounds of the graph based on whether autofit is selected or not. Otherwise values in textboxes will be set to the bounds"""
        if self.begin_widget.text() == "" or self.end_widget.text() == "":
            return
        if self.autofit_widget.isChecked():
            # NOTE: THIS MAY BE PROBLEMATIC WHEN ENABLED DUE TO IMPLEMENTATION
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
        """When called, click_trim() is responsible for adjusting the visible range of data, by about 10%. It zooms in if left click or zooms out if right click"""
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
        """When called, this function is responsible for updating and redrawing a graph with user-selected data and settings.
        It then 'draws' the graph, meaning it is an update to the appearance of a graph rather than a creation of a new plot. The performance
        difference could be negligible here. More importantly, limit every possible call to redraw the graph as much as one can
        """
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

    def play_graph(self):
        """May not be finished. This creates the animation to redraw the graph as it would iterate through the x values of the dataset. Calls animate() along the way"""
        try:
            self.ani = animation.FuncAnimation(
                self.plot_widget.fig,
                self.animate,
                frames=self.timestamper.time_generator,
                interval=100,
                repeat=False,
                save_count=50,
                cache_frame_data=True,
            )
            self.plot_widget.draw()
        except Exception as e:
            print("Error re-drawing graph: " + str(e))

    def animate(self, timestamp):
        """Helper for the animation, adds new data points to X and Y data lists, clears the existing plot, and then re-plots the updated data with new labels, a title, and a grid.
        WARNING: use of plot() could be better than draw(), but we made it necessary that the function will use plot() because of adding to the active x and y datasets
        """
        activeXY = self.active_dataX[
            (self.active_dataX["Time (s)"] >= 0)
            & (self.active_dataX["Time (s)"] <= timestamp)
        ][[self.selected_x, self.selected_y]]
        self.plot_widget.activeXY[0] = activeXY[self.selected_x].tolist()
        self.plot_widget.activeXY[1] = activeXY[self.selected_y].tolist()
        self.plot_widget.ax1.clear()
        self.plot_widget.ax1.plot(
            self.plot_widget.activeXY[0], self.plot_widget.activeXY[1]
        )
        self.plot_widget.ax1.set_xlabel(self.selected_x)
        self.plot_widget.ax1.set_ylabel(self.selected_y)
        self.plot_widget.ax1.legend()
        self.plot_widget.ax1.set_title(self.selected_x + " vs " + self.selected_y)
        self.plot_widget.ax1.grid()

    def get_info(self):
        """Returns value of self.x_set, the combobox for selecting the current dataset or csv. additionally it returns the current x and y columns"""
        return self.x_set.currentText(), self.selected_x, self.selected_y


# ------------------------------
# This class creates a graphical application with a main window that allows users to add and configure multiple datasets for plotting.
# This is what is shown in the GUI from the main file: dash_board.py. It encapsulates everything described in this file up until this point.
# ------------------------------


class GraphModule(QMainWindow):
    def __init__(self, live=False, timestamper=None):
        super().__init__()
        self.live = live
        self.data_set = []
        self.setWindowTitle("Module")
        self.setGeometry(100, 100, 1050, 600)
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

        self.timestamper = timestamper
        self.setChooser = DatasetChooser(
            self.central_widget, self.plot_widget, timestamper, self.live
        )
        sidebox, sidebox1 = self.setChooser.get_scroll_areas()
        self.data_set.append(self.setChooser)
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

    def play_graph(self):
        self.setChooser.play_graph()

    def add_dataset(self):
        """Function called when 'Add Dataset' button is clicked, creates a new sidebox to add to the existing sidebox"""
        setChooser = DatasetChooser(
            self.central_widget, self.plot_widget, self.timestamper
        )
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
        """Getter that returns an array with the layouts of the sideboxes"""
        info = []
        for i in self.data_set:
            info.append(i.get_info())

        return info

    # Why do we have this? ?
    """
    def init_combobox(self, xSet, xSelect, ySelect):
        self.data_set[0].init_combobox(xSet, xSelect, ySelect)
    """
