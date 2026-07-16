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
from os import mkfifo
from core import env
from core import benchutils


class Storage:
    def __init__(self, custom_dir = False):
        self.base_dir = self.init_base_dir(env.DATA_FOLDER)
        self.storage_dir = self.init_dir(env.STORAGE_FOLDER)
        self.logs_dir = self.init_dir(env.LOGS_FOLDER)
        self.temp_dir = self.init_dir(self.storage_dir.joinpath("temp"))
        self.pid_file = self.init_file(self.temp_dir.joinpath("handler.pid"))
        #self.export_dir = self.init_dir("export")

    def init_base_dir(self, base_dir_path):
        #dir = pathlib.Path(default_dir).joinpath("HANDLER")
        base_dir_path.mkdir(exist_ok = True)
        return base_dir_path
    
    def init_dir(self, dir_path):
        #dir = self.base_dir.joinpath(dir_name)
        dir_path.mkdir(exist_ok = True)
        return dir_path
    
    def init_file(self, file_path, file_name = False):
        #if bool(file_name):
        #    file_path.joinpath(file_name)
        file_path.touch(exist_ok = True)
        return file_path
    
    def write_file(self, file_path, data):
        if not self.file_path.exists:
            self.init_file(file_path)
        with open(file_path, "w") as F:
            F.write(data)
    
    def remove_file(self, file_path):
        file_path.unlink(missing_ok = True)

class BitcoinPeers(lib.base_storage.BaseDB):
    def __init__(self, custom_dir = False):
        self.db_path = custom_dir or DEFAULT_ROOT_FOLDER 
        self.db_file = "bitcoinpeers.db"
        self.db = self.db_path.joinpath(self.db_file)

        self.table_name = "geolocation"

        self.make_db_file() # init the db file if not existing
        self.create_geolocation_table() # init the table if not existing

    def create_geolocation_table(self):
        sql = f'''CREATE TABLE IF NOT EXISTS {self.table_name} (
                    ip CHAR PRIMARY KEY,
                    isp, org, hostname, latitude, longitude, 
                    postal_code, city, country_code, country_name, 
                    continent_code, continent_name, region, 
                    district, timezone_name, connection_type, 
                    asn_number, asn_org, asn, currency_code, 
                    currency_name, language_code, language_name, 
                    success, premium,
                    checksum CHAR NOT NULL );'''
        self.make_db_table(sql)

    def make_geolocation_dict(self, row: tuple):
        return {
            'ip':               row[0],
            'isp':              row[1],
            'org':              row[2],
            'hostname':         row[3],
            'latitude':         row[4],
            'longitude':        row[5],
            'postal_code':      row[6],
            'city':             row[7],
            'country_code':     row[8],
            'country_name':     row[9],
            'continent_code':   row[10],
            'continent_name':   row[11],
            'region':           row[12],
            'district':         row[13],
            'timezone_name':    row[14],
            'connection_type':  row[15],
            'asn_number':       row[16],
            'asn_org':          row[17],
            'asn':              row[18],
            'currency_code':    row[19],
            'currency_name':    row[20],
            'language_code':    row[21],
            'language_name':    row[22],
            'success':          row[23],
            'premium':          row[24],
            'checksum':         row[25],
        }
        
    def insert_geolocation(self, geo: dict):
        columns = ", ".join([":"+str(k) for k in geo.keys()])
        sql = f'''INSERT OR IGNORE INTO {self.table_name} VALUES({columns});'''
        self.raw_insert(sql, geo)
    
    def select_geolocation(self, ipaddrs: list ):
        sql = f'''SELECT * FROM {self.table_name} WHERE ip IN ({", ".join('?' * len(ipaddrs))});'''
        res = self.raw_select(sql, ipaddrs)
        geo = [self.make_geolocation_dict(row) for row in res] if bool(res) else []
        return geo

    def select_num_countries(self):
        sql = '''SELECT COUNT(DISTINCT country_name) FROM geolocation;'''
        res = self.raw_select(sql)
        return res[0][0]
    
    def select_num_cities(self):
        sql = '''SELECT COUNT(DISTINCT city) FROM geolocation;'''
        res = self.raw_select(sql)
        return res[0][0]
    
    def select_num_nodes(self):
        sql = '''SELECT COUNT(ip) FROM geolocation;'''
        res = self.raw_select(sql)
        return res[0][0]
    
    def select_top_countries_by_nodes(self, top: int = 0):
        sql = '''SELECT country_name, COUNT(ip) FROM geolocation GROUP BY country_name ORDER BY COUNT(ip) DESC;'''
        res = self.raw_select(sql)
        return res if not top else res[:top]

class HandlerDB(lib.base_storage.BaseDB):
    def __init__(self, custom_dir):
        self.db_path = custom_dir or DEFAULT_ROOT_FOLDER 
        self.db_file = "handler.db"
        self.db = self.db_path.joinpath(self.db_file)
        self.make_db_file()
        self.create_users_table()
        #self.table = {'users': ""}
    
    def create_users_table(self):
        sql = f'''CREATE TABLE IF NOT EXISTS users (
                    id CHAR PRIMARY KEY NOT NULL,
                    user NOT NULL, hashpassw NOT NULL);'''
        self.make_db_table(sql)

    def insert_user(self, user, passw):
        id = benchutils.short_id(str(user.lower() + passw).encode('utf-8'))
        hp = benchutils.full_hash(passw.encode('utf-8'))
        sql = f'''INSERT OR IGNORE INTO users VALUES(?, ?, ?);'''
        self.raw_insert(sql, (id, user, hp))
    
    def select_user(self, id):
        sql = '''SELECT * FROM users WHERE id IN (?);'''
        res = self.raw_select(sql, [id])
        return {'id': res[0][0], 'user': res[0][1], 'hashpassw': res[0][2]}

class LocalPipe:
    def __init__(self):
        self.pipe = env.PIPE_MSG
        if not self.pipe.exists():
            mkfifo(self.pipe)
    
    def close_pipe(self):
        self.pipe.unlink(missing_ok = True)

    def recv(self):
        with open(self.pipe, "r") as P:
            data = P.read()
        return data
    
    def send(self, data):
        with open(self.pipe, "w") as P:
            P.write(data)
    
