
import subprocess, json, time
import lib.crypto
from lib.storage import Logger

class Commands:
    calls = {'uptime', 'start', 'stop', 'updateall', 'closeconn', 'getblockchaininfo', 'getnetworkinfo', 'getmempoolinfo', 'getmininginfo'}

    @staticmethod
    def encodeCalls(hexCertificate):
        return {lib.crypto.getHashedCommand(call, hexCertificate) : call for call in Commands.calls}

    @staticmethod
    def check(command):
        return command in Commands.calls
    

class DaemonData:
    def __init__(self):
        self.PID = None

        self.startDate = None
        self.uptime = None

        self.blockchainInfo = None
        self.networkInfo = None
        self.mempoolInfo = None
        self.miningInfo = None

    def update(self, jsonData):
        print("data received: ")
        [print(f"{key} : {value}") for key, value in jsonData.items()]
        for key, value in jsonData.items():
            if key == 'uptime':
                self.uptime = int(value)
                self.startTime = int(time.time() - self.uptime)
            elif key == 'chain':
                self.chain = str(value)
            elif key == 'blocks':
                self.blocks == int(value)
            elif key == 'headers':
                self.header = int(value)
            elif key == 'connections_in':
                self.netIN = int(value)
            elif key == 'connections_out':
                self.netOUT = int(value)

    def getAllData(self):
        message = {}
        message['startData'] = self.startDate
        message['uptime'] = self.uptime
        message['blockchainInfo'] = self.blockchainInfo
        message['networkInfo'] = self.networkInfo
        message['mempoolInfo'] = self.mempoolInfo
        message['miningInfo'] = self.miningInfo
        return json.dumps(message)

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
            call = {"uptime": call}
        elif command == 'stop':
            subprocess.run([self.base, "stop"])
            call = {"stop": bool(self.checkDaemon())}
        elif command == 'start':
            subprocess.run(["bitcoind"])
            call = {"start": bool(self.checkDaemon())}
        else:
            call = self.caller(command)
        result = json.dumps(call)
        return result

    

