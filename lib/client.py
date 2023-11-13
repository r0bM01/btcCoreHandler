import lib.network
import lib.crypto
import json, threading, time

from lib.protocol import Commands

class AllInfo:
    def __init__(self):
        #Status Informations
        self.btcUptime = False
        self.btcChain = False
        self.btcHeaders = False
        self.btcVersion = False
        self.btcAgent = False
        self.btcConnections = False
        self.btcTransactions = False
    
    def update(self, allInfoDict):
        self.btcUptime = allInfoDict['uptime']
        self.btcChain = allInfoDict['chain']
        self.btcHeaders = allInfoDict['headers']
        self.btcVersion = allInfoDict['version']
        self.btcAgent = allInfoDict['agent']
        self.btcConnections = allInfoDict['connections']
        self.btcTransactions = allInfoDict['transactions']

class AllNetworkInfo:
    def __init__(self):
        self.netInfo = False
        self.peerInfo = False
    

class Client:
    def __init__(self):

        self.network = lib.network.Client()
        self.certificate = "fefa"

        self.calls = False


        self.statusPage = AllInfo()
        self.networkPage = AllNetworkInfo()
    
    def initHashedCalls(self):
        if self.network.isConnected:
            self.calls = {call : lib.crypto.getHashedCommand(call, self.certificate, self.network.handshakeCode) for call in Commands.calls}
        else:
            self.calls = False

    def initConnection(self):
        self.network.connectToServer()
        if self.network.isConnected:
            self.initHashedCalls()

    def getAllInfo(self):
        if self.network.isConnected:
            self.network.sender(self.calls['getallinfo'])
            reply = self.network.receiver()
            print(reply)
            if bool(reply):
                result = json.loads(reply)
            else:
                result = False
        else:
            result = False
        return result
    
    def getAllNetworkInfo(self):
        if self.network.isConnected:
            self.network.sender(self.calls['getnetworkinfo'])
            reply = self.network.receiver()
            if bool(reply):
                net = json.loads(reply)
                if "error" not in net: 
                    self.networkPage.netInfo = net
                    """
            self.network.sender(self.calls['getpeerinfo'])
            peers = json.loads(self.network.receiver())
            print(peers)
            if "error" not in peers: 
                self.networkPage.peerInfo = peers
                    """




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
