# Copyright [2023-present] [R0BM01@pm.me]                                   #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License");           #
# you may not use this file except in compliance with the License.          #
# You may obtain a copy of the License at                                   #
#                                                                           #
# http://www.apache.org/licenses/LICENSE:2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#############################################################################

import pathlib, json
import lib.base_storage
from lib.base_crypto import Utils

class Storage:
    def __init__(self, custom_dir = False):
        self.base_dir = self.init_base_dir(custom_dir or pathlib.Path.home())
        self.storage_dir = self.init_dir("storage")
        self.logs_dir = self.init_dir("logs")
        self.export_dir = self.init_dir("export")
        self.certificates = lib.base_storage.SimpleDB(self.storage_dir, "certificates.db")
        self.peers_data = lib.base_storage.SimpleDB(self.storage_dir, "peers_data.db")

    def init_base_dir(self, default_dir):
        dir = pathlib.Path(default_dir).joinpath("HANDLER")
        dir.mkdir(exist_ok = True)
        return dir
    
    def init_dir(self, dir_name):
        dir = self.base_dir.joinpath(dir_name)
        dir.mkdir(exist_ok = True)
        return dir

    def init_databases(self):
        self.init_db_certificates()
        self.init_db_peers_data()

    def init_db_certificates(self):
        if not self.certificates.check_db():
            base_cert = Utils.get_random_bytes(64) 
            self.certificates.create_db()
            self.certificates.create_table("certificates", ['id', 'cert', 'client'])
            self.certificates.insert( 'certificates', 
                                     {'id': Utils.get_hash(base_cert, size = 16),
                                      'cert': base_cert,
                                      'client': 'master'} )

    def init_db_peers_data(self):
        if not self.peers_data.check_db():
            self.peers_data.create_db()
            self.peers_data.create_table('geoinfo', ['id', 'addr', 'full_country', 'short_country', 'city', 'asn'])
            self.peers_data.create_table('peerinfo', ['id', 'version', 'subver', 'services'] )

            
    def load_master_certificate(self):
        return self.certificates.select("certificates", ['cert'], {'client': 'master'})[0]

    def load_certificate(self, peer_id):
        return self.certificates.select("certificates", ['id', 'cert', 'client'], {'id': peer_id})[0]
        
    def generate_certificate(self, peer_client):
        m = self.load_master_certificate()
        p = len(self.certificates.select("certificates")) + 1
        cert = Utils.get_derived_bytes(m, p) # generates a new certificate
        id = Utils.get_hash(cert, size = 16) # build cert id
        ## add the new certificate to the database
        values = {'id': id, 'cert': cert, 'client': peer_client.lower()} 
        self.certificates.insert("certificates", ['id', 'cert', 'client'], values)
        return id

    def export_certificate(self, peer_id):
        row = self.load_certificate(peer_id)
        C = open(self.export_dir.joinpath(row['id']), "wb") # creates a new file with "id" as name
        C.write(row['cert'])
        C.close()


class PeersData:
    def __init__(self):
        self.database = lib.base_storage.SimpleDB(self.storage_dir, "peers_data.db")
    
    def insert(self, id, addr, full_country, short_country, city, asn, version, subver, services):
        geovalues = {
            'id': id,
            'add': addr,
            'full_contry': full_country,
            'short_country': short_country,
            'city': city,
            'asn': asn
        }
        peervalues = {
            'id': id,
            'version': version, 
            'subver': subver,
            'services': services
        }
        self.database.insert('geoinfo', geovalues)
        self.database.insert('peerinfo', peervalues)
    
    