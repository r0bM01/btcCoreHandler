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

import socket
from lib.shared.network import Proto
from lib.shared.crypto import Peer
from lib.shared.crypto import Utils

###########################################################################################################
###########################################################################################################

class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else "" # if not provided binds it to all interfaces # socket.gethostbyname(socket.gethostname()) 
        self.port = int(port) if port else 4600

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
            return self._remoteSock
        except OSError:
            self.sockClosure()
            return False

      
###########################################################################################################
###########################################################################################################

class Peer(Proto):
    def __init__(self, peerSocket, peerCert, handshakeCode):
        self._remoteSock = peerSocket
        self.certificate = bytes.fromhex(peerCert)
        self.handshake_code = bytes.fromhex(handshakeCode)
        self.crypto = Peer(self.certificate, self.handshake_code)

        self.first_active = int(time.time())
        self.last_active = None
        self.session_calls = None

        self.crypto.make_cryptography_dict() # creates crypto dict as soon as peer is initialized

    def write(self, data):
        encrypted_data = self.crypto.encrypt(data)
        return self.sender(encrypted_data)
    
    def read(self, max_call_size = False):
        encrypted_data = self.receiver(max_call_size)
        if bool(encrypted_data): data = self.crypto.decrypt(encrypted_data)
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

class Handshake(Proto):
    def __init__(self, certificate_list, remote_socket):
        self._remoteSock = remote_socket
        self.all_certificates = [bytes.fromhex(cert) for cert in certificate_list]

        self.entropy_code = False
        self.remote_certificate = False
        self.handshake_code = False

        self.handshake_done = False

    def exchange_entropy(self):
        serverRandom = Utils.getRandomBytes(16)
        clientRandom = self.dataRecv(16)
        if bool(clientRandom) and self.dataSend(serverRandom):
            self.entropy_code = clientRandom + serverRandom
    
    def chose_certificate(self):
        if bool(self.entropy_code):
            allowed_certificates = {bytes.fromhex(Utils.getHandshakeCertificate(self.entropy_code, cert)) : cert for cert in self.all_certificates} # returns 16 bytes codes
            remote_certificate = self.dataRecv(16)
            if remote_certificate in allowed_certificates:
                self.remote_certificate = allowed_certificates[remote_certificate]
    
    def make_handshake(self):
        if bool(self.remote_certificate):
            handshake_nonce = Utils.getRandomBytes(16) # generates a nonce that must be hashed with entropy and correct certificate
            handshake = bytes.fromhex(Utils.getHandshakeCode(self.entropy_code, self.remote_certificate, handshake_nonce))
            if self.dataSend(handshake_nonce):
                self.handshake_code = handshake if self.dataRecv(16) == handshake else False
    
    def confirm_handshake(self):
        if bool(self.handshake_code):
            confirmation = bytes.fromhex(Utils.getHandshakeCode(b'handshakeaccepted', self.remote_certificate, self.handshake_code))
            if self.dataSend(confirmation):
                self.handshake_done = True
                self.remote_certificate = self.remote_certificate.hex()
                self.handshake_code = self.handshake_code.hex()
                     
    def start_process(self):
        ## step 1: exchange an entropy code
        self.exchange_entropy()
        ## step 2: hash all available certificates with the entropy and checks if remote certificate hash is in allowed certificates
        self.chose_certificate()
        ## step 3: random nonce will be sent to remote peer and the reply should be equal to entropy hashed with certificate and nonce
        self.make_handshake()
        ## step 4: when everything matches sends confirmation
        self.confirm_handshake()
        ## final: if peer received the confirmation, handshake is considered done
        
