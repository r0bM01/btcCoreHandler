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

import json, time
import core.data
import core.commands
import core.machine

class RequestHandler:
    """default request --> {'method': 'call_for_bitcoin_daemon', 'args': []} """
    def __init__(self, logger, interface):

        self.logger = logger
        self.interface = interface


    def validate_request(self, request):
        return core.commands.verify_command(request)


    def handle_request(self, request):
        if request['method'] == 'nocache' and self.validate_request(request['args'][0]):
            reply = self.interface.daemon_call(request['args'][0], request['args'][1:])
        elif request['method'] == 'handlerstop':
            reply = {'error': 'btcHandler can be stopped by local command only'}
        else:
            reply = self.interface.get_data(request['method'], request['args'])
        return reply

    # threading method handled by Controller class
    def peers_worker(self, peer):
        peer.set_waiting_mode(60)
        while peer.is_connected and peer.reputation:
            request = peer.recv_msg() # waits n seconds as per socket timeout default
            if bool(request):
                start_time = time.time()
                request = json.loads(request)
                if self.validate_request(request):
                    if request.get('method') != 'keepalive':
                        reply = json.dumps(self.handle_request(request))
                        peer.send_msg(reply)
                        self.logger.info("protocol request", peer.peer_addr, request['method'], f"bytes {len(reply)}", f"{int(time.time() - start_time)} secs" )
                else:
                    # data received but invalid
                    peer.send_msg(json.dumps({'error': 'invalid request'}))
                    peer.reputation -= 1
            else:
                self.logger.info("client disconnected", peer.peer_addr)
                peer.disconnect()
                #peer.is_connected = peer.is_alive()
        if not bool(peer.reputation):
            peer.is_connected = False

    # dedicated thread for btcHandlerCli managed by Controller class
    def local_cli_handler(self, local_cli, shutdown):
        local_cli.is_connected = True
        local_cli.set_waiting_mode()
        request = local_cli.recv_msg()
        if bool(request) and self.validate_request(json.loads(request)):
            request = json.loads(request)
            self.logger.info("protocol", "LOCAL", request['method'])
            if request['method'] != 'handlerstop':
                response = self.handle_request(request)
            else:
                # shut the server down
                response = {'confirm': 'handlerstop'}
        else:
            response = {'error': 'invalid request'}
        local_cli.send_msg(json.dumps(response))
        local_cli.disconnect()
        if request['method'] == 'handlerstop':
            self.logger.info("client local shutdown started")
            shutdown.set()
