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
