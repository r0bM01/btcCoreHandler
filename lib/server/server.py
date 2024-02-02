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



import json, time, subprocess, threading, platform, sys
import lib.shared.network
import lib.shared.crypto
import lib.server.machine
import lib.server.protocol
import lib.server.srpc


class Server(lib.server.protocol.RequestHandler):
    def __init__(self, logger, storage):
        lib.server.protocol.RequestHandler.__init__(self)
        #init procedure
        self.STORAGE = storage
        self.LOGGER = logger
        self.NETWORK = lib.shared.network.Server(lib.shared.network.Settings(host = lib.server.machine.MachineInterface.getLocalIP()))

        self.maxCallSize = 256 #bytes 

        self.eventController = threading.Event()
        self.SRPC = lib.server.srpc.ServerRPC(self.eventController)
        self.srpcT = threading.Thread(target = self.SRPC.waitForCall, daemon = True)
        
        #loadedGeodata = self.STORAGE.load_geolocation()
        #if bool(loadedGeodata): self.GEO_DATA.GEODATA.extend(loadedGeodata)
        self.GEO_DATA.FILES = self.STORAGE.geolocation
        self.GEO_DATA.loadDatabase()

        self.autoServing = threading.Thread(target = self.start_serving, daemon = True)
        self.isCached = False
        self.isServing = False
        self.isOnline = False

        self.autoCache = threading.Thread(target = self.cacheUpdater, daemon = True)
        self.autoCacheRun = False
        self.autoCacheRest = 30
        
        self.LOGGER.add("bitcoind running", self.bitcoindRunning)
    

    def start_all(self):
        self.autoCache.start()
        self.autoServing.start()
        self.LOGGER.verbose = False
        self.eventController.wait()
        self.LOGGER.add("closing server called from thread")
        self.isServing = False
        self.autoCacheRun = False
        self.LOGGER.add("saving geodata")
        self.STORAGE.write_geolocation(self.GEO_DATA.GEODATA)
        sys.exit()

    def start_network(self):
        self.eventController.clear()
        self.srpcT.start()
        self.NETWORK.openSocket()
        self.isOnline = bool(self.NETWORK.socket)
        self.LOGGER.add("SERVER", f"socket online: {self.isOnline}", f"bind to ip: {self.NETWORK.settings.host}")
        #self.LOGGER.add("bind to IP", self.NETWORK.settings.host)
        self.LOGGER.add("server succesfully started")

    def checkCacheData(self):
        self.isCached = bool(self.BITCOIN_DATA.uptime)
        return self.isCached

    def cacheUpdater(self):
        self.LOGGER.add("auto cache thread started")
        self.autoCacheRun = True
        while self.autoCacheRun and self.bitcoindRunning:
            self.updateCacheData()
            self.updateGeolocationData(self.LOGGER)
            time.sleep(self.autoCacheRest)
        self.LOGGER.add("auto cache thread stopped")
            

    def start_serving(self):
        self.isServing = True
        self.LOGGER.add("server started")
        self.LOGGER.add("waiting for incoming connections")
        while self.isServing and not self.SRPC.STOP:
         
            self.NETWORK.receiveClient(self.STORAGE.certificate) # creates an handshake random code when receiving a new client
            if bool(self.NETWORK.handshakeCode): 
                self.CONTROL.encodeCalls(self.STORAGE.certificate, self.NETWORK.handshakeCode) # temporary certificate "fefa"
                # self.LOGGER.add("handshake code generated", self.NETWORK.handshakeCode)
            if bool(self.NETWORK._remoteSock): 
                self.LOGGER.add("connected by", self.NETWORK.remoteAddr, f"handshake: {self.NETWORK.handshakeCode}", 
                                f"timeout: {self.NETWORK._remoteSock.gettimeout()}")
            # else: self.LOGGER.add("no incoming connection detected")

            while bool(self.NETWORK._remoteSock):
                remoteCall = self.NETWORK.receiver(self.maxCallSize)

                if remoteCall:
                    callResult = self.handle_request(remoteCall, self.LOGGER)
                    if callResult == "ADVANCEDCALLSERVICE":
                        jsonCall = json.loads(self.NETWORK.receiver())
                        # self.LOGGER.add("Advanced call", jsonCall['call'], jsonCall['arg'])
                        reply = self.directCall(jsonCall)
                    elif callResult == "TESTENCRYPTSERVICE":
                        reply = lib.shared.crypto.getEncrypted(json.dumps(self.BITCOIN_DATA.getStatusInfo()), self.STORAGE.certificate, self.NETWORK.handshakeCode)
                    else:
                        reply = callResult
                else:
                    self.LOGGER.add("client couldn't send remote call")
                    reply = False
                ######################################################
                if bool(reply) and bool(self.NETWORK._remoteSock):
                    # self.LOGGER.add("reply content size", len(reply.encode()))
                    replySent = self.NETWORK.sender(reply) #returns True or False
                    # self.LOGGER.add("reply sent", replySent)
                    self.LOGGER.add("new call by", self.NETWORK.remoteAddr, remoteCall, self.CONTROL.encodedCalls.get(remoteCall), f"succesfull: {replySent}")
                else:
                    # self.LOGGER.add("remote socket active", self.NETWORK._remoteSock)
                    self.LOGGER.add("connection closed")
                #######################################################
        self.LOGGER.add("serving loop exit")

        

"""
def main():
    storage = lib.server.storage.Data()
    storage.init_files()
    saved_geodata = storage.load_geolocation()
    logger = lib.server.storage.Logger(filePath = storage.fileLogs, verbose = True)
    eventController = threading.Event()
    SERVER = Server(logger, saved_geodata, eventController)

    logger.add("updating base cache data")
    SERVER.updateCacheData()

    logger.add("BitcoinCore uptime", SERVER.BITCOIN_DATA.uptime['uptime'])
    logger.add("BitcoinCore chain", SERVER.BITCOIN_DATA.blockchainInfo['chain'])
    logger.add("BitcoinCore blocks", SERVER.BITCOIN_DATA.blockchainInfo['blocks'])
    logger.add("BitcoinCore peers", SERVER.BITCOIN_DATA.networkInfo['connections'])

    logger.add("loaded geodata", len(saved_geodata))
    
    logger.add("updating geolocation data... wait until complete (up to 2 minutes)")
    SERVER.updateGeolocationData()

    logger.add("starting network")
    SERVER.start_network()
    eventController.clear()

    if SERVER.isOnline:

        try:
            SERVER.autoCache.start()
            logger.verbose = False
            SERVER.autoServing.start()
            eventController.wait()
        except KeyboardInterrupt:
            logger.verbose = True
            logger.add("Server stopped by keyboard interrupt")
        finally:
            storage.write_geolocation(SERVER.GEO_DATA.GEODATA)
            logger.verbose = True
            SERVER.isServing = False
            logger.add("Server stopped")
    else:
        logger.add("Server socket not working")
"""







