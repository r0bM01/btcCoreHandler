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
    _msgMaxSize = 2097152 # 2 MiB
    _opTimeout = 5
    _header = 4

    #################################################
        # LOW LEVEL SOCKET SEND/RECEIVE
    def sockSend(self, msg):
        try:
            msgSent = self._remoteSock.send(msg, socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            msgSent = 0
        return msgSent
    
    def sockRecv(self, size):
        try:
            msg = self._remoteSock.recv(int(size), socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            msg = b""
        return msg

    def sockClosure(self):
        try: 
            self._remoteSock.shutdown(socket.SHUT_RDWR)
            self._remoteSock.close()
        except (OSError, AttributeError):
            pass
        self._remoteSock = False
    #################################################
   
    
    ###########################################################################################################
        # MESSAGE SEND/RECEIVE WITH CONFIRM
    def dataSend(self, data):
        #tmpTimeout = self._remoteSock.gettimeout()
        #self._remoteSock.settimeout(self._opTimeout)
        
        lenghtMsg = bytes.fromhex(hex(len(data))[2:].zfill(self._header*2))
        lenghtSent = self.sockSend(lenghtMsg)

        dataSent = 0
        if lenghtSent == len(lenghtMsg):

            while dataSent < len(data):
                
                chunk = self.sockSend(data[dataSent:])

                if not bool(chunk): break
                dataSent += chunk
        
        #self._remoteSock.settimeout(tmpTimeout)
        return True if dataSent == len(data) else False
        
    def dataRecv(self, maxSize = False):
        #tmpTimeout = self._remoteSock.gettimeout()
        #self._remoteSock.settimeout(self._opTimeout)
        msgMaxSize = int(maxSize) if bool(maxSize) else self._msgMaxSize
        lenghtMsg = self.sockRecv(self._header)

        dataRecv = 0
        if bool(lenghtMsg):
            lenghtMsg = int(lenghtMsg.hex(), 16)
            if lenghtMsg <= msgMaxSize:
                dataArray = []
                while dataRecv < lenghtMsg:

                    chunk = self.sockRecv(min(lenghtMsg - dataRecv, self._bufferSize))
                    
                    if not bool(chunk): break
                    dataRecv += len(chunk)
                    dataArray.append(chunk)
        
        #self._remoteSock.settimeout(tmpTimeout)
        return  b"".join(dataArray) if dataRecv == lenghtMsg else False
    ###########################################################################################################
        # HIGH LEVEL INTERFACE SENDING/RECEIVING MESSAGES WITH SOCKET CLOSURE
    def sender(self, data):
        #data must be already encoded in json
        msgSent = self.dataSend(data.encode('utf-8'))
        if bool(msgSent): return True
        else: 
            self.sockClosure()
            return False
    
    def receiver(self, maxSize = False):
        msgReceived = self.dataRecv(maxSize)
        if bool(msgReceived): return msgReceived.decode('utf-8')
        else:
            self.sockClosure()
            return False

###########################################################################################################
###########################################################################################################

class Client(Proto):
    def __init__(self):
        self.remoteHost = None # has to be given by UI  
        self.remotePort = 4600 # default port
        self.timeout = self._opTimeout
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

###########################################################################################################
###########################################################################################################

class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else "" # if not provided binds it to all interfaces # socket.gethostbyname(socket.gethostname()) 
        self.port = int(port) if port else 4600

        self.socketTimeout = 30
        self.remoteSockTimeout = 120
        self.backlog = 5
        self.maxSockets = 1


class Server(Proto):
    def __init__(self, settings):
        self.settings = settings
        self.socket = False
        self.remoteAddr = None
        self.handshakeCode = False

    def openSocket(self):
        try:
            self.socket = socket.create_server((self.settings.host, self.settings.port), family = socket.AF_INET,
                                               backlog = self.settings.backlog, reuse_port = True)
            self.socket.settimeout(self.settings.socketTimeout)
        except OSError:
            self.socket = False

    def receiveClient(self, handshakeCode):
        try:
            self._remoteSock, self.remoteAddr = self.socket.accept()
            self._remoteSock.settimeout(self.settings.remoteSockTimeout)
            self.sender(handshakeCode)
            self.handshakeCode = handshakeCode
        except OSError:
            self.sockClosure()
            self.handshakeCode = False
    
###########################################################################################################
###########################################################################################################

class Utils:
    @staticmethod
    def ssl_default_context():
        return ssl.create_default_context()
    
    @staticmethod
    def getExternalIP():
        extIP = urllib.request.urlopen("https://ident.me").read().decode('utf-8')
        return extIP
    
    @staticmethod
    def getBitnodesInfo(extIP, port):
        # 300 requests per day only. For peers geolocation use "getPeersGeolocation"
        context = ssl.create_default_context()
        node = str(extIP) + str("-") + str(port)
        bitnodesUrl = "https://bitnodes.io/api/v1/nodes/" + node
        request = urllib.request.Request(url=bitnodesUrl, headers={'User-Agent': 'Mozilla/5.0'})
        nodeInfo = urllib.request.urlopen(req, context = context).read().decode()
        return nodeInfo
    
    @staticmethod
    def getGeolocation(ip):
        context = ssl.create_default_context()
        baseUrl = "https://api.iplocation.net/?ip=" + str(ip)
        request = urllib.request.Request(url=baseUrl, headers={'User-Agent': 'Mozilla/5.0'})
        locationData = urllib.request.urlopen(request, context = context).read().decode()
        return locationData
