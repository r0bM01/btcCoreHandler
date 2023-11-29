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



import socket, threading, ssl, time
import urllib.request

class Proto:
    _remoteSock = False
    _bufferSize = 2048
    _opTimeout = 5
    
    def sockClosure(self):
        try: 
            self._remoteSock.shutdown(socket.SHUT_RDWR)
            self._remoteSock.close()
        except (OSError, AttributeError):
            pass
        self._remoteSock = False

    #################################################
    def sockSend(self, msg):
        try:
            msgSent = self._remoteSock.send(msg, socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            msgSent = 0
        return True if msgSent == len(msg) else False
    
    def sockRecv(self, size):
        try:
            msg = self._remoteSock.recv(int(size), socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            msg = b""
        return msg if len(msg) == int(size) else False
    #################################################
    def highSend(self, data):
        tmpTimeout = self._remoteSock.gettimeout()
        self._remoteSock.settimeout(self._opTimeout)
        flag = True
        chunks = [data[c:c+self._bufferSize] for c in range(0, len(data), self._bufferSize)]
        for c in chunks:
            if not self.sockSend(c) or not bool(self.sockRecv(1)):
                flag = False
                break
        self._remoteSock.settimeout(tmpTimeout)
        return flag
        
    def highRecv(self, size):
        #tmpTimeout = self._remoteSock.gettimeout()
        #self._remoteSock.settimeout(self._opTimeout)
        bytesRecv = 0
        dataArray = []
        while bytesRecv < size:
            chunk = self.sockRecv(min(size - bytesRecv, self._bufferSize))
            if bool(chunk):
                self.sockSend(b"1")
                dataArray.append(chunk)
                bytesRecv += len(chunk)
            else:
                break
        return b"".join(dataArray)

    def sender(self, data):
        #data must be already encoded in json
        data = data.encode()
        dataLenght = hex(len(data))[2:].zfill(8)
        dataLenght = bytes.fromhex(dataLenght)
        dataSent = False
        if self.sockSend(dataLenght):
            if len(data) > self._bufferSize:
                dataSent = self.highSend(data)
            else:
                dataSent = self.sockSend(data)
        if dataSent:
            return True
        else:
            #self._remoteSock.close()
            #self._remoteSock = False
            self.sockClosure()
            return False
    
    def receiver(self):
        #self._remoteSock.settimeout(30)
        dataLenght = self.sockRecv(4)
        if dataLenght:
            dataLenght = int(dataLenght.hex(), 16)
            if dataLenght > self._bufferSize:
                data = self.highRecv(dataLenght)
            else:
                data = self.sockRecv(dataLenght)
        if dataLenght and data:
            return data.decode()
        else:
            #self._remoteSock.close()
            #self._remoteSock = False
            self.sockClosure()
            return False

class Client(Proto):
    def __init__(self):
        self.remoteHost = "192.168.1.238"
        self.remotePort = 4600
        self.timeout = None
        self.isConnected = False
        self.handshakeCode = False

    def connectToServer(self):
        try:
            self._remoteSock = socket.create_connection((self.remoteHost, self.remotePort), timeout = self.timeout)
            #self._remoteSock.settimeout(10)
            self.handshakeCode = self.receiver()
            self.isConnected = True if len(self.handshakeCode) == 32 else False
        except (OSError, TimeoutError):
            self.isConnected = False
            self._remoteSock = False

    def disconnectServer(self):
        #self._remoteSock.close()
        #self._remoteSock = False
        self.sockClosure()
        self.isConnected = False
        self.handshakeCode = False


class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else "192.168.1.238" #socket.gethostbyname(socket.gethostname()) #"192.168.1.238"
        self.port = int(port) if port else 4600

        self.socketTimeout = 30
        self.remoteSockTimeout = 120
        self.backlog = 5
        self.maxSockets = 1


class Server(Proto):
    def __init__(self, settings):
        self.settings = settings
        self.socket = False

    def openSocket(self):
        try:
            self.socket = socket.create_server((self.settings.host, self.settings.port), family = socket.AF_INET,
                                               backlog = self.settings.backlog, reuse_port = True)
            self.socket.settimeout(self.settings.socketTimeout)
        except OSError:
            self.socket = False

    def receiveClient(self, handshakeCode):
        try:
            self._remoteSock, addr = self.socket.accept()
            self._remoteSock.settimeout(self.settings.remoteSockTimeout)
            self.sender(handshakeCode)
        except OSError:
            self.sockClosure()
    
    def getExternalIP(self):
        extIP = urllib.request.urlopen("https://ident.me").read().decode('utf-8')
        return extIP
    
        


