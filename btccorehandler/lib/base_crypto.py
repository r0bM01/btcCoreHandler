# Copyright [2025-present] [R0BM01@pm.me]                                   #
#                                                                           #
# Distributed under the MIT software license, see the accompanying          #
# file COPYING or http://www.opensource.org/licenses/mit-license.php        #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#############################################################################


from hashlib import blake2b
from secrets import token_bytes
from random import randint
from base64 import b64encode, b64decode

class ScrumbledEggsProto:
    default_pad = bytes.fromhex("80") 
    block_size = 4 # bytes
    xor_rounds = 2 # encryption deepness
    

    def double_hash(self, bytes_data, key = b'', salt = b''):
        return blake2b(blake2b(bytes_data).digest(), key = key, salt = salt, digest_size = self.block_size).digest()
    
    def xor_operation(self, bytes_xor, bytes_block_data):
        xor_block = int(bytes_xor.hex(), 16) ^ int(bytes_block_data.hex(), 16)
        return bytes.fromhex(hex(xor_block)[2:].zfill(self.block_size*2))

    def generate_token(self, bytes_password = False):
        if not bytes_password:
            bytes_password = token_bytes(64)
        return self.double_hash(bytes_password)
    
    def prepare_data(self, bytes_data):
        bytes_data = b64encode(bytes_data)
        blocks_num = len(bytes_data) // self.block_size
        pad_size = self.block_size - (len(bytes_data) % self.block_size or self.block_size)
        pad_block = randint(0, blocks_num)
        pad_pos = self.block_size * pad_block
        return bytes_data[:pad_pos] + (self.default_pad * pad_size) + bytes_data[pad_pos:]
    
    def normalize_data(self, bytes_data):
        for size in reversed(range(self.block_size)):
            pad = self.default_pad * size
            if pad in bytes_data:
                pos = bytes_data.find(self.default_pad)
                bytes_data = bytes_data[:pos] + bytes_data[pos+size:]
                break
        bytes_data = b64decode(bytes_data)
        return bytes_data
    
    def generate_data_blocks(self, bytes_data):
        return [bytes_data[x:x+self.block_size] for x in range(0, len(bytes_data), self.block_size)]
    
    def generate_xor_blocks(self, bytes_password, data_blocks):
        key_rounds = len(data_blocks)
        xor_blocks = [] 
        for round in range(self.xor_rounds):
            salt = str(round).encode('utf-8')
            xor_blocks.append([self.double_hash(bytes_password, str(x).encode('utf-8'), salt)  for x in range(key_rounds)])
        return xor_blocks
    
    def blocks_cryptography(self, data_blocks, xor_blocks):
        for round in range(self.xor_rounds):
            data_blocks = [self.xor_operation(xor_blocks[round][i], data_blocks[i]) for i in range(len(data_blocks))]
        return b"".join(data_blocks)
        
    def encrypt_bytes(self, bytes_data, bytes_password):
        data_blocks = self.generate_data_blocks(self.prepare_data(bytes_data))
        xor_blocks = self.generate_xor_blocks(bytes_password, data_blocks)
        encrypted_data = self.blocks_cryptography(data_blocks, xor_blocks)
        return encrypted_data

    def decrypt_bytes(self, bytes_data, bytes_password):
        data_blocks = self.generate_data_blocks(bytes_data)
        xor_blocks = self.generate_xor_blocks(bytes_password, data_blocks)
        xor_blocks.reverse()
        decrypted_data = self.blocks_cryptography(data_blocks, xor_blocks)
        return self.normalize_data(decrypted_data)
    

class Messages(ScrumbledEggsProto):
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