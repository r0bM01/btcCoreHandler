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
from lib.network import Proto
from lib.crypto import Utils
from lib.crypto import Network


class Handshake(Proto):
    entropy_code = False
    local_certificate = False
    handshake_code = False
    handshake_done = False
    
    def exchange_entropy(self):
        clientRandom = Utils.get_random_bytes(16)
        serverRandom = self.dataRecv(16) if self.dataSend(clientRandom) else False
        if bool(serverRandom):
            self.entropy_code = clientRandom.hex() + serverRandom.hex()

    def choose_certificate(self, loaded_certificate):
        if bool(self.entropy_code):
            cert_checksum = Utils.get_checksum(bytes.fromhex(self.entropy_code), bytes.fromhex(loaded_certificate))
            if self.dataSend(bytes.fromhex(cert_checksum)):
                self.local_certificate = loaded_certificate
    
    def do_handshake(self):
        if bool(self.local_certificate):
            handshake_nonce = self.dataRecv(16) # gets new handshake nonce from server
            if bool(handshake_nonce):
                # creates the actual handshake 
                self.handshake_code =  Utils.make_handshake_code(bytes.fromhex(self.entropy_code), bytes.fromhex(self.local_certificate), handshake_nonce)
                
    def confirm_handshake(self):
        # sends the handshake created and waits for confirmation
        if self.dataSend( bytes.fromhex(self.handshake_code) ):
            confirmation = Utils.make_handshake_code(b'handshakeaccepted', bytes.fromhex(self.local_certificate), bytes.fromhex(self.handshake_code))
            # when confirmation matches, handshake is done
            if self.dataRecv(16) == bytes.fromhex(confirmation):
                self.handshake_done = True
                     
    def make_handshake(self, loaded_certificate):
        ## step 1: exchange a 16 bytes entropy code
        self.exchange_entropy()
        ## step 2: hash all available certificates with the entropy and checks if remote certificate checksum is allowed 
        self.choose_certificate(loaded_certificate)
        ## step 3: random nonce will be sent to remote peer and the reply should be equal to entropy hashed with certificate and nonce
        self.do_handshake()
        ## step 4: when everything matches sends confirmation
        self.confirm_handshake()
        ## final: if peer received the confirmation, handshake is considered done



class Client(Handshake):
    def __init__(self):
        self.remoteHost = None # has to be given by UI  
        self.remotePort = 46800 # default port
        self.timeout = 120
        self.isConnected = False
        self.crypto = None
                
    def connectToServer(self):
        try:
            self._remoteSock = socket.create_connection((self.remoteHost, self.remotePort), timeout = self._opTimeout)
            self.isConnected = True
        except (OSError, TimeoutError):
            self.isConnected = False
            self._remoteSock = False

    def disconnectServer(self):
        #self._remoteSock.close()
        #self._remoteSock = False
        self.sockClosure()
        self.isConnected = False
    
    def init_crypto(self):
        self.crypto = Network(self.local_certificate, self.handshake_code)
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

