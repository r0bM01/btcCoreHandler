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


class PeersList(QWidget):
    def __init__(self, connectedInfo):
        super().__init__()

        self.PEERS = connectedInfo

        self.RESULT = {}
        self.BUTTON = {}
        self.edit = {}
        labels = {}
        
        
        self.setFixedSize(640, 500)


        layout = QVBoxLayout()

        
        peersTable = PeersTable(connectedInfo)


        layout.addWidget(peersTable)
        
        self.setLayout(layout)
        self.setVisible(False)



class PeersTable(QWidget):
    def __init__(self, connectedInfo):
        super().__init__()

        self.peersInfo = connectedInfo

        # self.peers_view = self.create_peers_view(connectedinfo)

        self.setWindowTitle("Connected Peers")
        self.setFixedSize(800, 500)
        layout = QVBoxLayout()
        

        searchNode = QGroupBox("Search")
        searchNodeLayout = QVBoxLayout()
        self.searchNodeLineEdit = QLineEdit()
        self.searchNodeLineEdit.textChanged.connect(self.search)
        searchNodeLayout.addWidget(self.searchNodeLineEdit)
        searchNode.setLayout(searchNodeLayout)


        self.peersTable = QTableWidget()
        self.peersTable.setColumnCount(5)
        self.peersTable.setHorizontalHeaderLabels(['ID', 'ADDRESS', 'TYPE', 'DATA', 'COUNTRY'])
        self.peersTable.verticalHeader().setVisible(False)

        peersHeader = self.peersTable.horizontalHeader()
        peersHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        peersHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        peersHeader.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        peersHeader.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        peersHeader.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.peersTable.setRowCount(len(self.peersInfo))
        self.peersTable.setSelectionBehavior(QTableWidget.SelectRows)
        
        
        rowCounter = 0

        tableItem = {}
        for peer in self.peersInfo:
            ID = QTableWidgetItem(str(peer['id']))
            ADDR = QTableWidgetItem(str(peer['addr']))
            TYPE = QTableWidgetItem(str('Inbound' if peer['inbound'] else 'Outbound'))
            DATA = QTableWidgetItem(utils.convertBytesSizes(int(peer['bytessent']) + int(peer['bytesrecv'])))
            COUNTRY = QTableWidgetItem(utils.convertLongCountry(peer['country_name']))

            ID.setTextAlignment(Qt.AlignCenter)
            ADDR.setTextAlignment(Qt.AlignCenter)
            TYPE.setTextAlignment(Qt.AlignCenter)
            DATA.setTextAlignment(Qt.AlignCenter)
            COUNTRY.setTextAlignment(Qt.AlignCenter)
            
            ID.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            ADDR.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            TYPE.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            DATA.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            COUNTRY.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                            
            self.peersTable.setItem(rowCounter, 0, ID)
            self.peersTable.setItem(rowCounter, 1, ADDR)
            self.peersTable.setItem(rowCounter, 2, TYPE)
            self.peersTable.setItem(rowCounter, 3, DATA)
            self.peersTable.setItem(rowCounter, 4, COUNTRY)

            #self.peersTable.setItem(rowCounter, 3, QTableWidgetItem(peer['subversion']))
            rowCounter += 1
        
        self.peersTable.itemDoubleClicked.connect(lambda x: self.open_peer_detail(self.peersTable.currentRow()))
        layout.addWidget(searchNode)
        layout.addWidget(self.peersTable)
        self.setLayout(layout)
    
    """
    def create_peers_view(self, peersInfo, peersGeolocation):
        peersData = []
        
        for peer in peersInfo:
            pData = {}
            pData['id'] = peer['id']
            pData['addr'] = peer['addr']
            pData['type'] = 'Inbound' if peer['inbound'] else 'Outbound'
            pData['country'] = [geo[1] for geo in peersGeolocation if geo[0] == peer['addr'].split(":")[0]][0]
            peersData.append(pData)

        return peersData
    """
    
    def open_peer_detail(self, row):

        peerID = self.peersTable.item(row, 0)

        for peer in self.peersInfo:
            if str(peer['id']) == str(peerID.text()):
                selectedPeer = peer
        """
        for peer in self.peers_view:
            if str(peer['id']) == str(peerID.text()):
                selectedCountry = peer['country']
        """
        self.detailedView = PeerDetail(selectedPeer)
        self.detailedView.setVisible(True)
        
        #detail = PeerDetail(peer.text())
        #detail.setVisible(True)

    def search(self):
        self.peersTable.setCurrentItem(None)
        #if not text: return

        matching_items = self.peersTable.findItems(self.searchNodeLineEdit.text(), Qt.MatchContains)
        if matching_items:
            # we have found something
            item = matching_items[0]  # take the first
            self.peersTable.setCurrentItem(item)


class PeerDetail(QWidget):
    def __init__(self, peerData):
        super().__init__()

        # 'mapped_as' 'pingwait',

        selectedFields = ['id', 'addr', 'addrbind', 'addrlocal', 'network', 'services', 'servicesnames', 'relaytxes', 'lastsend',
                          'lastrecv', 'last_transaction', 'last_block', 'bytessent', 'bytesrecv', 'conntime', 'timeoffset', 'pingtime', 'minping',
                          'version', 'subver', 'inbound', 'synced_blocks', 'addr_relay_enabled', 'addr_processed', 'minfeefilter', 'connection_type']


        timeFields = ['lastsend', 'lastrecv', 'last_transaction', 'conntime']
        bytesFields = ['bytessent', 'bytesrecv']
                          

        labels = {}
        self.RESULT = {}
        #self.setFixedWidth(640)
        layout = QFormLayout()

        labels['country'] = QLabel("Country:")
        self.RESULT['country'] = QLineEdit(str(peerData['country_name']))
        self.RESULT['country'].setAlignment(Qt.AlignCenter)
        self.RESULT['country'].setReadOnly(True)

        layout.addRow(labels['country'], self.RESULT['country'])
        for field in selectedFields:
            if field in peerData:
                labels[field] = QLabel(str(field).capitalize() + ":")
                if field in timeFields: self.RESULT[field] = QLineEdit(time.ctime(int(peerData[field])))
                elif field in bytesFields: self.RESULT[field] = QLineEdit(utils.convertBytesSizes(peerData[field]))
                else: self.RESULT[field] = QLineEdit(str(peerData[field]))
                
                self.RESULT[field].setAlignment(Qt.AlignCenter)
                self.RESULT[field].setReadOnly(True)
                layout.addRow(labels[field], self.RESULT[field])


        width = self.maximumWidth()
        height = self.maximumHeight()
        
        self.setFixedSize(400, 700)

        self.setWindowTitle(f"Peer {peerData['id']} Details")
        self.setLayout(layout)
        self.setWindowModality(Qt.ApplicationModal)
        self.setVisible(False)



 
