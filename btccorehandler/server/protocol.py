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

import server.data
import server.machine


        
class RequestHandler:
    def __init__(self):
        #must be inherited by server class
        #do not instantiate directly

        self.BITCOIN_DAEMON = server.machine.BitcoinDaemon()
        self.CACHE = server.data.Cache() # New data holder
        

        self.bitcoindRunning = lib.server.machine.MachineInterface.checkDaemon()

        ## calls list
        self.cached_calls = { # cached calls that require bitcoin daemon running
            'blockchaininfo', 'networkinfo', 'nettotalsinfo',
            'mempoolinfo', 'mininginfo', 'peerinfo'
            }
        
        self.general_calls = { 'keepalive', 'getsysteminfo' } # general calls that do not require bitcoin daemon
        self.control_calls = { 'startdaemon', 'stopdaemon', 'getserverlogs' } # calls reserved to admin level. Do not require bitcoin daemon

        self.geolocation_calls = { 'connectedinfo', 'getgeolocation', 'searchgeolocation' }

        self.bitcoin_calls = {
            'getblockchaininfo', 'getnetworkinfo', 'getmempoolinfo', 'getmininginfo',
            'getnettotals', 'getconnectioncount', 'getpeerinfo', 'addnode', 'getaddednodeinfo', 'disconnectnode', 'listbanned',
            'getblockhash', 'getblockheader'
        }


    def handle_request(self, remote_message):
        remote_request = remote_message.split("#")
        main_call = remote_request[0]
        arguments = remote_request[1:]
        
        ## can reply without bitcoin daemon
        if main_call in self.general_calls: return json.dumps(self.general_call(main_call)) #eventual arguments will be disregarded
        ## if bitcoin daemon not running, default replies or 'startdaemon'
        if not self.BITCOIN_DAEMON.is_running and main_call == 'statusinfo': return json.dumps({"uptime": 0})
        elif not self.BITCOIN_DAEMON.is_running and main_call != 'startdaemon': return json.dumps({"error": "bitcoin daemon not running"})
        elif not self.BITCOIN_DAEMON.is_running and main_call == 'startdaemon': return json.dumps(self.BITCOIN_DAEMON.start())
        ## daemon stop request
        if self.BITCOIN_DAEMON.is_running and main_call == 'stopdaemon': return json.dumps(self.BITCOIN_DAEMON.stop())
        ## with bitcoin daemon running
        if main_call in self.cached_calls: return json.dumps(self.cached_call(main_call, arguments))
        elif main_call in self.geolocation_calls: return json.dumps(self.geolocation_call(main_call, arguments))
        elif main_call in self.bitcoin_calls: return json.dumps(self.bitcoin_call(main_call, arguments))
        ## calls not valid/existing returns error
        else: return json.dumps({"error": "invalid command"})
    
    def general_call(self, command):
        if command == 'keepalive': return {"confirm": "alive"}
        elif command == 'getsysteminfo': return self.CACHE.node_details

    def cached_call(self, command, args_list):
        if bool(args_list):
            #returns all the selected fields
            result = {a : self.CACHE.bitcoin_info[command][a] for a in args_list if a in self.CACHE.bitcoin_info[command]}
        else:
            #returns the whole cached call as a dict
            result = self.CACHE.bitcoin_info[command] 
        return result
        
    def geolocation_call(self, command, args_list):
        if command == 'connectedinfo': 
            result = self.CACHE.connectedInfo
        elif command == 'getgeolocation':
            if bool(args_list):
                result = { a : self.CACHE.get_geolocation_entry(a) for a in args_list }
            else:
                result = {'error': 'missing ip address'}
        elif command == 'searchgeolocation': #experimental
            if bool(args_list):
                search = " ".join(args_list)
                result = {'results': self.CACHE.get_geolocation_search(search)}
            else:
                result = {'error': 'missing search input'}
        return result

    def bitcoin_call(self, command, args_list):
        # temporary. Needs to be changed with new BitcoinDaemon interface
        return self.BITCOIN_DAEMON.run_command(command, args_list)
        
    

