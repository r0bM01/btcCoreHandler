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


class Test(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        
        label = QLabel("Pistelly pussy super hot")

        layout.addWidget(label)
        self.setLayout(layout)
        self.modal(True)
        #self.setWindowModality(Qt.ApplicationModal)

        #
        #self.setVisible(False)

class Alerts(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setText("none")
    
    def showRelease(self):
        self.setWindowTitle("Software Release")
        self.setText("Bitcoin Core Handler 0.1.0-Alpha coded by R0BM01")
        self.exec()

    def missingIPAddress(self):
        self.setWindowTitle("Address Missing")
        self.setText("You have to insert the node's address to connect to.")
        self.setInformativeText("You can check the connection settings in 'options' page.")
        self.exec()

    def disconnectedNode(self):
        self.setWindowTitle("Disconnected")
        self.setText("The connection to the node has been closed.")
        self.exec()
        
        