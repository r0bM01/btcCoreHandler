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
import server.machine


class Engine:
    def __init__(self, logger, daemon):

        self.services = []

        self.services_controller = threading.Event()
        

        self.logger = logger
        self.daemon_running = daemon

        self.worker = self.make_new_thread()
        self.worker_rest = 30

    def start(self):
        for service in self.services:
            service['active'] = True # activates all services
            self.logger.add("server: service", service['name'], service['active'])
        if not bool(self.worker):
            self.worker = self.make_new_thread()
        #if not self.worker.is_alive:
        self.services_controller.clear()
        self.worker.start()
        self.logger.add("server: services worker started", self.worker.is_alive())
    
    def stop(self):
        for service in self.services:
            service['active'] = False # deactivates all services
            self.logger.add("server: service", service['name'], service['active'])
        if self.worker.is_alive():
            self.services_controller.set()
            self.worker.join()

    def make_new_thread(self):
        return threading.Thread(target = self.services_worker, daemon = True)
    
    def add_new_service(self, name, target, bitcoind):
        self.services.append({'name': name, 'target': target, 'needbtcd': bitcoind, 'active': False})
    
    def services_running(self):
        return [service for service in self.services if service['active']]
    
    def services_exec(self, service):
        bitcoind_running = self.daemon_running()
        if service['needbtcd']:
            if bitcoind_running: service['target'](self.logger)
            else: service['active'] = False # disables the service if bitcoind is not running and necessary
        else:
            service['target'](self.logger)

    def services_worker(self):
        while not self.services_controller.is_set():
            for service in self.services:
                if service['active']: 
                    self.services_exec(service) # execute the service if active

            self.services_controller.wait(self.worker_rest)