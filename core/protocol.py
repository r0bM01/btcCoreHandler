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

import json
import core.data
import core.commands
import core.machine

class RequestHandler:
    """default request --> {'method': 'cached', 'call': 'systeminfo', 'args': []} """
    def __init__(self, get_data):
        self.keepalive = {'keepalive'}

        self.get_data = get_data

    def validate_request(self, request):
        valid = False
        if 'method' and 'call' in request:
                valid = server.commands.verify_command(request)
        return valid

    def handle_request(self, request):
        request = json.loads(request)
        if request['method'] == 'control' and request['call'] == 'keepalive':
            loaded_data = {"control": "keepalive"}
        else:
            loaded_data = self.get_data(request['method'], request['call'], request['args'])
        return loaded_data

    # threading method handled by Controller class
    def peers_worker(self, peer):
        while peer.is_connected and peer.reputation:
            request = peer.recv_msg() # waits 5 seconds as per socket timeout default
            if self.validate_request(request):
                peer.send_msg(json.dumps(self.handle_request(request)))
            else:
                if bool(request):
                    # data received but invalid
                    peer.send_msg(json.dumps({'error': 'invalid request'}))
                    peer.reputation -= 1
            peer.is_connected = peer.is_alive()
        if not bool(peer.reputation):
            peer.is_connected = False

    # dedicated thread for btcHandlerCli managed by Controller class
    def local_cli_handler(self, peer_cli, graceful_shutdown):
        request = json.loads(peer_cli.recv_msg())
        if self.validate_request(request):
            if request['method'] == 'handlerstop':
                # shut the server down
                response = {'control': 'handlerstop'}
                graceful_shutdown()
            else:
                response = self.handle_request(request)
        else:
            response = {'error': 'invalid request'}
        peer_cli.send_msg(json.dumps(response))
        peer_cli.disconnect()
