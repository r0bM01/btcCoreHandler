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

class LeftMenu(QWidget):
    def __init__(self, pages):
        super().__init__()

        self.RESULT = {}
        self.BUTTON = {}
        self.edit = {}
        labels = {}

        self.PAGES = pages

        layout = QVBoxLayout()

        labels['title'] = QLabel()
        labels['title'].setPixmap(QPixmap("ui/assets/bitcoin_64.png"))
        labels['title'].setAlignment(Qt.AlignBottom | Qt.AlignCenter)

        for key in self.PAGES:
            self.BUTTON[key] = QPushButton(str(key).capitalize())
        
        for key in self.BUTTON:
            self.BUTTON[key].clicked.connect(lambda x: self.menu_buttons(key))

        """
        self.BUTTON['STATUS'] = QPushButton("Status")
        self.BUTTON['NETWORK'] = QPushButton("Network")
        self.BUTTON['ADVANCED'] = QPushButton("Advanced")
        self.BUTTON['OPTIONS'] = QPushButton("Options")
        """

        labels['version'] = QLabel()
        labels['version'].setText("0.0.1 Alpha")
        #labelVersion.clicked.connect(QMessageBox.information(self, "Info", "Version 0.0.1 coded by R0bm01"))

        layout.addWidget(labels['title'])
        [layout.addWidget(self.BUTTON[key]) for key in self.BUTTON]
        layout.addStretch(1)
        layout.addWidget(labels['version'])
        #self.setStyleSheet("QPushButton:hover { background-color: #a9b0b6; border: 1px solid }")
        
        self.setLayout(layout)
        self.setStyleSheet("QPushButton { font: bold 18px; height: 40px; }")
        self.setFixedWidth(200)

    def menu_buttons(self, button):
        for key in self.PAGES:
            self.PAGES[key].setVisible(True) if key == button else self.PAGES[key].setVisible(False)