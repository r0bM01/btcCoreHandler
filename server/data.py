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

import platform, json, time
import server.machine
from lib.network import Utils


class Cache:
    def __init__(self):
        ## hosting machine details
        self.node_details = {
            'node': platform.node(),
            'machine': platform.machine(),
            'system': platform.system(),
            'release': platform.release() 
            }

        ## hosting machine bitcoin process ID
        self.PID = None

        ## btcCoreHandler server start time
        self.server_init_time = None

        ## Bitcoin related data
        self.bitcoin_info = {
            'uptime': None,
            'blockchaininfo': None,
            'networkinfo': None,
            'mempoolinfo': None,
            'mininginfo': None,
            'nettotalsinfo': None,
            'peersinfo': None 
            }
        ## last update time
        self.bitcoin_update_time = None

        ## IP Geolocation
        self.geolocation_index = None # database must be loaded ## index[ip_address] = position on file
        self.geolocation_write = None # function to write into database
        self.geolocation_read = None # function to read from database
        ## peersInfo + geolocation
        self.connectedInfo = None 
    
    def get_bitcoin_info(self, logger):
        ## runs the machine calls
        self.bitcoin_info['uptime'] = json.loads(server.machine.MachineInterface.runBitcoindCall("uptime"))
        self.bitcoin_info['blockchaininfo'] = json.loads(server.machine.MachineInterface.runBitcoindCall("getblockchaininfo"))
        self.bitcoin_info['networkinfo'] = json.loads(server.machine.MachineInterface.runBitcoindCall("getnetworkinfo"))
        self.bitcoin_info['nettotalsinfo']= json.loads(server.machine.MachineInterface.runBitcoindCall("getnettotals"))
        self.bitcoin_info['mempoolinfo'] = json.loads(server.machine.MachineInterface.runBitcoindCall("getmempoolinfo"))
        self.bitcoin_info['mininginfo'] = json.loads(server.machine.MachineInterface.runBitcoindCall("getmininginfo"))
        self.bitcoin_info['peersinfo'] = json.loads(server.machine.MachineInterface.runBitcoindCall("getpeerinfo"))
        self.bitcoin_update_time = int(time.time()) 

        for info, value in self.bitcoin_info.items():
            if not bool(value):
                logger.add("data: bitcoin call didn't work", info)

        #if not all(bool(value) for key, value in self.bitcoin_info.items()):
        #    logger.add("server: a bitcoin call didn't work")

    def get_geolocation_update(self, logger):
        all_peers = self.bitcoin_info['peersinfo']
        known_ips = []
        batch_ips = []
        geo_data = []
        for peer in all_peers:
            ip = peer['addr'].split(":")[0]
            known_ips.append(ip) if ip in self.geolocation_index else batch_ips.append(ip)

        if len(batch_ips) > 0:
            logger.add("geolocation: found new nodes", len(batch_ips))
            for x in range(0, len(batch_ips), 100):
                geo_data.extend(Utils.getBatchGeolocation(batch_ips[x:x+100]))
        
        for geo in geo_data:
            self.geolocation_index[geo['ip']] = self.geolocation_write(geo)

        geo_data = [self.geolocation_read(self.geolocation_index[ip]) for ip in known_ips]
        
        for peer in all_peers:
            ip = peer['addr'].split(":")[0]
            for geo in geo_data:
                if geo['ip'] == ip:
                    peer.update(geo)

        self.connectedInfo = all_peers

    def get_geolocation_entry(self, ip):
        if not Utils.getCheckedIp(ip): 
            result = {'error': 'ip address not valid'}
        elif ip in self.geolocation_index:
            result = self.geolocation_read(self.geolocation_index[ip])
        else:
            result = {'error': 'ip address not found'}
        return result

    def get_geolocation_search(self, txt_input):
        target = text_input.lower()
        result = []
        if Utils.getCheckedIp(target) and target in self.geolocation_index:
            result.append(self.geolocation_read(self.geolocation_index[target]))
        else: 
            for peer in self.geolocation_index:
                geo_data = self.geolocation_read(self.geolocation_index[peer])
                if len(target) == 2 and target in geo_data['country_code2'].lower():
                    result.append(geo_data)
                elif len(target) > 2 and target in geo_data['country_name'].lower():
                    result.append(geo_data)
                elif len(target) > 2 and target in geo_data['isp'].lower():
                    result.append(geo_data)
        if not bool(result):
                result.append({"error": "no results found!"})    
        return result

