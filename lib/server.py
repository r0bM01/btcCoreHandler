import json, time, subprocess, threading
import lib.network
import lib.storage
import lib.protocol

class DUpdater():
    def __init__(self, rpcCaller, bitcoinData):
        self.isRunning = False
        self.restTime = 60 * 2 #seconds
        self.rpcCaller = rpcCaller
        self.bitcoinData = bitcoinData
        self.thread = threading.Thread(target = self.updater_loop)

    def start(self):
        if not self.isRunning:
            self.thread.start()

    def stop(self):
        if self.isRunning:
            self.isRunning = False
            self.thread.join()

    def updater_loop(self):
        self.isRunning = True
        lib.storage.Logger.add("autoupdater loop started")
        while self.isRunning:
            self.sendUpdateCall() #update all bitcoin data field
            time.sleep(self.restTime) #rest for minutes
    
    def sendUpdateCall(self):
        uptime = self.rpcCaller.sendControl("uptime")
        uptime = json.loads(uptime)
        self.bitcoinData.update(uptime)

        blockchainInfo = self.rpcCaller.sendCall("getblockchaininfo")
        self.bitcoinData.blockchainInfo = json.loads(blockchainInfo)
        
        networkInfo = self.rpcCaller.sendCall("getnetworkinfo")
        self.bitcoinData.networkInfo = json.loads(networkInfo)

        mempoolInfo = self.rpcCaller.sendCall("getmempoolinfo")
        self.bitcoinData.mempoolInfo = json.loads(mempoolInfo)
        
        miningInfo = self.rpcCaller.sendCall("getmininginfo")
        self.bitcoinData.miningInfo = json.loads(miningInfo)
        
class Server:
    def __init__(self):
        #init procedure
        self.storage = lib.storage.Data()
        self.storage.init_files()
        lib.storage.Logger.FILE = self.storage.fileLogs

        self.rpcCaller = lib.protocol.RPC()
        self.bitcoinData = lib.protocol.DaemonData()

        self.bitcoinData.PID = self.rpcCaller.checkDaemon()
        self.autoUpdater = DUpdater(self.rpcCaller, self.bitcoinData)
        #init server settings
        self.netSettings = lib.network.Settings(host = self.rpcCaller.getLocalIP())
        self.network = lib.network.Server(self.netSettings)
        
        self.isServing = False
        self.isOnline = False
    
    def check_network(self):
        self.network.openSocket()
        self.isOnline = bool(self.network.socket)
        lib.storage.Logger.add("socket online: ", bool(self.network.socket))

    def start_serving(self):
        self.isServing = True
        while self.isServing:
            lib.storage.Logger.add("serving loop entered")
            self.network.receiveClient()
            lib.storage.Logger.add("connected by", self.network.remoteSock)
            while bool(self.network.remoteSock):
                request = self.network.receiver()
                lib.storage.Logger.add("request: ", request)
                if lib.protocol.Commands.check(request):
                    if request == "closeconn":
                        self.network.sender({"message": "connection closed"})
                        self.network.remoteSock.close()
                        self.network.remoteSock = False
                    else:
                        reply = self.handle_request(request)
                else:
                    reply = json.dumps({"error": "request not valid"})
                self.network.sender(reply)
                lib.storage.Logger.add("reply sent: ", reply)

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

        elif bool(self.bitcoinData.PID) and request == "updateall":
            reply = self.bitcoinData.getAllData()

        else:
            reply = self.rpcCaller.runCall(request)
        
        return reply
        

def main():

    SERVER = Server()
    lib.storage.Logger.add("server init")

    SERVER.check_network()

    if SERVER.isOnline:
        try:
            SERVER.start_serving()
        except KeyboardInterrupt:
            lib.storage.Logger.add("Server stopped")
    else:
        lib.storage.Logger.add("Server socket not working")







