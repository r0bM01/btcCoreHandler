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

import platform, json
from collections import Counter
from lib.shared.network import Utils


class Bitcoin:
    def __init__(self):
        self.PID = None

        self.uptime = None

        self.blockchainInfo = None
        self.networkInfo = None
        self.mempoolInfo = None
        self.miningInfo = None
        self.nettotalsInfo = None
        self.peersInfo = None
        self.connectedInfo = None # peersInfo + geolocation

    def getStatusInfo(self):
        message = {}
        #message['startData'] = self.startDate
        message['uptime'] = self.uptime['uptime']
        message['chain'] = self.blockchainInfo['chain']
        message['blocks'] = self.blockchainInfo['blocks']
        message['headers'] = self.blockchainInfo['headers']
        message['verificationprogress'] = self.blockchainInfo['verificationprogress']
        message['pruned'] = self.blockchainInfo['pruned']
        message['size_on_disk'] = self.blockchainInfo['size_on_disk']

        message['version'] = self.networkInfo['version']
        message['subversion'] = self.networkInfo['subversion']
        message['protocolversion'] = self.networkInfo['protocolversion']
        message['connections'] = self.networkInfo['connections']
        message['connections_in'] = self.networkInfo['connections_in']
        message['connections_out'] = self.networkInfo['connections_out']
        message['localservicesnames'] = self.networkInfo['localservicesnames']
        message['networks'] = self.networkInfo['networks']
        message['relayfee'] = self.networkInfo['relayfee']

        message['totalbytessent'] = self.nettotalsInfo['totalbytessent']
        message['totalbytesrecv'] = self.nettotalsInfo['totalbytesrecv']

        message['difficulty'] = self.miningInfo['difficulty']
        message['networkhashps'] = self.miningInfo['networkhashps']

        message['size'] = self.mempoolInfo['size']
        # message['bytes'] = self.mempoolInfo['bytes']
        message['usage'] = self.mempoolInfo['usage']
        message['mempoolminfee'] = self.mempoolInfo['mempoolminfee']
        message['fullrbf'] = self.mempoolInfo['fullrbf']
        return message
    
    def getSinglePeerInfo(self, peerID):
        for p in self.peersInfo:
            if str(peerID) == p['id']: message = p
        return message


class IPGeolocation:
        def __init__(self):
            #self.GEODATA = list()
            self.INDEX = False # index loaded with ipkey and relative file position
            self.FILES = False # Object accessing the database
    
        def loadDatabase(self):
            self.INDEX = self.FILES.load_database()

        def getGeolocation(self, ip):
            geoData = json.loads(Utils.getGeolocation(ip))
            key = self.FILES.make_key(Utils.getPackedIp(ip))
            filePos = self.FILES.set_value(geoData)
            self.INDEX[key] = filePos
            return geoData

        def updateDatabase(self, peersInfo, LOGGER):
            for peer in peersInfo:
                ip = peer['addr'].split(":")[0]
                if not self.isKnown(ip):
                    geoData = self.getGeolocation(ip)
                    LOGGER.add("new peer found", geoData['ip'], geoData['country_name'])
                key = self.FILES.make_key(Utils.getPackedIp(ip))
                rawData = self.FILES.get_value(self.INDEX[key])
                peer['country_name'] = rawData['country_name']
                peer['country_code'] = rawData['country_code']
                peer['isp'] = rawData['isp']
            return peersInfo #it returns the same list updated with geolocation data
                
        def isKnown(self, ip):
            return self.FILES.make_key(Utils.getPackedIp(ip)) in self.INDEX
        
        def getFromDatabase(self, ip):
            return self.FILES.get_value_by_ip(ip)
            


class Machine:
    dataInfo = {}
    dataInfo['node'] = platform.node()
    dataInfo['machine'] = platform.machine()
    dataInfo['system'] = platform.system()
    dataInfo['release'] = platform.release()