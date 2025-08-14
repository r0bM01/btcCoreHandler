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

## new imports
from time import time
from lib.base_network import Server, SimplePeer
from lib.base_crypto import Utils


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

    def get_new_peer(self):
        peer = False
        peer_socket, peer_addr = self.accept_new_client()
        peer_hello = self.recv_data(peer_socket)
        if bool(peer_socket) and bool(peer_hello):
            peer = Peer(peer_socket, peer_addr)
            peer.hello_msg = peer_hello
        else:
            self.raw_closure(peer_socket)
        return peer


class Peer(SimplePeer):
    def __init__(self, peer_socket, peer_addr):
        self.peer_socket = peer_socket
        self.peer_addr = peer_addr
        self.encryption_key = None
        self.hello_msg = False
        self.is_connected = False

        self.first_seen = int(time())
        self.last_seen = self.first_seen

        self.data_exchanged = 0
    
    def init_handshake(self):
        random_bytes = Utils.get_random_bytes(16)
        if self.send_data(self.peer_socket, random_bytes):
            return self.recv_data(self.peer_socket)
        


## older imports
import socket, time
from lib.network import Proto
from lib.crypto import (Network, Utils)



###########################################################################################################
###########################################################################################################

class Handshake(Proto):
    #def __init__(self, certificates_list, remote_socket):
    #self._remoteSock = remote_socket
    #self.all_certificates = [bytes.fromhex(cert) for cert in certificate_list]

    entropy_code = False
    remote_certificate = False
    handshake_code = False
    handshake_done = False

    def exchange_entropy(self):
        serverRandom = Utils.get_random_bytes(16)
        clientRandom = self.dataRecv(16)
        if bool(clientRandom) and self.dataSend(serverRandom):
            self.entropy_code = clientRandom.hex() + serverRandom.hex()
    
    def choose_certificate(self, certificates_list):
        if bool(self.entropy_code):
            # creates a dict with cert-checksum : cert
            certs_checksums = { Utils.get_checksum(bytes.fromhex(self.entropy_code), bytes.fromhex(cert)) : cert for cert in certificates_list } 
            remote_checksum = self.dataRecv(16)
            self.remote_certificate = certs_checksums.get(remote_checksum.hex())
    
    def start_handshake(self):
        if bool(self.remote_certificate):
            # generates a nonce that must be hashed with entropy and correct certificate
            handshake_nonce = Utils.get_random_bytes(16) 
            # creates the handshake code hashing the entropy created with the selected certificate and the nonce generated
            handshake = Utils.make_handshake_code(bytes.fromhex(self.entropy_code), bytes.fromhex(self.remote_certificate), handshake_nonce)
            if self.dataSend(handshake_nonce) and self.dataRecv(16) == bytes.fromhex(handshake):
                self.handshake_code = handshake
    
    def confirm_handshake(self):
        if bool(self.handshake_code):
            confirmation = Utils.make_handshake_code(b'handshakeaccepted', bytes.fromhex(self.remote_certificate), bytes.fromhex(self.handshake_code))
            if self.dataSend( bytes.fromhex(confirmation) ):
                self.handshake_done = True
                     
    def make_handshake(self, certificates_list):
        ## step 1: exchange a 16 bytes entropy code
        self.exchange_entropy()
        ## step 2: hash all available certificates with the entropy and checks if remote certificate checksum is allowed 
        self.choose_certificate(certificates_list)
        ## step 3: random nonce will be sent to remote peer and the reply should be equal to entropy hashed with certificate and nonce
        self.start_handshake()
        ## step 4: when everything matches sends confirmation
        self.confirm_handshake()
        ## final: if peer received the confirmation, handshake is considered done


class OLD_Peer(Handshake):
    def __init__(self, conn_details):
        ## inherits handshake object
        if bool(conn_details):
            self._remoteSock = conn_details[0]
            self.address = conn_details[1]

        self.timeout = 120
        self.isConnected = False

        self.crypto = None #Peer(self.certificate, self.handshake_code)

        self.first_active = int(time.time())
        self.last_active = None
        self.session_calls = []
    
    def set_waiting_mode(self, wait_seconds = False):
        self._remoteSock.settimeout(wait_seconds or self.timeout)
    
    def init_crypto(self):
        self.crypto = Network(self.remote_certificate, self.handshake_code)
        self.crypto.make_cryptography_dict()

    def write(self, data):
        encrypted_data = self.crypto.encrypt(data)
        return self.sender(encrypted_data)
    
    def read(self, max_call_size = False):
        encrypted_data = self.receiver(max_call_size)
        if bool(encrypted_data): 
            data = self.crypto.decrypt(encrypted_data)
            self.last_active = int(time.time())
        else: data = False
        return data

###########################################################################################################

class ServerRPC(Proto):
    def __init__(self, port = 46001):
        self.host = "127.0.0.1"
        self.port = int(port)

    def openSocket(self):
        try:
            self.socket = socket.create_server((self.host, self.port), family = socket.AF_INET,
                                                backlog = 1, reuse_port = True)
            self.socket.settimeout(None) #base server socket has no timeout. It blocks until a client is connecting
        except OSError:
            self.socket = False

    def receiveClient(self):
        try:
            self._remoteSock, self.remoteAddr = self.socket.accept()
            self._remoteSock.settimeout(self._opTimeout)

        except OSError:
            self.sockClosure()


        
