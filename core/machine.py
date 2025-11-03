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

import subprocess, json

class Node:
    def __init__(self):
        self.allowed_commands = []

    def get_local_IP(self):
        ip_list = str(subprocess.run(["hostname", "-I"], capture_output = True).stdout.decode().strip("\n")).split(" ")
        return ip_list[0]

    def get_external_IP(self):
        return str(subprocess.run(["curl", "ip.me"], capture_output = True).stdout.decode())

    def check_bitcoin_daemon(self):
        return bool(subprocess.run(["pidof", "bitcoind"], capture_output = True).stdout.decode())

    def run_command(self, command_list):
        return str(subprocess.run(command_list, capture_output = True).stdout.decode())


class BitcoinDaemon:
    def __init__(self):
        self.daemon = "bitcoind"
        self.client = "bitcoin-cli"
        self.is_running = self.daemon_running()

    def get_data(self, command, *args):
        return self.run_command(command, args)

    def daemon_running(self):
        return bool(subprocess.run(["pidof", self.daemon], capture_output = True).stdout.decode())

    def start(self):
        subprocess.run([self.daemon], capture_output = True)
        self.is_running = bool(subprocess.run(["pidof", self.daemon], capture_output = True).stdout.decode())
        return {"start": self.is_running}

    def stop(self):
        subprocess.run([self.client, "stop"])
        self.is_running = bool(subprocess.run(["pidof", self.daemon], capture_output = True).stdout.decode())
        return {"stop": self.is_running}

    def run_command(self, command, *args):
        full_call = [self.client]
        full_call.append(command)
        full_call.extend(args)
        return json.loads(subprocess.run(full_call, capture_output = True).stdout.decode())
