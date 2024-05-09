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

import socket, time
from lib.network import Proto
from lib.crypto import (Network, Utils)


###########################################################################################################
###########################################################################################################

class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else "" # if not provided binds it to all interfaces # socket.gethostbyname(socket.gethostname()) 
        self.port = int(port) if port else 46800

        self.socketTimeout = 5
        self.remoteSockTimeout = 120
        self.backlog = 5
        self.maxSockets = 1


class Server(Proto):
    def __init__(self, settings):
        self.settings = settings
        self.socket = False
        self.remoteAddr = None
        
    def openSocket(self):
        try:
            self.socket = socket.create_server((self.settings.host, self.settings.port), family = socket.AF_INET,
                                               backlog = self.settings.backlog, reuse_port = True)
            self.socket.settimeout(self.settings.socketTimeout)
        except OSError:
            self.socket = False

    def closeSocket(self):
        try: 
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except (OSError, AttributeError):
            pass
        self.socket = False

    def receiveClient(self):
        try:
            self._remoteSock, self.remoteAddr = self.socket.accept()
            self._remoteSock.settimeout(self._opTimeout) 
            return (self._remoteSock, self.remoteAddr)
        except OSError:
            self.sockClosure()
            return False

      
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
        serverRandom = Utils.getRandomBytes(16)
        clientRandom = self.dataRecv(16)
        if bool(clientRandom) and self.dataSend(serverRandom):
            self.entropy_code = clientRandom + serverRandom
    
    def choose_certificate(self, certificates_list):
        if bool(self.entropy_code):
            certs_checksums = {bytes.fromhex(Utils.getHandshakeCertificate(self.entropy_code, bytes.fromhex(cert))) : cert for cert in certificates_list} # returns 16 bytes codes
            remote_checksum = self.dataRecv(16)
            self.remote_certificate = certs_checksums.get(remote_certificate)
    
    def start_handshake(self):
        if bool(self.remote_certificate):
            handshake_nonce = Utils.getRandomBytes(16) # generates a nonce that must be hashed with entropy and correct certificate
            handshake = bytes.fromhex(Utils.getHandshakeCode(self.entropy_code, self.remote_certificate, handshake_nonce))
            if self.dataSend(handshake_nonce):
                self.handshake_code = handshake if self.dataRecv(16) == handshake else False
    
    def confirm_handshake(self):
        if bool(self.handshake_code):
            confirmation = bytes.fromhex(Utils.getHandshakeCode(b'handshakeaccepted', self.remote_certificate, self.handshake_code))
            if self.dataSend(confirmation):
                self._remoteSock.settimeout(120) ## with correct handshake, server can wait a request up to 120 seconds for this peer
                self.handshake_done = True
                self.remote_certificate = self.remote_certificate.hex()
                self.handshake_code = self.handshake_code.hex()
                     
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


class Peer(Handshake):
    def __init__(self, new_peer_tuple):
        ## inherits handshake object
        if bool(new_peer_tuple):
            self._remoteSock = new_peer_tuple[0]
            self.address = new_peer_tuple[1]

        self.crypto = None #Peer(self.certificate, self.handshake_code)

        self.first_active = int(time.time())
        self.last_active = None
        self.session_calls = []
    
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


        
