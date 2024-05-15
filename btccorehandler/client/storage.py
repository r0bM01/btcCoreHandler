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
from lib.storage import Base


class Client(Base):

    def check_base_dir(self):
        return self.check_exists(self.saveDir)
    
    def init_certificate(self):
        if not pathlib.Path.exists(self.file_tree['cert']):
            raise OSError("Missing certificate! You cannot start server without it!")
        if not self.verify_certificate():
            raise OSError("Certificate corrupted! Server cannot be started!")
        self.certificate = self.load_certificate()
    
    def init_cryptography(self):
        if not bool(self.certificate):
            raise OSError("Missing certificate! Cryptography cannot be initialized!")
        self.crypto = lib.crypto.Storage(self.certificate)

    def save_settings(Self):
        pass