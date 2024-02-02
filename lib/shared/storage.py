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


import os, pathlib, time, json
import lib.shared.settings
import lib.shared.crypto
from lib.shared.network import Utils


class Server:
    def __init__(self):
        self.fileCert = lib.shared.settings.BASE_DIR.joinpath("cert.rob")
        self.fileLogs = lib.shared.settings.BASE_DIR.joinpath(f"debug_{time.strftime('%a_%d_%b_%Y__%H:%M', time.gmtime())}.log")

        #self.geolocationFile = lib.shared.settings.BASE_DIR.joinpath("geolocation.rob")
        self.geolocation = Geolocation()

        self.certificate = False
    
    def init_files(self):
        if not os.path.exists(lib.shared.settings.BASE_DIR): os.mkdir(lib.shared.settings.BASE_DIR)
        if not os.path.exists(self.fileCert): self.create_certificate()
        else: self.load_certificate()
            #F = open(self.fileCert, "wb")
            #F.close()
        F = open(self.fileLogs, "w")
        F.close()


    def write_geolocation(self, geolocationData):
        encodedData = [str(json.dumps(peer)).encode() for peer in geolocationData]
        with open(self.geolocationFile, "wb") as F:
            [F.write(peer + b"\n") for peer in encodedData]
        
                

    def create_certificate(self):
        with open(self.fileCert, "wb") as F:
            dataBytes = lib.shared.crypto.getRandomBytes(lib.shared.settings.CERT_SIZE)
            F.write(dataBytes)
        self.certificate = dataBytes.hex()
        
    def load_certificate(self):
        with open(self.fileCert, "rb") as F:
            dataBytes = F.read()
            # self.certificate = lib.shared.crypto.getHash(tmpBytes.hex())
        self.certificate = dataBytes.hex()
        

    def check_certificate(self):
        if os.path.exists(self.fileCert):
            self.load_certificate()
            result = True if len(self.certificate) == lib.shared.settings.CERT_SIZE else False
        else:
            result = False
        return result
    

class Geolocation:
    def __init__(self, certificate):
        
        self.DB_FILE = lib.shared.settings.BASE_DIR.joinpath("geoDB")
        self.index = DB_FILE.joinpath("index.r0b")
        self.addrs = DB_FILE.joinpath("addresses.r0b")

        self.certificate = certificate

        self.ALPHA = lib.shared.crypto.getEncryptionAlpha(self.certificate)
        self.BETA = lib.shared.crypto.getDecryptionAlpha(self.certificate)
    

    def load_database():
        with open(self.index, "rb") as F:
            dbTemp = F.read()
        db = { dbTemp[x:x+8] : dbTemp[x+8:x+12] for x in range(0, len(dbTemp), 12) }
        return db
    
    def encode_to_cert(self, string):
        return "".join([self.ALPHA[c] for c in string])
    
    def decode_with_cert(self, string):
        return "".join([self.BETA[string[c:c+4]] for c in range(0, len(string), 4)])

    def make_key(self, data):
        return lib.shared.crypto.getKey(data, self.certificate)
    
    def make_lenght(self, data):
        #data already in bytes
        return bytes.fromhex(str(hex(len(data))[2:]).zfill(4))
    
    def make_value(self, geoObj):
        separator = str("#").encode()
        bytesValue = Utils.getPackedIp(geoObj['ip']) + separator
        bytesValue += bytes.fromhex(self.encode_to_cert(geoObj['country_code2'])) + separator
        bytesValue += bytes.fromhex(self.encode_to_cert(geoObj['country_name'])) + separator
        bytesValue += bytes.fromhex(self.encode_to_cert(geoObj['isp']))
        return self.make_lenght(bytesValue) + bytesValue

    def write_value(self, bytesValue):
        with open(self.addrs, "ab") as F:
            filePos = F.tell()
            F.write(bytesValue)
        return bytes.fromhex(str(hex(filePos)[2:]).zfill(8)) # 4 bytes

    def read_value(self, filePos):
        with open(self.addrs, "rb") as F:
            F.seek(int(filePos.hex(), 16))
            size = F.read(2)
            print(int(size.hex(), 16))
            data = F.read(int(size.hex(), 16))
        return data

    def get_value(self, filePos):
        rawData = self.read_value(filePos)
        rawData = rawData.split(b"#")
        peer['ip'] = Utils.getExplodedIp(rawData[0])
        peer['country_code'] = self.decode_with_cert(rawData[1].hex())
        peer['country_name'] = self.decode_with_cert(rawData[2].hex())
        peer['isp'] = self.decode_with_cert(rawData[3].hex())
        return peer

    def get_value_by_ip(self, ipaddr):
        ipKey = self.make_key(Utils.getPackedIp(ipaddr))
        index = self.load_database()
        return self.get_value(index[ipKey])

    def set_value(self, geoObj):
        indexKey = self.make_key(Utils.getPackedIp(geoObj['ip']))
        filePos = self.write_value(self.make_value(geoObj))
        with open(self.index, "ab") as F:
            F.write(indexKey)
            F.write(filePos)
        return filePos
        
    


class Logger:
    def __init__(self, filePath, verbose = False):
        self.verbose = verbose
        self.FILE = filePath
        self.SESSION = []

    def add(self, message, *args):
        
        log = str(f"{time.ctime(int(time.time()))} - {message}")
        if args:
            arguments = str([a for a in args])
            log += str(f": {arguments}")
        self.SESSION.append(log)
        with open(self.FILE, "a") as F:
            F.write(log + "\n")
        if self.verbose: print(log)
