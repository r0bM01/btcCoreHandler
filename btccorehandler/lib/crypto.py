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

import hmac, hashlib, secrets


class Network:
	def __init__(self, peerCert, handshakeCode):
		self.certificate = bytes.fromhex(peerCert)
		self.handshake_code = bytes.fromhex(handshakeCode)

		self.encryption_dict = False
		self.decryption_dict = False

	
	def make_handshake_code(self, entropy):
		if type(entropy) is not bytes:
			entropy = bytes.fromhex(entropy)
		return hashlib.blake2b(entropy, key = bytes.fromhex(certificate), digest_size = 16).hexdigest()

	def make_cryptography_dict(self):
		key = self.certificate
		psw = self.handshake_code
		enc = {} # thread safe encryption dict
		dec = {} # thread safe decryption dict
		for num in range(256):
			code = hex(num)[2:].zfill(2)
			value = hashlib.blake2b(code.encode('utf-8'), key = key, salt = psw, digest_size = 2).hexdigest()
			enc[code] = value
			dec[value] = code
		# can now add it to class property
		self.encryption_dict = enc
		self.decryption_dict = dec
			
	def encrypt(self, message):
		msg = message.encode('utf-8').hex()
		return "".join([ self.encryption_dict.get(msg[x:x+2]) for x in range(0, len(msg), 2) ])

	def decrypt(self, hex_message):
		msg = hex_message # message.encode('utf-8').hex()
		hex_decrypt = bytes.fromhex("".join([ self.decryption_dict.get(msg[x:x+4]) for x in range(0, len(msg), 4) ]))
		return hex_decrypt.decode('utf-8')


class Storage:
	def __init__(self, certificate):
		self.certificate = bytes.fromhex(certificate)
		self.encryption_dict = { hex(num)[2:].zfill(2) : self.hash_func(hex(num)[2:].zfill(2)) for num in range(256) }
		self.decryption_dict = { self.hash_func(hex(num)[2:].zfill(2)) : hex(num)[2:].zfill(2) for num in range(256) }

	def hash_func(self, code):
		return hashlib.blake2b(code.encode('utf-8'), key = self.certificate, digest_size = 2).hexdigest()

	def encrypt(self, data):
		if type(data) is str:
			msg = data.encode('utf-8').hex()
		elif type(data) is bytes:
			msg = data.hex()
		return "".join([ self.encryption_dict.get(msg[x:x+2]) for x in range(0, len(msg), 2) ])

	def decrypt(self, hex_data):
		msg = hex_data #data.encode('utf-8').hex()
		hex_decrypt = bytes.fromhex("".join([ self.decryption_dict.get(msg[x:x+4]) for x in range(0, len(msg), 4) ]))
		return hex_decrypt.decode('utf-8')


class Utils:
	@staticmethod
	def get_random_bytes(size):
		return secrets.token_bytes(int(size))
	
	@staticmethod
	def get_derived_certificate(cert_name, certificate, nonce):
		return hashlib.blake2b(cert_name, key = certificate, salt = nonce, digest_size = 64).hexdigest()

	@staticmethod
	def get_checksum(entropy, certificate):
		return hashlib.blake2b(entropy, key = certificate, digest_size = 16).hexdigest()
	
	@staticmethod
	def make_handshake_code(entropy, certificate, nonce):
		return hashlib.blake2b(entropy, key = certificate, salt = nonce, digest_size = 16).hexdigest()



