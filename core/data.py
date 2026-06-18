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

import platform, time
from threading import BoundedSemaphore

from lib.base_crypto import Utils

from core.machine import BitcoinDaemon
from core.network import get_geolocation
from core.storage import BitcoinPeers


class Interface:
    """Class used to dispatch the differnt types of data and limit the number of requests """
    """Cached data can be access by all peers togheter """
    """Database stored data can be accessed by 3 peers per time"""
    """Data retriewed from bitcoind can be accessed to 1 peer per time"""

    def __init__(self, storage):
        self.control = BoundedSemaphore(value = 1)
        self.daemon = BitcoinDaemon()
        self.database = BitcoinPeers(storage.storage_dir)

        self.system = {
            'started': int(time.time()),
            'node': platform.node(),
            'machine': platform.machine(),
            'system': platform.system(),
            'release': platform.release(),
        }

        self.cache = dict()
        self.cache_timestamp = None
    
    def update_cache(self, key, data):
        #self.cache[key].clear()
        self.cache[key] = data
        self.cache_timestamp = int(time.time())
        
    def cleanup_cache(self):
        self.cache.clear()

    def load_geolocation(self, ip_list: list)-> list:
        geo_from_db = self.database.select_geolocation(ip_list)
        [ip_list.remove(geo.get('ip')) for geo in geo_from_db if geo.get('ip') in ip_list]
        geo_from_web = [get_geolocation(ip) for ip in ip_list]
        [self.database.insert_geolocation(geo) for geo in geo_from_web]
        return geo_from_db + geo_from_web
    
    def daemon_call(self, method, *args):
        if self.control.acquire(timeout = 3):
            response = self.daemon.rpc(method, [a for a in args])
            self.control.release()
        else:
            response = {'error': 'bitcoin daemon is busy and cannot process your request'}
        return response

    # data calls will arrive here already checked
    def get_data(method, *args):
        if method in self.cache.keys():
            response = self.cache[method]
        elif method in self.system:
            response = self.system[method]
        else:
            response = self.daemon_call(method, *args)
        return response
            





