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

    remoteConn = Client()
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
            print("[1] - remote server info")
            print("[2] - bitcoin node status info")
            print("[3] - print all peers geolocation")
            print("[4] - print contries stats")
            print("[5] - send any call")
            print("[6] - send advanced call")
            print("[7] - test encryption messages")
            print("[0] - quit terminal")
            command = int(input(">> "))
            if not bool(command): command = 0
            if command == 0: break
            elif command == 1: print(remoteConn.systemInfo)
            elif command == 2: print(remoteConn.statusInfo)
            elif command == 3: [print(node) for node in remoteConn.peersGeolocation]
            elif command == 4: [print(f"{c[0]} : {c[1]}") for c in Counter([node[1] for node in remoteConn.peersGeolocation]).items()]
            elif command == 5: 
                command = input("\ninsert call: ")
                call = lib.shared.crypto.getHashedCommand(command, remoteConn.certificate, remoteConn.network.handshakeCode)
                print("requested call: ", call)
                eventThread.clear()
                if remoteConn.network.sender(call): reply = remoteConn.network.receiver()
                print(reply)
                eventThread.set()
            elif command == 6: 
                insertedCommand = input("\ninsert call: ")
                fullCommand = insertedCommand.lower().split(" ", 1)
                command = fullCommand[0]
                if command != "start" and command != "stop":
                    arg = fullCommand[1] if len(fullCommand) > 1 else False
                    eventThread.clear()
                    remoteReply = remoteConn.advancedCall(command, arg)
                    eventThread.set()
                    print(remoteReply)
                else:
                    print("control commands not allowed")
            elif command == 7:
                remoteConn.network.sender(remoteConn.calls['test'])
                reply = remoteConn.network.receiver()
                msg = lib.shared.crypto.getDecrypted(reply, "fefa", remoteConn.network.handshakeCode)
                print(msg)
            print("\n")
        remoteConn.closeConnection()

    except KeyboardInterrupt:
        remoteConn.closeConnection()
        print("closing")
