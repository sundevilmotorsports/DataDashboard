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
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, QObject
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
        #self.timestamper.slider.valueChanged.connect(lambda: self.trim_graph(source="slider"))
        self.animation_ongoing = False

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
        trim_upper = QHBoxLayout()
        trim_under = QHBoxLayout()
        self.trim_container = QVBoxLayout()


        #integer validation for text boxes
        validator = QIntValidator()


        ###   DEPRECATED AUTOFIT

        #self.autofit_widget = QCheckBox("Autofit")
        #self.autofit_widget.stateChanged.connect(self.trim_graph)
        #trim_upper.addWidget(self.autofit_widget)
        # self.active_trim_box = QCheckBox("Select Active Trim")
        # self.active_trim_box.stateChanged.connect(self.select_active_dataset_trim)
        trim_under.addWidget(QLabel("Trim:"))
        self.begin_widget = QLineEdit()
        self.begin_widget.setValidator(validator)
        self.begin_widget.setFixedWidth(50)
        #self.begin_widget.textChanged.connect(lambda: self.trim_graph(source="begin_widget"))
        trim_under.addWidget(self.begin_widget)
        trim_under.addWidget(QLabel("≤ x ≤"))
        self.end_widget = QLineEdit()
        self.end_widget.setValidator(validator)
        self.end_widget.setFixedWidth(50)
        #self.end_widget.textChanged.connect(lambda: self.trim_graph(source="end_widget"))
        trim_under.addWidget(self.end_widget)
        self.trim_container.addLayout(trim_upper)
        self.trim_container.addLayout(trim_under)


        ### array for managing all connections that call to trim_graph
        self.trim_connections = []
        self.trim_connections.append(self.begin_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.end_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.timestamper.slider.valueChanged.connect(self.slider_trim_graph))

        # creates labels and adds comboboxes to select columns in the graph
        self.set_combo_box()
        self.sidebox.addWidget(QLabel("Select Dataset:"))
        self.sidebox.addWidget(self.x_set)
        self.sidebox.addWidget(QLabel("Select X Axis Column:"))
        self.sidebox.addWidget(self.x_combo)
        self.sidebox.addWidget(QLabel("Select Y Axis Column:"))
        self.sidebox.addWidget(self.y_combo)
        self.sidebox.addLayout(self.trim_container)

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

    def get_scroll_areas_without_trim(self):
        """returns both sidebox layouts"""
        tempSidebox1 = self.sidebox
        tempSidebox2 = self.sidebox2
        tempSidebox1.removeItem(self.trim_container)
        tempSidebox2.removeItem(self.trim_container)
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
        ###TAKE NOTE THE NEXT 3 LINES CALL trim_graph 3 TIMES, don't think we want from a performance and maintenance perspective
        self.begin_widget.setText(str(self.active_dataX[self.selected_x].iloc[0]))
        self.end_widget.setText(str(self.active_dataX[self.selected_x].iloc[-1]))
        self.timestamper.set_init_time(self.active_dataX[self.selected_x].iloc[0])
        self.timestamper.set_max_time(self.active_dataX[self.selected_x].iloc[-1])
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
        print("normal trim or end or begin")
        try:
            self.begin_widget.textChanged.disconnect(self.trim_graph)
            self.end_widget.textChanged.disconnect(self.trim_graph)
            self.timestamper.slider.valueChanged.disconnect(self.slider_trim_graph)
            self.trim_connections = []
        except Exception as e:
            print("Could not disconnect all connections" + str(e))

        if self.begin_widget.text() == "" or self.end_widget.text() == "":
            return
        
        ''' AUTOFIT DEPRECATED       
        if self.autofit_widget.isChecked():
            # NOTE: THIS MAY BE PROBLEMATIC WHEN ENABLED DUE TO IMPLEMENTATION
            self.begin = self.active_dataX[self.selected_x].iloc[0]
            self.end = self.active_dataX[self.selected_x].iloc[-1]
            self.begin_widget.setDisabled(True)
            self.end_widget.setDisabled(True)
        else:
        '''            
        self.begin = float(self.begin_widget.text())
        self.end = float(self.end_widget.text())
        #self.begin_widget.setEnabled(True)
        #self.end_widget.setEnabled(True)

        self.timestamper.set_init_time(self.begin)
        #self.timestamper.set_max_time(self.end)
        self.begin_widget.setText(str(int(self.begin)))
        self.end_widget.setText(str(int(self.end)))
        self._plot_ref.axes.set_xlim(self.begin, self.end)
        self.plot_widget.draw()

        self.trim_connections = []
        self.trim_connections.append(self.begin_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.end_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.timestamper.slider.valueChanged.connect(self.slider_trim_graph))
        


    def slider_trim_graph(self):
        print("slider trim")
        try:
            self.begin_widget.textChanged.disconnect(self.trim_graph)
            self.end_widget.textChanged.disconnect(self.trim_graph)
            self.timestamper.slider.valueChanged.disconnect(self.slider_trim_graph)
            self.trim_connections = []
        except Exception as e:
            print("Could not disconnect all connections" + str(e))

        self.begin = float(self.timestamper.slider.value() * (self.timestamper.max_time / 100))
        self.end = float(self.begin + 100)
        self.timestamper.set_init_time(self.begin)
        #self.timestamper.set_max_time(self.end)
        self.begin_widget.setText(str(int(self.begin)))
        self.end_widget.setText(str(int(self.end)))
        self._plot_ref.axes.set_xlim(self.begin, self.end)
        self.plot_widget.draw()

        self.trim_connections = []
        self.trim_connections.append(self.begin_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.end_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.timestamper.slider.valueChanged.connect(self.slider_trim_graph))


    def click_trim(self):
        """When called, click_trim() is responsible for adjusting the visible range of data, by about 10%. It zooms in if left click or zooms out if right click"""
        if (
            self.begin_widget.text() == ""
            or self.end_widget.text() == ""
            #or self.autofit_widget.isChecked()
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
        self.animation_ongoing = True
        try:
            if hasattr(self, "ani") and self.ani.event_source != None:
                self.ani.resume()
                return
            self.ani = animation.FuncAnimation(
                self.plot_widget.fig,
                self.animate,
                frames=self.timestamper.time_generator,
                interval=50,
                repeat=True,
                save_count=50,
                cache_frame_data=True,
            )
            self.plot_widget.draw()
        except Exception as e:
            self.plot_graph()
            print("Error re-drawing graph: " + str(e))
        self.animation_ongoing = False
       

    def animate(self, timestamp):
        """Helper for the animation, adds new data points to X and Y data lists, clears the existing plot, and then re-plots the updated data with new labels, a title, and a grid.
        WARNING: use of plot() could be better than draw(), but we made it necessary that the function will use plot() because of adding to the active x and y datasets
        """
        ###allows modifying of labels without calling trim graph
        ##### also i wanted to move this into play_graph() but didnt work so its here.
        print("timestamp fed into animate: " + str(timestamp))
        try:
            print("removing connections")
            self.begin_widget.textChanged.disconnect(self.trim_graph)
            self.end_widget.textChanged.disconnect(self.trim_graph)
            self.timestamper.slider.valueChanged.disconnect(self.slider_trim_graph)
            self.trim_connections = []
        except Exception as e:
            print("Error disconnecting from trim_graph " + str(e))

        try:
            activeXY = self.active_dataX[
                (self.active_dataX.iloc[:, 0] >= 0)
                & (self.active_dataX.iloc[:, 0] <= timestamp)
            ][[self.selected_x, self.selected_y]]
            self.plot_widget.activeXY[0] = activeXY[self.selected_x].tolist()
            self.plot_widget.activeXY[1] = activeXY[self.selected_y].tolist()
            self.plot_widget.ax1.clear()
            plotrefs = self.plot_widget.ax1.plot(
                self.plot_widget.activeXY[0], self.plot_widget.activeXY[1]
            )

            self._plot_ref = plotrefs[0]
            self.plot_widget.ax1.set_xlabel(self.selected_x)
            self.plot_widget.ax1.set_ylabel(self.selected_y)
            ###added max so timestamp does not set below 1, not sure for upper bound but thats a problem for later
            self.plot_widget.ax1.set_xlim(max(1, timestamp - 100), max(2, timestamp))
            print("xlim min: " + str(max(1, timestamp - 100)) + "; xlim max: " + str(max(2, timestamp)))
            self.begin_widget.setText(str(int(self.plot_widget.ax1.get_xlim()[0])))
            self.end_widget.setText(str(int(self.plot_widget.ax1.get_xlim()[1])))
            # self.plot_widget.ax1.legend()
            self.plot_widget.ax1.set_title(self.selected_x + " vs " + self.selected_y)
            self.plot_widget.ax1.grid()
        except Exception as e:
            print("Error animating graph: " + str(e))


        #self.trim_connections = []
        print("reconnecting connections")
        self.trim_connections = []
        self.trim_connections.append(self.begin_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.end_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.timestamper.slider.valueChanged.connect(self.slider_trim_graph))



    def pause_graph(self):
        """Pauses the graph animation"""
        try:
            self.ani.pause()
            self.animation_ongoing = False
        except Exception as e:
            print("Error pausing graph " + str(e))
        ###Need to re-establish connections after pause
        try:
            self.begin_widget.textChanged.disconnect(self.trim_graph)
            self.end_widget.textChanged.disconnect(self.trim_graph)
            self.timestamper.slider.valueChanged.disconnect(self.slider_trim_graph)
            self.trim_connections = []
        except Exception as e:
            print("Could not disconnect all connections" + str(e))
        self.trim_connections = []
        self.trim_connections.append(self.begin_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.end_widget.textChanged.connect(self.trim_graph))
        self.trim_connections.append(self.timestamper.slider.valueChanged.connect(self.slider_trim_graph))

    def get_info(self):
        """Returns value of self.x_set, the combobox for selecting the current dataset or csv. additionally it returns the current x and y columns"""
        return self.x_set.currentText(), self.selected_x, self.selected_y

    ''' DOESNT WORK THOUGH IMPLEMENTATION IS ADVANTAGEOUS
    def add_connection(self, signal, slot):
        for connection in self.trim_connections:
            if connection.signal == signal and connection.receiver == slot:
                return 

        new_connection = signal.connect(slot)
        self.trim_connections.append(new_connection)
    '''

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
        self.reset_button = QPushButton("Reset", self.central_widget)
        self.reset_button.clicked.connect(self.reset)
        self.footer = QStatusBar()
        self.setStatusBar(self.footer)
        self.footer.addWidget(self.reset_button)
        sideBoxLayout.addWidget(self.add_dataset_button)

        collapsible_container = Collapsible()
        collapsible_container.setContentLayout(sideBoxLayout)
        self.layout.addWidget(collapsible_container)
        # self.layout.addLayout(sideBoxLayout)

        # self.plot_button.clicked.connect(self.plot_graph)

    def reset(self):
        self.pause_graph()
        self.setChooser.set_active_data()
        self.setChooser.plot_graph()

    def play_graph(self):
        self.setChooser.play_graph()

    def pause_graph(self):
        self.setChooser.pause_graph()

    def add_dataset(self):
        """Function called when 'Add Dataset' button is clicked, creates a new sidebox to add to the existing sidebox"""
        setChooser = DatasetChooser(
            self.central_widget, self.plot_widget, self.timestamper
        )
        self.data_set.append(setChooser)
        sideBoxLayout = QVBoxLayout()
        sidebox, sidebox1 = setChooser.get_scroll_areas_without_trim()
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