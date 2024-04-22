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


import lib.shared.crypto
import socket, ssl, time, ipaddress
import urllib.request

class Proto:
    _remoteSock = False
    _bufferSize = 2048 # bytes
    _msgMaxSize = 2097152 # 2 MiB
    _opTimeout = 3 # seconds
    _header = 4 # number of hex digits ex. 00ff

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
        tmpTimeout = self._remoteSock.gettimeout()
        self._remoteSock.settimeout(self._opTimeout)
        
        lenghtMsg = bytes.fromhex(hex(len(data))[2:].zfill(self._header*2))
        lenghtSent = self.sockSend(lenghtMsg)

        dataSent = 0
        if lenghtSent == len(lenghtMsg):

            while dataSent < len(data):
                
                chunk = self.sockSend(data[dataSent:])

                if not bool(chunk): break
                dataSent += chunk
        
        self._remoteSock.settimeout(tmpTimeout)
        return True if dataSent == len(data) else False
        
    def dataRecv(self, maxSize = False):

        msgMaxSize = int(maxSize) if bool(maxSize) else self._msgMaxSize
        lenghtMsg = self.sockRecv(self._header)

        tmpTimeout = self._remoteSock.gettimeout()
        self._remoteSock.settimeout(self._opTimeout)

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
        
        self._remoteSock.settimeout(tmpTimeout)
        return  b"".join(dataArray) if dataRecv == lenghtMsg else b"" # False
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

    def receiveClient(self, certificate):
        try:
            self._remoteSock, self.remoteAddr = self.socket.accept()
            self._remoteSock.settimeout(self._opTimeout)
            # self.sender(handshakeCode)
            # self.handshakeCode = handshakeCode
        except OSError:
            self.sockClosure()
            self.handshakeCode = False
        if bool(self._remoteSock): self.handshakeProcess(certificate)
        if bool(self.handshakeCode): self._remoteSock.settimeout(self.settings.remoteSockTimeout)
    
    def handshakeProcess(self, certificate):
        clientRandom = self.dataRecv(16)
        serverRandom = lib.shared.crypto.getRandomBytes(16)
        entropy = clientRandom + serverRandom
        if bool(clientRandom) and self.dataSend(serverRandom):
            handshakeCode = lib.shared.crypto.getHandshakeCode(entropy, certificate)
            request = lib.shared.crypto.getHashedCommand("handshake", certificate, handshakeCode)
            confirm = lib.shared.crypto.getHashedCommand("handshakeaccepted", certificate, handshakeCode)
            if self.dataRecv(16) == bytes.fromhex(request):
                self.handshakeCode = handshakeCode if self.dataSend(bytes.fromhex(confirm)) else False
        if not bool(self.handshakeCode): self.sockClosure()
        
            
        
###########################################################################################################
###########################################################################################################

class ServerRPC(Proto):
    def __init__(self, port = 46001):
        self.host = "127.0.0.1"
        self.port = int(port)

    def openSocket(self):
        try:
            self.socket = socket.create_server((self.host, self.port), family = socket.AF_INET,
                                                backlog = 1, reuse_port = True)
            self.socket.settimeout(None) #base server socket has no timeout. It blocks until a client is connecting
        except OSError:
            self.socket = False

    def receiveClient(self):
        try:
            self._remoteSock, self.remoteAddr = self.socket.accept()
            self._remoteSock.settimeout(self._opTimeout)

        except OSError:
            self.sockClosure()
            

class ClientRPC(Proto):
    def __init__(self, port = 46001):
        self.host = "127.0.0.1"
        self.port = int(port)
    
    def connect(self):
        try:
            self._remoteSock = socket.create_connection((self.remoteHost, self.remotePort), timeout = self._opTimeout)
            #self._remoteSock.settimeout(10)
            # self.handshakeCode = self.receiver()
            # self.isConnected = True if len(self.handshakeCode) == 32 else False
        except (OSError, TimeoutError):
            self.isConnected = False
            self._remoteSock = False
        
        return bool(self._remoteSock)

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
    def checkInternet(dest = False):
        addr = dest or 'https://8.8.8.8'
        if 'https://' and 'http://' not in addr: 
            addr = 'https://' + addr
        if 'https://' in addr:
            context = ssl.create_default_context()
        else:
            context = False 
        try:
            request = urllib.request.Request(url = addr, headers = {'User-Agent': 'Mozilla/5.0'})
            test = urllib.request.urlopen(request, context = context, timeout = 2).read().decode()
            return True
        except urllib.request.URLError: 
            return False
    
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

    @staticmethod
    def getCheckedIp(ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def getPackedIp(ip):
        return ipaddress.ip_address(ip).packed
    
    @staticmethod
    def getExplodedIp(packedIp):
        return ipaddress.ip_address(packedIp).exploded