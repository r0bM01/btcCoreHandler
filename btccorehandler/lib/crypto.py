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

import lib.base_crypto
from hashlib import blake2b
from secrets import token_bytes

class Messages(lib.base_crypto.ScrumbledEggsProto):
	def __init__(self):
		self.xor_rounds = 4

	def encrypt_message(self, message, password):
		bytes_data = self.data_to_bytes(message)
		bytes_passw = self.data_to_bytes(password)
		return self.encrypt_bytes(bytes_data, bytes_pasw)
	
	def decrypt_message(self, encrypted_data, password):
		bytes_data = self.data_to_bytes(encrypted_data)
		bytes_passw = self.data_to_bytes(password)
		return self.decrypt_bytes(bytes_data, bytes_passw)

	def data_to_bytes(self, data):
		match data:
			case int():
				result = str(data).encode('utf-8')
			case str():
				result = data.encode('utf-8')
			case bytes():
				result = data
		return result


class Utils:
	@staticmethod
	def get_random_bytes(size):
		return token_bytes(int(size))
	
	@staticmethod
	def get_derived_bytes(bytes_data, rounds):
		for r in range(int(rounds)):
			bytes_data = blake2b(bytes_data, key = str(r).encode('utf-8')).digest()
		return bytes_data

	@staticmethod
	def get_checksum(entropy, certificate):
		return hashlib.blake2b(entropy, key = certificate, digest_size = 16).hexdigest()
	
	@staticmethod
	def make_handshake_code(entropy, certificate, nonce):
		return hashlib.blake2b(entropy, key = certificate, salt = nonce, digest_size = 16).hexdigest()



