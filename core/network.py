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

import ssl, json, base64, ipaddress

class NetworkServer(Server):
    def __init__(self, bind_addr, open_port):
        self.server_addr = bind_addr
        self.server_port = open_port

        self.server_ready = False

        self.max_peers = 5
        self.connected_peers = []

    def server_enable(self):
        self.create_server()
        self.server_ready = bool(self.server_socket)

    def server_disable(self):
        #self.disconnect_all_peers()
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
            if self.is_loopback(peer_addr[0]):
                peer = LocalCli(peer_socket, peer_addr[0])
                peer.is_local_cli = True
            else:
                peer = Peer(peer_socket, peer_addr[0])
                peer.is_local_cli = False
        else:
            self.raw_closure(peer_socket)
        return peer


class Peer(SimplePeer):
    def __init__(self, peer_socket, peer_addr):
        self.peer_socket = peer_socket
        self.peer_addr = peer_addr
        self.peer_crypto = ScrumbledEggsProto()
        self.peer_id = None
        self.encryption_key = None
        self.is_connected = False
        self.is_local_cli = False
        self.waiting_mode = 60
        self.first_seen = int(time())
        self.last_seen = self.first_seen
        self.data_exchanged = 0
        self.reputation = 5


    def set_waiting_mode(self, wait_seconds = 0):
        self.peer_socket.settimeout(wait_seconds if bool(wait_seconds) else self.waiting_mode)

    def handshake(self, certificate):
        random_bytes = Utils.get_random_bytes(16)
        solution_bytes = Utils.get_hash(certificate, random_bytes)
        self.peer_id = self.recv_data() # not processed yet // for the future
        if self.send_data(random_bytes) and self.recv_data() == solution_bytes:
            self.encryption_key = Utils.get_hash(certificate, solution_bytes)
            self.is_connected = True

    def is_alive(self):
        return (int(time()) - self.last_seen) < self.waiting_mode

    def send_msg(self, msg: str) -> bool:
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


class LocalCli(SimplePeer):
    def __init__(self, cli_socket, cli_addr):
        self.peer_socket = cli_socket
        self.peer_addr = cli_addr
        self.peer_socket.settimeout(30)
        self.is_local_cli = False

    def send_msg(self, msg: str) -> bool:
        msg = msg.encode('utf-8')
        return self.send_data(msg)

    def recv_msg(self) -> str:
        msg = self.recv_data().decode('utf-8')
        return msg

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


BTCDAEMON_HOST = None
BTCDAEMON_PORT = None
BTCDAEMON_USER = ""
BTCDAEMON_PASS = ""

NEXTCLOUD_USER = ""
NEXTCLOUD_PASS = ""
NEXTCLOUD_CHAT = ""

def get_external_ips() -> list:
    endpoints = ["https://api.ipify.org", "https://api64.ipify.org"]
    ips = list()
    for ep in endpoints:
        req = request.urlopen(url = ep, context = ssl.create_default_context())
        if req.status == 200:
            ip = ipaddress.ip_address(req.read().decode())
            if ip not in ips:
                ips.append(ip)
    return ips

def get_geolocation(ip_addr) -> dict:
    req = request.Request(url = "https://json.geoiplookup.io/" + str(ip_addr), headers = {'User-Agent': 'Mozilla/5.0'})
    res = request.urlopen(url = req, context = ssl.create_default_context()).read().decode()
    geo = json.loads(res)
    geo['checksum'] = Utils.make_checksum(str("".join([str(geo[v]) for v in geo if v != 'ip'])).encode('utf-8'))
    return geo

def get_bitcoin_daemon(command) -> json:
    url = "http://" + BTCDAEMON_HOST + ":" + BTCDAEMON_PORT
    usr = BTCDAEMON_USER.encode('utf-8')
    psw = BTCDAEMON_PASS.encode('utf-8')
    auth = base64.b64encode(usr + b':' + psw)
    auth = auth.decode()
    header = {'content-type': 'application/json', 'Authorization': 'Basic ' + auth}
    req = request.Request(url = url, data = json.dumps(command).encode('utf-8'), headers = header)
    res = request.urlopen(req).read().decode()
    return json.loads(res)

def send_nextcloud_msg(message) -> None:
    url = "https://cloud.bareminds.eu/ocs/v2.php/apps/spreed/api/v1/chat/" + NEXTCLOUD_CHAT
    usr = NEXTCLOUD_USER.encode('utf-8')
    psw = NEXTCLOUD_PASS.encode('utf-8')
    auth = base64.b64encode(usr + b':' + psw)
    auth = auth.decode()
    header = {'User-Agent': 'Mozilla/5.0', 'content-type': 'application/json', 'OCS-APIRequest': 'true', 'Authorization': 'Basic ' + auth}
    data = json.dumps({'token': NEXTCLOUD_CHAT, 'message': message, 'silent': False})
    req = request.Request(url = url, data = data.encode('utf-8'), headers = header)
    res = request.urlopen(req)