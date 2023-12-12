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


import os, pathlib, time
import lib.settings
import lib.crypto

def getTime():
    return int(time.time())

class Data:
    def __init__(self):
        self.fileCert = lib.settings.BASE_DIR.joinpath("cert.rob")
        self.fileLogs = lib.settings.BASE_DIR.joinpath(f"debug_{getTime()}.log")

        self.certificate = False
    
    def init_files(self):
        if not os.path.exists(lib.settings.BASE_DIR): os.mkdir(lib.settings.BASE_DIR)
        F = open(self.fileCert, "wb")
        F.close()
        F = open(self.fileLogs, "w")
        F.close()
    
    def create_certificate(self):
        with open(self.fileCert, "wb") as F:
            dataBytes = lib.crypto.getRandomBytes(lib.settings.CERT_SIZE)
            F.write(dataBytes)
        
    def load_certificate(self):
        with open(self.fileCert, "rb") as F:
            tmpBytes = F.read()
            self.certificate = lib.crypto.getHash(tmpBytes.hex())

    def check_certificate(self):
        if os.path.exists(self.fileCert):
            self.load_certificate()
            result = True if len(self.certificate) == lib.settings.CERT_SIZE else False
        else:
            result = False
        return result
    

class Logger:
    def __init__(self, filePath, verbose = False):
        self.verbose = verbose
        self.FILE = filePath
        self.SESSION = []

    def add(self, message, *args):
        
        log = str(f"{time.ctime(getTime())} - {message}")
        if args:
            arguments = str([a for a in args])
            log += str(f": {arguments}")
        self.SESSION.append(log)
        with open(self.FILE, "a") as F:
            F.write(log + "\n")
        if self.verbose: print(log)
