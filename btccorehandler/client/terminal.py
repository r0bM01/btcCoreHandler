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

import lib.crypto
import client.network
import client.storage
import json, threading, time, queue, sys
from collections import Counter
from client.client import Client


def terminal_exit():
    print("terminal stopping")
    sys.exit(0)

def main():
    # init storage
    storage = client.storage.Client()
    storage.init_certificate()
    storage.init_cryptography()
    # init network
    network = client.network.Client()

    # start terminal interface
    print("#### Bitcoin Core Handler terminal ####")
    server_addr = input("\ninsert server ip >> ")
    server_port = int(input("\ninsert server port >>"))

    print(f"connecting to {server_addr}")
    network.remoteHost = server_addr
    network.remotePort = server_port
    # connecting to server
    network.connectToServer()
    # handshake
    if network.isConnected:
        network.make_handshake(storage.certificate)
    else:
        print(f"couldn't connect to server {server_addr}")
        terminal_exit()
    
    if not network.handshake_done:
        print(f"handshake to server {server_addr} refused")
        terminal_exit()
    
    print(f"connection to {server_addr} established and handshake [{network.handshake_done}]")

    # init network crypto
    network.init_crypto()

    # open terminal calls interface
    print("Insert a call request or digit 'exit' to close the terminal")
    while network.isConnected:
        request = str(input("\n>> ")).lower()
        result = None
        if request == 'exit': terminal_exit()
        if network.write(request):
            result = network.read()
        if bool(result):
            result = json.loads(result)
            for key, value in result:
                print(f"{key}: {value}")




if __name__ == '__main__':
    main()


