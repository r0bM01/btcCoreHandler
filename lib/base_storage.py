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

import pathlib, dbm.sqlite3

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


class SimpleDB(BaseStorage):
    db_dir = False
    db_file = False
        
    def create_db(self, db_name = "storage.db"):
        if not self.db_dir:
            self.db_dir = self.base_dir.joinpath("db_storage")
            self.new_dir(self.db_dir)
        self.db_file = self.db_dir.joinpath(db_name)
        DB = dbm.sqlite3.open(self.db_file, flag = "n")
        DB.close()

    def insert(self, key, value):
        with dbm.sqlite3.open(self.db_file, flag = "w") as DB:
            if key not in DB:
                DB[key] = value
                result = True
            else:
                result = False
        return result
        
    def update(self, key, value):
        with dbm.sqlite3.open(self.db_file, flag = "w") as DB:
            if key in DB:
                DB[key] = value
                result = True
            else:
                result = False
        return result
    
    def select(self, key):
        with dbm.sqlite3.open(self.db_file, flag = "r") as DB:
            result = DB.get(key, False)
        return result
    
    def remove(self, key):
        with dbm.sqlite3.open(self.db_file, flag = "w") as DB:
            if key in DB:
                del DB[key]
                result = True
            else:
                result = False
        return result



