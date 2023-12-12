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


class Server(lib.server.protocol.RequestHandler):
    def __init__(self, logger):
        self.LOG = logger
        lib.server.protocol.RequestHandler.__init__(self)
        #init procedure
        self.LOGGER = logger
        self.NETWORK = lib.network.Server(lib.network.Settings(host = lib.server.machine.MachineInterface.getLocalIP()))

        self.isCached = False
        self.isServing = False
        self.isOnline = False

        self.autoCache = threading.Thread(target = self.cacheUpdater, daemon = True)
        self.autoCacheRun = False
        self.autoCacheRest = 30
        
        self.LOGGER.add("bitcoind running", self.bitcoindRunning)
    
    def start_network(self):
        self.NETWORK.openSocket()
        self.isOnline = bool(self.NETWORK.socket)
        self.LOGGER.add("socket online", self.isOnline)
        self.LOGGER.add("bind to IP", self.NETWORK.settings.host)

    def checkCacheData(self):
        self.isCached = bool(self.BITCOIN_DATA.uptime)
        return self.isCached

    def cacheUpdater(self):
        self.LOGGER.add("auto cache thread started")
        self.autoCacheRun = True
        while self.autoCacheRun and self.bitcoindRunning:
            self.updateCacheData()
            self.updateGeolocationData()
            time.sleep(self.autoCacheRest)
        self.LOGGER.add("auto cache thread stopped")
            

    def start_serving(self):
        self.isServing = True
        self.LOGGER.add("server started")
        self.LOGGER.add("waiting for incoming connections")
        while self.isServing:
         
            self.NETWORK.receiveClient(lib.crypto.getRandomBytes(16).hex()) # creates an handshake random code when receiving a new client
            if bool(self.NETWORK.handshakeCode): 
                self.CONTROL.encodeCalls("fefa", self.NETWORK.handshakeCode) # temporary certificate "fefa"
                self.LOGGER.add("handshake code generated", self.NETWORK.handshakeCode)
            if bool(self.NETWORK._remoteSock): self.LOGGER.add("connected by", self.NETWORK._remoteSock)
            else: self.LOGGER.add("no incoming connection detected")

            while bool(self.NETWORK._remoteSock):
                remoteCall = self.NETWORK.receiver()
                self.LOGGER.add("encoded call: ", remoteCall)

                if remoteCall:
                    callResult = self.handle_request(remoteCall)

                    if callResult == "ADVANCEDCALLSERVICE":
                        jsonCall = json.loads(self.NETWORK.receiver())
                        self.LOGGER.add("Advanced call", jsonCall['call'], jsonCall['arg'])
                        reply = self.directCall(jsonCall)
                    else:
                        reply = callResult
                else:
                    self.LOGGER.add("client couldn't send remote call")
                    reply = False
                ######################################################
                if bool(reply) and bool(self.NETWORK._remoteSock):
                    self.LOGGER.add("reply content size", len(reply.encode()))
                    replySent = self.NETWORK.sender(reply) #returns True or False
                    self.LOGGER.add("reply sent", replySent)
                else:
                    self.LOGGER.add("remote socket active", self.NETWORK._remoteSock)
                    self.LOGGER.add("connection closed")
                #######################################################
        self.LOGGER.add("serving loop exit")

        


def main():
    storage = lib.server.storage.Data()
    storage.init_files()
    logger = lib.server.storage.Logger(filePath = storage.fileLogs, verbose = True)

    SERVER = Server(logger)

    logger.add("update base cache data")
    SERVER.updateCacheData()

    logger.add("update geolocation data")
    SERVER.updateGeolocationData()

    logger.add("starting network")
    SERVER.start_network()

    if SERVER.isOnline:
        try:
            SERVER.autoCache.start()
            SERVER.start_serving()
        except KeyboardInterrupt:
            
            SERVER.isServing = False
            logger.add("Server stopped")
    else:
        logger.add("Server socket not working")







