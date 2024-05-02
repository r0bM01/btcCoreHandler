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


class Peer:
	def __init__(self, peerCert, handshakeCode):
		self.certificate = bytes.fromhex(peerCert)
		self.handshake_code = bytes.fromhex(handshakeCode)

		self.encryption_dict = False
		self.decryption_dict = False

		self.get_entropy = Utils.getRandomBytes
	
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
		key = self.certificate
		psw = self.handshake_code
		msg = message.encode('utf-8').hex()
		return "".join([ self.encryption_dict.get(msg[x:x+2]) for x in range(0, len(msg), 2) ])

	def decrypt(self, message):
		key = self.certificate
		psw = self.handshake_code
		msg = message.encode('utf-8').hex()
		hex_decrypt = bytes.fromhex("".join([ self.decryption_dict.get(msg[x:x+l]) for x in range(0, len(msg), 4) ]))
		return hex_decrypt.decode('utf-8')



class Utils:
	@staticmethod
	def getRandomBytes(size):
		return secrets.token_bytes(int(size))
	
	@staticmethod
	def getHashedCommand(command, certificate, handshakeCode):
		return hashlib.blake2b(command.encode(), key = bytes.fromhex(certificate), salt = bytes.fromhex(handshakeCode), digest_size = 8).hexdigest()

	@staticmethod
	def getHandshakeCertificate(entropy, certificate):
		return hashlib.blake2b(entropy, key = certificate, digest_size = 16).hexdigest()
	
	@staticmethod
	def getHandshakeCode(entropy, certificate, nonce):
		return hashlib.blake2b(entropy, key = certificate, salt = nonce, digest_size = 16).hexdigest()

def getHash(data):
	return hashlib.blake2b(data.encode()).hexdigest()

def getMiniHash(data):
	return hashlib.blake2b(data.encode(), digest_size = 2).hexdigest()

def getHashedCommand(command, certificate, handshakeCode):
	return hashlib.blake2b(command.encode(), digest_size = 8, key = bytes.fromhex(certificate), salt = bytes.fromhex(handshakeCode)).hexdigest()

def getHandshakeCode(entropy, certificate):
	return hashlib.blake2b(entropy, key = bytes.fromhex(certificate), digest_size = 16).hexdigest()

def getKey(data, certificate): # accept bytes directly
    return hashlib.blake2b(data, digest_size = 8, key = certificate).digest()

def getEncryptionAlpha(certificate):
	return {chr(n): hashlib.blake2b(chr(n).encode(), digest_size = 2, key = certificate).hexdigest() for n in range(32, 127)}

def getDecryptionAlpha(certificate):
	return {hashlib.blake2b(chr(n).encode(), digest_size = 2, key = certificate).hexdigest() : chr(n) for n in range(32, 127)}

def getEncrypted(data, key, salt = ""):
	alpha = [chr(n) for n in range(32, 127)]
	crypt = {l : hashlib.blake2b((l).encode(), digest_size = e_size, key = bytes.fromhex(key), salt = bytes.fromhex(salt)).hexdigest() for l in alpha}

	encryptedMsg = [crypt[l] for l in data]
	return "".join(encryptedMsg)

def getDecrypted(msg, key, salt = ""):
	alpha = [chr(n) for n in range(32, 127)]
	crypt = {hashlib.blake2b((l).encode(), digest_size = e_size, key = bytes.fromhex(key), salt = bytes.fromhex(salt)).hexdigest() : l for l in alpha}

	chunks = [msg[c:c+4] for c in range(0, len(msg), 4)]
	data = [crypt[l] for l in chunks]
	return "".join(data)
