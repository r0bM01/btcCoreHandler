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


import time
from threading import Event
from core.shared import Log

class Engine:
    def __init__(self):

        self.services = dict()

        self.controller = Event()

        self.logger = Log.info

        self.worker_on = False
        self.worker_rest = 30
        self.worker_last_round = None

    def start_service(self, name):
        self.services[name]['active'] = True

    def stop_service(self, name):
        self.services[name]['active'] = False

    def start_all(self):
        for name in self.services:
            self.services[name]['active'] = True

    def stop_all(self):
        for name in self.services:
            self.services[name]['active'] = False

    def is_working(self):
        return self.worker_on

    def get_time(self):
        return int(time.time())

    def set_pause(self, seconds):
        return self.get_time() + int(seconds)

    def add_new_service(self, name, target, bitcoind):
        service = {'name': name, 'target': target, 'bitcoind': bitcoind, 'active': False}
        service['last_run'] = None
        service['pause'] = None
        service['errors'] = None
        self.services[name] = service

    def errors(self):
        return {self.services[service]['name'] : self.services[service]['errors'] for service in self.services}

    def running(self):
        return [self.services[service]['name'] for service in self.services if self.services[service]['active']]

    def sanitizer(self, service, error_code):
        self.logger.add("server: service error", service['name'], error_code)
        if service['errors'] < 5:
            service['pause'] = self.set_pause(120)
        else:
            service['pause'] = self.set_pause(300)
        service['errors'] += 1
        self.logger.add("server: service sanitizing attempt", service['errors'])

    def run_service(self, name):
        service = self.services[name]
        if service['active'] and (service['pause'] < self.get_time()):
            try:
                service['target']() # executes the callback function
                service['last_run'] = self.get_time()
                service['pause'] = 0
            except Exception as error_code:
                # log the error and try to sanitaze
                self.sanitizer(service, error_code)
                pass

    def worker(self):
        while self.is_working:
            [self.run_service(name) for name in self.services]
            self.worker_last_round = self.get_time()
            self.controller.wait(self.worker_rest)
