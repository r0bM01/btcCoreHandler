



import lib.client
import sys, time, random, json, threading
from PySide6.QtCore import Qt 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout,
                            QHBoxLayout, QGroupBox, QTextEdit, QMessageBox )

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

        self.init_left_menu()
        self.init_status()
        self.init_advanced()


        self.mainLayout.addWidget(self.MENU)
        self.mainLayout.addWidget(self.STATUS)
        self.mainLayout.addWidget(self.ADVANCED)
        
        
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
            time.sleep(5)

    def refreshStatusInfo(self):
        self.CLIENT.getStatusInfo()

        if self.CLIENT.statusInfo:
            uptimeSecs = int(self.CLIENT.statusInfo['uptime'])
            d = uptimeSecs // 86400
            h = (uptimeSecs % 86400) // 3600
            m = ( (uptimeSecs % 86400) % 3600 ) // 60
            s = ( (uptimeSecs % 86400) % 3600) % 60 
            self.CLIENT.statusInfo['uptime'] = str(f"{d} Days {h}h{m}m{s}s")

            #adds the data to the status result
            for key, value in self.statusResult.items():
                self.statusResult[key].setText(str(self.CLIENT.statusInfo[key]))



    def init_left_menu(self):
        self.MENU = QWidget()

        MENUlayout = QVBoxLayout()
        labelTitle = QLabel()
        labelTitle.setPixmap(QPixmap("ui/assets/bitcoin_64.png"))
        labelTitle.setAlignment(Qt.AlignBottom | Qt.AlignCenter)

        self.btSTATUS = QPushButton("Status")
        self.btSTATUS.clicked.connect(lambda x: self.menu_buttons("status"))
        self.btNETWORK = QPushButton("Network")
        self.btADVANCED = QPushButton("Advanced")
        self.btADVANCED.clicked.connect(lambda x: self.menu_buttons("advanced"))
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
        self.STATUS = QWidget()
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

        groupNodeStatus = QGroupBox("Node Status")
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
        statusLabel['relayfee'] = QLabel("Relay Fee:")

        statusLabel['size'] = QLabel("Transactions:")
        statusLabel['bytes'] = QLabel("Tot. Size:")
        statusLabel['usage'] = QLabel("Usage Size:")
        statusLabel['mempoolminfee'] = QLabel("Min. Fee:")
        statusLabel['fullrbf'] = QLabel("Full RBF:")

        #creates a result label for each of statusLabel
        for key, value in statusLabel.items():
            self.statusResult[key] = QLabel() 
        #sets all result labels with alignment center
        [self.statusResult[key].setAlignment(Qt.AlignCenter) for key, value in self.statusResult.items()]
        #sets all result labels with default text " - "
        self.setStatusDefault()

        #creates the formlayout
        for key, value in statusLabel.items():
            groupNodeStatusLayout.addRow(statusLabel[key], self.statusResult[key])

        groupNodeStatus.setLayout(groupNodeStatusLayout)
        

        STATUSlayout.addWidget(groupConn)
        STATUSlayout.addWidget(groupNodeStatus)
        STATUSlayout.addStretch()

        

        self.STATUS.setLayout(STATUSlayout)

    def init_advanced(self):
        self.ADVANCED = QWidget()

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

        self.ADVANCED.setLayout(ADVANCEDlayout)
        self.ADVANCED.setVisible(False)
        #self.ADVANCED.setStyleSheet("QPushButton { border: 0px; }")
    
    def setStatusDefault(self):
        for key, value in self.statusResult.items():
            self.statusResult[key].setText(" - ")

    def menu_buttons(self, button):
        if button == "advanced":
            self.STATUS.setVisible(False)
            self.ADVANCED.setVisible(True)
        elif button == "status":
            self.STATUS.setVisible(True)
            self.ADVANCED.setVisible(False)
    
    def handle_connection(self):
        if self.CLIENT.network.isConnected:
            self.CLIENT.network.disconnectServer()
        else:
            self.CLIENT.initConnection()           
        
        if self.CLIENT.network.isConnected:
            self.groupConnLEdit.setEnabled(False)
            self.groupConnButton.setText("Disconnect")
            
        else:
            self.groupConnButton.setText("Connect")
            self.groupConnLEdit.setEnabled(True)

    def send_advanced_command(self):
        command = self.commandLine.text()
        self.CLIENT.network.sender(self.CLIENT.calls[command])
        result = self.CLIENT.network.receiver()
        self.debugLog.append(result)


app = QApplication(sys.argv)
app.setStyleSheet(ALL_CSS)

window = MainWindow()
window.show()

app.exec_()

