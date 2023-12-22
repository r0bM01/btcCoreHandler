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

import ui.pages.peers_list
import ui.utils as utils
from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
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


        openList = QGroupBox("Open")
        openListLayout = QHBoxLayout()
        self.BUTTON['peerslist'] = QPushButton("Peers")
        self.BUTTON['addedlist'] = QPushButton("Added")
        openListLayout.addWidget(self.BUTTON['peerslist']) 
        openListLayout.addWidget(self.BUTTON['addedlist'])
        openList.setLayout(openListLayout)


        addNode = QGroupBox("Addnode")
        addNodeLayout = QFormLayout()
        self.edit['addnode'] = QLineEdit("Figa")
        self.BUTTON['addnode'] = QPushButton("Add")
        addNodeLayout.addRow(self.edit['addnode'])
        addNode.setLayout(addNodeLayout)

        centralWidgets = QHBoxLayout()
        centralWidgets.addWidget(openList)
        centralWidgets.addWidget(addNode)



        layout.addWidget(networkStats)
        layout.addLayout(centralWidgets)
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
    
    def open_peers_list(self, peersInfo, peersGeolocation):
        self.PEERSLIST = ui.pages.peers_list.PeersTable(peersInfo, peersGeolocation)
        self.PEERSLIST.setVisible(True)
