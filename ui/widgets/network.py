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

import ui.widgets.peers_list
import ui.widgets.added_list
import ui.utils as utils
from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QFrame, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout, QHeaderView,
                            QHBoxLayout, QGroupBox, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem )



class Network(QWidget):
    def __init__(self):
        super().__init__()

        self.RESULT = {}
        self.BUTTON = {}
        self.edit = {}
        labels = {}

        layout = QVBoxLayout()

        networkStats = QGroupBox("Informations")
        networkStatsLayout = QHBoxLayout()

        leftForm = QFormLayout()
        labels['subversion'] = QLabel("Node Agent:")
        labels['totalbytessent'] = QLabel("Bytes Sent:")
        labels['totalbytesrecv'] = QLabel("Bytes Received:")

        rightForm = QFormLayout()
        labels['connections'] = QLabel("Connections:")
        labels['connections_in'] = QLabel("Inbound:")
        labels['connections_out'] = QLabel("Outbound:")


        for key, value in labels.items():
            self.RESULT[key] = QLabel(" - ")
            self.RESULT[key].setAlignment(Qt.AlignCenter)


        leftForm.addRow(labels['subversion'], self.RESULT['subversion'])
        leftForm.addRow(labels['totalbytessent'], self.RESULT['totalbytessent'])
        leftForm.addRow(labels['totalbytesrecv'], self.RESULT['totalbytesrecv'])

        rightForm.addRow(labels['connections'], self.RESULT['connections'])
        rightForm.addRow(labels['connections_out'], self.RESULT['connections_out'])
        rightForm.addRow(labels['connections_in'], self.RESULT['connections_in'])

        networkStatsLayout.addLayout(leftForm)
        networkStatsLayout.addLayout(rightForm)

        networkStats.setLayout(networkStatsLayout)



        nodeVersion = QGroupBox("Node Version")
        nodeVersionLayout = QVBoxLayout()
        self.RESULT['version'] = QLabel(" - ")
        self.RESULT['version'].setAlignment(Qt.AlignCenter)
        nodeVersionLayout.addWidget(self.RESULT['version'])
        nodeVersion.setLayout(nodeVersionLayout)

        protocol = QGroupBox("Protocol")
        protocolLayout = QVBoxLayout()
        self.RESULT['protocolversion'] = QLabel(" - ")
        self.RESULT['protocolversion'].setAlignment(Qt.AlignCenter)
        protocolLayout.addWidget(self.RESULT['protocolversion'])
        protocol.setLayout(protocolLayout)


        hashrate = QGroupBox("Hashrate")
        hashrateLayout = QVBoxLayout()
        self.RESULT['networkhashps'] = QLabel(" - ")
        self.RESULT['networkhashps'].setAlignment(Qt.AlignCenter)
        hashrateLayout.addWidget(self.RESULT['networkhashps'])
        hashrate.setLayout(hashrateLayout)

        difficulty = QGroupBox("Difficulty")
        difficultyLayout = QVBoxLayout()
        self.RESULT['difficulty'] = QLabel(" - ")
        self.RESULT['difficulty'].setAlignment(Qt.AlignCenter)
        difficultyLayout.addWidget(self.RESULT['difficulty'])
        difficulty.setLayout(difficultyLayout)

        centralWidgets = QHBoxLayout()
        centralWidgets.addWidget(nodeVersion)
        centralWidgets.addWidget(protocol)
        centralWidgets.addWidget(hashrate)
        centralWidgets.addWidget(difficulty)



        networksList = QGroupBox("Networks")
        networksListLayout = QFormLayout()
        netLabels = {}
        netLabels['ipv4'] = QLabel("IPv4:")
        netLabels['ipv6'] = QLabel("IPv6:")
        netLabels['onion'] = QLabel("ToR:")
        netLabels['i2p'] = QLabel("I2P:")
        netLabels['cjdns'] = QLabel("CJDNS:")

        for g in netLabels:
            self.RESULT[g] = QLabel(" - ")
            self.RESULT[g].setAlignment(Qt.AlignCenter)
            # self.RESULT[g].setFrameStyle(QFrame.Panel | QFrame.Raised)
            networksListLayout.addRow(netLabels[g], self.RESULT[g])
        
        networksList.setLayout(networksListLayout)

        self.openList = QGroupBox("Manage")
        openListLayout = QVBoxLayout()
        self.BUTTON['peerslist'] = QPushButton("Peers")
        self.BUTTON['bannedlist'] = QPushButton("Banned")
        self.BUTTON['addnodes'] = QPushButton("Add Nodes")
        openListLayout.addWidget(self.BUTTON['peerslist']) 
        openListLayout.addWidget(self.BUTTON['bannedlist'])
        openListLayout.addWidget(self.BUTTON['addnodes'])
        self.openList.setLayout(openListLayout)

        bottomCentralWidgets = QHBoxLayout()
        bottomCentralWidgets.addWidget(networksList)
        bottomCentralWidgets.addWidget(self.openList)

        layout.addWidget(networkStats)
        layout.addLayout(centralWidgets)
        layout.addLayout(bottomCentralWidgets)
        
        layout.addStretch()
        #NETWORKlayout.addWidget(groupTable)
        
        self.setLayout(layout)
    
    def setDefault(self):
        [self.RESULT[key].setText(" - ") for key in self.RESULT]

    def write_result(self, statusInfo, peersGeolocation):
        self.RESULT['subversion'].setText(str(statusInfo['subversion']))
        self.RESULT['totalbytessent'].setText(utils.convertBytesSizes(statusInfo['totalbytessent']))
        self.RESULT['totalbytesrecv'].setText(utils.convertBytesSizes(statusInfo['totalbytesrecv']))

        self.RESULT['connections'].setText(str(statusInfo['connections']))
        self.RESULT['connections_out'].setText(str(statusInfo['connections_out']))
        self.RESULT['connections_in'].setText(str(statusInfo['connections_in']))

        self.RESULT['version'].setText(str(statusInfo['version']))
        self.RESULT['protocolversion'].setText(str(statusInfo['protocolversion']))

        for n in statusInfo['networks']:
            self.RESULT[n["name"]].setText("Reachable" if bool(n["reachable"]) else "False")

        self.RESULT['networkhashps'].setText(utils.convertBigSizes(statusInfo['networkhashps']) + "H/s")
        self.RESULT['difficulty'].setText(utils.convertBigSizes(statusInfo['difficulty']))
    
    def open_peers_list(self, peersInfo, peersGeolocation):
        self.PEERSLIST = ui.widgets.peers_list.PeersTable(peersInfo, peersGeolocation)
        self.PEERSLIST.setVisible(True)

    def open_added_list(self, clientGeneralCall, clientAddnodeCommand):
        self.ADDEDLIST = ui.widgets.added_list.AddedNodes(clientGeneralCall, clientAddnodeCommand)
        self.ADDEDLIST.setVisible(True)

