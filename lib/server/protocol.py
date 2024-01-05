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
import lib.shared.crypto
import lib.shared.commands
import lib.server.data
import lib.server.machine

from lib.shared.network import Utils

class BaseRequest:
    _maxLenght = 256

    def deserialize(self, fullRequest):
        self.baseCall = fullRequest[:16]
        self.params = fullRequest[16:].split(":")
        
class RequestHandler:
    def __init__(self):
        #must be inherited by server class
        #do not instantiate directly
        
        self.CONTROL = lib.shared.commands.Control()
        self.BITCOIN_DATA = lib.server.data.Bitcoin()
        self.GEO_DATA = lib.server.data.IPGeolocation()

        self.bitcoindRunning = lib.server.machine.MachineInterface.checkDaemon()
        
    def handle_request(self, remoteCall, LOGGER):
        call = remoteCall[:16]
        args = remoteCall[16:]
        if not self.CONTROL.check(call): return json.dumps({"error": "invalid command"})
        request = self.CONTROL.encodedCalls[call]
        # LOGGER.add("call", request)
        if not self.bitcoindRunning and request != "start": return json.dumps({"error": "bitcoin daemon not running"})
        elif not self.bitcoindRunning and request == "start": self.startbitcoind()
        elif self.bitcoindRunning and request == "stop": self.stopbitcoind()

        if request == "keepalive": return json.dumps({"confirm": "alive"})
        elif request == "getsysteminfo": return json.dumps(lib.server.data.Machine.dataInfo) 
        elif request == "getstatusinfo": return json.dumps(self.BITCOIN_DATA.getStatusInfo())
        elif request == "getpeerinfo": return json.dumps(self.BITCOIN_DATA.peersInfo)
        elif request == "getgeolocationinfo": return json.dumps(self.GEO_DATA.getCountryList(self.BITCOIN_DATA.peersInfo))
        elif request == "getserverlogs": return json.dumps(LOGGER.SESSION)
        elif request == "test": return "TESTENCRYPTSERVICE"
        elif request == "advancedcall": return self.directCall(args)
        elif request in self.CONTROL.bitcoinCalls: return lib.server.machine.MachineInterface.runBitcoindCall(request)

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
    
    def directCall(self, remoteArgs):
        call = remoteArgs[:16]
        args = remoteArgs[16:].split(" ") if bool(remoteArgs[16:]) else False
        jsonCall = {}
        jsonCall['call'] = self.CONTROL.encodedCalls.get(call)
        if jsonCall['call'] in self.CONTROL.bitcoinCalls:
            if jsonCall['call'] != "start" and jsonCall['call'] != "stop":
                result = lib.server.machine.MachineInterface.runBitcoindCall(jsonCall['call'], args)
                return json.dumps(result)
            else:
                return json.dumps({"error": "command not authorized"})
        else:
            return json.dumps({"error": "invalid command"})
        
    def updateCacheData(self):
        if self.bitcoindRunning:
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
    
    def updateGeolocationData(self, LOGGER):
        if self.BITCOIN_DATA.peersInfo:
            self.GEO_DATA.updateData(self.BITCOIN_DATA.peersInfo, LOGGER)



