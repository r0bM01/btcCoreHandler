# Copyright [2025-present] [R0BM01@pm.me]                                   #
#                                                                           #
# Distributed under the MIT software license, see the accompanying          #
# file COPYING or http://www.opensource.org/licenses/mit-license.php        #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#############################################################################

import sqlite3
import pathlib, dbm

class BaseStorage:
    base_dir = pathlib.Path.home().joinpath("CustomApp")
    default_mode = 'b' # bytes
    default_ext = '.dat'

    def new_dir(self, dir_path = False):
        if not dir_path:
            dir_path = self.base_dir.joinpath("NewFolder")
        dir_path.mkdir(parents = True, exist_ok = True)

    def new_file(self, file_path = False):
        if not file_path:
            file_path = self.base_dir.joinpath("NewFile" + self.default_ext)
        file_path.touch(exist_ok = True)

    def append_data(self, file_path, file_data, mode = False):
        if not pathlib.Path.exists(file_path):
            file_path = self.base_dir.joinpath(file_path)
        mode = (mode or self.default_mode)
        with open(file_path, 'a' + mode) as F:
            data_pos = F.tell()
            data_size = F.write(file_data)
        return (data_pos, data_size)

    def write_data(self, file_path, file_data, mode = False):
        if not pathlib.Path.exists(file_path):
            file_path = self.base_dir.joinpath(file_path)
        mode = (mode or self.default_mode)
        with open(file_path, 'w' + mode) as F:
            data_size = F.write(file_data)
        return data_size

    def read_data(self, file_path, data_pos = 0, data_lenght = -1, mode = False):
        if not pathlib.Path.exists(file_path):
            file_path = self.base_dir.joinpath(file_path)
        mode = (mode or self.default_mode)
        with open(file_path, 'r' + mode) as F:
            F.seek(data_pos)
            data = F.read(data_lenght)
        return data

    def get_file_size(self, file_path):
        return file_path.stat().st_size


class SimpleDB:
    def __init__(self, db_dir, db_name):
        self.db_dir = pathlib.Path(db_dir)
        self.db_file = self.db_dir.joinpath(db_name)

    def check_db(self):
        return self.db_file.exists()

    def create_db(self):
        sq3 = sqlite3.connect(self.db_name)
        sq3.close()
    
    def create_table(self, table, fields):
        query = f"CREATE TABLE {table}({', '.join(fields)})"
        sq3 = sqlite3.connect(self.db_file)
        cur = sq3.cursor()
        cur.execute(query)
        sq3.commit()
        sq3.close()

    def insert(self, table, values_dict):
        f = ', '.join(values_dict.keys())
        v = ', '.join([':' + str(k) for k in values_dict.values()])
        query = f"INSERT INTO {table} ({f}) VALUES({v})"
        sq3 = sqlite3.connect(self.db_file)
        cur = sq3.cursor()
        cur.execute(query, values_dict)
        sq3.commit()
        sq3.close()
    
    def select(self, table, fields = None, cond_dict = None):
        f = ', '.join(fields) if bool(fields) else '*'
        query = f"SELECT {f} FROM {table}" 
        if bool(cond_dict):
            c = [str(key) + "=" + "?" for key in cond_dict]
            v = list(cond_dict.values())
            query += f" WHERE {' AND '.join(c)}"              
        sq3 = sqlite3.connect(self.db_file)
        cur = sq3.cursor()
        cur.execute(query, v) if bool(cond_dict) else cur.execute(query)
        result = cur.fetchall()
        sq3.close()
        return result
