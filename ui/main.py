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


import lib.client.client
import lib.shared.storage
import ui.assets.css
import ui.widgets.alerts
import ui.widgets.left_menu
import ui.widgets.status
import ui.widgets.options
import ui.widgets.network
import ui.widgets.advanced
import ui.utils as utils
import sys, time, random, json, threading, queue
from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout, QHeaderView,
                            QHBoxLayout, QGroupBox, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem )





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bitcoin Core Handler")
        self.setFixedSize(640, 500)
        appIcon = QIcon(QPixmap("ui/assets/bitcoin_64.png"))
        self.setWindowIcon(appIcon)
        self.mainLayout = QHBoxLayout()
        #self.setStyleSheet("background-color: #2c3746;")

        self.alerts = ui.widgets.alerts.Alerts()

        self.storage = lib.shared.storage.Client()
        self.certificate = self.init_certificate()

        self.CLIENT = lib.client.client.Client(self.certificate)
        
        self.PAGES = {}
        self.init_pages()
        self.init_left_menu()

        self.mainLayout.addWidget(self.MENU)
        [self.mainLayout.addWidget(self.PAGES[key]) for key in self.PAGES]

        container = QWidget()
        container.setLayout(self.mainLayout)
        self.setCentralWidget(container)

        
        self.commandEvent = threading.Event()
    
    def init_certificate(self):
        if not self.storage.check_base_dir(): self.storage.init_dir(self.saveDir)
        certificate = self.storage.init_certificate()
        if not bool(certificate): self.alerts.missingCertificate
        return certificate

    def init_pages(self):
        self.PAGES['STATUS'] = ui.widgets.status.Status()
        self.PAGES['STATUS'].BUTTON['connect'].clicked.connect(self.handle_connection)
        self.PAGES['STATUS'].setVisible(True)
    
        self.PAGES['OPTIONS'] = ui.widgets.options.Options()   
        self.PAGES['OPTIONS'].setVisible(False)

        self.PAGES['NETWORK'] = ui.widgets.network.Network()
        self.PAGES['NETWORK'].BUTTON['peerslist'].clicked.connect(lambda x: self.PAGES['NETWORK'].open_peers_list(self.CLIENT.connectedInfo))
        self.PAGES['NETWORK'].BUTTON['addnodes'].clicked.connect(lambda x: self.PAGES['NETWORK'].open_added_list(self.send_addednode_call))
                                                                 
        self.PAGES['NETWORK'].setVisible(False)

        self.PAGES['ADVANCED'] = ui.widgets.advanced.Advanced()
        self.PAGES['ADVANCED'].BUTTON['command'].clicked.connect(self.send_advanced_command)
        self.PAGES['ADVANCED'].edit['command'].returnPressed.connect(self.send_advanced_command)
        self.PAGES['ADVANCED'].BUTTON['clear'].clicked.connect(lambda x: self.PAGES['ADVANCED'].RESULT['command'].clear())
        self.PAGES['ADVANCED'].setVisible(False)
        #self.ADVANCED.setStyleSheet("QPushButton { border: 0px; }")

    def init_left_menu(self):
        self.MENU = ui.widgets.left_menu.LeftMenu(self.PAGES)
        self.MENU.BUTTON['version'].setText(self.CLIENT.version)
        self.MENU.BUTTON['version'].clicked.connect(self.alerts.showRelease)
        self.MENU.setVisible(True)
    

    def handle_connection(self):
        if not self.CLIENT.network.isConnected: 
            IPaddress = self.PAGES['OPTIONS'].hostEdit.text()
            if IPaddress: 
                self.CLIENT.initConnection(IPaddress) #self.CLIENT.initConnection(self.groupConnLEdit.text()) # gets ip address from line edit in status
                if self.CLIENT.network.isConnected:
                    self.commandEvent.set()
                    self.refreshThread = threading.Thread(target = self.refreshAll, daemon = True)
                    self.refreshThread.start()
                else:
                    self.alerts.connectionFailed()
            else:
                self.alerts.missingIPAddress()
        else:
            self.CLIENT.closeConnection()
            self.alerts.disconnectedNode()
            # self.refreshThread.join()
        self.refreshConnectionStatus()
        self.writeStatusInfo()
            
    def refreshAll(self):
        while self.CLIENT.network.isConnected and self.CLIENT.bitcoindRunning:
            self.refreshConnectionStatus() #always check the connection status
            timeNow = time.time()
            if (timeNow - self.CLIENT.lastPeersUpdate) > 120:
                self.commandEvent.wait(10)
                # self.CLIENT.getPeersInfo()
                # self.CLIENT.getPeersGeolocation()
                self.CLIENT.getConnectedInfo()
            
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
            self.PAGES['STATUS'].RESULT['node'].setText("succesfully connected") # self.PAGES['OPTIONS'].hostEdit.text()
            self.PAGES['STATUS'].BUTTON['connect'].setText("Disconnect")
            self.PAGES['NETWORK'].openList.setEnabled(True)
        else:
            self.PAGES['OPTIONS'].setEnabled(True)
            self.PAGES['STATUS'].BUTTON['connect'].setText("Connect")
            self.PAGES['STATUS'].setDefault()
            self.PAGES['STATUS'].RESULT['node'].setText("not connected")
            self.PAGES['NETWORK'].setDefault()
            self.PAGES['NETWORK'].openList.setEnabled(False)
            


    def writeStatusInfo(self):
        if not self.CLIENT.bitcoindRunning: self.alerts.bitcoindFailed()
        if self.CLIENT.bitcoindRunning and self.CLIENT.statusInfo:
            #adds the data to the status result
            self.PAGES['STATUS'].write_result(self.CLIENT.statusInfo, self.CLIENT.systemInfo, self.CLIENT.connectedInfo)
            self.PAGES['NETWORK'].write_result(self.CLIENT.statusInfo)
        else:
            self.PAGES['STATUS'].setDefault()
            self.PAGES['NETWORK'].setDefault()
            
    def send_addednode_call(self, nodeAddress, nodeCommand):
        self.commandEvent.clear()
        reply = self.CLIENT.addnodeCall(nodeAddress, nodeCommand)
        self.commandEvent.set()
        return reply


    def send_advanced_command(self):
        insertedCommand = self.PAGES['ADVANCED'].edit['command'].text()
        fullCommand = insertedCommand.lower().split(" ", 1)
        command = fullCommand[0]
        if command != "start" and command != "stop":
            arg = fullCommand[1] if len(fullCommand) > 1 else False
            self.commandEvent.clear() #blocks the updater until advanced commmand has sent a request and received an answer
            reply = self.CLIENT.advancedCall(command, arg)
            self.commandEvent.set() # updater can now restart
            self.PAGES['ADVANCED'].RESULT['command'].append(utils.convertToPrintable(reply))
        else:
            self.PAGES['ADVANCED'].RESULT['command'].append("error: control commands not allowed")



app = QApplication(sys.argv)
app.setStyleSheet(ui.assets.css.ALL_CSS)

window = MainWindow()
window.show()
sys.exit(app.exec_())


