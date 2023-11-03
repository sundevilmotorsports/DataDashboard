import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QAbstractAnimation, QParallelAnimationGroup
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QToolButton, QFrame, QScrollArea, QSizePolicy


class Collapsible(QWidget):
    def __init__(self, title="", animationDuration=300, parent=None):
        super().__init__(parent)
        self.animationDuration = animationDuration

        self.mainLayout = QVBoxLayout()
        self.horizontalLayout = QHBoxLayout()
        self.toggleButton = QToolButton()
        self.headerLine = QFrame()
        self.toggleAnimation = QParallelAnimationGroup()
        self.contentArea = QScrollArea()

        self.initUI(title)

    def initUI(self, title):

        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.setText(title)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(True)

        self.headerLine.setFrameShape(QFrame.HLine)
        self.headerLine.setFrameShadow(QFrame.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.contentArea.setMaximumWidth(0)
        self.contentArea.setMinimumHeight(0)
        self.contentArea.setMinimumWidth(10)
        self.contentArea.show()

        for _ in range(3):
            self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumWidth"))
            self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumWidth"))
        
        #self.mainLayout.setSpacing(0)
        #self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.toggleButton)
        #self.mainLayout.addWidget(self.headerLine)
        #self.mainLayout.addWidget(self.contentArea)
        

        #horizontalLayout.addWidget(self.toggleButton)
        #horizontalLayout.addWidget(self.headerLine)
        self.horizontalLayout.addWidget(self.contentArea)
        self.mainLayout.addLayout(self.horizontalLayout)

        self.setLayout(self.mainLayout)
        #self.setLayout(horizontalLayout)

        self.toggleButton.clicked.connect(self.onToggle)

    def setContentLayout(self, contentLayout):
        # Check if there is an existing layout
        if self.contentArea.layout():
            self.contentArea.layout().deleteLater()

        # Set the new content layout
        self.contentArea.setLayout(contentLayout)
        self.contentArea.setMaximumWidth(contentLayout.sizeHint().width())
        #self.contentArea.setMaximumHeight(contentLayout.sizeHint().height())
        self.contentArea.setMaximumHeight(900)
        
        # Rest of the method remains the same
        #collapsedWidth = self.sizeHint().width() - self.contentArea.maximumWidth()
        collapsedWidth = 50
        contentWidth = contentLayout.sizeHint().width()          

        for i in range(self.toggleAnimation.animationCount() - 1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedWidth)
            spoilerAnimation.setEndValue(collapsedWidth + contentWidth)

        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentWidth)
        self.contentArea.update()


    def onToggle(self):
        checked = self.toggleButton.isChecked()
        if (checked):
            self.contentArea.show()
        else:
            self.contentArea.hide()

        self.toggleButton.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.toggleAnimation.setDirection(QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward)
        self.toggleAnimation.start()