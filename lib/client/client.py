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
import lib.shared.network
import lib.shared.settings
import json, threading, time, queue, pathlib



class Client:
    def __init__(self):

        self.version = lib.shared.settings.VERSION

        self.control = lib.shared.commands.Control()

        self.network = lib.shared.network.Client()
        self.certificate = self.load_certificate()
        self.calls = False
        
        self.systemInfo = False
        self.statusInfo = False

        self.nettotalsInfo = False
        self.networkInfo = False
        self.peersInfo = False

        self.peersGeolocation = False
        
        self.lastStatusUpdate = False
        self.lastPeersUpdate = False
        self.lastConnCheck = False
        
    def load_certificate(self):
        cwd = pathlib.Path.cwd()
        path = cwd.joinpath("lib/client/cert.rob")
        with open(path, "rb") as F:
            dataBytes = F.read()
        return dataBytes.hex()

    def initHashedCalls(self):
        if self.network.isConnected:
            self.calls = {call : lib.shared.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode) for call in self.control.calls}
        else:
            self.calls = False

    def initConnection(self, host, port = False):
        if not self.network.isConnected: 
            self.network.remoteHost = str(host)
            self.network.connectToServer(self.certificate)
        if self.network.isConnected:
            self.initHashedCalls()
            self.getSystemInfo()
            self.getStatusInfo()
            self.getPeersInfo()
            self.getPeersGeolocation()
            
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
            self.lastStatusUpdate = time.time()
            self.lastConnCheck = time.time()
    
    def getPeersInfo(self):
        if self.network.isConnected and self.network.sender(self.calls['getpeerinfo']):
            reply = self.network.receiver()
            self.peersInfo = json.loads(reply) if bool(reply) else False
            self.lastPeersUpdate = time.time()
            self.lastConnCheck = time.time()
        
    def getAllNetworkInfo(self):
        if self.network.isConnected and self.network.sender(self.calls['getnettotals']):
            reply = self.network.receiver()
            self.nettotalsInfo = json.loads(reply)
        if self.network.isConnected and self.network.sender(self.calls['getnetworkinfo']):
            reply = self.network.receiver()
            self.networkInfo = json.load(reply)
        if self.network.isConnected and self.network.sender(self.calls['getpeerinfo']):
            reply = self.network.receiver()
            self.peersInfo = json.loads(reply)

    def getPeersGeolocation(self):
        if self.network.isConnected and self.network.sender(self.calls["getgeolocationinfo"]):
            self.peersGeolocation = json.loads(self.network.receiver())
    
    def getGeneralCall(self, call):
        if self.network.isConnected and self.network.sender(self.calls[call]):
            return json.loads(self.network.receiver())

    def addnodeCall(self, nodeAddress, nodeCommand):
        if not bool(nodeAddress) or not bool(nodeCommand): return {"error": "node host and command required"}
        if nodeCommand in ['add', 'remove', 'onetry']:
            args = nodeAddress + str(" ") + nodeCommand
            reply = self.advancedCall("addnode", args)
            return reply

    def advancedCall(self, call, arg = False):
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
            


