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
import lib.server.network
import lib.server.services



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
        self.NETWORK = lib.server.network.Server(lib.server.network.Settings(host = lib.server.machine.MachineInterface.getLocalIP()))
        self.SERVICES = lib.server.services.Engine(self.CACHE, self.GEO_DATA, self.LOGGER)

        self.maxCallSize = 256 #bytes
        self.maxPeersWorker = 5 # max 5 peers connected at the same time, which equals to max 5 child threads
        self.connected_peers = [] # list of peer thread workers

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

        self.localControllerEvent.wait() # main thread server hangs here!! 
        # when activated it will stop the application
        sys.exit(0) 

    def start_network(self):
        self.NETWORK.openSocket()
        self.isOnline = bool(self.NETWORK.socket)
        self.LOGGER.add("server- socket ready", self.isOnline)
        self.LOGGER.add("server- socket bind to address", self.NETWORK.settings.host)
        #self.LOGGER.add("bind to IP", self.NETWORK.settings.host)
        self.LOGGER.add("server- network succesfully started")
    
    def available_workers(self):
        return len(self.self.connected_peers) < self.maxPeersWorker
    
    def cleanup_workers(self):
        for peer in self.connected_peers:
            if not peer.is_alive():
                peer.join()
                self.connected_peers.remove(peer)

    def remote_peer_handler(self, new_peer):
        new_peer.init_crypto()
        #connectedPeer = lib.server.network.Peer(remotePeerSocket, handshake.remote_certificate, handshake.handshake_code)
        while new_peer._remoteSock and not self.localControllerEvent.is_set():
            remote_request = new_peer.read(self.maxCallSize)
            self.LOGGER.add("server- peer has sent a new request", new_peer.address, remote_request)
            result = self.handle_request(remote_request)
            reply_sent = new_peer.write(result)
            self.LOGGER.add("server- peer reply sent", new_peer.address, reply_sent)
            new_peer.session_calls.append({'time': int(time.time()), 'request': remote_request, 'success': reply_sent})
        else:
            self.LOGGER.add("server- peer has disconnected", new_peer.address)
            new_peer.sockClosure()

    def start_serving(self):
        self.isServing = True
        self.LOGGER.add("server- waiting for incoming connections")
        while self.isServing and not self.localControllerEvent.is_set(): 

            new_peer = lib.server.network.Peer(self.NETWORK.receiveClient())
            ## handshake is managed by server daemon thread
            if bool(new_peer._remoteSock):
                self.LOGGER.add("server- peer is trying to connect", new_peer.address)
                new_peer.make_handshake([self.STORAGE.certificate])
            ## if handshake is successfull it will be created a thread to handle the remote peer requests
            if bool(new_peer._remoteSock) and bool(new_peer.handshake_done) and self.available_workers():
                self.LOGGER.add("server- peer successfully connected", new_peer.address)
                remotePeerThread = threading.Thread(target = self.remote_peer_handler, args = (new_peer))
                remotePeerThread.start()
                self.connected_peers.append(remotePeerThread)
            
            self.cleanup_workers()
            self.LOGGER.add("server- connected peers", len(self.connected_peers))
        else:
            self.LOGGER.add("server- serving loop exit")

