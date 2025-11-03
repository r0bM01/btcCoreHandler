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


class Interface:
    """Class used to dispatch the differnt types of data and limit the number of requests """
    """Cached data can be access by all peers togheter """
    """Database stored data can be accessed by 3 peers per time"""
    """Data retriewed from bitcoind can be accessed to 1 peer per time"""

    def __init__(self, storage, cache, bitcoind):
        self.bitcoind_pipe = BoundedSemaphore(value = 1) # limit requests to 1 peer per time
        self.database_pipe = BoundedSemaphore(value = 3) # limit requests to 3 peer per time
        self.data = {
            'stored': storage,
            'cached': cache,
            'bitcoin': bitcoind
        }
    def bitcoind_pipeline(self, method_call, *method_args):
        is_ready = self.bitcoind_pipe.acquire(timeout = 2)
        if is_ready:
            response = self.data['bitcoind'].get_data(method_call, method_args)
            self.bitcoind_pipe.release()
        else:
            response = {'error': 'bitcoin daemon is busy and cannot process your request'}
        return response

    def database_pipeline(self, method_call, *method_args):
        is_ready = self.database_pipe.acquire(timeout = 2)
        if bool(is_ready):
            response = self.data['stored'].get_data(method_call, method_args)
            self.database_pipe.release()
        else:
            response = {'error': 'database is busy and cannot serve your request'}
        return response

    def get_data(self, method_type, method_call, *method_args):
        if method_type == 'cached':
            data = self.data[method_type].get_data(method_call, method_args)
        elif method_type == 'stored':
            data = self.database_pipeline(method_call, method_args)
        else:
            data = self.bitcoind_pipeline(method_call, method_args)
        return data


class Cache:
    def __init__(self):

        self.info_data = {
            'systeminfo': {
                    'started': int(time.time()),
                    'node': platform.node(),
                    'machine': platform.machine(),
                    'system': platform.system(),
                    'release': platform.release(),
                    'bitcoindpid': None,
            },
            'uptimeinfo': None,
            'blockchaininfo': None,
            'networkinfo': None,
            'mempoolinfo': None,
            'mininginfo': None,
            'nettotalsinfo': None,
            'peersinfo': None
            }

        self.last_update = int()

    def get_data(self, info_type, *info_fields):
        if bool(info_fields):
            response = {f: self.info_data[info_type].get(f, 'invalid argument') for f in info_fields}
        else:
            response = self.info_data[info_type]
        return response

    def update_info(self, info_type, info_value):
        self.info_data[info_type] = info_value
