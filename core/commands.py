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

COMMANDS = {
    'control': {'handlerstop', 'handlerlogs', 'keepalive', 'bitcoindrunning', 'test'},
    'cached': {'systeminfo','blockchaininfo', 'networkinfo', 'nettotalsinfo', 'mempoolinfo', 'mininginfo', 'peerinfo'},
    'bitcoin': {'uptime', 'getblockchaininfo', 'getnetworkinfo', 'getmempoolinfo', 'getmininginfo', 'getpeerinfo', 'getnettotals',
                'addnode', 'getaddednodeinfo'},
    'stored': {'geobyip'}
}


def verify_command(request):
    return (request['method'] in COMMANDS and request['call'] in COMMANDS[request['method']])
