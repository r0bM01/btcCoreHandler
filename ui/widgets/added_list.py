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
from lib.shared.crypto import getMiniHash
from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout, QHeaderView,
                            QHBoxLayout, QGroupBox, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem, QScrollArea )




class AddedNodes(QWidget):
    def __init__(self, clientGeneralCall, clientAddnodeCommand):
        super().__init__()

        self.clientAddnodeCommand = clientAddnodeCommand
        self.clientGeneralCall = clientGeneralCall

        self.updateList()

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

        
        nodeListGroup = QGroupBox("Added Nodes List")
        self.nodeListGroupLayout = QVBoxLayout()

        self.nodeListObjects = []
        for node in self.nodeList:
            nodeID = getMiniHash(node['addednode'])
            nodeObject = self.createNodeLine(node)
            self.nodeListObjects.append((nodeID, nodeObject))
            self.nodeListGroupLayout.addLayout(nodeObject)
      
        nodeListGroup.setLayout(self.nodeListGroupLayout)

        layout.addWidget(addNode)
        layout.addWidget(nodeListGroup)
        layout.addStretch()

        self.setLayout(layout)


    def updateList(self):
        self.nodeList = self.clientGeneralCall('getaddednodeinfo')

    def createNodeLine(self, nodeDict):
        nodeLine = QHBoxLayout()
        
        host = QLineEdit(nodeDict['addednode'])
        host.setAlignment(Qt.AlignCenter)
        host.setReadOnly(True)
        
        connected = nodeDict['connected']
        connected.setAlignment(Qt.AlignCenter)
        connected.setReadOnly(True)

        self.BUTTON[node['addednode']] = QPushButton("Remove")
        self.BUTTON[node['addednode']].clicked.connect(lambda x: self.removeNode(nodeDict['addednode']))

        nodeLine.addWidget(QLabel("host: "))
        nodeLine.addWidget(host)
        nodeLine.addStretch()
        nodeLine.addWidget(QLabel("Connected: "))
        nodeLine.addWidget(connected)
        nodeLine.addStretch()
        nodeLine.addWidget(self.BUTTON[node['addednode']])

        return nodeLine

    def addNode(self):
        nodeAddress = str(self.edit['nodehost'].text()) + str(":") + str(self.edit['nodeport'].text())
        result = self.clientAddnodeCommand(nodeAddress, 'add')
        self.updateList()
        for n in self.nodeList:
            if n['addednode'] == nodeAddress:
                nodeID = getMiniHash(n['addednode'])
                nodeObject = self.createNodeLine(n)
                self.nodeListObjects.append((nodeID, nodeObject))
                self.nodeListGroupLayout.addLayout(nodeObject)

        # self.nodeList.updateList()

    def removeNode(self, node):
        result = self.clientAddnodeCommand(node, 'remove')
        nodeID = getMiniHash(node)
        for n in self.nodeListObjects:
            if nodeID == n[0]:
                self.BUTTON[node].deleteLater()
                self.BUTTON.pop(node)
                n[1].deleteLater() 
                self.nodeListObjects.remove(n)
        
        # self.nodeList.updateList()









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
        updatedList = [n['addednode'] for n in self.addednodeInfo]
        [self.removeFromList(node) not in updatedList for node in self.NODES]
            
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
                    # self.BUTTON[node['addednode']].clicked.connect(lambda x: self.removeNode(node['addednode']))
                    self.NODES[node['addednode']].addWidget(self.BUTTON[node['addednode']])

                    self.nodeListLayout.addLayout(self.NODES[node['addednode']])
        else:
            [self.NODES[node].deleteLater() for node in self.NODES]
            [self.NODES.pop(node) for node in self.NODES]
            self.nodeListLayout.addWidget(QLabel("You haven't added any node yet."))

    def removeFromList(self, nodeAddress):
        # result = self.clientAddnodeCommand(nodeAddress, 'remove')
        self.NODES[nodeAddress].deleteLater()
        self.BUTTON[nodeAddress].deleteLater()