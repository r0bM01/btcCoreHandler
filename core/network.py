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

## new imports
from lib.base_network import Server, SimplePeer
from lib.base_crypto import ScrumbledEggsProto, Utils
from time import time
from urllib import request

import ssl, json

class NetworkServer(Server):
    def __init__(self, bind_addr, open_port):
        self.server_addr = bind_addr
        self.server_port = open_port

        self.server_ready = False

        self.max_peers = 5
        self.connected_peers = []

    def start_serving(self):
        self.create_server()
        self.server_ready = bool(self.server_socket)

    def stop_serving(self):
        self.disconnect_all_peers()
        self.close_server()
        self.server_ready = False

    def disconnect_all_peers(self):
        for peer in self.connected_peers:
            peer.disconnect()
            self.connected_peers.remove(peer)

    def cleanup_peers(self):
        for peer in self.connected_peers:
            if not peer.is_connected:
                self.connected_peers.remove(peer)

    def get_new_peer(self):
        peer = False
        peer_socket, peer_addr = self.accept_new_client()
        if bool(peer_socket):
            peer_id = self.raw_recv(peer_socket, 16)
            peer = Peer(peer_socket, peer_addr, peer_id)
            peer.is_local_cli = self.is_loopback(peer_addr)
        else:
            self.raw_closure(peer_socket)
        return peer


class Peer(SimplePeer):
    def __init__(self, peer_socket, peer_addr, peer_id):
        self.peer_socket = peer_socket
        self.peer_addr = peer_addr
        self.peer_crypto = ScrumbledEggsProto()
        self.peer_id = peer_id
        self.encryption_key = None
        self.is_connected = False
        self.is_local_cli = False
        self.waiting_mode = 120
        self.first_seen = int(time())
        self.last_seen = self.first_seen
        self.data_exchanged = 0
        self.reputation = 5


    def set_waiting_mode(self, wait_seconds = False):
        self.peer_socket.settimeout(wait_seconds or self.waiting_mode)

    def handshake(self, certificate):
        random_bytes = Utils.get_random_bytes(16)
        solution_bytes = self.peer_crypto.double_hash(certificate, random_bytes)
        if self.send_data(random_bytes) and self.recv_data() == solution_bytes:
            self.encryption_key = self.peer_crypto.double_hash(certificate, solution_bytes)
            self.is_connected = True

    def is_alive(self):
        return (int(time()) - self.last_seen) < 120

    def send_msg(self, msg) -> bool:
        if type(msg) is str:
            msg = msg.encode('utf-8')
        encrypted_msg = self.peer_crypto.encrypt_bytes(msg, self.encryption_key)
        self.data_exchanged += len(encrypted_msg)
        return self.send_data(encrypted_msg)

    def recv_msg(self) -> str:
        msg = str()
        encrypted_bytes = self.recv_data()
        if bool(encrypted_bytes):
            decrypted_msg = self.peer_crypto.decrypt_bytes(encrypted_bytes, self.encryption_key)
            msg = decrypted_msg.decode('utf-8')
            self.data_exchanged += len(encrypted_bytes)
            self.last_seen = int(time())
        return msg

    def disconnect(self):
        self.is_connected = False
        self.close_socket()


###########################################################################################################
###########################################################################################################

"""
class GeoLocation:
    def __init__(self):
        self.endpoints = {
            'geoiplookupio': {'endpoint': "https://json.geoiplookup.io/", 'context': ssl.create_default_context()},
            'ip-api': {'endpoint': "http://ip-api.com/batch?fields=61439", 'context': None}
        } ## to be use in future

    def get_geolocation(ip_list = []):
        result = []
        for ip in ip_list:
            req = request.Request(url = "https://json.geoiplookup.io/" + str(ip), headers = {'User-Agent': 'Mozilla/5.0'})
            res = request.urlopen(url = req, context = ssl.create_default_context())
"""

def get_geolocation(ip_addr):
    req = request.Request(url = "https://json.geoiplookup.io/" + str(ip_addr), headers = {'User-Agent': 'Mozilla/5.0'})
    res = request.urlopen(url = req, context = ssl.create_default_context()).read().decode()
    return json.loads(res)


"""
@staticmethod
    def getGeolocation(ip):
        context = ssl.create_default_context()
        
        #baseUrl = "https://api.iplocation.net/?ip=" + str(ip)
        
        baseUrl = "http://ip-api.com/json/" + str(ip) + str("?fields=26139")
        request = urllib.request.Request(url=baseUrl, headers={'User-Agent': 'Mozilla/5.0'})
        locationData = json.loads(urllib.request.urlopen(request).read().decode())
        ## format data to old mode
        geo_data = {'ip': locationData['query'], 'country_code2': locationData['countryCode'], 'country_name': locationData['country'], 'isp': locationData['isp']}
        return json.dumps(geo_data)

    @staticmethod
    def getBatchGeolocation(ips_list):
        ips = json.dumps(ips_list).encode('utf-8')
        endpoint = "http://ip-api.com/batch?fields=26139"
        request = urllib.request.Request(url = endpoint, data = ips, headers = {'User-Agent': 'Mozilla/5.0'})
        response = json.loads(urllib.request.urlopen(request).read().decode())
        for geo in response:
            geo['ip'] = geo['query']
            del geo['query']
        return response
    """