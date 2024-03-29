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


def getRandomBytes(size):
	return secrets.token_bytes(int(size))

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
