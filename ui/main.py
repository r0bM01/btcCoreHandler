




import sys, time, random, json
from PySide2.QtCore import Qt
from PySide2.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout,
                            QAction, QHBoxLayout, QGroupBox, QTextEdit )

#import lib.network


ALL_CSS = """
            QPushButton {
                border-radius: 4px;
                background-color: #bdc3c7;
                font-weight: 500;
                width: 40px;
                height: 40px;
            }
            QPushButto:hover {
                background-color: #a9b0b6;
            }
"""

class LeftMenu(QWidget):
    def __init__(self):
        super().__init__()

        

        self.layout = QVBoxLayout()

        self.labelTitle = QLabel()
        self.labelTitle.setText("btcCoreHandler")
        self.labelTitle.setAlignment(Qt.AlignBottom | Qt.AlignCenter)

        self.STATUS = QPushButton()
        self.STATUS.setText("Status")

        self.NETWORK = QPushButton()
        self.NETWORK.setText("Network")

        self.ADVANCED = QPushButton()
        self.ADVANCED.setText("Advanced")

        self.OPTIONS = QPushButton()
        self.OPTIONS.setText("Options")

        self.labelVersion = QLabel()
        self.labelVersion.setText("0.0.1 Alpha")

        self.layout.addWidget(self.labelTitle)
        self.layout.addWidget(self.STATUS)
        self.layout.addWidget(self.NETWORK)
        self.layout.addWidget(self.ADVANCED)
        self.layout.addWidget(self.OPTIONS)
        self.layout.addStretch(1)
        self.layout.addWidget(self.labelVersion)
        #self.setStyleSheet("QPushButton:hover { background-color: #a9b0b6; border: 1px solid }")


class Status(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.GROUP = QGroupBox("STATUS PORCO")

        self.layout.addWidget(self.GROUP)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(640, 500)
        self.mainLayout = QHBoxLayout()

        self.left_Menu = LeftMenu()
        self.status_Page = Status()

        self.mainLayout.addLayout(self.left_Menu.layout)
        self.mainLayout.addLayout(self.status_Page.layout)


        container = QWidget()
        container.setLayout(self.mainLayout)
        self.setCentralWidget(container)
        



app = QApplication(sys.argv)
app.setStyleSheet(ALL_CSS)

window = MainWindow()
window.show()

app.exec_()

