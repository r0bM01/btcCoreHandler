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



import json, time, subprocess, threading, platform, sys, signal
import lib.shared.network
import lib.shared.crypto
import lib.server.machine
import lib.server.protocol
import lib.server.srpc

class Services:
    def __init__(self, cache_data, geolocation_data, logger):

        self.services = [{'name': 'bitcoin', 'target': self.bitcoin_service, 'active': False}, 
                         {'name': 'geodata', 'target': self.geodata_service, 'active': False}]

        self.services_controller = threading.Event()

        self.cache = cache_data # new data holder

        self.geolocation = geolocation_data
        self.logger = logger

        self.worker = self.make_new_thread()
        self.worker_rest = 30

    def start(self):
        for service in self.services:
            service['active'] = True # activates all services
            self.logger.add("server- service", service['name'], service['active'])
        if not bool(self.worker):
            self.worker = self.make_new_thread()
        if not self.worker.is_alive:
            self.services_controller.clear()
            self.worker.start()
            self.logger.add("server- services working", self.worker.is_alive())
    
    def stop(self):
        for service in self.services:
            service['active'] = False # deactivates all services
            self.logger.add("server- service", service['name'], service['active'])
        if self.worker.is_alive():
            self.services_controller.set()
            self.worker.join()

    def make_new_thread(self):
        return threading.Thread(target = self.services_worker, daemon = True)

    def services_worker(self):
        while not self.services_controller.is_set():
            for service in self.services:
                if service['active']: service['target']() # execute the service if active
            self.services_controller.wait(self.worker_rest)

    def bitcoin_service(self):
        ## runs the machine calls
        uptime = lib.server.machine.MachineInterface.runBitcoindCall("uptime")
        blockchainInfo = lib.server.machine.MachineInterface.runBitcoindCall("getblockchaininfo")
        networkInfo = lib.server.machine.MachineInterface.runBitcoindCall("getnetworkinfo")
        nettotalsInfo = lib.server.machine.MachineInterface.runBitcoindCall("getnettotals")
        mempoolInfo = lib.server.machine.MachineInterface.runBitcoindCall("getmempoolinfo")
        miningInfo = lib.server.machine.MachineInterface.runBitcoindCall("getmininginfo")
        peersInfo = lib.server.machine.MachineInterface.runBitcoindCall("getpeerinfo")
        ## saves the data into cache
        self.cache.bitcoin['uptime'] = json.loads(uptime)
        self.cache.bitcoin['blockchainInfo'] = json.loads(blockchainInfo)
        self.cache.bitcoin['networkInfo'] = json.loads(networkInfo)
        self.cache.bitcoin['nettotalsInfo'] = json.loads(nettotalsInfo)
        self.cache.bitcoin['mempoolInfo'] = json.loads(mempoolInfo)
        self.cache.bitcoin['miningInfo'] = json.loads(miningInfo)
        self.cache.bitcoin['peersInfo'] = json.loads(peersInfo)
        self.cache.bitcoin_update_time = int(time.time()) 

    def geodata_service(self):
        self.cache.connectedInfo = self.geolocation.updateDatabase(self.bitcoin.peersInfo, self.logger)

class Server(lib.server.protocol.RequestHandler):
    def __init__(self, logger, storage):
        lib.server.protocol.RequestHandler.__init__(self)

        signal.signal(signal.SIGINT, self.nice_server_shutdown)
        signal.signal(signal.SIGTERM, self.nice_server_shutdown)

        self.initTime = int(time.time())
        self.internetIsOn = lib.shared.network.Utils.checkInternet()
        self.bitcoindRunning = lib.server.machine.MachineInterface.checkDaemon()

        #init procedure
        self.STORAGE = storage
        self.LOGGER = logger
        self.NETWORK = lib.shared.network.Server(lib.shared.network.Settings(host = lib.server.machine.MachineInterface.getLocalIP()))
        self.SERVICES = Services(self.CACHE, self.GEO_DATA, self.LOGGER)

        self.maxCallSize = 256 #bytes 

        self.localControllerEvent = threading.Event()
        self.localControllerNetwork = lib.shared.network.ServerRPC()
        self.localControllerThread = threading.Thread(target = self.local_server_controller, daemon = True)
        
        #loadedGeodata = self.STORAGE.load_geolocation()
        #if bool(loadedGeodata): self.GEO_DATA.GEODATA.extend(loadedGeodata)
        self.GEO_DATA.FILES = self.STORAGE.geolocation
        self.GEO_DATA.loadDatabase()

        self.autoServing = threading.Thread(target = self.start_serving, daemon = True)
        self.isServing = False
        self.isOnline = False

    def local_server_controller(self):
        # command line operation
        self.localControllerNetwork.openSocket()
        self.LOGGER.add("server- local socket ready", bool(self.localControllerNetwork.socket))
        self.localControllerEvent.clear() # sets the internal flag to "False"
        self.LOGGER.add("server- local controller started", not self.localControllerEvent.is_set())
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
                    self.LOGGER.add("server- received closure call", call)
                    stop = True
        else:
            self.nice_server_shutdown()

    def nice_server_shutdown(self):
        # server closure procedure
        # self.LOGGER.verbose = True
        self.LOGGER.add("server- nice shutdown started")

        self.LOGGER.add("server- closing network sockets")
        self.NETWORK.sockClosure() #closes the connected socket if any
        self.NETWORK.closeSocket() #closes the server socket
        
        self.LOGGER.add("server- stopping main loop")
        self.isServing = False #stops server infinite loop
        # self.autoServing.join()

        self.LOGGER.add("server- stopping autocache service")
        self.SERVICES.stop()

        self.LOGGER.add("server- shutdown completed")
        self.localControllerNetwork.sender("shutdown completed")
        self.localControllerNetwork.sender("handlerstopped")
        self.localControllerNetwork.sockClosure() #socket must always be closed
        self.localControllerEvent.set() # this will cause server stop

    def start_all(self):
        # self.autoCache.start()
        self.SERVICES.start()
        self.autoServing.start()
        self.LOGGER.verbose = False

        self.localControllerEvent.wait() # server hangs here!! 
        # when activated it will stop the application
        sys.exit(0) 

    def start_network(self):
        
        #self.srpcT.start()
        self.NETWORK.openSocket()
        self.isOnline = bool(self.NETWORK.socket)
        self.LOGGER.add("server- socket ready", self.isOnline)
        self.LOGGER.add("server- socket bind to address", self.NETWORK.settings.host)
        #self.LOGGER.add("bind to IP", self.NETWORK.settings.host)
        self.LOGGER.add("server- network succesfully started")

            
    def start_serving(self):
        self.isServing = True
        self.LOGGER.add("server- waiting for incoming connections")
        while self.isServing: #and not self.SRPC.STOP:
         
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

class Peer(lib.shared.network.Proto):
    def __init__(self, remoteSocket):
        self._remoteSock = remoteSocket
        self.certificate = None
        self.handshake_code = None
        self.crypto = None

        self.first_active = int(time.time())
        self.last_active = None
        self.session_calls = None

    def handshake_process(self):
        """
        clientRandom = self.dataRecv(16)
        serverRandom = lib.shared.crypto.getRandomBytes(16)
        entropy = clientRandom + serverRandom
        if bool(clientRandom) and self.dataSend(serverRandom):
            handshakeCode = lib.shared.crypto.getHandshakeCode(entropy, certificate)
            request = lib.shared.crypto.getHashedCommand("handshake", certificate, handshakeCode)
            confirm = lib.shared.crypto.getHashedCommand("handshakeaccepted", certificate, handshakeCode)
            if self.dataRecv(16) == bytes.fromhex(request):
                self.handshakeCode = handshakeCode if self.dataSend(bytes.fromhex(confirm)) else False
        if not bool(self.handshakeCode): self.sockClosure()
        """
        pass
    
    def activate_cryptography(self):
        self.crypto = lib.shared.crypto.Peer(self.certificate, self.handshake_code)
        self.crypto.make_cryptography_dict()

    def write(self, data):
        encrypted_data = self.crypto.encrypt(data)
        return self.sender(encrypted_data)
    
    def read(self, max_call_size = False):
        encrypted_data = self.receiver(max_call_size)
        if bool(encrypted_data): data = self.crypto.decrypt(encrypted_data)
        else: data = False
        return data
            






