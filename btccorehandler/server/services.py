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


import json, threading, time
import server.machine


class Engine:
    def __init__(self, logger, daemon):

        self.services = []

        self.services_controller = threading.Event()
        
        self.logger = logger
        self.daemon_running = daemon

        self.worker = self.make_new_thread()
        self.worker_rest = 30
        self.worker_last_round = None

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

    def get_time(self):
        return int(time.time())

    def set_pause(self, seconds):
        return self.get_time() + int(seconds)

    def make_new_thread(self):
        return threading.Thread(target = self.services_worker, daemon = True)
    
    def add_new_service(self, name, target, bitcoind):
        service = {'name': name, 'target': target, 'needbtcd': bitcoind, 'active': False}
        service['last_run'] = 0
        service['pause'] = 0
        service['errors'] = 0
        self.services.append(service)

    def services_errors(self):
        return {service['name'] : service['errors'] for service in self.services}
    
    def services_running(self):
        return [service['name'] for service in self.services if service['active']]

    def services_sanitizer(self, service, error_code):
        self.logger.add("server: service error", service['name'], error_code)
        if service['needbtcd']:
            service['active'] = True if self.daemon_running() else False

        if service['errors'] < 5:
            service['pause'] = self.set_pause(120)
        else:
            service['pause'] = self.set_pause(300)
        service['errors'] += 1
        self.logger.add("server: service sanitizing attempt", service['errors'])

    def services_exec(self, service):
        bitcoind_running = self.daemon_running()
        if (service['needbtcd'] and bitcoind_running) or not service['needbtcd']:
            try: 
                service['target'](self.logger)
                service['last_run'] = self.get_time()
                service['pause'] = 0
            except Exception as error_code:
                self.services_sanitizer(service, error_code)
        else: 
            service['active'] = False # disables the service if bitcoind is not running and necessary

    def services_worker(self):
        while not self.services_controller.is_set():
            for service in self.services:
                if service['active'] and service['pause'] < self.get_time(): 
                    self.services_exec(service) # execute the service if active
            self.worker_last_round = self.get_time()
            self.services_controller.wait(self.worker_rest)