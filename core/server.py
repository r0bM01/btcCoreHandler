# Copyright [2023-present] [R0BM01@pm.me]                                   #
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

import time, threading, sys, signal

import core.logger
import core.network
import core.storage 
import core.protocol 
import core.data 
import core.machine 
import core.services 


class ThreadMan:
    pass

class Controller:
    def __init__(self, config):
        signal.signal(signal.SIGINT, self.signal_shutdown)
        signal.signal(signal.SIGTERM, self.signal_shutdown)

        self.shutdown_notification = threading.Event()
        self.shutdown_notification.clear()
        

        self.storage = core.storage.Storage()
        self.logger = core.logger.Logger(self.storage.logs_dir)
        self.interface = core.data.Interface(self.storage)


        core.network.BTCDAEMON_HOST = config['bitcoin']['host']
        core.network.BTCDAEMON_PORT = config['bitcoin']['port']
        core.network.BTCDAEMON_USER = config['bitcoin']['user']
        core.network.BTCDAEMON_PASS = config['bitcoin']['pass']

        self.certificate = config['network']['certificate']

        
        self.NODE = core.machine.Node()
        self.network = core.network.NetworkServer(config['network']['host'], config['network']['port'])
        
        
        self.SERVICES = core.services.Engine(self.logger, self.interface)
        self.protocol = core.protocol.RequestHandler(self.logger, self.interface)


        self.logger_thread = threading.Thread(target = self.logger.worker, name = "logger-thread", daemon = True)
        self.server_thread = threading.Thread(target = self.peers_receiver, name = "server-thread", daemon = True)
        self.services_thread = threading.Thread(target = self.SERVICES.work, name = "services-thread", daemon = True)


        self.is_serving = False
        self.internet_on = False
        self.local_ip_addr = None
        self.external_ip_addr = None

        self.max_peers = 5
        self.active_peers = [] # list of dicts {'peer': peer, 'worker': worker}

        ##.logger init
        self.logger.is_working = True
        self.logger_thread.start()
        self.logger.info("server starting")

    def init_network(self):
        self.logger.info("init network")
        self.local_ip_addr = self.NODE.get_local_IP()
        self.external_ip_addr = core.network.get_external_ips()
        self.network.server_enable()
        self.logger.info("network socket ready", bool(self.network.server_ready))
        self.logger.info("network bind address", self.network.server_addr)
        self.logger.info("network port open", self.network.server_port)
        self.logger.info("network local address", self.local_ip_addr)
        for ip in self.external_ip_addr:
            self.logger.info("network external address",  f"IPv{ip.version}", ip.exploded)
        self.is_serving = True

    def init_services(self):
        self.logger.info("init services")
        self.SERVICES.worker.clear()
        self.SERVICES.add_new_service(core.services.BitcoinDaemonChecker)
        self.SERVICES.add_new_service(core.services.BitcoinCacheUpdater)
        self.SERVICES.add_new_service(core.services.BitcoinPeersGeolocation)
        self.SERVICES.add_new_service(core.services.NextcloudNotifications)
        self.SERVICES.activate_all()
        
    def run_all(self):
        self.logger.info(f"bitcoin daemon running", self.interface.daemon.is_running)
        if self.interface.daemon.is_running:
            self.logger.info("starting threads")
            self.server_thread.start()
            self.services_thread.start()
            self.logger.info(f"{self.server_thread.name}", "active", self.server_thread.is_alive())
            self.logger.info(f"{self.services_thread.name}", "active", self.services_thread.is_alive())
            self.SERVICES.worker.set() # starts working here
        else:
            self.logger.info("btcCoreHandler cannot work without the bitcoin daemon!")

    def is_server_on(self):
        if bool(self.serving_thread):
            self.is_serving = (self.serving_thread.is_alive() and self.SERVICES.is_working())
        else:
            self.is_serving = False
        return self.is_serving

    def peers_receiver(self):
        while self.is_serving:
            peer = self.network.get_new_peer()
            if isinstance(peer, core.network.Peer):
                self.logger.info("server client connecting", peer.peer_addr)
                if peer.is_local_cli:
                    self.logger.info("server client connected", "LOCAL")
                    local_cli_worker = threading.Thread(target = self.protocol.local_cli_handler, args = [peer, self.shutdown_notification])
                    local_cli_worker.start()
                    local_cli_worker.join()
                else:
                    #peer_cert = self.storage.load_certificate(peer.peer_id)
                    #self.logger.info("server handshaking with client", peer.peer_id.hex())
                    peer_cert = bytes.fromhex(self.certificate)
                    peer.handshake(peer_cert)
                    if peer.is_connected and self.available_slots():
                        self.logger.info("server client connected", peer.peer_addr, peer.is_connected)
                        worker = threading.Thread(target = self.protocol.peers_worker, args = [peer], name = f"peer-{peer.peer_id.hex()}")
                        self.active_peers.append({'peer': peer, 'worker': worker})
                        worker.start()
                    elif not peer.is_connected:
                        self.logger.info("server client refused", peer.peer_addr)
                        peer.disconnect()
                    
                    else:
                        peer.send_msg({'error': 'server has reached the maximum peers'})
            else:
                # no peer received
                # might do something
                pass
            self.cleanup_peers()
        else:
            self.logger.info("server shutting down")
            pass

    def available_slots(self):
        return len(self.active_peers) < self.max_peers

    def cleanup_peers(self):
        for peer_ in self.active_peers:
            if not peer_['peer'].is_connected:
                peer_['worker'].join() # it does nothing but just for clarity
                self.active_peers.remove(peer_)

    def service_daemon(self):
        return self.NODE.check_bitcoin_daemon()


    def wait_for_shutdown(self):
        self.logger.info("btcCoreHandler server fully started")
        while not self.shutdown_notification.is_set():
            if not self.interface.daemon.is_running: 
                self.logger.info("bitcoin daemon is not running!")
                self.shutdown_notification.set()
            self.shutdown_notification.wait(15) # <-- main thread waits here
        else:
            self.graceful_shutdown()
        

    def signal_shutdown(self, signum, frame):
        self.logger.info("shutdown from signal", signum)
        self.shutdown_notification.set()
    

    def graceful_shutdown(self):
        self.logger.info("shutting down gracefully")
        
        """"
        for peer_ in self.active_peers:
            peer_['peer'].disconnect()
            peer_['worker'].join(3)"""

        self.is_serving = False
        self.server_thread.join(3)

        self.network.server_disable()
        self.logger.info("network shutting down")
        self.logger.info("services shutting down")
        self.SERVICES.deactivate_all()
        self.SERVICES.worker.set()
        self.services_thread.join(3)
        
        self.logger.info(f"{self.server_thread.name}", self.server_thread.is_alive())
        self.logger.info(f"{self.services_thread.name}", self.services_thread.is_alive())

        self.logger.queue.join()
        self.logger.is_working = False
        #self.service_thread.join()
        sys.exit(0)
