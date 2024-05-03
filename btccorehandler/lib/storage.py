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

class Base:
    def __init__(self):
        self.base_dir = pathlib.Path.home().joinpath(".btcCoreHandler")

        self.dir_tree = {'cert': self.base_dir.joinpath('cert'),
                         'debug': self.base_dir.joinpath('debug'), 
                         'geoDb': self.base_dir.joinpath('geoDb'),
                         'statsDb': self.base_dir.joinpath('statsDb'),}
        
        self.file_tree = {'cert': self.dir_tree['cert'].joinpath('cert.r0b'),
                          'geoDbIndex': self.dir_tree['geoDb'].joinpath('index.r0b'),
                          'geoDbContent': self.dir_tree['geoDb'].joinpath('addresses.r0b'),
                          'statsDbIndex': self.dir_tree['statsDb'].joinpath('index.r0b'),
                          'statsDbContent': self.dir_tree['statsDb'].joinpath('statistics.r0b')}
    
    def check_exists(self, filePath):
        realPath = pathlib.Path(filePath)
        return pathlib.Path.exists(realPath)
    
    def init_dir(self, dirPath):
        realPath = pathlib.Path(dirPath)
        realPath.mkdir(exist_ok = True)
        
    def init_file(self, filePath):
        realPath = pathlib.Path(filePath)
        realPath.touch(exist_ok = True)
        
    def init_all(self):
        [self.init_dir(self.dir_tree[d]) for d in self.dir_tree] # init and rewrites directories
        [self.init_file(f) for f in self.file_tree] #init and rewrites files
        
    def generate_certificate(self):
        self.init_file(self.file_tree['cert']) # avoid previous certificate
        certBytes = lib.shared.crypto.getRandomBytes(lib.shared.settings.CERT_SIZE)
        with open(self.file_tree['cert'], "wb") as F:
            F.write(certBytes)
        
    def import_certificate(self, sourceFile):
        sourcePath = pathlib.Path(sourceFile)
        self.init_file(self.file_tree['cert']) # avoid previous certificate
        with open(sourcePath, "rb") as F:
            source = F.read()
        with open(self.file_tree['cert'], "wb") as F:
            F.write(source)
    
    def load_certificate(self):
        with open(self.file_tree['cert'], "rb") as F:
            certBytes = F.read()
        return certBytes.hex()
    
    def verify_certificate(self):
        return len(self.load_certificate()) == 128
    
    def write(self, filePath, dataBytes):
        realPath = pathlib.Path(filePath)
        dataLenght = bytes.fromhex(str(hex(len(dataBytes))[2:]).zfill(4))
        with open(realPath, "ab") as F:
            dataPos = F.tell()
            F.write(dataLenght + dataBytes)
        return dataPos
    
    def read_all(self, filePath):
        realPath = pathlib.Path(filePath)
        data_array = []
        with open(realPath, "rb") as F:
            while True:
                data_pos = F.tell()
                data_size = int(F.read(2), 16)
                if bool(data_size):
                    data_bytes = F.read(data_size)
                    data_array.append({'dataPos': data_pos, 'dataBytes': data_bytes})
                    F.seek(data_size, 1)
                else:
                    break
        return data_array



class Client(Base):

    def check_base_dir(self):
        return self.check_exists(self.saveDir)

    def init_certificate(self):
        if self.check_exists(self.saveDirs['cert']) and self.check_exists(self.saveFiles['cert']):
            return self.load_certificate() if self.check_certificate() else False
        else:
            self.init_dir(self.saveDirs['cert'])
            self.init_file(self.saveFiles['cert'])
            return False
    

class Geolocation:
    def __init__(self, certificate, dirPath):
        
        self.DB_DIR = pathlib.Path(dirPath)
        self.index = self.DB_DIR.joinpath("index.r0b")
        self.addrs = self.DB_DIR.joinpath("addresses.r0b")

        self.certificate = bytes.fromhex(certificate)

        self.ALPHA = lib.shared.crypto.getEncryptionAlpha(self.certificate)
        self.BETA = lib.shared.crypto.getDecryptionAlpha(self.certificate)
    
    def load_database(self):
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
    
    def get_value_by_lenght(self, data):
        l = int(data[:2].hex(), 16)
        v = data[2:2+l]
        return v, data[2+l:]
    
    def make_value(self, geoObj):
        ip = Utils.getPackedIp(geoObj['ip']) 
        country_name = bytes.fromhex(self.encode_to_cert(geoObj['country_name'])) 
        isp = bytes.fromhex(self.encode_to_cert(geoObj['isp']))

        bytesValue = self.make_lenght(ip) + ip
        bytesValue += bytes.fromhex(self.encode_to_cert(geoObj['country_code2']))
        bytesValue += self.make_lenght(country_name) + country_name
        bytesValue += self.make_lenght(isp) + isp
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
            data = F.read(int(size.hex(), 16))
        return data

    def get_value(self, filePos):
        data = rawData = self.read_value(filePos)

        peer = {}
        ip, data = self.get_value_by_lenght(data)
        code, data = data[:4], data[4:]
        country, data  = self.get_value_by_lenght(data)
        isp, data  = self.get_value_by_lenght(data)

        # return (ip, code, country, isp)

        peer['ip'] = Utils.getExplodedIp(ip)
        peer['country_code'] = self.decode_with_cert(code.hex())
        peer['country_name'] = self.decode_with_cert(country.hex())
        peer['isp'] = self.decode_with_cert(isp.hex())

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
    def __init__(self, dirPath, verbose = False):
        self.verbose = verbose
        self.FILE = dirPath.joinpath(f"debug_{time.strftime('%a_%d_%b_%Y__%H:%M', time.gmtime())}.log")
        self.FILE.touch()
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
