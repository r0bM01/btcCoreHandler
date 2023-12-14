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
   
    
    ###########################################################################################################
    def dataSend(self, data):
        #tmpTimeout = self._remoteSock.gettimeout()
        #self._remoteSock.settimeout(self._opTimeout)
        
        lenghtMsg = bytes.fromhex(hex(len(data))[2:].zfill(8))

        try:
            lengtSent = self._remoteSock.send(lenghtMsg, socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            lengtSent = 0
        
        dataSent = 0
        if lengtSent == len(lenghtMsg):

            while dataSent < len(data):

                try:
                    chunk = self._remoteSock.send(data[dataSent:], socket.MSG_WAITALL)
                except (OSError, TimeoutError):
                    chunk = 0
            
                if not bool(chunk): break
                dataSent += chunk
        
        #self._remoteSock.settimeout(tmpTimeout)
        return True if dataSent == len(data) else False
        
    def dataRecv(self):
        #tmpTimeout = self._remoteSock.gettimeout()
        #self._remoteSock.settimeout(self._opTimeout)

        try:
            lenghtMsg = self._remoteSock.recv(4, socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            lenghtMsg = 0
        
        dataRecv = 0
        if bool(lenghtMsg):
            lenghtMsg = int(lenghtMsg.hex(), 16)
            
            dataArray = []
            while dataRecv < lenghtMsg:

                try:
                    chunk = self._remoteSock.recv(min(lenghtMsg - dataRecv, self._bufferSize), socket.MSG_WAITALL)
                except (OSError, TimeoutError):
                    chunk = b""
                
                if not bool(chunk): break
                dataRecv += len(chunk)
                dataArray.append(chunk)
        
        #self._remoteSock.settimeout(tmpTimeout)
        return  b"".join(dataArray) if dataRecv == lenghtMsg else False
    ###########################################################################################################


    def sender(self, data):
        #data must be already encoded in json
        msgSent = self.dataSend(data.encode())
        if bool(msgSent): return True
        else: 
            self.sockClosure()
            return False
    

    def receiver(self):
        msgReceived = self.dataRecv()
        if bool(msgReceived): return msgReceived.decode()
        else:
            self.sockClosure()
            return False
        

class Client(Proto):
    def __init__(self):
        self.remoteHost = None # has to be given by UI  
        self.remotePort = 4600 # default port
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
            self._remoteSock, addr = self.socket.accept()
            self._remoteSock.settimeout(self.settings.remoteSockTimeout)
            self.sender(handshakeCode)
            self.handshakeCode = handshakeCode
        except OSError:
            self.sockClosure()
            self.handshakeCode = False
    
    
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
