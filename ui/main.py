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


import lib.client
#import ui.pages.advanced
import ui.pages.status
import ui.pages.options
import ui.pages.network
import ui.utils as utils
import sys, time, random, json, threading, queue
from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout, QHeaderView,
                            QHBoxLayout, QGroupBox, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem )

#import lib.network


ALL_CSS = """
.left-menu {
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




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bitcoin Core Handler")
        self.setFixedSize(640, 500)
        self.mainLayout = QHBoxLayout()

        self.PAGES = {}

        self.init_left_menu()
        self.init_status()
        self.init_network()
        self.init_advanced()
        self.init_options()

        self.mainLayout.addWidget(self.MENU)
        self.mainLayout.addWidget(self.PAGES['STATUS'])
        self.mainLayout.addWidget(self.PAGES['NETWORK'])
        self.mainLayout.addWidget(self.PAGES['ADVANCED'])
        self.mainLayout.addWidget(self.PAGES['OPTIONS'])
        
        container = QWidget()
        container.setLayout(self.mainLayout)
        self.setCentralWidget(container)

        self.CLIENT = lib.client.Client()

        self.commandEvent = threading.Event()

    def handle_connection(self):
        if not self.CLIENT.network.isConnected: 
            self.CLIENT.initConnection(self.PAGES['OPTIONS'].hostEdit.text()) #self.CLIENT.initConnection(self.groupConnLEdit.text()) # gets ip address from line edit in status
            self.commandEvent.set()
            self.refreshThread = threading.Thread(target = self.refreshAll, daemon = True)
            self.refreshThread.start()
        else:
            self.CLIENT.closeConnection()
            # self.refreshThread.join()
        self.refreshConnectionStatus()
        self.writeStatusInfo()
        self.writePeersInfo()
            
    def refreshAll(self):
        while self.CLIENT.network.isConnected:
            self.refreshConnectionStatus() #always check the connection status
            timeNow = time.time()
            if (timeNow - self.CLIENT.lastPeersUpdate) > 120:
                self.commandEvent.wait(10)
                self.CLIENT.getPeersInfo()
                self.writePeersInfo()
            
            if (timeNow - self.CLIENT.lastStatusUpdate) > 60:
                self.commandEvent.wait(10)
                self.CLIENT.getStatusInfo()
                self.writeStatusInfo()
                
            if (timeNow - self.CLIENT.lastConnCheck) > 30:
                self.commandEvent.wait(10)
                self.CLIENT.keepAlive()
                
            time.sleep(5)
        

    def refreshConnectionStatus(self):
        if self.CLIENT.network.isConnected:
            self.PAGES['OPTIONS'].setEnabled(False)
            self.PAGES['STATUS'].RESULT['nodeip'].setText(self.PAGES['OPTIONS'].hostEdit.text())
            self.PAGES['STATUS'].BUTTON['connect'].setText("Disconnect")
        else:
            self.PAGES['OPTIONS'].setEnabled(True)
            self.PAGES['STATUS'].setStatusDefault()
            self.PAGES['STATUS'].BUTTON['connect'].setText("Connect")


    def writeStatusInfo(self):
        # self.CLIENT.getStatusInfo()
        # job = {'func': self.CLIENT.getStatusInfo, 'args': False}
        # self.JOBS.put(job)
        if self.CLIENT.statusInfo:
            #adds the data to the status result
            self.PAGES['STATUS'].write_result(self.CLIENT.statusInfo, self.CLIENT.systemInfo, self.CLIENT.peersGeolocation)
            self.PAGES['NETWORK'].write_result(self.CLIENT.statusInfo, self.CLIENT.peersGeolocation)
        else:
            self.PAGES['STATUS'].setStatusDefault()

    """
    def refreshNetworkInfo(self):
        self.CLIENT.getNetworkStats()
        if self.CLIENT.networkStats:
            self.lastUpdate = time.time()
            for key, value in self.statsResult.items():
                self.statsResult[key].setText(str(self.CLIENT.networkStats[key]))
    """

    def writePeersInfo(self):
        # self.CLIENT.getPeersInfo()
        if self.CLIENT.peersInfo:
            pass
            """
            self.peersTable.setRowCount(len(self.CLIENT.peersInfo))
            rowCounter = 0
            for peer in self.CLIENT.peersInfo:
                typeC = 'Inbound' if peer['inbound'] else 'Outbound'
                self.peersTable.setItem(rowCounter, 0, QTableWidgetItem(str(peer['id'])))
                self.peersTable.setItem(rowCounter, 1, QTableWidgetItem(str(peer['addr'])))
                self.peersTable.setItem(rowCounter, 2, QTableWidgetItem(typeC))
                #self.peersTable.setItem(rowCounter, 3, QTableWidgetItem(peer['subversion']))
                rowCounter += 1
            """
        else:
            self.setNetworkDefault()
    

    def init_status(self):
        self.PAGES['STATUS'] = ui.pages.status.Status()
        self.PAGES['STATUS'].BUTTON['connect'].clicked.connect(self.handle_connection)
        self.PAGES['STATUS'].setVisible(True)
    
    def init_options(self):
        self.PAGES['OPTIONS'] = ui.pages.options.Options()   
        self.PAGES['OPTIONS'].setVisible(False)

    def init_network(self):
        self.PAGES['NETWORK'] = ui.pages.network.Network()
        self.PAGES['NETWORK'].setVisible(False)



    def init_left_menu(self):
        self.MENU = QWidget()

        MENUlayout = QVBoxLayout()
        labelTitle = QLabel()
        labelTitle.setPixmap(QPixmap("ui/assets/bitcoin_64.png"))
        labelTitle.setAlignment(Qt.AlignBottom | Qt.AlignCenter)

        self.btSTATUS = QPushButton("Status")
        self.btSTATUS.clicked.connect(lambda x: self.menu_buttons("STATUS"))
        self.btNETWORK = QPushButton("Network")
        self.btNETWORK.clicked.connect(lambda x: self.menu_buttons("NETWORK"))
        self.btADVANCED = QPushButton("Advanced")
        self.btADVANCED.clicked.connect(lambda x: self.menu_buttons("ADVANCED"))
        self.btOPTIONS = QPushButton("Options")
        self.btOPTIONS.clicked.connect(lambda x: self.menu_buttons("OPTIONS"))

        labelVersion = QLabel()
        labelVersion.setText("0.0.1 Alpha")
        #labelVersion.clicked.connect(QMessageBox.information(self, "Info", "Version 0.0.1 coded by R0bm01"))

        MENUlayout.addWidget(labelTitle)
        MENUlayout.addWidget(self.btSTATUS)
        MENUlayout.addWidget(self.btNETWORK)
        MENUlayout.addWidget(self.btADVANCED)
        MENUlayout.addWidget(self.btOPTIONS)
        MENUlayout.addStretch(1)
        MENUlayout.addWidget(labelVersion)
        #self.setStyleSheet("QPushButton:hover { background-color: #a9b0b6; border: 1px solid }")
        

        self.MENU.setLayout(MENUlayout)
        self.MENU.setStyleSheet("QPushButton { font: bold 18px; height: 40px; }")
        self.MENU.setFixedWidth(200)



    def init_advanced(self):
        self.PAGES['ADVANCED'] = QWidget()

        
        ADVANCEDlayout = QVBoxLayout()

        commandForm = QHBoxLayout()
        #commandLabel = QLabel("command: ")
        commandLabel = QLabel("command:")
        self.commandLine = QLineEdit()
        self.commandButton = QPushButton()
        self.commandButton.setIcon(QPixmap("ui/assets/play_32.png"))
        self.commandButton.setFixedWidth(35)
        self.commandButton.clicked.connect(self.send_advanced_command)
        
        commandForm.addWidget(commandLabel)
        commandForm.addWidget(self.commandLine)
        commandForm.addWidget(self.commandButton)

        self.debugLog = QTextEdit()
        self.debugLog.setReadOnly(True)

        ADVANCEDlayout.addLayout(commandForm)
        ADVANCEDlayout.addWidget(self.debugLog)

        self.PAGES['ADVANCED'].setLayout(ADVANCEDlayout)
        self.PAGES['ADVANCED'].setVisible(False)
        #self.ADVANCED.setStyleSheet("QPushButton { border: 0px; }")
    
    
    def setNetworkDefault(self):
        for key, value in self.statsResult.items():
            self.statsResult[key].setText(" - ")

    def menu_buttons(self, button):
        for key, value in self.PAGES.items():
            self.PAGES[key].setVisible(True) if key == button else self.PAGES[key].setVisible(False)
        

    def send_advanced_command(self):
        insertedCommand = self.commandLine.text()
        fullCommand = insertedCommand.lower().split(" ", 1)
        command = fullCommand[0]
        if command != "start" and command != "stop":
            arg = fullCommand[1] if len(fullCommand) > 1 else False
            self.commandEvent.clear() #blocks the updater until advanced commmand has sent a request and received an answer
            reply = self.CLIENT.advancedCall(command, arg)
            self.commandEvent.set() # updater can now restart
            self.debugLog.append(utils.convertToPrintable(reply))
        else:
            self.debugLog.append("error: control commands not allowed")

        
        
        


app = QApplication(sys.argv)
app.setStyleSheet(ALL_CSS)

window = MainWindow()
window.show()

app.exec_()

