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
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_shutdown)
        signal.signal(signal.SIGTERM, self.signal_shutdown)

        self.STORAGE = core.storage.Storage()
        self.LOGGER = core.logger.Logger(self.STORAGE.logs_dir)
        self.BITCOIN = core.machine.BitcoinDaemon()
        self.NODE = core.machine.Node()
        self.NETWORK = core.network.NetworkServer("0.0.0.0", 46850)
        
        self.data_interface = core.data.Interface(self.STORAGE)
        self.SERVICES = core.services.Engine(self.LOGGER, self.data_interface)
        self.protocol = core.protocol.RequestHandler()

        self.internet_on = False
        self.local_ip_addr = None
        self.bitcoind_running = False
        self.is_serving = False

        #self.shutdown_notify = threading.Event()
        self.logger_thread = threading.Thread(target = self.LOGGER.worker, name = "logger-thread", daemon = True)
        self.server_thread = threading.Thread(target = self.peers_receiver, name = "server-thread", daemon = True)
        self.services_thread = threading.Thread(target = self.SERVICES.work, name = "services-thread", daemon = True)

        self.max_peers = 5
        self.active_peers = [] # list of dicts {'peer': peer, 'worker': worker}

        ## logger init
        self.LOGGER.is_working = True
        self.logger_thread.start()
        self.LOGGER.info("server starting")

    def init_network(self):
        self.LOGGER.info("init network")
        self.local_ip_addr = self.NODE.get_local_IP()
        self.external_ip_addr = self.NODE.get_external_IP()
        self.is_serving = True
        self.NETWORK.start_serving()
        self.LOGGER.info("network socket ready", self.NETWORK.server_ready)
        self.LOGGER.info("network server address", self.local_ip_addr)
        self.LOGGER.info("network external ip", self.external_ip_addr)
        self.LOGGER.info("bitcoin daemon ready", self.service_daemon())

    def init_services(self):
        self.LOGGER.info("init services")
        self.SERVICES.worker.clear()
        self.SERVICES.add_new_service(core.services.BitcoinDaemonChecker)
        self.SERVICES.add_new_service(core.services.BitcoinCacheUpdater)
        self.SERVICES.activate_all()
        
    
    def run_all(self):
        self.LOGGER.info("starting threads")

        self.server_thread.start()
        self.services_thread.start()

        self.LOGGER.info(f"{self.server_thread.name}", "active", self.server_thread.is_alive())
        self.LOGGER.info(f"{self.services_thread.name}", "active", self.services_thread.is_alive())

        self.SERVICES.worker.set() # starts working here

    def is_server_on(self):
        if bool(self.serving_thread):
            self.is_serving = (self.serving_thread.is_alive() and self.SERVICES.is_working())
        else:
            self.is_serving = False
        return self.is_serving

    def peers_receiver(self):
        while self.is_serving:
            peer = self.NETWORK.get_new_peer()
            if bool(peer):
                if peer.is_local_cli:
                    local_cli_worker = threading.Thread(target = self.protocol.local_cli_handler, args = [peer])
                    local_cli_worker.start()
                else:
                    peer_cert = self.STORAGE.load_certificate(peer.peer_id)
                    peer.handshake(peer_cert)
                    if peer.is_connected and self.available_slots():
                        #self.NETWORK.connected_peers.append(peer)
                        worker = threading.Thread(target = self.protocol.peers_worker, args = [peer], name = f"peer-{peer.peer_id}")
                        self.active_peers.append({'peer': peer, 'worker': worker})
                        worker.start()
                    else:
                        if not peer.is_connected:
                            # peer couldn't pass handshake
                            pass
                        else:
                            peer.send_msg({'error': 'server has reached the maximum peers'})
            else:
                # no peer received
                # might do something
                pass
            self.cleanup_peers()
        else:
            """stopped serving"""
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


    def signal_shutdown(self, signum, frame):
        # shutdown by signal
        # to log it
        self.graceful_shutdown()

    def graceful_shutdown(self):
        self.LOGGER.info("shutting down gracefully")
        self.is_serving = False
        #self.serving_thread.join()
        for peer_ in self.active_peers:
            peer_['peer'].disconnect()
            peer_['worker'].join()
        self.SERVICES.deactivate_all()
        self.SERVICES.worker.set()
        #self.server_thread.join()
        #self.services_thread.join()
        self.LOGGER.info(f"{self.server_thread.name}", self.server_thread.is_alive())
        self.LOGGER.info(f"{self.services_thread.name}", self.services_thread.is_alive())


        self.LOGGER.is_working = False
        #self.service_thread.join()
        #sys.exit(0)
