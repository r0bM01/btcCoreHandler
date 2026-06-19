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



class BaseDB:
    db_path = pathlib.Path.home().joinpath("database")
    db_file = "default.db"
    db = db_path.joinpath(db_file)
    
    def make_db_file(self):
        try:
            sqlite = sqlite3.connect(self.db)
            sqlite.close()
        except sqlite3.OperationalError as err:
            assert f"impossible to create database file: {err}"
    
    def make_db_table(self, sql: str):
        try:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
        except sqlite3.OperationalError as err:
            assert f"error while creating tables: {err}"
    
    def raw_insert(self, sql: str, data):
        try:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
        except sqlite3.OperationalError as err:
            assert f"operation failed: {err}"

    def raw_insert_many(self, sql: str, data_list: list):
        try:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, data_list)
                conn.commit()
        except sqlite3.OperationalError as err:
            assert f"error while creating tables: {err}"
    
    def raw_select(self, sql: str, data: list = []):
        try:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, data)
                rows = cursor.fetchall()
                return rows
        except sqlite3.OperationalError as err:
            assert f"operation failed: {err}"
        