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
import ui.assets.css
import ui.pages.alerts
import ui.pages.left_menu
import ui.pages.status
import ui.pages.options
import ui.pages.network
import ui.pages.advanced
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
        self.mainLayout = QHBoxLayout()
        #self.setStyleSheet("background-color: #2c3746;")

        self.alerts = ui.pages.alerts.Alerts()
        
        self.PAGES = {}
        self.init_pages()
        self.init_left_menu()

        self.mainLayout.addWidget(self.MENU)
        [self.mainLayout.addWidget(self.PAGES[key]) for key in self.PAGES]

        container = QWidget()
        container.setLayout(self.mainLayout)
        self.setCentralWidget(container)

        self.CLIENT = lib.client.Client()
        self.commandEvent = threading.Event()

    def init_pages(self):
        self.PAGES['STATUS'] = ui.pages.status.Status()
        self.PAGES['STATUS'].BUTTON['connect'].clicked.connect(self.handle_connection)
        self.PAGES['STATUS'].setVisible(True)
    
        self.PAGES['OPTIONS'] = ui.pages.options.Options()   
        self.PAGES['OPTIONS'].setVisible(False)

        self.PAGES['NETWORK'] = ui.pages.network.Network()
        self.PAGES['NETWORK'].BUTTON['peerslist'].clicked.connect(lambda x: self.PAGES['NETWORK'].open_peers_list(self.CLIENT.peersInfo, self.CLIENT.peersGeolocation))
        self.PAGES['NETWORK'].setVisible(False)

        self.PAGES['ADVANCED'] = ui.pages.advanced.Advanced()
        self.PAGES['ADVANCED'].BUTTON['command'].clicked.connect(self.send_advanced_command)
        self.PAGES['ADVANCED'].setVisible(False)
        #self.ADVANCED.setStyleSheet("QPushButton { border: 0px; }")

    def init_left_menu(self):
        self.MENU = ui.pages.left_menu.LeftMenu(self.PAGES)
        self.MENU.setVisible(True)
    

    def handle_connection(self):
        if not self.CLIENT.network.isConnected: 
            IPaddress = self.PAGES['OPTIONS'].hostEdit.text()
            if IPaddress: 
                self.CLIENT.initConnection(IPaddress) #self.CLIENT.initConnection(self.groupConnLEdit.text()) # gets ip address from line edit in status
                self.commandEvent.set()
                self.refreshThread = threading.Thread(target = self.refreshAll, daemon = True)
                self.refreshThread.start()
            else:
                self.alerts.missingIPAddress()
        else:
            self.CLIENT.closeConnection()
            self.alerts.disconnectedNode()
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
                self.CLIENT.getPeersGeolocation()
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
            self.PAGES['STATUS'].BUTTON['connect'].setText("Connect")
            self.PAGES['STATUS'].setDefault()
            self.PAGES['NETWORK'].setDefault()
            


    def writeStatusInfo(self):
        if self.CLIENT.statusInfo:
            #adds the data to the status result
            self.PAGES['STATUS'].write_result(self.CLIENT.statusInfo, self.CLIENT.systemInfo, self.CLIENT.peersGeolocation)
            self.PAGES['NETWORK'].write_result(self.CLIENT.statusInfo, self.CLIENT.peersGeolocation)
        else:
            self.PAGES['STATUS'].setDefault()


    def writePeersInfo(self):
        # self.CLIENT.getPeersInfo()
        if self.CLIENT.peersInfo:
            pass

        else:
            self.PAGES['NETWORK'].setDefault()
    

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



#




app = QApplication(sys.argv)
app.setStyleSheet(ui.assets.css.ALL_CSS)

window = MainWindow()
window.show()
sys.exit(app.exec_())


