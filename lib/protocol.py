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



import subprocess, json, time, threading
import lib.crypto
import lib.data
from lib.storage import Logger
from lib.network import Utils

class Control:
    def __init__(self):
        
        self.calls = {'uptime', 'start', 'stop', 'closeconn', 'keepalive',
                      'getstatusinfo', 'getblockchaininfo', 'getnetworkinfo', 
                      'getmempoolinfo', 'getmininginfo', 'getpeerinfo', 'getnettotals',
                      'advancedcall', 'systeminfo', 'getgeolocation'}
        
        self.encodedCalls = False

        # self.LEVELS = {"blocked": 0, "user": 1, "admin": 2} not implemented yet
     

    def encodeCalls(self, hexCertificate, handshakeCode):
        self.encodedCalls = {lib.crypto.getHashedCommand(call, hexCertificate, handshakeCode) : call for call in self.calls}

    def check(self, call):
        return call in self.calls
                  
        
class RequestHandler:
    def __init__(self):
        #must be inherited by server class
        #do not instantiate directly
        self.OPERATOR = MachineInterface()
        self.CONTROL = Control()
        self.BITCOIN_DATA = lib.data.Bitcoin()

        self.bitcoindRunning = self.OPERATOR.checkDaemon()
        

    def handle_request(self, remoteCall):
        if not self.CONTROL.check(remoteCall): return json.dumps({"error": "invalid command"})
        request = self.CONTROL.encodedCalls[remoteCall]
        if not self.bitcoindRunning and request != "start": return json.dumps({"error": "bitcoin daemon not running"})
        elif not self.bitcoindRunning and request == "start": self.startbitcoind()
        elif self.bitcoindRunning and request == "stop": self.stopbitcoind()

        if request == "keepalive": self.keepalive()
        elif request == "systeminfo": self.getsysteminfo()
        elif request == "statusinfo": self.getstatusinfo()
        elif request == "peerinfo": self.getpeerinfo()
        elif request == "geolocationinfo": self.getgeolocationinfo()
        elif request == "advancedcall": self.getadvancedcall()


    def startbitcoind(self):
        if not bool(self.OPERATOR.checkDaemon()):
            return self.OPERATOR.runCall("start")
        else:
            return json.dumps({"error": "bitcoind already running"})
    
    def stopbitcoind(self):
        if bool(self.OPERATOR.checkDaemon()):
            return self.OPERATOR.runCall("stop")
        else:
            return json.dumps({"error": "bitcoind already stopped"})

    def keepalive(self):
        return json.dumps({"confirm": "alive"})

    def getsysteminfo(self):
        return json.dumps(Machine.dataInfo) 
    
    def getstatusinfo(self):
        return json.dumps(self.BITCOIN_DATA.getStatusInfo())

    def getpeerinfo(self):
        return json.dumps(self.BITCOIN_DATA.peersInfo)
    
    def getgeolocationinfo(self):
        return "GEOLOCATIONSERVICE"
    
    def getadvancedcall(self):
        return "ADVANCEDCALLSERVICE"
         
    def updateCacheData(self):
        uptime = self.OPERATOR.runCall("uptime")
        self.BITCOIN_DATA.uptime = json.loads(uptime)

        blockchainInfo = self.OPERATOR.runCall("getblockchaininfo")
        self.BITCOIN_DATA.blockchainInfo = json.loads(blockchainInfo)
        
        networkInfo = self.OPERATOR.runCall("getnetworkinfo")
        self.BITCOIN_DATA.networkInfo = json.loads(networkInfo)

        nettotalsInfo = self.OPERATOR.runCall("getnettotals")
        self.BITCOIN_DATA.nettotalsInfo = json.loads(nettotalsInfo)

        mempoolInfo = self.OPERATOR.runCall("getmempoolinfo")
        self.BITCOIN_DATA.mempoolInfo = json.loads(mempoolInfo)
        
        miningInfo = self.OPERATOR.runCall("getmininginfo")
        self.BITCOIN_DATA.miningInfo = json.loads(miningInfo)

        peersInfo = self.OPERATOR.runCall("getpeerinfo")
        self.BITCOIN_DATA.peersInfo = json.loads(peersInfo)

              

class MachineInterface:
    def __init__(self):
        self.base = "bitcoin-cli"
    
    def checkDaemon(self):
        PID = subprocess.run(["pidof", "bitcoind"], capture_output = True).stdout.decode()
        return bool(PID)

    def getLocalIP(self):
        IP = subprocess.run(["hostname", "-I"], capture_output = True).stdout.decode().strip(" \n")
        return str(IP)
    
    def runCall(self, command, arg = False):
        if command == 'uptime':
            call = subprocess.run([self.base, command], capture_output = True).stdout.decode()
            call = json.dumps({"uptime": int(call)})
        elif command == 'stop':
            subprocess.run([self.base, "stop"])
            call = json.dumps({"stop": bool(self.checkDaemon())})
        elif command == 'start':
            subprocess.run(["bitcoind"])
            call = json.dumps({"start": bool(self.checkDaemon())})
        else:
            caller = [self.base, command, arg] if arg else [self.base, command]
            call = subprocess.run(caller, capture_output = True).stdout.decode()
        return call

    

