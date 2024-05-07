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

import subprocess, json


class Node:
    def __init__(self):
        self.allowed_commands = []
    
    def get_local_IP(self):
        return str(subprocess.run(["hostname", "-I"], capture_output = True).stdout.decode().strip("\n"))
    
    def check_bitcoin_daemon(self):
        return bool(subprocess.run(["pidof", "bitcoind"], capture_output = True).stdout.decode())

    def run_command(self, command):
        if command not in self.allowed_commands: return {"error", "command not allowed"}

class BitcoinDaemon:
    def __init__(self):
        self.daemon = "bitcoind"
        self.client = "bitcoin-cli"

        self.is_running = bool(subprocess.run(["pidof", self.daemon], capture_output = True).stdout.decode())
    
    def start(self):
        subprocess.run([self.daemon])
        self.is_running = bool(subprocess.run(["pidof", self.daemon], capture_output = True).stdout.decode())
        return {"start": self.is_running}

    def stop(self):
        subprocess.run([self.client, "stop"])
        self.is_running = bool(subprocess.run(["pidof", self.daemon], capture_output = True).stdout.decode())
        return {"stop": self.is_running}

    def run_command(self, command, args_list):
        full_call = [self.client].extend(command)
        full_call = full.call.extend(args_list)
        result = subprocess.run(full_call, capture_output = True).stdout.decode()
        return result




class MachineInterface:
    
    @staticmethod
    def checkDaemon():
        PID = subprocess.run(["pidof", "bitcoind"], capture_output = True).stdout.decode()
        return bool(PID)

    @staticmethod
    def getLocalIP():
        IP = subprocess.run(["hostname", "-I"], capture_output = True).stdout.decode().strip(" \n")
        return str(IP)
    
    @staticmethod
    def runBitcoindCall(command, arg = False):
        if command == 'uptime':
            call = subprocess.run(["bitcoin-cli", command], capture_output = True).stdout.decode()
            call = json.dumps({"uptime": int(call)})
        elif command == 'stop':
            subprocess.run(["bitcoin-cli", "stop"])
            call = json.dumps({"stop": bool(self.checkDaemon())})
        elif command == 'start':
            subprocess.run(["bitcoind"])
            call = json.dumps({"start": bool(self.checkDaemon())})
        else:
            caller = ["bitcoin-cli", command] 
            if bool(arg): caller.extend(arg)
            call = subprocess.run(caller, capture_output = True).stdout.decode()
            if not bool(call): call = {command: "True"}
        return call
