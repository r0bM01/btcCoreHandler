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
        message['networkactive'] = self.networkInfo['networkactive']
        message['relayfee'] = self.networkInfo['relayfee']

        message['totalbytessent'] = self.nettotalsInfo['totalbytessent']
        message['totalbytesrecv'] = self.nettotalsInfo['totalbytesrecv']

        message['size'] = self.mempoolInfo['size']
        message['bytes'] = self.mempoolInfo['bytes']
        message['usage'] = self.mempoolInfo['usage']
        message['mempoolminfee'] = self.mempoolInfo['mempoolminfee']
        message['fullrbf'] = self.mempoolInfo['fullrbf']
        return message
    
    def getSinglePeerInfo(self, peerID):
        for p in self.peersInfo:
            if str(peerID) == p['id']: message = p
        return message

class IPGeolocation:
        knownNodes = list()
        connectedNodes = list()
        knwownCountries = list()
    
        @staticmethod
        def updateList(nodeList):
            IPGeolocation.connectedNodes = []
            for nodeip in nodeList:
                if not IPGeolocation.isKnown(nodeip):
                    nodeGeodata = json.loads(Utils.getGeolocation(nodeip))
                    IPGeolocation.knownNodes.append(nodeGeodata)
                else:
                    nodeGeodata = IPGeolocation.getKnownData(nodeip)
                if nodeGeodata['country_name'] not in IPGeolocation.knwownCountries:
                    IPGeolocation.knwownCountries.append(nodeGeodata['country_name'])
                
                IPGeolocation.connectedNodes.append(nodeGeodata)

        @staticmethod
        def isKnown(nodeip):
            return any(node['ip'] == nodeip for node in IPGeolocation.knownNodes)
        
        @staticmethod
        def getKnownData(nodeip):
            if IPGeolocation.isKnown(nodeip):
                return [node for node in IPGeolocation.knownNodes if node['ip'] == nodeip][0]
        
        @staticmethod
        def getConnectedCountries():
            connectedCountries = [nodeGeodata['country_name'] for nodeGeodata in IPGeolocation.connectedNodes]
            counted = [{'country': country, 'counts': connectedCountries.count(country)} for country in IPGeolocation.knwownCountries]
            return [country for country in counted if country['counts'] != 0]

class Machine:
    dataInfo = {}
    dataInfo['node'] = platform.node()
    dataInfo['machine'] = platform.machine()
    dataInfo['system'] = platform.system()
    dataInfo['release'] = platform.release()