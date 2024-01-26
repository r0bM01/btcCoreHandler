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



class Status(QWidget):
    def __init__(self):
        super().__init__()

        self.RESULT = {}
        self.BUTTON = {}
        labels = {}

        layout = QVBoxLayout()
        centralGroups = QHBoxLayout()
       
        ## NODE CONNECTION GROUP 1 ROW
        nodeConnection = QGroupBox("Node Connection")
        nodeConnectionLayout = QHBoxLayout()
        # labels['node'] = QLabel("node IP:")
        self.RESULT['node'] = QLabel(" - ") 
        self.BUTTON['connect'] = QPushButton("Connect")
        self.BUTTON['connect'].setFixedWidth(80)

        # self.groupConnButton.clicked.connect(self.handle_connection)
        

        ## NODE STATUS GROUP 3 ROWS
        nodeStatus = QGroupBox("Node Status")
        nodeStatusLayout = QFormLayout()
        labels['upsince'] = QLabel("Started:")
        labels['uptime'] = QLabel("Uptime:")
        labels['machine'] = QLabel("Server:")
        
        ## BLOCKCHAIN GROUP 4 ROWS
        blockchain = QGroupBox("Blockchain")
        blockchainLayout = QFormLayout()
        labels['chain'] = QLabel("Chain:")
        labels['blocks'] = QLabel("Blocks:")
        labels['verificationprogress'] = QLabel("Verification:")
        labels['size_on_disk'] = QLabel("Size:")

        ## MEMPOOL GROUP 4 ROWS
        mempool = QGroupBox("Mempool")
        mempoolLayout = QFormLayout()
        labels['size'] = QLabel("Transactions:")
        labels['usage'] = QLabel("Memory Usage:")
        labels['mempoolminfee'] = QLabel("Min. Fee:")
        labels['fullrbf'] = QLabel("Full RBF:")

        ## NETWORK GROUP 4 ROWS
        network = QGroupBox("Network")
        networkLayout = QFormLayout()
        labels['localservicesnames'] = QLabel("Services:")
        labels['connections'] = QLabel("Peers:")
        labels['countries'] = QLabel("Connected countries:")
        labels['totaldata'] = QLabel("Data exchanged:")
        

        # result fields creation for each label
        for key in labels:
            self.RESULT[key] = QLabel(" - ")
            self.RESULT[key].setAlignment(Qt.AlignCenter)

        # adding result fields to each group
        # node connection
        # nodeConnectionLayout.addWidget(labels['nodeip'])
        nodeConnectionLayout.addWidget(self.RESULT['node'])
        nodeConnectionLayout.addWidget(self.BUTTON['connect'])
        # node status
        nodeStatusLayout.addRow(labels['upsince'], self.RESULT['upsince'])
        nodeStatusLayout.addRow(labels['uptime'], self.RESULT['uptime'])
        nodeStatusLayout.addRow(labels['machine'], self.RESULT['machine'])
        # blockchain
        blockchainLayout.addRow(labels['chain'], self.RESULT['chain'])
        blockchainLayout.addRow(labels['blocks'], self.RESULT['blocks'])
        blockchainLayout.addRow(labels['verificationprogress'], self.RESULT['verificationprogress'])
        blockchainLayout.addRow(labels['size_on_disk'], self.RESULT['size_on_disk'])
        # mempool
        mempoolLayout.addRow(labels['size'], self.RESULT['size'])
        mempoolLayout.addRow(labels['usage'], self.RESULT['usage'])
        mempoolLayout.addRow(labels['mempoolminfee'], self.RESULT['mempoolminfee'])
        mempoolLayout.addRow(labels['fullrbf'], self.RESULT['fullrbf'])
        # network
        networkLayout.addRow(labels['localservicesnames'], self.RESULT['localservicesnames'])
        networkLayout.addRow(labels['connections'], self.RESULT['connections'])
        networkLayout.addRow(labels['countries'], self.RESULT['countries'])
        networkLayout.addRow(labels['totaldata'], self.RESULT['totaldata'])

        ## LAYOUT CONSTRUCTION
        nodeConnection.setLayout(nodeConnectionLayout)
        nodeStatus.setLayout(nodeStatusLayout)
        blockchain.setLayout(blockchainLayout)
        mempool.setLayout(mempoolLayout)
        network.setLayout(networkLayout)

        centralGroups.addWidget(blockchain)
        centralGroups.addWidget(mempool)

        layout.addWidget(nodeConnection)
        layout.addWidget(nodeStatus)
        layout.addLayout(centralGroups)
        layout.addWidget(network)
        layout.addStretch()

        # set layout for the STATUS widget
        self.setLayout(layout)
        
        #sets all result labels with default text " - "
        #self.setStatusDefault()
    
    def setDefault(self):
        [self.RESULT[key].setText(" - ") for key in self.RESULT]

    def write_result(self, statusInfo, systemInfo, connectedInfo):
        #self.RESULT['nodeip']
        # node status
        self.RESULT['upsince'].setText(utils.uptimeSince(statusInfo['uptime']))
        self.RESULT['uptime'].setText(utils.convertElapsedTime(statusInfo['uptime']))
        self.RESULT['machine'].setText(utils.printSystem(systemInfo))
        # blockchain
        self.RESULT['chain'].setText(str(statusInfo['chain']))
        self.RESULT['blocks'].setText(str(statusInfo['blocks']))
        self.RESULT['verificationprogress'].setText(utils.convertPercentage(statusInfo['verificationprogress']))
        self.RESULT['size_on_disk'].setText(utils.convertBytesSizes(statusInfo['size_on_disk']))
        # mempool
        self.RESULT['size'].setText(str(statusInfo['size']))
        self.RESULT['usage'].setText(utils.convertBytesSizes(statusInfo['usage']))
        self.RESULT['mempoolminfee'].setText(str(statusInfo['mempoolminfee']))
        self.RESULT['fullrbf'].setText(str(statusInfo['fullrbf']))
        # network
        self.RESULT['localservicesnames'].setText(str(statusInfo['localservicesnames']))
        self.RESULT['connections'].setText(str(statusInfo['connections']))
        self.RESULT['countries'].setText(str(utils.countriesStatsCount(connectedInfo)))
        self.RESULT['totaldata'].setText(utils.convertBytesSizes(int(statusInfo['totalbytesrecv']) + int(statusInfo['totalbytessent'])))
        
        

    