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
import core.shared

class Controller:
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_shutdown)
        signal.signal(signal.SIGTERM, self.signal_shutdown)

        self.STORAGE = core.storage.Storage()
        self.LOGGER = core.logger.Logger(self.STORAGE.logs_dir)
        self.BITCOIN = core.machine.BitcoinDaemon()
        self.NODE = core.machine.Node()
        self.NETWORK = core.network.NetworkServer("0.0.0.0", 46850)
        self.CACHE = core.data.Cache()
        self.DATA = core.data.Interface(self.STORAGE, self.CACHE, self.BITCOIN)
        self.SERVICES = core.services.Engine()
        self.PROTOCOL = core.protocol.RequestHandler(self.DATA.get_data)

        self.internet_on = False
        self.local_ip_addr = None
        self.bitcoind_running = False
        self.is_serving = False

        self.logger_thread = threading.Thread(target = self.LOGGER.worker, name = "logger-thread", daemon = True)
        self.server_thread = threading.Thread(target = self.peers_receiver, name = "server-thread", daemon = True)
        self.services_thread = threading.Thread(target = self.SERVICES.worker, name = "services-thread", daemon = True)

        self.max_peers = 5
        self.active_peers = [] # list of dicts {'peer': peer, 'worker': worker}

        ## logger init
        self.LOGGER.is_working = True
        self.logger_thread.start()
        core.shared.Log.info = self.LOGGER.info
        core.shared.Log.warning = self.LOGGER.warning
        core.shared.Log.critical = self.LOGGER.critical
        ## internal apis
        core.shared.Data.get = self.DATA.get_data
        self.LOGGER.info("server init")

    def init_network(self):
        self.LOGGER.info("init network")
        self.local_ip_addr = self.NODE.get_local_IP()
        self.NETWORK.start_serving()
        #self.serving_thread = threading.Thread(target = self.peers_receiver, name = "serving-thread", daemon = True)

    def init_services(self):
        self.LOGGER.info("init services")
        self.CACHE.info_data['systeminfo']['bitcoindpid'] = self.NODE.run_command(["pidof", "bitcoind"])
        self.SERVICES.add_new_service('BtcCoreDaemon', self.service_daemon, False)
        self.SERVICES.add_new_service('UpdateCache', self.service_update_cache, True)
        #self.service_thread = threading.Thread(target = self.SERVICES.worker, name = "service-thread", daemon = True)
        self.SERVICES.controller.clear()
        self.SERVICES.worker_on = True

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
                    local_cli_worker = threading.Thread(target = self.PROTOCOL.local_cli_handler, args = [peer])
                    local_cli_worker.start()
                else:
                    peer_cert = self.STORAGE.load_certificate(peer.peer_id)
                    peer.handshake(peer_cert)
                    if peer.is_connected and self.available_slots():
                        #self.NETWORK.connected_peers.append(peer)
                        worker = threading.Thread(target = self.PROTOCOL.peers_worker, args = [peer], name = f"peer-{peer.peer_id}")
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
        self.bitcoind_running = self.NODE.check_bitcoin_daemon()

    def service_update_cache(self):
        self.CACHE.info_data['uptimeinfo'] = self.NODE.run_command(["bitcoin-cli", "uptime"])
        self.CACHE.info_data['blockchaininfo'] = self.NODE.run_command(["bitcoin-cli", "getblockchaininfo"])
        self.CACHE.info_data['networkinfo'] = self.NODE.run_command(["bitcoin-cli", "getnetworkinfo"])
        self.CACHE.info_data['mempoolinfo'] = self.NODE.run_command(["bitcoin-cli", "getmempoolinfo"])
        self.CACHE.info_data['mininginfo'] = self.NODE.run_command(["bitcoin-cli", "getmininginfo"])
        self.CACHE.info_data['nettotalsinfo'] = self.NODE.run_command(["bitcoin-cli", "getnettotalsinfo"])
        self.CACHE.info_data['peersinfo'] = self.NODE.run_command(["bitcoin-cli", "getpeersinfo"])
        self.CACHE.last_update = int(time.time())
        self.LOGGER.info("bitcoin cache updated")

    def service_geolocation(self):
        pass

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
        self.SERVICES.stop_all()
        self.SERVICES.worker_on = False
        #self.service_thread.join()
        #sys.exit(0)
