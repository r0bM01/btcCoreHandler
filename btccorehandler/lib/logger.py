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
        self.FILE = dirPath.joinpath(f"debug_{time.strftime('%a_%d_%b_%Y__%H:%M', time.gmtime())}.log")
        self.FILE.touch()


    def verbose_f(self, argument):
        if type(argument) is bool and argument is True:
            arg = "\x1b[1;32m" + str(argument) + "\x1b[0m"
        elif type(argument) is bool and argument is False:
            arg = "\x1b[1;31m" + str(argument) + "\x1b[0m"
        else:
            arg = str(argument)
        return arg

    def add(self, message, *args):
        log = str(f"{time.ctime(int(time.time()))} - {message}: ")
        if args:
            #arguments = str([a for a in args])
            arguments = str([self.verbose_f(a) for a in args])
            log = log + arguments

        with open(self.FILE, "a") as F:
            F.write(log + "\n")

        if self.verbose:
            sys.stdout.write(log + "\n")
            sys.stdout.flush()

            