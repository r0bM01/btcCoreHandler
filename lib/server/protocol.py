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

        self.CACHE = lib.server.data.Cache() # New data holder
        
        self.CONTROL = lib.shared.commands.Control()
        self.BITCOIN_DATA = lib.server.data.Bitcoin()
        self.GEO_DATA = lib.server.data.IPGeolocation()

        self.bitcoindRunning = lib.server.machine.MachineInterface.checkDaemon()
        
    def handle_request(self, remoteCall):
        remote_request = remoteCall.split("#")
        call = remote_request[0]
        args = remote_request[1:]

        
        if call not in self.CONTROL.calls: return json.dumps({"error": "invalid command"})
        if call in self.CONTROL.cachedCalls: return json.dumps(call())
        
        if call == "keepalive": return json.dumps({"confirm": "alive"})

        if not self.CONTROL.check(call): return json.dumps({"error": "invalid command"})

        if not self.bitcoindRunning and request == "getstatusinfo": return json.dumps({"uptime": 0})
        if not self.bitcoindRunning and request != "start": return json.dumps({"error": "bitcoin daemon not running"})
        elif not self.bitcoindRunning and request == "start": self.startbitcoind()
        elif self.bitcoindRunning and request == "stop": self.stopbitcoind()

        elif request == "getgeolocationinfo": return json.dumps(self.GEO_DATA.getCountryList(self.CACHE.bitcoin['peersInfo']))

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

    def getconnectedinfo(self):
        return json.dumps(self.CACHE.connectedInfo)

    def getsysteminfo(self):
        return json.dumps(self.CACHE.node_details)

    def getpeerinfo(self):
        return jsoin.dumps(self.CACHE.bitcoin['peersInfo'])
        
    def getstatusinfo(self):
        message = {}
        #message['startData'] = self.startDate
        message['uptime'] = self.CACHE.bitcoin['uptime']['uptime']
        message['chain'] = self.CACHE.bitcoin['blockchainInfo']['chain']
        message['blocks'] = self.CACHE.bitcoin['blockchainInfo']['blocks']
        message['headers'] = self.CACHE.bitcoin['blockchainInfo']['headers']
        message['verificationprogress'] = self.CACHE.bitcoin['blockchainInfo']['verificationprogress']
        message['pruned'] = self.CACHE.bitcoin['blockchainInfo']['pruned']
        message['size_on_disk'] = self.CACHE.bitcoin['blockchainInfo']['size_on_disk']

        message['version'] = self.CACHE.bitcoin['networkInfo']['version']
        message['subversion'] = self.CACHE.bitcoin['networkInfo']['subversion']
        message['protocolversion'] = self.CACHE.bitcoin['networkInfo']['protocolversion']
        message['connections'] = self.CACHE.bitcoin['networkInfo']['connections']
        message['connections_in'] = self.CACHE.bitcoin['networkInfo']['connections_in']
        message['connections_out'] = self.CACHE.bitcoin['networkInfo']['connections_out']
        message['localservicesnames'] = self.CACHE.bitcoin['networkInfo']['localservicesnames']
        message['networks'] = self.CACHE.bitcoin['networkInfo']['networks']
        message['relayfee'] = self.CACHE.bitcoin['networkInfo']['relayfee']

        message['totalbytessent'] = self.CACHE.bitcoin['nettotalsInfo']['totalbytessent']
        message['totalbytesrecv'] = self.CACHE.bitcoin['nettotalsInfo']['totalbytesrecv']

        message['difficulty'] = self.CACHE.bitcoin['miningInfo']['difficulty']
        message['networkhashps'] = self.CACHE.bitcoin['miningInfo']['networkhashps']

        message['size'] = self.CACHE.bitcoin['mempoolInfo']['size']
        # message['bytes'] = self.mempoolInfo['bytes']
        message['usage'] = self.CACHE.bitcoin['mempoolInfo']['usage']
        message['mempoolminfee'] = self.CACHE.bitcoin['mempoolInfo']['mempoolminfee']
        message['fullrbf'] = self.CACHE.bitcoin['mempoolInfo']['fullrbf']
        return message



