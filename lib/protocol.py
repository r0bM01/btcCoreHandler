
import subprocess, json, time
import lib.crypto
from lib.storage import Logger

class Commands:
    calls = {'uptime', 'start', 'stop', 'closeconn', 
             'getallinfo', 'getblockchaininfo', 'getnetworkinfo', 
             'getmempoolinfo', 'getmininginfo', 'getpeerinfo'}

    @staticmethod
    def encodeCalls(hexCertificate, handshakeCode):
        return {lib.crypto.getHashedCommand(call, hexCertificate, handshakeCode) : call for call in Commands.calls}

    @staticmethod
    def check(command):
        return command in Commands.calls
    

class DaemonData:
    def __init__(self):
        self.PID = None

        self.uptime = None
        self.blockchainInfo = None
        self.networkInfo = None
        self.mempoolInfo = None
        self.miningInfo = None

        self.peersInfo = None

    def getAllData(self):
        message = {}
        #message['startData'] = self.startDate
        message['uptime'] = self.uptime['uptime']
        message['chain'] = self.blockchainInfo['chain']
        message['headers'] = self.blockchainInfo['headers']
        message['version'] = self.networkInfo['version']
        message['agent'] = self.networkInfo['subversion']
        message['connections'] = self.networkInfo['connections']
        message['transactions'] = self.mempoolInfo['size']
        reply = json.dumps(message)
        return reply

class RPC:
    def __init__(self):
        self.base = "bitcoin-cli"
    
    def checkDaemon(self):
        PID = subprocess.run(["pidof", "bitcoind"], capture_output = True).stdout.decode()
        print(PID)
        if PID != "": PID = int(PID)
        else: PID = False
        return PID

    def getLocalIP(self):
        IP = subprocess.run(["hostname", "I"], capture_output = True).stdout.decode()
        return str(IP)
    
    def caller(self, command):
        call = subprocess.run([self.base, command], capture_output = True)
        return call.stdout.decode()
        
    def runCall(self, command):
        if command == 'uptime':
            call = self.caller(command)
            call = json.dumps({"uptime": int(call)})
        elif command == 'stop':
            subprocess.run([self.base, "stop"])
            call = json.dumps({"stop": bool(self.checkDaemon())})
        elif command == 'start':
            subprocess.run(["bitcoind"])
            call = json.dumps({"start": bool(self.checkDaemon())})
        else:
            call = self.caller(command)
        return call

    

