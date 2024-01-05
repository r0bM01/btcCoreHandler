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
import time
from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout, QHeaderView,
                            QHBoxLayout, QGroupBox, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem, QScrollArea )




class AddedNodes(QWidget):
    def __init__(self, clientGeneralCall, clientAddnodeCommand):
        super().__init__()

        self.clientAddnodeCommand = clientAddnodeCommand

        self.setWindowTitle("Added Nodes")
        self.setFixedSize(640, 500)

        self.RESULT = {}
        self.BUTTON = {}
        self.edit = {}

        layout = QVBoxLayout()

        addNode = QGroupBox("Add a Node")
        addNodeLayout = QHBoxLayout()
        self.edit['nodehost'] = QLineEdit()
        self.edit['nodeport'] = QLineEdit("8333")
        self.BUTTON['addnode'] = QPushButton("Add")
        self.BUTTON['addnode'].clicked.connect(self.addNode) 
        addNodeLayout.addWidget(QLabel("Host:"))
        addNodeLayout.addWidget(self.edit['nodehost']) 
        addNodeLayout.addWidget(QLabel("Port:"))
        addNodeLayout.addWidget(self.edit['nodeport']) 
        addNodeLayout.addWidget(self.BUTTON['addnode'])

        addNode.setLayout(addNodeLayout)

        self.nodeList = AddedNodeList(clientGeneralCall, clientAddnodeCommand)
        self.nodeList.updateList()

        layout.addWidget(addNode)
        layout.addWidget(self.nodeList)
        layout.addStretch()

        self.setLayout(layout)

    def addNode(self):
        nodeAddress = str(self.edit['nodehost'].text()) + str(":") + str(self.edit['nodeport'].text())
        result = self.clientAddnodeCommand(nodeAddress, 'add')
        self.nodeList.updateList()



class AddedNodeList(QGroupBox):
    def __init__(self, clientGeneralCall, clientAddnodeCommand):
        super().__init__()
        self.BUTTON = {}
        self.NODES = {}

        self.clientGeneralCall = clientGeneralCall
        self.clientAddnodeCommand = clientAddnodeCommand
        self.addednodeInfo = False
        self.setTitle("Added Nodes List")

        self.nodeListLayout = QVBoxLayout()
        #self.updateList()
        self.setLayout(self.nodeListLayout)


    def updateList(self):
        
        self.addednodeInfo = self.clientGeneralCall('getaddednodeinfo')
        if bool(self.addednodeInfo):
            for node in self.addednodeInfo:
                if node['addednode'] not in self.NODES:
                    self.NODES[node['addednode']] = QHBoxLayout()
                    self.NODES[node['addednode']].addWidget(QLabel("host:"))
                    self.NODES[node['addednode']].addWidget(QLabel(str(node['addednode'])))
                    self.NODES[node['addednode']].addStretch()
                    self.NODES[node['addednode']].addWidget(QLabel("connected:"))
                    self.NODES[node['addednode']].addWidget(QLabel(str(node['connected'])))
                    self.NODES[node['addednode']].addStretch()
                    self.NODES[node['addednode']].addWidget(QLabel("addresses:"))
                    self.NODES[node['addednode']].addWidget(QLabel(str(node['addresses'])))
                    self.NODES[node['addednode']].addStretch()
                    self.BUTTON[node['addednode']] = QPushButton("Remove")
                    self.BUTTON[node['addednode']].clicked.connect(lambda x: self.removeNode(node['addednode']))
                    self.NODES[node['addednode']].addWidget(self.BUTTON[node['addednode']])

                    self.nodeListLayout.addLayout(self.NODES[node['addednode']])
        else:
            self.nodeListLayout.addWidget(QLabel("HERE THE ADDED NODES"))

    def removeNode(self, nodeAddress):
        result = self.clientAddnodeCommand(nodeAddress, 'remove')
        self.NODES[nodeAddress].deleteLater()
        self.BUTTON[nodeAddress].deleteLater()