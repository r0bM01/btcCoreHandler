# Copyright [2023] [R0BM01@pm.me]                                           #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License");           #
# you may not use this file except in compliance with the License.          #
# You may obtain a copy of the License at                                   #
#                                                                           #
# http://www.apache.org/licenses/LICENSE:2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#############################################################################



import time, threading, sys, signal, json
import lib.network

import server.machine
import server.protocol
import server.network
import server.services



class Server(server.protocol.RequestHandler):
    def __init__(self, logger, storage):
        server.protocol.RequestHandler.__init__(self)

        signal.signal(signal.SIGINT, self.signal_server_shutdown)
        signal.signal(signal.SIGTERM, self.signal_server_shutdown)

        self.initTime = int(time.time())
        self.internetIsOn = lib.network.Utils.checkInternet()
        self.bitcoindRunning = server.machine.MachineInterface.checkDaemon()

        #init procedure
        self.STORAGE = storage
        self.LOGGER = logger
        self.NETWORK = server.network.Server(server.network.Settings(host = server.machine.MachineInterface.getLocalIP()))
        self.SERVICES = server.services.Engine(self.LOGGER, self.BITCOIN_DAEMON.daemon_running)

        self.maxCallSize = 256 #bytes
        self.maxPeersWorker = 5 # max 5 peers connected at the same time, which equals to max 5 child threads
        self.connected_clients = [] # list of peer thread workers

        self.localControllerEvent = threading.Event()
        self.localControllerNetwork = server.network.ServerRPC()
        self.localControllerThread = threading.Thread(target = self.local_server_controller, daemon = True)
        self.localControllerStop = True

        self.autoServing = threading.Thread(target = self.start_serving, daemon = True)
        self.isServing = False
        self.isOnline = False

    def init_geolocation_cache(self):
        self.CACHE.geolocation_index = self.STORAGE.geolocation_load_db_index()
        self.CACHE.geolocation_write = self.STORAGE.geolocation_write_entry
        self.CACHE.geolocation_read = self.STORAGE.geolocation_load_entry
    
    def init_services(self):
        self.SERVICES.add_new_service('bitcoin', self.CACHE.get_bitcoin_info, True) # adds bitcoin 'info' service update
        self.SERVICES.add_new_service('geolocation', self.CACHE.get_geolocation_update, True) 
        # self.SERVICES.add_new_service('protonvpn_pf', server.MachineInterface.protonvpn_pf_test, False) # test for looping open port forward protonvpn

    def local_server_controller(self):
        # command line operation
        self.localControllerNetwork.openSocket()
        self.LOGGER.add("server: local socket ready", bool(self.localControllerNetwork.socket))
        self.localControllerEvent.clear() # sets the internal flag to "False"
        self.LOGGER.add("server: local controller started", not self.localControllerEvent.is_set())
        # self.LOGGER.add("server: local event controller is waiting")
        # cmds = ['handlerstop', 'handlerinfo'] # command line accepts only 2 words
        self.localControllerStop = False
        while not self.localControllerStop:
            try:
                self.localControllerNetwork.receiveClient() #blocking call for infinite time
                if bool(self.localControllerNetwork._remoteSock):
                    call = self.localControllerNetwork.receiver()
                    if bool(call) and call == 'handlerinfo':
                        message = json.dumps({
                            'started': time.ctime(self.initTime),
                            'platform': self.CACHE.node_details,
                            'clients': len(self.connected_clients),
                            'services': self.SERVICES.services_running(),
                            'bitcoind': self.BITCOIN_DAEMON.daemon_running(),
                            'last_cache': time.ctime(self.CACHE.bitcoin_update_time),
                            'geo_db_size': len(self.CACHE.geolocation_index) })
                        self.localControllerNetwork.sender(message)
                    elif bool(call) and call == 'bitcoininfo':
                        message = json.dumps({
                            'uptime': self.CACHE.bitcoin_info['uptime'],
                            'chain': self.CACHE.bitcoin_info['blockchaininfo']['chain'],
                            'blocks': self.CACHE.bitcoin_info['blockchaininfo']['blocks'],
                            'peers': self.CACHE.bitcoin_info['networkinfo']['connections'] })
                    elif bool(call) and call == 'handlernewcert':
                        message = json.dumps({'certsaved': self.STORAGE.make_client_certificate('dummy')})
                        self.localControllerNetwork.sender(message)
                    elif bool(call) and call == 'handlerstop':
                        self.LOGGER.add("server: received closure call", call)
                        self.localControllerNetwork.sender("handler server stopping now")
                        self.localControllerStop = True
                    self.localControllerNetwork.sockClosure() # closes the socket after each call
                    self.LOGGER.add("server: local controller call", call)
            except Exception as E:
                self.LOGGER.add("server error: local controller has encountered an error on receiving a call")
                self.LOGGER.add("server error: error reported", E)
        else:
            self.nice_server_shutdown()
    
    def signal_server_shutdown(self, signum, frame):
        if not self.localControllerStop:
            self.LOGGER.add("server: shutdown called by signal", signum)
            self.localControllerStop = True
            #self.nice_server_shutdown()

    def nice_server_shutdown(self):
        # server closure procedure
        # self.LOGGER.verbose = True
        self.LOGGER.add("server: nice shutdown started")
        

        # self.LOGGER.add("server: closing network sockets")
        # self.NETWORK.sockClosure() #closes the connected socket if any
        # self.NETWORK.closeSocket() #closes the server socket
        
        self.LOGGER.add("server: stopping main loop")
        self.isServing = False #stops server infinite loop
        # self.autoServing.join()

        self.LOGGER.add("server: stopping autocache service")
        self.SERVICES.stop()

        self.LOGGER.add("server: shutdown completed")
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
        self.LOGGER.add("server: socket ready", self.isOnline)
        self.LOGGER.add("server: socket bind to address", self.NETWORK.settings.host)
        #self.LOGGER.add("bind to IP", self.NETWORK.settings.host)
        self.LOGGER.add("server: network succesfully started")
    
    def available_workers(self):
        return len(self.connected_clients) < self.maxPeersWorker
    
    def cleanup_workers(self):
        for client in self.connected_clients:
            if not client.is_alive():
                client.join()
                self.connected_clients.remove(peer)

    def remote_peer_handler(self, new_client):
        new_client.set_waiting_mode() ## set socket max waiting time to 2 minutes
        new_client.init_crypto()
        #connectedPeer = lib.server.network.Peer(remotePeerSocket, handshake.remote_certificate, handshake.handshake_code)
        while new_client._remoteSock and not self.localControllerEvent.is_set():
            remote_request = new_client.read(self.maxCallSize)
            if bool(remote_request):
                self.LOGGER.add("client: new request", new_client.address, remote_request)
                result = self.handle_request(remote_request)
                reply_sent = new_client.write(result)
                self.LOGGER.add("client: reply sent", new_client.address, reply_sent)
                new_client.session_calls.append({'time': int(time.time()), 'request': remote_request, 'success': reply_sent})
        else:
            self.LOGGER.add("server: peer has disconnected", new_client.address)
            new_client.sockClosure()

    def start_serving(self):
        self.isServing = True
        self.LOGGER.add("server: waiting for incoming connections")
        while self.isServing and not self.localControllerEvent.is_set(): 

            new_client = server.network.Peer(self.NETWORK.receiveClient()) ## waits 5 seconds for new peer
            ## handshake is managed by server daemon thread
            if bool(new_client._remoteSock):
                self.LOGGER.add("server: client is trying to connect", new_client.address)
                new_client.make_handshake([self.STORAGE.certificate])
            ## if handshake is successfull it will be created a thread to handle the remote peer requests
            if bool(new_client._remoteSock) and bool(new_client.handshake_done) and self.available_workers():
                self.LOGGER.add("server: client successfully connected", new_client.address)
                remoteClientThread = threading.Thread(target = self.remote_peer_handler, args = [new_client])
                remoteClientThread.start()
                self.connected_clients.append(remoteClientThread)
                self.LOGGER.add("server: connected clients", len(self.connected_clients))
            # cleaning operation after each new client connection
            self.cleanup_workers()
            
        else:
            self.LOGGER.add("server: serving loop exit")

