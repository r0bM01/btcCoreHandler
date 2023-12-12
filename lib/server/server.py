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
import lib.server.machine
import lib.server.storage
import lib.server.protocol

       
               
 
class Server(lib.protocol.RequestHandler):
    def __init__(self):
        lib.protocol.RequestHandler.__init__(self)
        #init procedure
        self.STORAGE = lib.storage.Data()
        self.NETWORK = lib.network.Server(lib.network.Settings(host = lib.server.machine.MachineInterface.getLocalIP()))

        self.isServing = False
        self.isOnline = False

        self.autoCache = threading.Thread(target = self.cacheUpdater, daemon = True)
        self.autoCacheRun = False
        self.autoCacheRest = 30
        
        self.STORAGE.init_files()
        lib.storage.Logger.FILE = self.storage.fileLogs
        lib.storage.Logger.add("bitcoind running", bool(self.BITCOIN_DATA.PID))

    
    
    def check_network(self):
        self.NETWORK.openSocket()
        self.isOnline = bool(self.NETWORK.socket)
        lib.storage.Logger.add("socket online", self.isOnline)
        lib.storage.Logger.add("bind to IP", self.NETWORK.settings.host)
    
    def cacheUpdater(self):
        self.autoCacheRun = True
        while self.autoCacheRun and self.bitcoindRunning:
            self.updateCacheData()
            time.sleep(self.autoCacheRest)

    def start_serving(self):
        self.isServing = True
        lib.storage.Logger.add("serving loop entered")
        while self.isServing:
         
            self.NETWORK.receiveClient(lib.crypto.getRandomBytes(16).hex()) # creates an handshake random code when receiving a new client
            if bool(self.NETWORK.handshakeCode): 
                self.CONTROL.encodeCalls("fefa", self.NETWORK.handshakeCode) # temporary certificate "fefa"
                lib.storage.Logger.add("handshake code generated", self.NETWORK.handshakeCode)
            if bool(self.NETWORK._remoteSock): lib.storage.Logger.add("connected by", self.NETWORK._remoteSock)
            else: lib.storage.Logger.add("no incoming connection detected")

            while bool(self.NETWORK._remoteSock):

                remoteCall = self.NETWORK.receiver()
                lib.storage.Logger.add("call: ", remoteCall)

                if remoteCall:
                    callResult = self.handle_request(remoteCall)

                    if callResult == "ADVANCEDCALLSERVICE":
                        jsonCall = json.loads(self.NETWORK.receiver())
                        lib.storage.Logger.add("Advanced call", jsonCall['call'], jsonCall['arg'])
                        if jsonCall['call'] != "start" and jsonCall['call'] != "stop":
                            reply = lib.server.machine.MachineInterface.runBitcoindCall(jsonCall['call'], jsonCall['arg'])
                        else:
                            reply = json.dumps({"error": "command not allowed"})

                    elif callResult == "GEOLOCATIONSERVICE":
                        reply = json.dumps(lib.protocol.IPGeolocation.connectedNodes)

                    elif callResult == "CLOSECONNECTIONSERVICE":
                        reply = False
                    
                    else:
                        reply = callResult
                else:
                    reply = False
                ######################################################
                if bool(reply) and bool(self.NETWORK._remoteSock):
                    lib.storage.Logger.add("reply content size", len(reply.encode()))
                    replySent = self.NETWORK.sender(reply) #returns True or False
                    lib.storage.Logger.add("reply sent", replySent)
                else:
                    lib.storage.Logger.add("remote socket active", self.NETWORK._remoteSock)
                    lib.storage.Logger.add("connection closed")
            ############################################################################################
        lib.storage.Logger.add("serving loop exit")

        
    def listGeolocation(self):
        if self.bitcoinData.peersInfo:
            nodeList = [peer['addr'].split(":")[0] for peer in self.bitcoinData.peersInfo]
            lib.protocol.IPGeolocation.updateList(nodeList)



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







