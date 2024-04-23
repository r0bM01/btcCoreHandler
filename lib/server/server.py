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

        self.initTime = int(time.time())
        self.internetIsOn = lib.shared.network.Utils.checkInternet()

        #init procedure
        self.STORAGE = storage
        self.LOGGER = logger
        self.NETWORK = lib.shared.network.Server(lib.shared.network.Settings(host = lib.server.machine.MachineInterface.getLocalIP()))

        self.maxCallSize = 256 #bytes 

        #self.SRPC = lib.server.srpc.ServerRPC(self.eventController)
        self.localControllerNetwork = lib.shared.network.ServerRPC()
        self.localControllerThread = threading.Thread(target = self.local_server_controller, daemon = True)
        
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
    
    def local_server_controller(self):
        # command line operation
        self.localControllerNetwork.openSocket()
        self.LOGGER.add("server- local socket ready", bool(self.localControllerNetwork.socket))
        self.LOGGER.add("server- local controller started")
        # self.LOGGER.add("server- local event controller is waiting")
        # cmds = ['handlerstop', 'handlerinfo'] # command line accepts only 2 words
        stop = False
        while not stop:
            self.localControllerNetwork.receiveClient() #blocking call for infinite time
            if bool(self.localControllerNetwork._remoteSock):
                call = self.localControllerNetwork.receiver()
                if bool(call) and call == 'handlerinfo':
                    message = json.dumps({'handlerUptime': self.initTime, 'handlerMachine': 'dummymex'})
                    self.localControllerNetwork.sender(message)
                elif bool(call) and call == 'handlerstop':
                    stop = True
            self.localControllerNetwork.sockClosure() #socket must always be closed
        else:
            nice_server_shutdown()
        

    def nice_server_shutdown(self):
        # server closure procedure
        self.LOGGER.verbose = True
        self.NETWORK.sockClosure() #closes the connected socket if any

        self.isServing = False #stops server infinite loop
        #self.autoServing.join()

        self.autoCacheRest = 2 #sets to 2 the sleeping time
        self.autoCacheRun = False #stops cache updater
        #self.autoCache.join()

        

    def start_all(self):
        self.autoCache.start()
        self.autoServing.start()
        self.LOGGER.verbose = False

        # self.localControllerEvent.wait() # when activated it will stop the application
        """
        self.LOGGER.add("server- closure called from thread")
        self.isServing = False
        self.autoCacheRun = False
        sys.exit(1)
        """
    def start_network(self):
        self.eventController.clear()
        #self.srpcT.start()
        self.NETWORK.openSocket()
        self.isOnline = bool(self.NETWORK.socket)
        self.LOGGER.add("server-", f"socket ready: {self.isOnline}", f"bind to ip: {self.NETWORK.settings.host}")
        #self.LOGGER.add("bind to IP", self.NETWORK.settings.host)
        self.LOGGER.add("server- network succesfully started")

    def checkCacheData(self):
        self.isCached = bool(self.BITCOIN_DATA.uptime)
        return self.isCached

    def cacheUpdater(self):
        self.LOGGER.add("server- auto cache thread started")
        self.autoCacheRun = True
        while self.autoCacheRun and self.bitcoindRunning:
            self.updateCacheData()
            self.updateGeolocationData(self.LOGGER)
            time.sleep(self.autoCacheRest)
        self.LOGGER.add("server- auto cache thread stopped")
            

    def start_serving(self):
        self.isServing = True
        self.LOGGER.add("server- waiting for incoming connections")
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
        self.LOGGER.add("server- serving loop exit")

        






