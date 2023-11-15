



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
        self.CLIENT.getAllInfo()

        if self.CLIENT.allInfo:
            uptimeSecs = int(self.CLIENT.allInfo['uptime'])
            d = uptimeSecs // 86400
            h = (uptimeSecs % 86400) // 3600
            m = ( (uptimeSecs % 86400) % 3600 ) // 60
            s = ( (uptimeSecs % 86400) % 3600) % 60 
            uptime = str(f"{d}Days {h}h{m}m{s}s")

            self.uptimeResult.setText(uptime)
            self.chainResult.setText(str(self.CLIENT.allInfo['chain']))
            self.blocksResult.setText(str(self.CLIENT.allInfo['blocks']))
            self.sizeResult.setText(str(self.CLIENT.allInfo['size_on_disk']))

            self.versionResult.setText(str(self.CLIENT.allInfo['version']))
            self.agentResult.setText(str(self.CLIENT.allInfo['agent']))
            self.relayResult.setText(str(self.CLIENT.allInfo['localrelay']))
            self.connectionsResult.setText(str(self.CLIENT.allInfo['connections']))

            self.transactionsResult.setText(str(self.CLIENT.allInfo['transactions']))
            self.bytesResult.setText(str(self.CLIENT.allInfo['bytes']))
            self.relayfeeResult.setText(str(self.CLIENT.allInfo['minrelaytxfee']))
            self.fullrbfResult.setText(str(self.CLIENT.allInfo['fullrbf']))

            #self.weightResult.setText(self.CLIENT.allInfo['currentblockweight'])
            #self.blocktxResult.setText(self.CLIENT.allInfo['currentblocktx'])
            self.difficultyResult.setText(str(self.CLIENT.allInfo['difficulty']))
            self.hashpsResult.setText(str(self.CLIENT.allInfo['networkhashps']))



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

        groupChain = QGroupBox("Blockchain")
        groupChainLayout = QFormLayout()
        uptimeLabel = QLabel("Uptime: ")
        self.uptimeResult = QLabel(" - ")
        self.uptimeResult.setAlignment(Qt.AlignCenter)
        chainLabel = QLabel("Chain: ")
        self.chainResult = QLabel(" - ")
        self.chainResult.setAlignment(Qt.AlignCenter)
        blocksLabel = QLabel("Blocks: ")
        self.blocksResult = QLabel(" - ")
        self.blocksResult.setAlignment(Qt.AlignCenter)
        sizeLabel = QLabel("Size: ")
        self.sizeResult = QLabel(" - ")
        self.sizeResult.setAlignment(Qt.AlignCenter)
        groupChainLayout.addRow(uptimeLabel, self.uptimeResult)
        groupChainLayout.addRow(chainLabel, self.chainResult)
        groupChainLayout.addRow(blocksLabel, self.blocksResult)
        groupChainLayout.addRow(sizeLabel, self.sizeResult)
        groupChain.setLayout(groupChainLayout)

        groupNetwork = QGroupBox("Network")
        groupNetworkLayout = QFormLayout()
        versionLabel = QLabel("Version: ")
        self.versionResult = QLabel(" - ")
        self.versionResult.setAlignment(Qt.AlignCenter)
        agentLabel = QLabel("Agent: ")
        self.agentResult = QLabel(" - ")
        self.agentResult.setAlignment(Qt.AlignCenter)
        relayLabel = QLabel("Relay: ")
        self.relayResult = QLabel(" - ")
        self.relayResult.setAlignment(Qt.AlignCenter)
        connectionsLabel = QLabel("Connections: ")
        self.connectionsResult = QLabel(" - ")
        self.connectionsResult.setAlignment(Qt.AlignCenter)
        groupNetworkLayout.addRow(versionLabel, self.versionResult)
        groupNetworkLayout.addRow(agentLabel, self.agentResult)
        groupNetworkLayout.addRow(relayLabel, self.relayResult)
        groupNetworkLayout.addRow(connectionsLabel, self.connectionsResult)
        groupNetwork.setLayout(groupNetworkLayout)

        groupMempool = QGroupBox("Mempool")
        groupMempoolLayout = QFormLayout()
        transactionsLabel = QLabel("Transactions: ")
        self.transactionsResult = QLabel(" - ")
        self.transactionsResult.setAlignment(Qt.AlignCenter)
        bytesLabel = QLabel("Size: ")
        self.bytesResult = QLabel(" - ")
        self.bytesResult.setAlignment(Qt.AlignCenter)
        relayfeeLabel = QLabel("Relay fee: ")
        self.relayfeeResult = QLabel(" - ")
        self.relayfeeResult.setAlignment(Qt.AlignCenter)
        fullrbfLabel = QLabel("Full RBF: ")
        self.fullrbfResult = QLabel(" - ")
        self.fullrbfResult.setAlignment(Qt.AlignCenter)
        groupMempoolLayout.addRow(transactionsLabel, self.transactionsResult)
        groupMempoolLayout.addRow(bytesLabel, self.bytesResult)
        groupMempoolLayout.addRow(relayfeeLabel, self.relayfeeResult)
        groupMempoolLayout.addRow(fullrbfLabel, self.fullrbfResult)
        groupMempool.setLayout(groupMempoolLayout)

        groupMining = QGroupBox("Mining")
        groupMiningLayout = QFormLayout()
        weightLabel = QLabel("Weight: ")
        self.weightResult = QLabel(" - ")
        self.weightResult.setAlignment(Qt.AlignCenter)
        blocktxLabel = QLabel("Block Txs: ")
        self.blocktxResult = QLabel(" - ")
        self.blocktxResult.setAlignment(Qt.AlignCenter)
        difficultyLabel = QLabel("Difficulty: ")
        self.difficultyResult = QLabel(" - ")
        self.difficultyResult.setAlignment(Qt.AlignCenter)
        hashpsLabel = QLabel("Hash P/S: ")
        self.hashpsResult = QLabel(" - ")
        self.hashpsResult.setAlignment(Qt.AlignCenter)
        groupMiningLayout.addRow(weightLabel, self.weightResult)
        groupMiningLayout.addRow(blocktxLabel, self.blocktxResult)
        groupMiningLayout.addRow(difficultyLabel, self.difficultyResult)
        groupMiningLayout.addRow(hashpsLabel, self.hashpsResult)
        groupMining.setLayout(groupMiningLayout)


        allStatus = QWidget()
        allStatusLayout = QGridLayout()
        allStatusLayout.addWidget(groupChain, 0, 0)
        allStatusLayout.addWidget(groupNetwork, 0, 1)
        allStatusLayout.addWidget(groupMempool, 1, 0)
        allStatusLayout.addWidget(groupMining, 1, 1)
        allStatus.setLayout(allStatusLayout)

        STATUSlayout.addWidget(groupConn)
        STATUSlayout.addWidget(allStatus)
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

