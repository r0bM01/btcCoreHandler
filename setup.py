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


class Base:
    def __init__(self):
        self.source = {'lib': pathlib.Path.cwd().joinpath('lib'),
                       'ui': pathlib.Path.cwd().joinpath('ui')}
        self.base = pathlib.Path('/usr/lib/btcCoreHandler')
        self.dest = {'lib': self.base.joinpath('lib'),
                     'ui': self.base.joinpath('ui'),
                     'data': pathlib.Path.home().joinpath('./btcCoreHandler')}

class Server(Base):
    def install(self):
        print("Installing server files")
        # creates library folder 
        if not pathlib.Path.exists(self.base):
            pathlib.Path.mkdir(self.base)
        
        # creates folders
        if not pathlib.Path.exists(self.dest['lib']):
            pathlib.Path.mkdir(self.dest['lib'])
        if not pathlib.Path.exists(self.dest['data']):
            pathlib.Path.mkdir(self.dest['data'])
            pathlib.Path.mkdir(self.dest['data'].joinpath('cert'))
            pathlib.Path.mkdir(self.dest['data'].joinpath('geoDb'))
            pathlib.Path.mkdir(self.dest['data'].joinpath('logs'))
        
        # creates directory tree
        try:
            shutil.copytree(self.source['lib'], self.dest['lib'])
        except Error as E:
            print("Error while copying files into the directories!")
            print(E)
            sys.exit()
        
        print("Files correctly installed!")
        

        
        
        
        
        
        

    