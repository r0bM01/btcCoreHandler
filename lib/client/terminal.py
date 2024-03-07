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


import lib.shared.network
import lib.shared.crypto
import lib.shared.storage
import json, threading, time, queue
from collections import Counter
from lib.client.client import Client




def clientTerminal():
    def keepConnAlive():
        while remoteConn.network.isConnected:
            eventThread.wait()
            remoteConn.keepAlive()
            time.sleep(10)
        print("\nconnection terminated")


    storage = lib.shared.storage.Client()

    certificate = storage.init_certificate()

    print(bool(certificate))

    remoteConn = Client(certificate)
    eventThread = threading.Event()
    keepAliveThread = threading.Thread(target = keepConnAlive, daemon = True)

    print("Bitcoin Core Handler terminal")
    ipAddr = input("insert server ip: \n>> ")
    input("\nPress enter to connect\n")
    remoteConn.initConnection(ipAddr)
    
    print(f"Handshake code: {remoteConn.network.handshakeCode} \n")
    print("receiving info from server...")
    time.sleep(0.5)
    print(f"connected to server: {remoteConn.network.isConnected}\n")

    if remoteConn.network.isConnected:
        eventThread.set()
        keepAliveThread.start()
        print("keep alive thread started")
        
    try:

        while True and remoteConn.network.isConnected:
            print("\nInsert a call or 'quit' to close the terminal; ")
            c = str(input("\n>> ")).lower()
            if c == 'quit': break
            encodedCall = lib.shared.crypto.getHashedCommand(c, remoteConn.certificate, remoteConn.network.handshakeCode)
            message = str(remoteConn.calls['advancedcall']) + str(encodedCall)
            eventThread.clear()
            if remoteConn.network.sender(message): reply = remoteConn.network.receiver()
            eventThread.set()

            print(f"\nCall sent: {c}: {encodedCall}")
            print(f"reply: \n{reply}")
        remoteConn.closeConnection()

    except KeyboardInterrupt:
        remoteConn.closeConnection()
        print("closing")


