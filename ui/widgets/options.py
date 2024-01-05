


from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout, QHeaderView,
                            QHBoxLayout, QGroupBox, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem )


class Options(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        buttons = dict()

        groupConnectionSettings = QGroupBox("Node")
        addressForm = QFormLayout()
        hostLabel = QLabel("Host:")
        portLabel = QLabel("Port:")
        self.hostEdit = QLineEdit("192.168.1.238")
        self.portEdit = QLineEdit("4600")
        addressForm.addRow(hostLabel, self.hostEdit)
        addressForm.addRow(portLabel, self.portEdit)
        groupConnectionSettings.setLayout(addressForm)


        buttonsLayout = QHBoxLayout()
        buttons['clear'] = QPushButton("Clear")
        buttons['save'] = QPushButton("Save")
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(buttons['clear'])
        buttonsLayout.addWidget(buttons['save'])

        layout.addWidget(groupConnectionSettings)
        layout.addStretch()
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)