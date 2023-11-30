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


import lib.network
import lib.crypto
import json, threading, time, queue

from lib.protocol import Commands

class Client:
    def __init__(self):

        self.network = lib.network.Client()
        self.certificate = "fefa" # temporary certificate
        self.calls = False
        
        self.systemInfo = False
        self.statusInfo = False

        self.nettotalsInfo = False
        self.networkInfo = False
        self.peersInfo = False
        
        self.lastStatusUpdate = False
        self.lastPeersUpdate = False
        self.lastConnCheck = False
        
    
    def initHashedCalls(self):
        if self.network.isConnected:
            self.calls = {call : lib.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode) for call in Commands.calls}
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
            
    def closeConnection(self):
        if self.network.isConnected:
            self.network.disconnectServer()
            self.calls = False
        
    def keepAlive(self):
        if self.network.isConnected and self.network.sender(self.calls['keepalive']):
            reply = self.network.receiver()
            self.lastConnCheck = time.time()

    def getSystemInfo(self):
        if self.network.isConnected and self.network.sender(self.calls['systeminfo']):
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
    
    def advancedCall(self, call, arg = False):
        if self.network.isConnected and self.network.sender(self.calls['advancedcall']):
            #encodedCall = lib.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode)
            jsonCommand = {'call': call, 'arg': arg}
            self.network.sender(json.dumps(jsonCommand))
            reply = self.network.receiver()
            return reply

    def getBitnodesInfo(self, extIP, port):
        context = ssl.create_default_context()
        node = str(extIP) + str("-") + str(port)
        bitnodesUrl = "https://bitnodes.io/api/v1/nodes/" + node
        req = urllib.request.Request(url=bitnodesUrl, headers={'User-Agent': 'Mozilla/5.0'})
        nodeInfo = json.loads(urllib.request.urlopen(req, context = context).read().decode())
        return nodeInfo

def clientTerminal():
    remoteConn = Client()
    eventThread = threading.Event()
    keepAliveThread = threading.Thread(target = keepConnAlive, daemon = True)
    def keepConnAlive():
        while remoteConn.network.isConnected:
            eventThread.wait()
            remoteConn.keepAlive()
            time.sleep(10)

    print("Bitcoin Core Handler terminal")
    ipAddr = input("insert server ip: \n>> ")
    input("\nPress enter to connect\n")
    remoteConn.initConnection(ipAddr)
    
    print(f"Handshake code: {self.network.handshakeCode} \n")
    print("receiving info from server...")
    time.sleep(0.5)
    print(f"connected to server: {remoteConn.network.isConnected}\n")

    try:

        while True:
            print("[1] - remote server info")
            print("[2] - bitcoin node status info")
            print("[3] - send advanced call")
            print("[0] - print remote server info")
            command = int(input(">> "))
            if command == 0: break
            elif command == 1: print(remoteConn.systemInfo)
            elif command == 2: print(remoteConn.statusInfo)
            elif command == 3: 
                call = input("\ninsert call: ")
                eventThread.clear()
                remoteReply = remoteConn.advancedCall(call)
                eventThread.set()
                print(remoteReply)
            print("\n")
        remoteConn.closeConnection()

    except KeyboardInterrupt:
        remoteConn.closeConnection()
        print("closing")
