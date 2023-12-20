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
        labels = {}

        layout = QVBoxLayout()

        networkStats = QGroupBox("Network Stats")
        networkStatsLayout = QHBoxLayout()

        leftForm = QFormLayout()
        labels['networkactive'] = QLabel("Network Active:")
        labels['totalbytessent'] = QLabel("Bytes Sent:")
        labels['totalbytesrecv'] = QLabel("Bytes Received:")

        rightForm = QFormLayout()
        labels['connections'] = QLabel("Connections:")
        labels['connections_in'] = QLabel("Inbound:")
        labels['connections_out'] = QLabel("Outbound:")


        for key, value in labels.items():
            self.RESULT[key] = QLabel(" - ")
            self.RESULT[key].setAlignment(Qt.AlignCenter)


        leftForm.addRow(labels['networkactive'], self.RESULT['networkactive'])
        leftForm.addRow(labels['totalbytessent'], self.RESULT['totalbytessent'])
        leftForm.addRow(labels['totalbytesrecv'], self.RESULT['totalbytesrecv'])

        rightForm.addRow(labels['connections'], self.RESULT['connections'])
        rightForm.addRow(labels['connections_out'], self.RESULT['connections_out'])
        rightForm.addRow(labels['connections_in'], self.RESULT['connections_in'])

        networkStatsLayout.addLayout(leftForm)
        networkStatsLayout.addLayout(rightForm)

        networkStats.setLayout(networkStatsLayout)

        """
        groupTable = QGroupBox("Connected Peers")
        groupTableLayout = QVBoxLayout()
        self.peersTable = QTableWidget()
        self.peersTable.setColumnCount(3)
        self.peersTable.setHorizontalHeaderLabels(['ID', 'ADDRESS', 'TYPE'])
        peersHeader = self.peersTable.horizontalHeader()
        peersHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        peersHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        peersHeader.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        groupTableLayout.addWidget(self.peersTable)
        groupTable.setLayout(groupTableLayout)
        """

        layout.addWidget(networkStats)
        layout.addStretch()
        #NETWORKlayout.addWidget(groupTable)
        
        self.setLayout(layout)
    
    def setDefault(self):
        [self.RESULT[key].setText(" - ") for key in self.RESULT]

    def write_result(self, statusInfo, peersGeolocation):
        self.RESULT['networkactive'].setText(str(statusInfo['networkactive']))
        self.RESULT['totalbytessent'].setText(utils.convertBytesSizes(statusInfo['totalbytessent']))
        self.RESULT['totalbytesrecv'].setText(utils.convertBytesSizes(statusInfo['totalbytesrecv']))

        self.RESULT['connections'].setText(str(statusInfo['connections']))
        self.RESULT['connections_out'].setText(str(statusInfo['connections_out']))
        self.RESULT['connections_in'].setText(str(statusInfo['connections_in']))
    

            
