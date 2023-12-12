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
            caller = ["bitcoin-cli", command, arg] if arg else ["bitcoin-cli", command]
            call = subprocess.run(caller, capture_output = True).stdout.decode()
        return call
