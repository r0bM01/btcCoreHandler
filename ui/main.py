



import lib.client
import sys, time, random, json
from PySide6.QtCore import Qt 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout,
                            QHBoxLayout, QGroupBox, QTextEdit )

#import lib.network


ALL_CSS = """
QPushButton {
    /*border-radius: 4px;*/
    /*border: 1px solid white;*/
    /*background-color: #3396ff;*/
    font: bold 18px;
    height: 40px;
}
/*
QPushButton:hover {
    background-color: #33acff;
}*/

"""

class LeftMenu(QWidget):
    def __init__(self):
        super().__init__()

        

        self.layout = QVBoxLayout()

        self.labelTitle = QLabel()
        img = QPixmap("ui/assets/bitcoin_64.png")
        self.labelTitle.setPixmap(img)
        
        self.labelTitle.setAlignment(Qt.AlignBottom | Qt.AlignCenter)

        self.STATUS = QPushButton()
        self.STATUS.setText("Status")

        self.NETWORK = QPushButton()
        self.NETWORK.setText("Network")

        self.ADVANCED = QPushButton()
        self.ADVANCED.setText("Advanced")
        self.ADVANCED.setIcon(QIcon("ui/assets/advanced_32.png"))

        self.OPTIONS = QPushButton()
        self.OPTIONS.setText("Options")

        self.labelVersion = QLabel()
        self.labelVersion.setText("0.0.1 Alpha")

        self.layout.addWidget(self.labelTitle)
        self.layout.addStretch(1)
        self.layout.addWidget(self.STATUS)
        self.layout.addWidget(self.NETWORK)
        self.layout.addWidget(self.ADVANCED)
        self.layout.addWidget(self.OPTIONS)
        self.layout.addStretch(1)
        self.layout.addWidget(self.labelVersion)
        #self.setStyleSheet("QPushButton:hover { background-color: #a9b0b6; border: 1px solid }")
        self.setProperty("class", ["left-menu"])


class Status(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.GROUP = QGroupBox("SERVER DEBUG")

        debugLayout = QVBoxLayout()
        self.debugResult = QTextEdit()
        self.debugResult.setReadOnly(True)
        debugLayout.addWidget(self.debugResult)

        self.GROUP.setLayout(debugLayout)

        self.layout.addWidget(self.GROUP)

        self.setProperty("class", ["status"])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(640, 500)
        self.mainLayout = QHBoxLayout()

        self.left_Menu = LeftMenu()
        self.status_Page = Status()

        self.mainLayout.addLayout(self.left_Menu.layout, 1)
        self.mainLayout.addLayout(self.status_Page.layout, 3)

        

        container = QWidget()
        container.setLayout(self.mainLayout)
        self.setCentralWidget(container)

        self.left_Menu.STATUS.clicked.connect(self.start_updater)
        
        self.CLIENT = lib.client.Client()
        self.CLIENT.initConnection()
        self.status_Page.debugResult.append(f"client connected: {self.CLIENT.network.isConnected}")
        self.CLIENT.initHashedCalls()

    def start_updater(self):
        if not self.CLIENT.updaterIsRunning:
            self.CLIENT.autoUpdater.start()
            self.status_Page.debugResult.append("loop started")
        else:
            self.CLIENT.updaterIsRunning = False
            self.status_Page.debugResult.append("loop stopped")

app = QApplication(sys.argv)
app.setStyleSheet(ALL_CSS)

window = MainWindow()
window.show()

app.exec_()

