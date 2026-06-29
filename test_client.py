
import threading, tomllib, json

from lib.base_network import Client
from lib.base_crypto import ScrumbledEggsProto, Utils
# CLIENT TEST


class Test(Client):
    def __init__(self, remote_addr, remote_port):
        super().__init__(remote_addr, remote_port)

        self.crypto = ScrumbledEggsProto()
        self.id = bytes.fromhex("42726ffff8517a4f306df3307aad46ad")
        self.encryption_key = None
        self.is_connected = False
        self.is_local_cli = False
        self.waiting_mode = 120

        self.data_exchanged = 0


    def set_waiting_mode(self, wait_seconds = False):
        self.client_socket.settimeout(30)

    def handshake(self, certificate):
        certificate = bytes.fromhex(certificate)
        if self.send_data(self.id):
            random_bytes = self.recv_data()
        print("random bytes received ", random_bytes.hex())
        solution_bytes = Utils.get_hash(certificate, random_bytes)
    
        if self.send_data(solution_bytes):
            self.encryption_key = Utils.get_hash(certificate, solution_bytes)
            print("encryption key ", self.encryption_key.hex())
            self.is_connected = True

    def is_alive(self):
        return (int(time()) - self.last_seen) < 120

    def send_msg(self, msg) -> bool:
        if type(msg) is str:
            msg = msg.encode('utf-8')
        encrypted_msg = self.crypto.encrypt_bytes(msg, self.encryption_key)
        self.data_exchanged += len(encrypted_msg)
        return self.send_data(encrypted_msg)

    def recv_msg(self) -> str:
        msg = str()
        encrypted_bytes = self.recv_data()
        if bool(encrypted_bytes):
            decrypted_msg = self.crypto.decrypt_bytes(encrypted_bytes, self.encryption_key)
            msg = decrypted_msg.decode('utf-8')
            self.data_exchanged += len(encrypted_bytes)
            #self.last_seen = int(time())
        return msg

    def disconnect(self):
        self.is_connected = False
        self.close_socket()


KEEPALIVE = {'method': 'keepalive', 'args': []}


with open("config.toml", "rb") as f:
        config = tomllib.load(f)



client = Test("192.168.1.225", 46850)

print("connecting...")
client.connect_to_remote()

print("socket: ", bool(client.client_socket))

client.handshake(config['network']['certificate'])

print("Connected to server: ", client.is_connected)
if client.is_connected:
    client.set_waiting_mode()
while True:
    cmd = input("send a command: ")
    if cmd == "quit":
        break
    request = json.dumps({'method': cmd, 'args': []})

    client.send_msg(request)
    result = client.recv_msg()
    print("RESULT:\n", result)

client.disconnect_from_remote()