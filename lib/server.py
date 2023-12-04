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



import json, time, subprocess, threading, platform
import lib.network
import lib.storage
import lib.protocol


class Machine:
    dataInfo = {}
    dataInfo['node'] = platform.node()
    dataInfo['machine'] = platform.machine()
    dataInfo['system'] = platform.system()
    dataInfo['release'] = platform.release()

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
            # self.thread.join()
            lib.storage.Logger.add("autoupdater loop stopped")

    def updater_loop(self):
        self.isRunning = True
        lib.storage.Logger.add("autoupdater loop started")
        while self.isRunning:
            self.sendUpdateCall() #update all bitcoin data field
            # self.listGeolocation()
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
        self.bitcoinData.peersInfo = json.loads(peersInfo)
        # self.bitcoinData.peersInfo = [p for p in peersInfo]
        
    def listGeolocation(self):
        if self.bitcoinData.peersInfo:
            nodeList = [peer['addr'].split(":")[0] for peer in self.bitcoinData.peersInfo]
            lib.protocol.IPGeolocation.updateList(nodeList)
                
               

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
            # handshakeCode = lib.crypto.getRandomBytes(16)
            # lib.storage.Logger.add("handshake code generated", handshakeCode.hex())

            # self.calls = lib.protocol.Commands.encodeCalls("fefa", handshakeCode.hex()) # temporary certificate "fefa"

            # self.network.receiveClient(handshakeCode.hex())
            self.network.receiveClient(lib.crypto.getRandomBytes(16).hex()) # creates an handshake random code when receiving a new client and not before
            if bool(self.network.handshakeCode): 
                self.calls = lib.protocol.Commands.encodeCalls("fefa", self.network.handshakeCode) # temporary certificate "fefa"
                lib.storage.Logger.add("handshake code generated", self.network.handshakeCode)
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
                    lib.storage.Logger.add("reply content size", len(reply.encode()))
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
        
        elif bool(self.bitcoinData.PID) and request == "advancedcall":
            jsonCall = json.loads(self.network.receiver()) #wait for actual call
            lib.storage.Logger.add("Advanced call", jsonCall['call'], jsonCall['arg'])
            if jsonCall['call'] != "start" and jsonCall['call'] != "stop":  
                reply = self.rpcCaller.runCall(jsonCall['call'], jsonCall['arg'])
            else:
                reply = False
            if not bool(reply): reply = json.dumps({"error": "command not allowed"})

        elif request == "keepalive":
            reply = "keepalive"
        
        elif request == "systeminfo":
            reply = json.dumps(Machine.dataInfo)
        
        elif request == "externalip":
            reply = json.dumps({'extIP': self.network.getExternalIP()})

        elif bool(self.bitcoinData.PID) and request == "getgeolocation":
            reply = json.dumps(lib.protocol.IPGeolocation.connectedNodes)

        else:
            reply = json.dumps({"error": "command not allowed"})
        
        return reply


def main():

    SERVER = Server()

    SERVER.check_network()
    lib.storage.Logger.add("calling first update")
    SERVER.autoUpdater.sendUpdateCall()
    lib.storage.Logger.add("getting geolocation connected peers")
    # SERVER.autoUpdater.listGeolocation()

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







