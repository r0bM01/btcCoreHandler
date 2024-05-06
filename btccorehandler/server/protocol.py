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

        
class RequestHandler:
    def __init__(self):
        #must be inherited by server class
        #do not instantiate directly

        self.CACHE = lib.server.data.Cache() # New data holder
        self.CONTROL = lib.shared.commands.Control()
        self.BITCOIN_DAEMON = server.machine.BitcoinDaemon()

        self.bitcoindRunning = lib.server.machine.MachineInterface.checkDaemon()

        ## calls list
        self.cached_calls = { # cached calls that require bitcoin daemon running
            'getstatusinfo', 'getconnectedinfo', 'getblockchaininfo', 'getnetworkinfo',
            'getnettotals', 'getmempoolinfo', 'getmininginfo', 'getpeerinfo'
            }
        
        self.general_calls = { 'keepalive', 'getsysteminfo' } # general calls that do not require bitcoin daemon
        self.control_calls = { 'startdaemon', 'stopdaemon', 'getserverlogs' } # calls reserved to admin level. Do not require bitcoin daemon

        self.updated_calls = { 'updated', 'getgeolocation' }


    def handle_request(self, remote_message, remote_level):
        remote_request = remote_message.split("#")
        main_call = remote_request[0]
        

        if main_call in self.general_calls: return json.dumps(main_call())


        if not self.BITCOIN_DAEMON.is_running and main_call == 'getstatusinfo': return json.dumps({"uptime": 0})
        elif not self.BITCOIN_DAEMON.is_running and main_call != 'start': return json.dumps({"error": "bitcoin daemon not running"})
        elif not self.BITCOIN_DAEMON.is_running and main_call == 'start': return jsoin.dumps(self.BITCOIN_DAMEMON.start())
        
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
    
    def keepalive(self):
        return {"confirm": "alive"}

    def getsysteminfo(self):
        return json.dumps(self.CACHE.node_details)
    
    def bitcoin_call(self, command, args):
        pass
        
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

    def getblockchaininfo(self):
        return json.dumps(self.CACHE.bitcoin_info['blockchainInfo'])

    def getnetworkinfo(self):
        return json.dumps(self.CACHE.bitcoin_info['networkInfo'])

    def getnettotals(self):
        return json.dumps(self.CACHE.bitcoin_info['nettotalsInfo'])
    
    def getmempoolinfo(self):
        return json.dumps(self.CACHE.bitcoin_info['mempoolInfo'])

    def getmininginfo(self):
        return json.dumps(self.CACHE.bitcoin_info['miningInfo'])  

    def getpeerinfo(self):
        return json.dumps(self.CACHE.bitcoin_info['peersInfo'])

    def getconnectedinfo(self):
        return json.dumps(self.CACHE.connectedInfo)
    
