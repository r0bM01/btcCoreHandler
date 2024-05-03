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

import lib.shared.crypto

class Control:
    def __init__(self):
        
        self.cachedCalls = {'getsysteminfo', 'getstatusinfo', 'getgeolocationinfo', 'getconnectedinfo'}
        self.bitcoinCalls = {'uptime', 'getblockchaininfo', 'getnetworkinfo', 'getmempoolinfo', 'getmininginfo', 'getpeerinfo', 'getnettotals',
                             'addnode', 'getaddednodeinfo'}
        self.controlCalls = {'start', 'stop', 'keepalive', 'advancedcall', 'bitcoindrunning', 'getserverlogs', 'test'}

        self.calls = set()
        self.calls.update(self.cachedCalls)
        self.calls.update(self.bitcoinCalls)
        self.calls.update(self.controlCalls)


        self.encodedCalls = False

        # self.LEVELS = {"blocked": 0, "user": 1, "admin": 2} not implemented yet
     

    def encodeCalls(self, hexCertificate, handshakeCode):
        self.encodedCalls = {lib.shared.crypto.getHashedCommand(call, hexCertificate, handshakeCode) : call for call in self.calls}

    def check(self, call):
        return call in self.encodedCalls
                  