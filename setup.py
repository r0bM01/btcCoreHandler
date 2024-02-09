#############################################################################
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

import pathlib, shutil, sys
import secrets
import argparse


class Base:
    def __init__(self):

        self.base = pathlib.Path('/usr/lib/btcCoreHandler')

        self.source = {'lib': pathlib.Path.cwd().joinpath('lib'),
                       'ui': pathlib.Path.cwd().joinpath('ui')}

        self.dest = {'lib': self.base.joinpath('lib'),
                     'ui': self.base.joinpath('ui')}
        
        self.home = pathlib.Path.home()
        
    def create_certificate(self):
        return secrets.token_bytes(64)
    
    def import_certificate(self, source):
        with open(pathlib.Path(source), "rb") as F:
            data = F.read()
        return data if len(data) == 64 else False

    def install(self):
        if not pathlib.Path.exists(self.base):
            pathlib.Path.mkdir(self.base)
        
        # creates folders
        if not pathlib.Path.exists(self.dest['lib']):
            pathlib.Path.mkdir(self.dest['lib'])

        if not pathlib.Path.exists(self.dest['ui']):
            pathlib.Path.mkdir(self.dest['ui'])

        if not pathlib.Path.exists(self.dest['data']):
            pathlib.Path.mkdir(self.dest['data'])
            pathlib.Path.mkdir(self.dest['data'].joinpath('cert'))

        try:
            shutil.copytree(self.source['lib'], self.dest['lib'])
            shutil.copytree(self.source['ui'], self.dest['ui'])
        except OSError as E:
            print("Error while copying files into directories!")
            print(E)

        print("Files correctly installed!")

        if bool(importCertificate):
            certificate = self.import_certificate(importCertificate)
        else:
            certificate = self.create_certificate()
        
        if bool(certificate):
            homeFolder = self.dest['data']
            with open(self.dest['data'].joinpath('cert', 'cert.r0b'), "wb") as C:
                C.write(certificate)
            print("Certificate correctly created/imported!")
        else:
            print("Error in creating/importing certificate!")
        sys.exit()


        
        
        
        
        
def main():
    print("TESTING CLIENT INSTALLER")

    C = Client()
    C.install()


if __name__ == '__main__':
    main()

    