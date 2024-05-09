# Copyright [2023 - 2024] [R0BM01@pm.me]                                    #
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

import pathlib

import lib.storage
import lib.crypto

class Storage(lib.storage.Base):

    def init_base(self):
        if not self.check_exists(self.base_dir):
            self.init_dir(self.base_dir)
        if not self.check_exists(self.dir_tree['debug']):
            self.init_dir(self.dir_tree['debug'])
    
    def init_cryptography(self):
        if not bool(self.certificate):
            raise OSError("Missing certificate! Cryptography cannot be initialized!")
        self.crypto = lib.crypto.Storage(self.certificate)

    def check_base_dir(self):
        return self.check_exists(self.base_dir)
    
    def check_certificate(self):
        return self.check_exists(self.file_tree['cert'])

    def init_certificate(self):
        if not pathlib.Path.exists(self.file_tree['cert']):
            raise OSError("Missing certificate! You cannot start server without it!")
        if not self.verify_certificate():
            raise OSError("Certificate corrupted! Server cannot be started!")
        self.certificate = self.load_certificate()

    def init_geolocation(self):
        if not bool(self.certificate):
            raise OSError("Missing certificate! You cannot init Geolocation without it!")
        if not pathlib.Path.exists(self.dir_tree['geoDb']):
            raise OSError("Geolocation database folder missing!")
        if not pathlib.Path.exists(self.file_tree['geoDbIndex']):
            raise OSError("Missing geolocation database index!")
        if not pathlib.Path.exists(self.file_tree['geoDbContent']):
            raise OSError("Missing geolocation database!")
        self.geolocation = Geolocation(self.certificate, self.dir_tree['geoDb'])
    
    def geolocation_load_db_index(self):
        full_data_file = self.read_all_file(self.file_tree['geoDbContent']) #returns dict['dataPos] : int / dict['dataBytes] : bytes
        database = {}
        for entry in full_data_file:
            entry_file_pos = entry['dataPos']
            geolocation_data = self.crypto.decrypt(entry['dataBytes'].hex()).split("#")
            database[geolocation_data[0]] = entry['dataPos']
        return database # returns a dict "ip_bytes_key" : "peer_file_position_value"
    
    def geolocation_load_entry(self, file_pos):
        single_entry = self.read_single_entry(file_pos)
        retrieved_data = self.crypto.decrypt(single_entry.hex()).split("#")
        geolocation_data = {
            'ip': retrieved_data[0],
            'country_code2': retrieved_data[1].upper(),
            'country_name': retrieved_data[2].capitalize(),
            'isp': retrieved_data[3].capitalize()
            }
        return geolocation_data
    
    def geolocation_write_entry(self, entry_data):
        concat = str(entry_data['ip']) + "#" + entry_data['country_code2'] + "#" + entry_data['country_name'] + "#" + entry_data['isp']
        encrypted_data = self.crypto.encrypt(concat)
        entry_pos = self.write_append(self.file_tree['geoDbContent'], encrypted_data)
        return entry_pos

        
