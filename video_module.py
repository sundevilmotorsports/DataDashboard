import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtWidgets import QStatusBar, QFileDialog
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon
import math

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Video Player")
        """self.setFixedWidth(250)
        self.setFixedHeight(250)"""
        self.setWindowIcon(QIcon("90129757.jpg"))

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()  # Use QVideoWidget to display video
        self.media_player.setVideoOutput(self.video_widget)

        self.layout.addWidget(self.video_widget, 5)

        self.control_layout = QVBoxLayout()
        self.layout.addLayout(self.control_layout)

        self.open_button = QPushButton("Open Video")
        self.play_button = QPushButton("Play")
        #self.open_button.setGeometry(0,0,500,100)
        self.slider = QSlider(Qt.Horizontal)
        self.status_bar = QStatusBar()

        self.control_layout.addWidget(self.open_button)
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.slider)

        self.layout.addWidget(self.status_bar)


        self.timestamp = QLabel()
        self.layout.addWidget(self.timestamp)
        self.media_player.positionChanged.connect(self.updateTimestampLabel)
        

        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)

        self.open_button.clicked.connect(self.openFile)
        self.play_button.clicked.connect(self.play)
        self.slider.sliderMoved.connect(self.setPosition)

        self.play_button.setEnabled(False)
        self.slider.setEnabled(False)
        #self.status_bar.showMessage("No Media")

    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv);;All Files (*)", options=options)

        if file_name:
            media = QMediaContent(QUrl.fromLocalFile(file_name))
            self.media_player.setMedia(media)
            self.play_button.setEnabled(True)
            self.slider.setEnabled(True)
            #self.video_widget.resize(500,500)
            #self.status_bar.showMessage(file_name)

    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediaStateChanged(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")

    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)

    def setPosition(self, position):
        self.media_player.setPosition(position)

    def updateTimestampLabel(self):
        self.timestamp.setText(str(int(self.media_player.position()/3600000))  + ":" + str(int(self.media_player.position()/60000)%60).zfill(2) + ":" + str(math.ceil(self.media_player.position()/1000)%60).zfill(2))

"""if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())"""



'''
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.videoplayer import VideoPlayer

class Video(MDApp):
    title = "test video"

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        player = VideoPlayer(source="C:/Users/ryans/Downloads/minions.mp4")

        player.state = "play"

        player.options = {"eos": "pause"}

        player.allow_stretch = True

        return player

if __name__ == "__main__":
    Video().run()
'''







