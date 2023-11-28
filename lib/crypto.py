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

def getHashedCommand(command, key, salt):
		return hashlib.blake2b(command.encode(), digest_size = 8, key = bytes.fromhex(key), salt = bytes.fromhex(salt)).hexdigest()







