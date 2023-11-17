


import lib.client
import ui.utils as utils
import sys, time, random, json, threading
from PySide6.QtCore import Qt 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout,
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


        self.mainLayout.addWidget(self.MENU)
        self.mainLayout.addWidget(self.PAGES['STATUS'])
        self.mainLayout.addWidget(self.PAGES['NETWORK'])
        self.mainLayout.addWidget(self.PAGES['ADVANCED'])
        
        
        container = QWidget()
        container.setLayout(self.mainLayout)
        self.setCentralWidget(container)

        
        self.refreshThread = threading.Thread(target = self.refreshController, daemon = True)
        self.CLIENT = lib.client.Client()

        self.refreshThread.start()

    
    def refreshController(self):
        while True:
            if self.CLIENT.network.isConnected:
                self.refreshStatusInfo()
                #self.refreshNetworkInfo()
                self.refreshPeersInfo()
            else:
                self.setStatusDefault()
            time.sleep(5)
        
    def refreshConnectionStatus(self):
        if self.CLIENT.network.isConnected:
            self.groupConnButton.setText("Disconnect")
        else:
            self.groupConnButton.setText("Connect")


    def refreshStatusInfo(self):
        self.CLIENT.getStatusInfo()
        if self.CLIENT.statusInfo:
            #adds the data to the status result
            for key, value in self.statusResult.items():
                if key == 'uptime': self.statusResult[key].setText(utils.convertElapsedTime(self.CLIENT.statusInfo[key]))
                elif key == 'verificationprogress': self.statusResult[key].setText(utils.convertPercentage(self.CLIENT.statusInfo[key]))
                elif key == 'size_on_disk': self.statusResult[key].setText(utils.convertBytesSizes(self.CLIENT.statusInfo[key]))
                elif key == 'bytes': self.statusResult[key].setText(utils.convertBytesSizes(self.CLIENT.statusInfo[key]))
                elif key == 'usage': self.statusResult[key].setText(utils.convertBytesSizes(self.CLIENT.statusInfo[key]))
                else: self.statusResult[key].setText(str(self.CLIENT.statusInfo[key]))

            for key, value in self.statsResult.items():
                if key == 'totalbytesrecv': self.statsResult[key].setText(utils.convertBytesSizes(self.CLIENT.statusInfo[key]))
                elif key == 'totalbytesrecv': self.statsResult[key].setText(utils.convertBytesSizes(self.CLIENT.statusInfo[key]))
                else: self.statsResult[key].setText(str(self.CLIENT.statusInfo[key]))


    def refreshNetworkInfo(self):
        self.CLIENT.getNetworkStats()
        if self.CLIENT.networkStats:
            for key, value in self.statsResult.items():
                self.statsResult[key].setText(str(self.CLIENT.networkStats[key]))

    def refreshPeersInfo(self):
        self.CLIENT.getPeersInfo()
        if self.CLIENT.peersInfo:
            rowCounter = 0
            for peer in self.peersInfo:
                typeC = 'Inbound' if peer['inbound'] else: 'Outbound'
                self.peersTable.setItem(rowCounter, 0, QTableWidgetItem(peer['id']))
                self.peersTable.setItem(rowCounter, 1, QTableWidgetItem(peer['addr']))
                self.peersTable.setItem(rowCounter, 2, QTableWidgetItem(typeC))
                self.peersTable.setItem(rowCounter, 3, QTableWidgetItem(peer['subversion']))
                rowCounter += 1
                
        

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

    def init_status(self):
        self.PAGES['STATUS'] = QWidget()
        self.statusResult = {}
        statusLabel = {}
        STATUSlayout = QVBoxLayout()
       
        groupConn = QGroupBox("Node Connection")
        groupConnLayout = QHBoxLayout()
        groupConnLabel = QLabel("node IP:")
        self.groupConnLEdit = QLineEdit("192.168.1.238")
        self.groupConnButton = QPushButton("Connect")
        self.groupConnButton.setFixedWidth(80)
        self.groupConnButton.clicked.connect(self.handle_connection)
        groupConnLayout.addWidget(groupConnLabel)
        groupConnLayout.addWidget(self.groupConnLEdit)
        groupConnLayout.addWidget(self.groupConnButton)
        groupConn.setLayout(groupConnLayout)

        self.groupNodeStatus = QGroupBox("Node Status")
        groupNodeStatusLayout = QFormLayout()
        statusLabel['uptime'] = QLabel("Uptime:")
        statusLabel['chain'] = QLabel("Chain:")
        statusLabel['blocks'] = QLabel("Blocks:")
        statusLabel['headers'] = QLabel("Headers:")
        statusLabel['verificationprogress'] = QLabel("Verification:")
        statusLabel['pruned'] = QLabel("Pruned:")
        statusLabel['size_on_disk'] = QLabel("Size:")

        statusLabel['version'] = QLabel("Version:")
        statusLabel['subversion'] = QLabel("Agent:")
        statusLabel['protocolversion'] = QLabel("Protocol:")
        statusLabel['connections'] = QLabel("Connections:")
        #statusLabel['relayfee'] = QLabel("Relay Fee:")

        statusLabel['size'] = QLabel("Transactions:")
        #statusLabel['bytes'] = QLabel("Tot. Size:")
        statusLabel['usage'] = QLabel("Memory Usage:")
        statusLabel['mempoolminfee'] = QLabel("Min. Fee:")
        statusLabel['fullrbf'] = QLabel("Full RBF:")

        #creates a result label for each of statusLabel
        for key, value in statusLabel.items():
            self.statusResult[key] = QLabel() 
            self.statusResult[key].setAlignment(Qt.AlignCenter)
        
        #sets all result labels with default text " - "
        self.setStatusDefault()
        self.groupNodeStatus.setEnabled(False)

        #creates the formlayout
        for key, value in statusLabel.items():
            groupNodeStatusLayout.addRow(statusLabel[key], self.statusResult[key])

        self.groupNodeStatus.setLayout(groupNodeStatusLayout)
        

        STATUSlayout.addWidget(groupConn)
        STATUSlayout.addWidget(self.groupNodeStatus)
        STATUSlayout.addStretch()

        

        self.PAGES['STATUS'].setLayout(STATUSlayout)
    
    def init_network(self):
        self.PAGES['NETWORK'] = QWidget()

        statsLabel = {}
        self.statsResult = {}

        NETWORKlayout = QVBoxLayout()

        groupStats = QGroupBox("Network Stats")
        groupStatsLayout = QHBoxLayout()
        groupStatsForm1 = QFormLayout()
        groupStatsForm2 = QFormLayout()
        statsLabel['networkactive'] = QLabel("Network Active:")
        statsLabel['totalbytesrecv'] = QLabel("Bytes Sent:")
        statsLabel['totalbytessent'] = QLabel("Bytes Received:")
        statsLabel['connections'] = QLabel("Connections:")
        statsLabel['connections_in'] = QLabel("Inbound:")
        statsLabel['connections_out'] = QLabel("Outbound:")
        for key, value in statsLabel.items():
            self.statsResult[key] = QLabel(" - ")
            self.statsResult[key].setAlignment(Qt.AlignCenter)
        groupStatsForm1.addRow(statsLabel['networkactive'], self.statsResult['networkactive'])
        groupStatsForm1.addRow(statsLabel['totalbytesrecv'], self.statsResult['totalbytesrecv'])
        groupStatsForm1.addRow(statsLabel['totalbytessent'], self.statsResult['totalbytessent'])
        groupStatsForm2.addRow(statsLabel['connections'], self.statsResult['connections'])
        groupStatsForm2.addRow(statsLabel['connections_in'], self.statsResult['connections_in'])
        groupStatsForm2.addRow(statsLabel['connections_out'], self.statsResult['connections_out'])
        groupStatsLayout.addLayout(groupStatsForm1)
        groupStatsLayout.addLayout(groupStatsForm2)
        groupStats.setLayout(groupStatsLayout)

        groupTable = QGroupBox("Connected Peers")
        groupTableLayout = QVBoxLayout()
        self.peersTable = QTableWidget()
        self.peersTable.setColumnCount(4)
        self.peersTable.setHorizontalHeaderLabels(['ID', 'ADDRESS', 'TYPE', 'AGENT'])
        groupTableLayout.addWidget(self.peersTable)
        groupTable.setLayout(groupTableLayout)

        NETWORKlayout.addWidget(groupStats)
        NETWORKlayout.addWidget(groupTable)
        
        self.PAGES['NETWORK'].setLayout(NETWORKlayout)
        self.PAGES['NETWORK'].setVisible(False)

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
    
    def setStatusDefault(self):
        for key, value in self.statusResult.items():
            self.statusResult[key].setText(" - ")

    def menu_buttons(self, button):
        for key, value in self.PAGES.items():
            self.PAGES[key].setVisible(True) if key == button else self.PAGES[key].setVisible(False)
        
    
    def handle_connection(self):
        if self.CLIENT.network.isConnected:
            self.CLIENT.network.disconnectServer()
            self.setStatusDefault()
            self.groupNodeStatus.setEnabled(False)
        else:
            self.CLIENT.initConnection()           
        
        if self.CLIENT.network.isConnected:
            self.groupConnLEdit.setEnabled(False)
            self.groupConnButton.setText("Disconnect")

            self.groupNodeStatus.setEnabled(True)
            
        else:
            self.groupConnButton.setText("Connect")
            self.groupConnLEdit.setEnabled(True)
            self.groupNodeStatus.setEnabled(False)

    def send_advanced_command(self):
        command = self.commandLine.text()
        self.CLIENT.network.sender(self.CLIENT.calls[command])
        result = self.CLIENT.network.receiver()
        result = json.loads(result)
        if type(result) is list:
            [self.debugLog.append(str(x)) for x in result]
        elif type(result) is dict:
            [self.debugLog.append(str(f"{key}: {value}")) for key, value in result.items()]
        else:
            self.debugLog.append(str(result))
        


app = QApplication(sys.argv)
app.setStyleSheet(ALL_CSS)

window = MainWindow()
window.show()

app.exec_()

