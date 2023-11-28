# Copyright [2023] [R0BM01@pm.me]                                           #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License");           #
# you may not use this file except in compliance with the License.          #
# You may obtain a copy of the License at                                   #
#                                                                           #
# http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#############################################################################

import sys, time, random, json
from PySide2.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout,
                            QAction, QHBoxLayout, QGroupBox, QTextEdit, QFrame )
from PySide2.QtCore import Qt
import lib.network

class ConnectForm(QWidget):
    def __init__(self):
        super().__init__()


        self.lbHost = QLabel()
        self.lbHost.setText("Host: ")
        self.lbHost.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.lnHost = QLineEdit()
        self.lnHost.setText("192.168.1.238")
        

        self.btClear = QPushButton()
        self.btClear.setText("Clear")

        self.btConnect = QPushButton()
        self.btConnect.setText("Connect")

        self.btLayout = QHBoxLayout()
        self.btLayout.addWidget(self.btClear)
        self.btLayout.addWidget(self.btConnect)

        self.layout = QFormLayout()
        self.layout.addRow(self.lbHost, self.lnHost)
        self.layout.addRow(self.btLayout)


class CommandForm(QWidget):
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



class FileMenu(QMenu):
    def __init__(self):
        super().__init__()

        #self.fileMenu = QMenu()
        self.setTitle("File")


        self.addAction("Connect")

        settWdw = QAction("Settings", self)
        settWdw.triggered.connect(self.showSettings)
        self.addAction(settWdw)

        exitVoice = QAction("Exit", self)
        exitVoice.triggered.connect(self.exitProgram)
        self.addAction(exitVoice)


    def exitProgram(self):
        sys.exit()

    def showSettings(self):
        sts = SettingsWindow()
        sts.show()
        print("diocane")

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Setting")
        #self.setFixedSize(340, 220)
        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.CLIENT = lib.network.Client()

        self.setWindowTitle("btcCoreHandler")

        self.setFixedSize(640, 320)

        #fileMenu = FileMenu()
        self.mainMenu = QMenuBar()
        self.mainMenu.addMenu(FileMenu())


        #self.statusBar.showMessage("Disconnected")
        """
        FILE.addAction("Connect")
        FILE.addAction("Settings")
        FILE.addAction("Exit")
        """
        #self.statusBar = QStatusBar()

        #Widget drawings
        self.connector = ConnectForm()
        self.connector.btConnect.clicked.connect(self.handleConnection)


        self.commander = CommandForm()
        self.commander.btCommand.clicked.connect(self.sendCommand)
        self.commander.btClear.clicked.connect(self.showSettings)


        #widget signals
        #self.btCommand.clicked.connect(self.sendCommand)
        vlayout = QVBoxLayout()

        tlayout = QHBoxLayout()

        connectionBox = QGroupBox()
        connectionBox.setLayout(self.connector.layout)

        commandBox = QGroupBox("Commands:")
        commandBox.setLayout(self.commander.layout)

        resultBox = QGroupBox("Server:")
        resultBox.setAlignment(Qt.AlignLeft)
        self.rLabel = QTextEdit()
        self.rLabel.setReadOnly(True)
        resultBoxLayout = QVBoxLayout()
        resultBoxLayout.addWidget(self.rLabel)
        resultBox.setLayout(resultBoxLayout)


        tlayout.addWidget(connectionBox)
        tlayout.addWidget(commandBox)

        vlayout.addLayout(tlayout)
        vlayout.addWidget(resultBox)

        container = QWidget()
        container.setLayout(vlayout)

        self.setCentralWidget(container)

    def showSettings(self):
        self.sts = SettingsWindow()
        self.sts.show()
        print("diocane")

    def handleConnection(self):
        if self.CLIENT.isConnected:
            #self.CLIENT.remoteHost = self.lnHost.text()
            self.CLIENT.sender("closeconn")
            self.CLIENT.disconnectServer()
            self.connector.lnHost.setReadOnly(False)
            self.connector.lnHost.setEnabled(True)
            self.connector.btConnect.setText("Connect")
            self.rLabel.append(str(self.CLIENT.remoteSock))
        else:
            self.CLIENT.connectToServer()
            if self.CLIENT.remoteSock:
                self.connector.lnHost.setReadOnly(True)
                self.connector.lnHost.setEnabled(False)
                self.connector.btConnect.setText("Disconnect")
            self.rLabel.append(str(self.CLIENT.remoteSock))
            self.rLabel.append(f"Connected to server: {bool(self.CLIENT.remoteSock)}")

    def sendCommand(self):
        command = self.commander.lnCommand.text()
        self.CLIENT.sender(command)
        self.rLabel.append(f"Sent command: {command}")
        result = json.loads(self.CLIENT.receiver())
        self.rLabel.append("Reply from server: ")
        for key, value in result.items():
            self.rLabel.append(f"{str(key)}: {str(value)}")




app = QApplication(sys.argv)

window = MainWindow()
window.show()


app.exec_()
