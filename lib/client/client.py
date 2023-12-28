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


import lib.shared.network
import lib.shared.crypto
import json, threading, time, queue
from collections import Counter

class Commands:
    
    calls = {'uptime', 'start', 'stop', 'keepalive',
            'getstatusinfo', 'getblockchaininfo', 'getnetworkinfo', 
            'getmempoolinfo', 'getmininginfo', 'getpeerinfo', 'getnettotals',
            'advancedcall', 'getsysteminfo', 'getgeolocationinfo'}

class Client:
    def __init__(self):

        self.network = lib.shared.network.Client()
        self.certificate = "fefa" # temporary certificate
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
        
    
    def initHashedCalls(self):
        if self.network.isConnected:
            self.calls = {call : lib.shared.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode) for call in Commands.calls}
        else:
            self.calls = False

    def initConnection(self, host, port = False):
        if not self.network.isConnected: 
            self.network.remoteHost = str(host)
            self.network.connectToServer()
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
    
    def advancedCall(self, call, arg = False):
        if self.network.isConnected and self.network.sender(self.calls['advancedcall']):
            #encodedCall = lib.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode)
            self.network.sender(json.dumps({'call': call, 'arg': arg}))
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
            


def clientTerminal():
    def keepConnAlive():
        while remoteConn.network.isConnected:
            eventThread.wait()
            remoteConn.keepAlive()
            time.sleep(10)
        print("\nconnection terminated")

    remoteConn = Client()
    eventThread = threading.Event()
    keepAliveThread = threading.Thread(target = keepConnAlive, daemon = True)

    print("Bitcoin Core Handler terminal")
    ipAddr = input("insert server ip: \n>> ")
    input("\nPress enter to connect\n")
    remoteConn.initConnection(ipAddr)
    
    print(f"Handshake code: {remoteConn.network.handshakeCode} \n")
    print("receiving info from server...")
    time.sleep(0.5)
    print(f"connected to server: {remoteConn.network.isConnected}\n")

    if remoteConn.network.isConnected:
        eventThread.set()
        keepAliveThread.start()
        print("keep alive thread started")
        
    try:

        while True and remoteConn.network.isConnected:
            print("[1] - remote server info")
            print("[2] - bitcoin node status info")
            print("[3] - print all peers geolocation")
            print("[4] - print contries stats")
            print("[5] - send advanced call")
            print("[0] - quit terminal")
            command = int(input(">> "))
            if not bool(command): command = 0
            if command == 0: break
            elif command == 1: print(remoteConn.systemInfo)
            elif command == 2: print(remoteConn.statusInfo)
            elif command == 3: [print(node) for node in remoteConn.peersGeolocation]
            elif command == 4: [print(f"{c[0]} : {c[1]}") for c in Counter([node[1] for node in remoteConn.peersGeolocation]).items()]
            elif command == 5: 
                insertedCommand = input("\ninsert call: ")
                fullCommand = insertedCommand.lower().split(" ", 1)
                command = fullCommand[0]
                if command != "start" and command != "stop":
                    arg = fullCommand[1] if len(fullCommand) > 1 else False
                    eventThread.clear()
                    remoteReply = remoteConn.advancedCall(command, arg)
                    eventThread.set()
                    print(remoteReply)
                else:
                    print("control commands not allowed")
            print("\n")
        remoteConn.closeConnection()

    except KeyboardInterrupt:
        remoteConn.closeConnection()
        print("closing")
