import json, time, subprocess, threading
import lib.network
import lib.storage
import lib.protocol

class DUpdater():
    def __init__(self, rpcCaller, bitcoinData):
        self.isRunning = False
        self.restTime = 30 #seconds
        self.rpcCaller = rpcCaller
        self.bitcoinData = bitcoinData
        self.thread = threading.Thread(target = self.updater_loop, daemon = True)

    def start(self):
        if not self.isRunning:
            self.thread.start()

    def stop(self):
        if self.isRunning:
            self.isRunning = False
            self.thread.join()
            lib.storage.Logger.add("autoupdater loop stopped")

    def updater_loop(self):
        self.isRunning = True
        lib.storage.Logger.add("autoupdater loop started")
        while self.isRunning:
            self.sendUpdateCall() #update all bitcoin data field
            time.sleep(self.restTime) #rest for minutes
    
    def sendUpdateCall(self):
        uptime = self.rpcCaller.runCall("uptime")
        self.bitcoinData.uptime = json.loads(uptime)

        blockchainInfo = self.rpcCaller.runCall("getblockchaininfo")
        self.bitcoinData.blockchainInfo = json.loads(blockchainInfo)
        
        networkInfo = self.rpcCaller.runCall("getnetworkinfo")
        self.bitcoinData.networkInfo = json.loads(networkInfo)

        nettotalsInfo = self.rpcCaller.runCall("getnettotals")
        self.bitcoinData.nettotalsInfo = json.loads(nettotalsInfo)

        mempoolInfo = self.rpcCaller.runCall("getmempoolinfo")
        self.bitcoinData.mempoolInfo = json.loads(mempoolInfo)
        
        miningInfo = self.rpcCaller.runCall("getmininginfo")
        self.bitcoinData.miningInfo = json.loads(miningInfo)

        peersInfo = self.rpcCaller.runCall("getpeerinfo")
        peersInfo = json.loads(peersInfo)
        self.bitcoinData.peersInfo = [p for p in peersInfo]
        
        
class Server:
    def __init__(self):
        #init procedure
        self.storage = lib.storage.Data()
        self.storage.init_files()
        lib.storage.Logger.FILE = self.storage.fileLogs

        self.calls = None #lib.protocol.Commands.encodeCalls("fefa")

        self.rpcCaller = lib.protocol.RPC()
        self.bitcoinData = lib.protocol.DaemonData()

        self.bitcoinData.PID = self.rpcCaller.checkDaemon()
        lib.storage.Logger.add("bitcoind running", bool(self.bitcoinData.PID))

        self.autoUpdater = DUpdater(self.rpcCaller, self.bitcoinData)
        #init server settings
        self.netSettings = lib.network.Settings(host = self.rpcCaller.getLocalIP())
        self.network = lib.network.Server(self.netSettings)
        
        self.isServing = False
        self.isOnline = False
    
    def check_network(self):
        self.network.openSocket()
        self.isOnline = bool(self.network.socket)
        lib.storage.Logger.add("socket online", self.isOnline)
        lib.storage.Logger.add("bind to IP", self.network.settings.host)
        

    def start_serving(self):
        self.isServing = True
        lib.storage.Logger.add("serving loop entered")
        while self.isServing:
            handshakeCode = lib.crypto.getRandomBytes(16)
            lib.storage.Logger.add("handshake code generated", handshakeCode.hex())

            self.calls = lib.protocol.Commands.encodeCalls("fefa", handshakeCode.hex())

            self.network.receiveClient(handshakeCode.hex())
            if bool(self.network._remoteSock): lib.storage.Logger.add("connected by", self.network._remoteSock)
            else: lib.storage.Logger.add("no incoming connection detected")

            while bool(self.network._remoteSock):

                encodedCall = self.network.receiver()
                lib.storage.Logger.add("call: ", encodedCall)

                if encodedCall in self.calls:

                    request = self.calls[encodedCall]
                    lib.storage.Logger.add("request: ", request)
                    if request != "closeconn": reply = self.handle_request(request)
                    else: reply = False
                        
                else:
                    reply = json.dumps({"error": "request not valid"})
                ######################################################
                if bool(reply) and bool(self.network._remoteSock):
                    lib.storage.Logger.add("reply content", len(reply.encode()))
                    replySent = self.network.sender(reply) #returns True or False
                    lib.storage.Logger.add("reply sent", replySent)
                else:
                    lib.storage.Logger.add("remote socket active", self.network._remoteSock)
                    lib.storage.Logger.add("connection closed")

        lib.storage.Logger.add("serving loop exit")

    def handle_request(self, request):
        if not bool(self.bitcoinData.PID) and request == "start":
            #starts the daemon if not running
            reply = self.rpcCaller.runCall(request)
            self.bitcoinData.PID = self.rpcCaller.checkDaemon()
            if bool(self.bitcoinData.PID): self.autoUpdater.start()

        elif not bool(self.bitcoinData.PID) and request != "start":
            reply = json.dumps({"error": "bitcoin daemon not running"})

        elif bool(self.bitcoinData.PID) and request == "start":
            reply = json.dumps({"error": "bitcoin daemon already running"})

        elif bool(self.bitcoinData.PID) and request == "stop":
            reply = self.rpcCaller.runCall(request)
            self.bitcoinData.PID = self.rpcCaller.checkDaemon()
            self.autoUpdater.stop()

        elif bool(self.bitcoinData.PID) and request == "getstatusinfo":
            reply = self.bitcoinData.getStatusInfo()

        elif bool(self.bitcoinData.PID) and request == "getpeerinfo":
            reply = self.bitcoinData.getPeerInfo()
        
        elif request == "keepalive":
            reply = "keepalive"

        else:
            reply = self.rpcCaller.runCall(request)
        
        return reply
        

def main():

    SERVER = Server()

    SERVER.check_network()

    if SERVER.isOnline:
        try:
            SERVER.autoUpdater.start()
            SERVER.start_serving()
        except KeyboardInterrupt:
            SERVER.autoUpdater.stop()
            SERVER.isServing = False
            lib.storage.Logger.add("Server stopped")
    else:
        lib.storage.Logger.add("Server socket not working")







