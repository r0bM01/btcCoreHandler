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



class Advanced(QWidget):
    def __init__(self):
        super().__init__()

        self.RESULT = {}
        self.BUTTON = {}
        self.edit = {}
        labels = {}

        layout = QVBoxLayout()

        controller = QGroupBox("Bitcoin Daemon")
        controller.setCheckable(True)
        controller.setChecked(False)

        controllerLayout = QHBoxLayout()
        self.BUTTON['start'] = QPushButton("Start")
        self.BUTTON['stop'] = QPushButton("Stop")
        controllerLayout.addWidget(self.BUTTON['start'])
        controllerLayout.addWidget(self.BUTTON['stop'])
        

        controller.setLayout(controllerLayout)

        consoleForm = QHBoxLayout()
        labels['command'] = QLabel("command:")
        self.edit['command'] = QLineEdit()
        self.BUTTON['command'] = QPushButton()
        self.BUTTON['command'].setIcon(QPixmap("ui/assets/play_32.png"))
        self.BUTTON['command'].setFixedWidth(35)
        
        consoleForm.addWidget(labels['command'])
        consoleForm.addWidget(self.edit['command'])
        consoleForm.addWidget(self.BUTTON['command'])

        self.RESULT['command'] = QTextEdit()
        self.RESULT['command'].setReadOnly(True)

        layout.addWidget(controller)
        layout.addLayout(consoleForm)
        layout.addWidget(self.RESULT['command'])

        self.setLayout(layout)