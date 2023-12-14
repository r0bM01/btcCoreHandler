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

import lib.server.server
import lib.client

print("[1] - start server")
print("[2] - start client")
print("[3] - start GUI")
print("[4] - subprocess server")

c = int(input(">> "))

if c == 1: lib.server.server.main()
if c == 2: lib.client.clientTerminal()
if c == 3: import ui.main
if c == 4:
    import subprocess
    subprocess.run(["./test_server.py"])

print("program closed")
