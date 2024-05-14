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


import socket, ssl, time, ipaddress, json
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


###########################################################################################################
###########################################################################################################

        
###########################################################################################################
###########################################################################################################


###########################################################################################################
###########################################################################################################


class ClientRPC(Proto):
    def __init__(self, port = 46001):
        self.host = "127.0.0.1"
        self.port = int(port)

        self.isConnected = False
    
    def connect(self):
        try:
            self._remoteSock = socket.create_connection((self.host, self.port), timeout = self._opTimeout)
            self.isConnected = True
        except (OSError, TimeoutError):
            self.isConnected = False
            self._remoteSock = False
    
    def disconnect(self):
        self.sockClosure()
    
    def is_server_running(self):
        self.connect()
        is_on = self.isConnected
        self.sockClosure()
        return is_on
    
    def get_server_info(self):
        self.connect()
        self.sender("handlerinfo")
        info = self.receiver()
        self.sockClosure()
        return info
    
    def server_stop(self):
        self.connect()
        self.sender("handlerstop")
        confirm = self.receiver()
        self.sockClosure()


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
        if 'https://' not in addr and 'http://' not in addr: 
            addr = 'https://' + addr
        if 'https://' in addr:
            context = ssl.create_default_context()
        else:
            context = False 
        try:
            request = urllib.request.Request(url = addr, headers = {'User-Agent': 'Mozilla/5.0'})
            test = urllib.request.urlopen(request, context = context, timeout = 2).read().decode('utf-8')
            return True
        except urllib.request.URLError as e: 
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
        """
        baseUrl = "https://api.iplocation.net/?ip=" + str(ip)
        """
        baseUrl = "http://ip-api.com/json/" + str(ip) + str("?fields=26139")
        request = urllib.request.Request(url=baseUrl, headers={'User-Agent': 'Mozilla/5.0'})
        locationData = json.loads(urllib.request.urlopen(request).read().decode())
        ## format data to old mode
        geo_data = {'ip': locationData['query'], 'country_code2': locationData['countryCode'], 'country_name': locationData['country'], 'isp': locationData['isp']}
        return json.dumps(geo_data)

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