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


import pathlib, time, sys


class Logger:
    def __init__(self, dirPath, verbose = False):
        self.verbose = verbose
        self.FILE = dirPath.joinpath(f"log_{time.strftime('%a_%d_%b_%Y__%H:%M', time.gmtime())}.log")
        self.FILE.touch()

    def write_on_disk(self, log, arg_list):
        if args:
            log += ": " + str([a for a in args])
        with open(self.FILE, "a") as F:
            F.write(log + "\n")

    def verbose_print(self, log, arg_list):
        for a in arg_list:
            if type(a) is bool and a is True:
                log += "[" + "\x1b[1;32m" + str(a) + "\x1b[0m" + "]"
            elif type(a) is bool and a is False:
                log += "[" + "\x1b[1;31m" + str(a) + "\x1b[0m" + "]"
            else:
                log += "[" + str(a) + "]"
        print(log)

    def add(self, message, *args):
        log = str(f"{time.ctime(int(time.time()))} - {message} ") 
        self.write_on_disk(log, args)
        if self.verbose:
            self.verbose_print(log, args)
        

            
            

            