



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
        self.labelTitle.setPixmap(QPixmap("ui/assets/bitcoin_64.png"))
        self.labelTitle.setAlignment(Qt.AlignBottom | Qt.AlignCenter)

        self.STATUS = QPushButton("Status")
        self.NETWORK = QPushButton("Network")
        self.ADVANCED = QPushButton("Advanced")
        self.OPTIONS = QPushButton("Options")

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


class Advanced(QWidget):
    def __init__(self):
        super().__init__()
        self.lbCommand = QLabel()
        self.lbCommand.setText("Command: ")
        self.lnCommand = QLineEdit()

        self.btClear = QPushButton()
        self.btClear.setText("Clear")
        self.btCommand = QPushButton()
        self.btCommand.setText("Send")

        self.btLayout = QHBoxLayout()
        self.btLayout.addWidget(self.btClear)
        self.btLayout.addWidget(self.btCommand)

        self.layout = QFormLayout()
        self.layout.addRow(self.lbCommand, self.lnCommand)
        self.layout.addRow(self.btLayout)


class Status(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGroupBox("SERVER DEBUG")

        self.debugLayout = QVBoxLayout()
        self.debugResult = QTextEdit()
        self.debugResult.setReadOnly(True)
        self.debugLayout.addWidget(self.debugResult)

        self.layout.setLayout(self.debugLayout)


        self.setProperty("class", ["status"])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(640, 500)
        self.mainLayout = QHBoxLayout()

        self.STATUS = Status()
        self.STATUS.setVisible(True)

        self.ADVANCED = Advanced()
        self.STATUS.setVisible(False)


        self.leftMenu = LeftMenu()
        self.leftMenu.setFixedWidht(100)
        self.centralPage = QWidget()
        self.centralPage.addWidget(self.STATUS)
        self.centralPage.addWidget(self.ADVANCED)

        self.mainLayout.addWidget(self.leftMenu)
        self.mainLayout.addWidget(self.centralPage)
        
        container = QWidget()
        container.setLayout(self.mainLayout)
        self.setCentralWidget(container)

        
        
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
    
    def openAdvanced(self):
        self.STATUS.setVisible(False)
        self.ADVANCED.setVisible(True)

app = QApplication(sys.argv)
app.setStyleSheet(ALL_CSS)

window = MainWindow()
window.show()

app.exec_()

