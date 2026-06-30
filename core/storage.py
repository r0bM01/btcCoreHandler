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


DEFAULT_ROOT_FOLDER = pathlib.Path.home().joinpath("btcCoreHandlerData")


class Storage:
    def __init__(self, custom_dir = False):
        self.base_dir = self.init_base_dir(custom_dir or pathlib.Path.home())
        self.storage_dir = self.init_dir("storage")
        self.logs_dir = self.init_dir("logs")
        self.export_dir = self.init_dir("export")

    def init_base_dir(self, default_dir):
        dir = pathlib.Path(default_dir).joinpath("HANDLER")
        dir.mkdir(exist_ok = True)
        return dir
    
    def init_dir(self, dir_name):
        dir = self.base_dir.joinpath(dir_name)
        dir.mkdir(exist_ok = True)
        return dir


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

        self.tables = ["certificates"]
