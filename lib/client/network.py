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


import socket
from lib.shared.network import Proto



class Client(Proto):
    def __init__(self):
        self.remoteHost = None # has to be given by UI  
        self.remotePort = 4600 # default port
        self.timeout = 120
        self.isConnected = False
        self.handshakeCode = False
        
    def connectToServer(self, certificate):
        try:
            self._remoteSock = socket.create_connection((self.remoteHost, self.remotePort), timeout = self._opTimeout)
            #self._remoteSock.settimeout(10)
            # self.handshakeCode = self.receiver()
            # self.isConnected = True if len(self.handshakeCode) == 32 else False
        except (OSError, TimeoutError):
            self.isConnected = False
            self._remoteSock = False
        
        if bool(self._remoteSock): 
            self.handshakeProcess(certificate)

    def disconnectServer(self):
        #self._remoteSock.close()
        #self._remoteSock = False
        self.sockClosure()
        self.isConnected = False
        self.handshakeCode = False
    
    def handshakeProcess(self, certificate):
        clientRandom = lib.shared.crypto.getRandomBytes(16)
        serverRandom = self.dataRecv(16) if self.dataSend(clientRandom) else False
        entropy = clientRandom + serverRandom
        if bool(serverRandom):
            handshakeCode = lib.shared.crypto.getHandshakeCode(entropy, certificate)
            request = lib.shared.crypto.getHashedCommand("handshake", certificate, handshakeCode)
            confirm = lib.shared.crypto.getHashedCommand("handshakeaccepted", certificate, handshakeCode)
            if self.dataSend(bytes.fromhex(request)) and self.dataRecv(8) == bytes.fromhex(confirm):
                self.handshakeCode = handshakeCode
                self.isConnected = True
                self._remoteSock.settimeout(self.timeout)
        if not bool(self.handshakeCode): self.sockClosure() 