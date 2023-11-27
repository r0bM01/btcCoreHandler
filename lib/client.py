import lib.network
import lib.crypto
import json, threading, time, queue

from lib.protocol import Commands

class Client:
    def __init__(self):

        self.network = lib.network.Client()
        self.certificate = "fefa"
        self.calls = False
        
        self.statusInfo = False
        self.networkStats = False

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

    def initConnection(self):
        if not self.network.isConnected: 
            self.network.connectToServer()
        if self.network.isConnected:
            self.initHashedCalls()
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
    
    def getNetworkStats(self):
        if self.network.isConnected and self.network.sender(self.calls['getnetworkstats']):
            reply = self.network.receiver()
            self.networkStats = json.loads(reply)
    
    def advancedCall(self, call, arg = False):
        if self.network.isConnected and self.network.sender(self.calls['advancedcall']):
            #encodedCall = lib.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode)
            jsonCommand = {'call': call, 'arg': arg}
            self.network.sender(json.dumps(jsonCommand))
            reply = self.network.receiver()
            return json.loads(reply)


def main():
    print("btcCoreHandler")
    remoteConn = lib.network.Client()
    remoteConn.connectToServer()
    print(remoteConn)
    print(remoteConn.handshakeCode)

    try:

        while True:
            command = input("cmd >> ")
            hashed = lib.crypto.getHashedCommand(command, "fefa", remoteConn.handshakeCode)
            print(command)

            remoteConn.sender(hashed)
            if command == "closeconn": 
                break
            result = json.loads(remoteConn.receiver())
    
            if command == 'getpeerinfo':
                for p in result:
                    print(p['addr'])
            else:
                for key, value in result.items():
                    print(f"{key}: {value}")

    except KeyboardInterrupt:
        remoteConn.sender("closeconn")
        print("closing")
