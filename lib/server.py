import json, time, subprocess, threading
import lib.network
import lib.storage
import lib.protocol

class DUpdater(threading):
    def __init__(self, rpcCaller, bitcoinData):
        self.isRunning = False
        self.restTime = 60 * 2 #seconds
        self.rpcCaller = rpcCaller
        self.bitcoinData = bitcoinData
        self.thread = Thread(target = self.start)

    def start(self):
        if not self.isRunning:
            self.thread.run()

    def stop(self):
        if self.isRunning:
            self.isRunning = False
    
    def updater_loop(self):
        self.isRunning = True
        while self.isRunning:
            self.sendUpdateCall() #update all bitcoin data field
            time.sleep(self.restTime) #rest for minutes
    
    def sendUpdateCall(self):
        uptime = self.rpcCaller.sendControl("uptime")
        uptime = json.loads(uptime)
        self.bitcoinData.update(uptime)

        blockchainInfo = self.rpcCaller.sendCall("getblockchaininfo")
        blockchainInfo = json.loads(blockchainInfo)
        self.bitcoinData.update(blockchainInfo)

        networkInfo = self.rpcCaller.sendCall("getnetworkinfo")
        networkInfo = json.loads(networkInfo)
        self.bitcoinData.update(networkInfo)

        mempoolInfo = self.rpcCaller.sendCall("getmempoolinfo")
        mempoolInfo = json.loads(mempoolInfo)
        self.bitcoinData.update(mempoolInfo)

        miningInfo = self.rpcCaller.sendCall("getmininginfo")
        miningInfo = json.loads(miningInfo)
        self.bitcoinData.update(miningInfo)


def main():
    #init procedure
    storage = lib.storage.Data()
    netSettings = lib.network.Settings()
    bitcoinData = lib.protocol.DaemonData()
    rpcCaller = lib.protocol.RPC()
    autoUpdater = DUpdater()
    #init server settings
    server = lib.network.Server(netSettings)
    #check bitcoind running
    bitcoinData.PID = rpcCaller.checkDaemon()

    #if bitcoind is running, server will start the auto updater to gather info
    #if not started yet, will wait for remote bitcoind start
    if bitcoinData.PID: 
        autoUpdater.start()
    
    server.openSocket()

    if server.socket:
        print(time.ctime(time.time()))
        print("Server started")
        try:
            while True:
                server.receiveClient()
                if server.remoteSock:
                    print("Client connected ")
                    setRunning = True
                    while setRunning:
                        #block until command is sent
                        request = server.receiver()
                        requestValidity = lib.protocol.commands.Commands.check(command)
                        print("Received command: ", request)
                        if requestValidity:
                            if bitcoinData.PID:
                                reply = rpcCaller.runCall(request)
                            elif not bitcoinData.PID and request == 'start':
                                reply = rpcCaller.runCall(request)
                                opt = json.loads(reply)
                                if opt['start']:
                                    autoUpdater.start()
                            elif not bitcoinData.PID and request != 'start':
                                result = {'message': 'bitcoin daemon not running'}
                                reply = json.dumps(result)
                            server.sender(reply)
                        elif request == 'updateall':
                            reply = bitcoinData.getAllData()
                            server.sender(reply)                            
                        else:
                            setRunning = False
                            server.remoteSock.close()
                            
        except KeyboardInterrupt:
            print("Server stopped")







