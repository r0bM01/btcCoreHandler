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

        self.baseDir = pathlib.Path('/usr/lib/btcCoreHandler')

        self.source = {'lib': pathlib.Path.cwd().joinpath('lib'),
                       'ui': pathlib.Path.cwd().joinpath('ui')}

        self.dest = {'lib': self.baseDir.joinpath('lib'),
                     'ui': self.baseDir.joinpath('ui')}
        
        self.usrHome = pathlib.Path.home()
        self.saveDir = self.usrHome.joinpath('.btcCoreHandler')
        
    def create_certificate(self):
        if pathlib.Path.exists(self.saveDir.joinpath('cert')):
            certFile = self.saveDir.joinpath('cert', 'cert.r0b')
            with open(certFile, "wb") as F:
                F.write(secrets.token_bytes(64))
        print("Certificate generated")
    
    def import_certificate(self, sourceFile):
        if pathlib.Path.exists(sourceFile):
            with open(pathlib.Path(sourceFile), "rb") as F:
                data = F.read()
            if len(data) == 64:
                certFile = self.saveDir.joinpath('cert', 'cert.r0b')
                with open(certFile, "wb") as F:
                    F.write(data)
                print("Certificate correctly imported!")
            else:
                print("Source certificate not valid!")
        else:
            print("Source file not found!")
    
    def init_save_dirs(self):
        ## save folders
        if not pathlib.Path.exists(self.saveDir):
            pathlib.Path.mkdir(self.saveDir)
            pathlib.Path.mkdir(self.saveDir.joinpath('cert'))
            pathlib.Path.mkdir(self.saveDir.joinpath('geoDb'))
            pathlib.Path.mkdir(self.saveDir.joinpath('statDb'))
            print("Data directories created")
        #############################################
    
    def init_save_files(self):
        if pathlib.Path.exists(self.saveDir):
            self.saveDir.joinpath('geoDb', 'index.r0b').touch()
            self.saveDir.joinpath('geoDb', 'addresses.r0b').touch()
            self.saveDir.joinpath('statDb', 'index.r0b').touch()
            self.saveDir.joinpath('statDb', 'statistics.r0b').touch()

    def init_install_dirs(self):
        if not pathlib.Path.exists(self.baseDir):
            try:
                pathlib.Path.mkdir(self.baseDir)
                pathlib.Path.mkdir(self.dest['lib'])
                pathlib.Path.mkdir(self.dest['ui'])
                print("Installation directories created")
            except OSError as E:
                print("Error while creating directories: ", E)

    def copy_install_files(self):
        if pathlib.Path.exists(self.baseDir):
            try:
                shutil.copytree(self.source['lib'], self.dest['lib'], dirs_exist_ok=True)
                shutil.copytree(self.source['ui'], self.dest['ui'], dirs_exist_ok=True)
                print("Files copied")
            except OSError as E:
                print("Error while copying files: ", E)


    def install(self, importCert = False):
        input("setup must be run as root!\nPress enter to install")
        ## installation folders    
        print("Bitcoin Core Handler installation in progress...")
        self.init_install_dirs()
        self.copy_install_files()

        self.init_save_dirs()
        self.init_save_files()

        if bool(importCert): self.import_certificate(importCert)
        else: self.create_certificate()
        
        
        
        
def main():
    print("TESTING CLIENT INSTALLER")

    C = Base()
    C.install()


if __name__ == '__main__':
    main()

    