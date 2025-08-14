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



import socket


class SocketOperations:
    """Do not instantiate directly!
       This class is extended by Server and Client classes""" 


    _buffer = 4096 # bytes size
    _header = 2 # bytes size
    _timeout = 2 # seconds

    def raw_send(self, connected_socket, bytes_msg):
        try:
            msg_sent = connected_socket.send(bytes_msg, socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            msg_sent = 0
        return msg_sent
    
    def raw_recv(self, connected_socket, bytes_size):
        try:
            msg_recv = connected_socket.recv(int(bytes_size), socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            msg_recv = b""
        return msg_recv

    def raw_closure(self, connected_socket):
        try: 
            connected_socket.shutdown(socket.SHUT_RDWR)
            connected_socket.close()
        except (OSError, AttributeError):
            pass
        connected_socket = None
    
    def send_proto(self, connected_socket, bytes_msg): 
        # pre-sending ops
        connected_socket.settimeout(self._timeout) #reset operation timeout to low value
        header_msg = bytes.fromhex(hex(len(bytes_msg))[2:].zfill(self._header * 2))
        # data sending ops
        header_sent = self.raw_send(connected_socket, header_msg)
        msg_sent = self.raw_send(connected_socket, bytes_msg)
        # sending verification
        result = True if msg_sent == len(bytes_msg) else False
        return result

    def recv_proto(self, connected_socket): 
        # pre-receiving ops
        connected_socket.settimeout(self._timeout) #reset operation timeout to low value
        # receiving header message
        header_recv = self.raw_recv(connected_socket, self._header)
        header_msg = int(header_recv.hex(), 16)
        # receving data 
        msg_recv = []
        bytes_left = header_msg
        while b"" not in msg_recv and bool(bytes_left):
            msg_recv.append(self.raw_recv(connected_socket, min(bytes_left, self._buffer)))
            bytes_left -= len(msg_recv[-1])
        # joins bytes vector into a single bytes message
        bytes_msg = b"".join(msg_recv)
        # receiving verification
        result = bytes_msg if header_msg == len(bytes_msg) else False
        return result


class Server(SocketOperations):
    """Do not instantiate directly. 
       This class has to be extented with a custom Server Class"""

    # server default values
    server_addr = 'localhost'
    server_port = 45000
    server_backlog = 5
    server_socket = None
    default_server_timeout = 5
    default_remote_timeout = 5
    default_hello_msg = b"\xadR1\xa8\x8c)9\xc2\x11\xb1=\xcb\xc6\x14\xe0\xb8" # 16 bytes
        
    def create_server(self):
        try:
            self.server_socket = socket.create_server((self.server_addr, self.server_port), family = socket.AF_INET, backlog = self.server_backlog, reuse_port = True)
            self.server_socket.settimeout(self.default_server_timeout)
        except OSError:
            self.server_socket = None
    
    def close_server(self):
        self.raw_closure(self.server_socket)

    def accept_new_client(self):
        try:
            remote_socket, remote_addr = self.server_socket.accept()
            remote_socket.settimeout(self.default_remote_timeout)
            hello_msg = self.raw_recv(remote_socket, len(self.default_hello_msg))
        except OSError:
            remote_socket = None
            remote_addr = None
        if not hello_msg == self.default_hello_msg:
            self.disconnect_remote_client(remote_socket)
            remote_socket = None
            remote_addr = None
        return remote_socket, remote_addr

    def disconnect_remote_client(self, remote_socket):
        self.raw_closure(remote_socket)
    
    def is_ready(self):
        return bool(self.server_socket)
    
    def recv_data(self, remote_socket):
        saved_timeout = remote_socket.gettimeout()
        remote_data = self.recv_proto(remote_socket)
        remote_socket.settimeout(saved_timeout)
        return remote_data

    def send_data(self, remote_socket, data):
        saved_timeout = remote_socket.gettimeout()
        data_sent = self.send_proto(remote_socket, data)
        remote_socket.settimeout(saved_timeout)
        return data_sent


class SimplePeer(SocketOperations):

    def recv_data(self):
        saved_timeout = self.client_socket.gettimeout()
        remote_data = self.recv_proto(self.client_socket)
        self.client_socket.settimeout(saved_timeout)
        return remote_data

    def send_data(self, data):
        saved_timeout = self.client_socket.gettimeout()
        data_sent = self.send_proto(self.client_socket, data)
        self.client_socket.settimeout(saved_timeout)
        return data_sent

class Client(SocketOperations):
    """Client class can be directly instantiated"""

    def __init__(self, remote_addr, remote_port):
        # client default values
        self.remote_addr = remote_addr
        self.remote_port = remote_port
        self.client_socket = None
        self.default_client_timeout = 5

    def connect_to_remote(self):
        try:
            self.client_socket = socket.create_connection((self.remote_addr, self.remote_port), timeout = self.default_client_timeout)
        except OSError:
            self.client_socket = None
    
    def disconnect_from_remote(self):
        self.raw_closure(self.client_socket)

    def is_connected(self):
        return bool(self.client_socket)

    def recv_data(self):
        saved_timeout = self.client_socket.gettimeout()
        remote_data = self.recv_proto(self.client_socket)
        self.client_socket.settimeout(saved_timeout)
        return remote_data

    def send_data(self, data):
        saved_timeout = self.client_socket.gettimeout()
        data_sent = self.send_proto(self.client_socket, data)
        self.client_socket.settimeout(saved_timeout)
        return data_sent



    

    
    

