




import sys, time, random, json
from PySide2.QtWidgets import ( QApplication, QMainWindow, QMenuBar, QMenu, QStatusBar, QPushButton,
                            QLabel, QLineEdit, QGridLayout, QWidget, QFormLayout, QVBoxLayout,
                            QAction, QHBoxLayout, QGroupBox, QTextEdit )

#import lib.network

class LeftMenu():
    def __init__(self):
        super().__init__()

        self.layout = QFormLayout()

        self.LABEL = QLabel()
        self.LABEL.setText("FIGA")

        self.layout.addRow(self.LABEL)


app = QApplication(sys.argv)

leftm = QWidget()
menu = LeftMenu()

leftm.setLayout(menu.layout)

leftm.show()

app.exec_()

