

import hmac, hashlib, secrets


def getRandomBytes(size):
		return secrets.token_bytes(int(size))

def getHash(data):
		return hashlib.blake2b(data.encode()).hexdigest()

def getHashedCommand(command, key, salt):
		return hashlib.blake2b(command.encode(), digest_size = 8, key = bytes.fromhex(key), salt = bytes.fromhex(salt)).hexdigest()







