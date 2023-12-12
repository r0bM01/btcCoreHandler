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
import lib.server.data
import lib.server.machine

from lib.server.storage import Logger
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
        
        self.CONTROL = Control()
        self.BITCOIN_DATA = lib.server.data.Bitcoin()

        self.bitcoindRunning = lib.server.machine.MachineInterface.checkDaemon()
        

    def handle_request(self, remoteCall):
        if not self.CONTROL.check(remoteCall): return json.dumps({"error": "invalid command"})
        request = self.CONTROL.encodedCalls[remoteCall]
        if not self.bitcoindRunning and request != "start": return json.dumps({"error": "bitcoin daemon not running"})
        elif not self.bitcoindRunning and request == "start": self.startbitcoind()
        elif self.bitcoindRunning and request == "stop": self.stopbitcoind()

        if request == "keepalive": return json.dumps({"confirm": "alive"})
        elif request == "systeminfo": return json.dumps(Machine.dataInfo) 
        elif request == "statusinfo": return json.dumps(self.BITCOIN_DATA.getStatusInfo())
        elif request == "peerinfo": return json.dumps(self.BITCOIN_DATA.peersInfo)
        elif request == "geolocationinfo": return "GEOLOCATIONSERVICE"
        elif request == "advancedcall": return "ADVANCEDCALLSERVICE"
        elif request == "closeconn": return "CLOSECONNECTIONSERVICE"


    def startbitcoind(self):
        if not bool(self.bitcoindRunning):
            return lib.server.machine.MachineInterface.runBitcoindCall("start")
        else:
            return json.dumps({"error": "bitcoind already running"})
    
    def stopbitcoind(self):
        if bool(self.bitcoindRunning):
            return lib.server.machine.MachineInterface.runBitcoindCall("stop")
        else:
            return json.dumps({"error": "bitcoind already stopped"})

         
    def updateCacheData(self):
        uptime = lib.server.machine.MachineInterface.runBitcoindCall("uptime")
        self.BITCOIN_DATA.uptime = json.loads(uptime)

        blockchainInfo = lib.server.machine.MachineInterface.runBitcoindCall("getblockchaininfo")
        self.BITCOIN_DATA.blockchainInfo = json.loads(blockchainInfo)
        
        networkInfo = lib.server.machine.MachineInterface.runBitcoindCall("getnetworkinfo")
        self.BITCOIN_DATA.networkInfo = json.loads(networkInfo)

        nettotalsInfo = lib.server.machine.MachineInterface.runBitcoindCall("getnettotals")
        self.BITCOIN_DATA.nettotalsInfo = json.loads(nettotalsInfo)

        mempoolInfo = lib.server.machine.MachineInterface.runBitcoindCall("getmempoolinfo")
        self.BITCOIN_DATA.mempoolInfo = json.loads(mempoolInfo)
        
        miningInfo = lib.server.machine.MachineInterface.runBitcoindCall("getmininginfo")
        self.BITCOIN_DATA.miningInfo = json.loads(miningInfo)

        peersInfo = lib.server.machine.MachineInterface.runBitcoindCall("getpeerinfo")
        self.BITCOIN_DATA.peersInfo = json.loads(peersInfo)



