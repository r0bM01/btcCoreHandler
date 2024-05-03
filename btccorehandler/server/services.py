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


import json, threading
import lib.server.machine


class Engine:
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