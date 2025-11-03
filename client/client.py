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

import lib.shared.commands
import lib.shared.crypto
import lib.client.network
import lib.shared.settings
import lib.shared.storage
import json, threading, time, queue, pathlib



class Client:
    def __init__(self, certificate):

        self.version = lib.shared.settings.VERSION

        self.control = lib.shared.commands.Control()

        self.network = lib.client.network.Client()

        #self.storage = lib.share.storage.Client()

        self.certificate = certificate
        self.calls = False
        
        self.systemInfo = False
        self.statusInfo = False
        self.connectedInfo = False

        self.nettotalsInfo = False
        self.networkInfo = False
        self.peersInfo = False

        self.peersGeolocation = False
        
        self.bitcoindRunning = False
        self.lastStatusUpdate = False
        self.lastPeersUpdate = False
        self.lastConnCheck = False
        
    def load_certificate(self):
        if self.storage.check_base_dir():
            if self.storage.check_exists(self.storage.saveFiles['cert']):
                if self.storage.check_certificate():
                    return self.storage.load_certificate()
        return False


    def initHashedCalls(self):
        if self.network.isConnected:
            self.calls = {call : lib.shared.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode) for call in self.control.calls}
        else:
            self.calls = False

    def initConnection(self, host, port = False):
        if not self.network.isConnected and bool(self.certificate): 
            self.network.remoteHost = str(host)
            self.network.connectToServer()
            self.network.make_handshake(self.certificate)
        if self.network.isConnected:
            self.initHashedCalls()
            self.getSystemInfo()
            self.getStatusInfo()
            # self.getPeersInfo()
            # self.getPeersGeolocation()
            self.getConnectedInfo()
            
    def closeConnection(self):
        if self.network.isConnected:
            self.network.disconnectServer()
            self.calls = False
            self.systemInfo = False
            self.statusInfo = False
        
    def keepAlive(self):
        if self.network.isConnected and self.network.sender(self.calls['keepalive']):
            reply = self.network.receiver()
            self.lastConnCheck = time.time()
            if not bool(reply): self.network.disconnectServer()

    def getSystemInfo(self):
        if self.network.isConnected and self.network.sender(self.calls['getsysteminfo']):
            reply = self.network.receiver()
            self.systemInfo = json.loads(reply) if bool(reply) else False

    def getStatusInfo(self):
        if self.network.isConnected and self.network.sender(self.calls['getstatusinfo']):
            reply = self.network.receiver()
            self.statusInfo = json.loads(reply) if bool(reply) else False
            self.bitcoindRunning = bool(self.statusInfo['uptime'])
            self.lastStatusUpdate = time.time()
            self.lastConnCheck = time.time()
    
    def getConnectedInfo(self):
        if self.network.isConnected and self.network.sender(self.calls['getconnectedinfo']):
            reply = self.network.receiver()
            self.connectedInfo = json.loads(reply) if bool(reply) else False
            self.lastPeersUpdate = time.time()
            self.lastConnCheck = time.time()
    
    def getPeersInfo(self):
        if self.network.isConnected and self.network.sender(self.calls['getpeerinfo']):
            reply = self.network.receiver()
            self.peersInfo = json.loads(reply) if bool(reply) else False
            self.lastPeersUpdate = time.time()
            self.lastConnCheck = time.time()
        
    def getPeersGeolocation(self):
        if self.network.isConnected and self.network.sender(self.calls["getgeolocationinfo"]):
            self.peersGeolocation = json.loads(self.network.receiver())
    
    def getGeneralCall(self, call):
        if self.network.isConnected and self.network.sender(self.calls[call]):
            return json.loads(self.network.receiver())

    def addnodeCall(self, nodeAddress = False, nodeCommand = 'getaddednodeinfo'):
        if nodeCommand == 'getaddednodeinfo': return self.getGeneralCall(nodeCommand)
        if not bool(nodeAddress) or not bool(nodeCommand): return {"error": "node host and command required"}
        if nodeCommand in ['add', 'remove', 'onetry']:
            args = nodeAddress + str(" ") + nodeCommand
            reply = self.advancedCall("addnode", args)
            return reply

    def advancedCall(self, call, arg = False):
        if call not in self.calls: return {"error": "invalid command"}
        msg = str(self.calls['advancedcall']) + str(self.calls[call])
        if bool(arg): msg += str(arg)
        if self.network.isConnected and self.network.sender(msg):
            # encodedCall = lib.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode)
            # self.network.sender(json.dumps({'call': call, 'arg': arg}))
            reply = self.network.receiver()
            return json.loads(reply)
    """
    def getBitnodesInfo(self, extIP, port):
        # 300 requests per day only. For peers geolocation use "getPeersGeolocation"
        context = lib.network.Utils.ssl_default_context()
        node = str(extIP) + str("-") + str(port)
        bitnodesUrl = "https://bitnodes.io/api/v1/nodes/" + node
        req = urllib.request.Request(url=bitnodesUrl, headers={'User-Agent': 'Mozilla/5.0'})
        nodeInfo = json.loads(urllib.request.urlopen(req, context = context).read().decode())
        return nodeInfo
    
    """          
            


    """
    def getstatusinfo(self):
        message = {}
        #message['startData'] = self.startDate
        message['uptime'] = self.CACHE.bitcoin['uptime']['uptime']
        message['chain'] = self.CACHE.bitcoin['blockchainInfo']['chain']
        message['blocks'] = self.CACHE.bitcoin['blockchainInfo']['blocks']
        message['headers'] = self.CACHE.bitcoin['blockchainInfo']['headers']
        message['verificationprogress'] = self.CACHE.bitcoin['blockchainInfo']['verificationprogress']
        message['pruned'] = self.CACHE.bitcoin['blockchainInfo']['pruned']
        message['size_on_disk'] = self.CACHE.bitcoin['blockchainInfo']['size_on_disk']

        message['version'] = self.CACHE.bitcoin['networkInfo']['version']
        message['subversion'] = self.CACHE.bitcoin['networkInfo']['subversion']
        message['protocolversion'] = self.CACHE.bitcoin['networkInfo']['protocolversion']
        message['connections'] = self.CACHE.bitcoin['networkInfo']['connections']
        message['connections_in'] = self.CACHE.bitcoin['networkInfo']['connections_in']
        message['connections_out'] = self.CACHE.bitcoin['networkInfo']['connections_out']
        message['localservicesnames'] = self.CACHE.bitcoin['networkInfo']['localservicesnames']
        message['networks'] = self.CACHE.bitcoin['networkInfo']['networks']
        message['relayfee'] = self.CACHE.bitcoin['networkInfo']['relayfee']

        message['totalbytessent'] = self.CACHE.bitcoin['nettotalsInfo']['totalbytessent']
        message['totalbytesrecv'] = self.CACHE.bitcoin['nettotalsInfo']['totalbytesrecv']

        message['difficulty'] = self.CACHE.bitcoin['miningInfo']['difficulty']
        message['networkhashps'] = self.CACHE.bitcoin['miningInfo']['networkhashps']

        message['size'] = self.CACHE.bitcoin['mempoolInfo']['size']
        # message['bytes'] = self.mempoolInfo['bytes']
        message['usage'] = self.CACHE.bitcoin['mempoolInfo']['usage']
        message['mempoolminfee'] = self.CACHE.bitcoin['mempoolInfo']['mempoolminfee']
        message['fullrbf'] = self.CACHE.bitcoin['mempoolInfo']['fullrbf']
        return message
        """