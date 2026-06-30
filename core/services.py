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

import gc
import datetime as dt
from threading import Event
from time import time


class Engine:
    def __init__(self, logger, interface):
        self.logger = logger
        self.interface = interface

        self.services = list() 

        self.worker = Event()
        self.worker_rest = 30
        self.worker_last_round = None
        self.worker_nums_round = 0

    def activate_service(self, service):
        service.active = True
        self.logger.info(f"service {service.name}", "activated")

    def deactivate_service(self, service):
        service.active = False
        self.logger.info(f"service {service.name}", "deactivated")

    def activate_all(self):
        for service in self.services:
            self.activate_service(service)

    def deactivate_all(self):
        for service in self.services:
            self.deactivate_service(service)

    def is_working(self):
        return not self.worker.is_set()

    def get_time(self):
        return int(time())

    def set_pause(self, seconds):
        return self.get_time() + int(seconds)

    def add_new_service(self, service):
        new_service = service(self.interface)
        self.services.append(new_service)
        self.logger.info("service added", new_service.name)

    def sanitizer(self, service, error_code):
        self.logger.info("server: service error", service.name, error_code)
        if service.errors < 5:
            service.pause = self.set_pause(320)
        else:
            service.pause = self.set_pause(640)
        service.errors += 1
        self.logger.info("service sanitizing attempt", service.errors)

    def run_service(self, service):
        if service.active and (service.pause < self.get_time()):
            if not (self.worker_nums_round % 100):
                garbage = gc.collect()
                self.logger.info("services garbage collected", f"{garbage} objects")
                self.logger.info("service still running", service.name)
            try:
                start_time = self.get_time()
                service.run()  # executes the callback function
                service.pause = 0
                service.last_run = self.get_time()
                service.run_time = service.last_run - start_time
                if service.run_time > 30:
                    self.logger.info("services long run", service.name, service.run_time)
                    service.errors += 1
            except Exception as error_code:
                # log the error and try to sanitaze
                self.sanitizer(service, error_code)
                pass

    def work(self):
        self.worker.wait()
        self.worker.clear()  # reset worker condition to false
        while self.is_working():
            start_time = self.get_time()
            [self.run_service(service) for service in self.services]
            self.worker_last_round = self.get_time()
            self.worker_nums_round += 1
            self.worker.wait(self.worker_rest - (self.worker_last_round - start_time))
        else:
            self.logger.info("services engine worker has stopped")


class BitcoinCacheUpdater:
    def __init__(self, interface):
        self.name = "BitcoinCacheUpdater"
        self.active = False
        self.pause = 0
        self.last_run = 0
        self.errors = 0
        self.interface = interface
        self.automated_calls = [
            "uptime",
            "getblockchaininfo",
            "getnetworkinfo",
            "getmempoolinfo",
            "getmininginfo",
            "getpeerinfo",
            "getnettotals",
        ]

    def run(self):
        for call in self.automated_calls:
            data = self.interface.daemon_call(call)
            self.interface.update_cache(call, data[call])


class BitcoinDaemonChecker:
    def __init__(self, interface):
        self.name = "BitcoinDaemonChecker"
        self.active = False
        self.pause = 0
        self.last_run = 0
        self.errors = 0
        self.interface = interface

    def run(self):
        self.interface.daemon.is_running = self.interface.daemon.daemon_running()


class BitcoinPeersGeolocation:
    def __init__(self, interface):
        self.name = "BitcoinPeersGeolocation"
        self.active = False
        self.pause = 0
        self.last_run = 0
        self.errors = 0
        self.interface = interface
        self.interface.cache["getpeergeo"] = dict()

    def run(self):
        active_ips = [
            peer["addr"].rpartition(":")[0].strip("[]")
            for peer in self.interface.cache["getpeerinfo"]
        ]
        geo_data = {
            ip: self.interface.cache["getpeergeo"].get(ip)
            for ip in active_ips
            if ip in self.interface.cache["getpeergeo"].keys()
        }
        ip_list = [
            ip
            for ip in active_ips
            if ip not in self.interface.cache["getpeergeo"].keys()
        ]
        geo_data.update(
            {geo.get("ip"): geo for geo in self.interface.load_geolocation(ip_list)}
        )
        self.interface.update_cache("getpeergeo", geo_data)


class NextcloudNotifications:
    def __init__(self, interface):
        self.name = "NextcloudNotifications"
        self.active = False
        self.pause = 0
        self.last_run = 0
        self.errors = 0
        self.interface = interface
        self.schedules = [(18, 30)] # list of [tuple(hour, min)]
        self.timestamps = []
    
    def build_timestamps(self):
        if not bool(self.timestamps):
            for s in self.schedules:
                ts = dt.datetime(dt.datetime.now().year, dt.datetime.now().month, dt.datetime.now().day, s[0], s[1]).timestamp()
                if ts <= dt.datetime.now().timestamp():
                    ts += (60 * 60 * 24)
                self.timestamps.append(ts)
        if not bool(self.pause):
            if len(self.timestamps) < (len(self.schedules) * 2):
                new_ts = [ts + (60 * 60 * 24) for ts in self.timestamps]
                self.timestamps.extend(new_ts)
        self.timestamps.sort()

    def run(self):
        self.build_timestamps()
        if dt.datetime.now().timestamp() >= self.timestamps[0]:
            message = "Some info regarding bitcoin code node\n"
            message += f"BitcoinD uptime: {self.interface.cache['uptime']}\n"
            message += f"Connected Peers: {len(self.interface.cache['getpeerinfo'])}\n"
            self.interface.send_to_nextcloud(message)
            self.timestamps.pop(0)


                  
