
import subprocess, json, time


class Commands:
    authCall = {'getblockchaininfo', 'getnetworkinfo', 'getmempoolinfo', 'getmininginfo'}
    authControl = {'uptime', 'start', 'stop'}
    authHandler = {'updateall', 'closeconn'}

    @staticmethod
    def check(command):
        return command in Commands.authCall or command in Commands.authControl
    


class DaemonData:
    def __init__(self):
        self.PID = None

        self.startDate = None
        self.uptime = None

        self.chain = None
        self.blocks = None
        self.headers = None

        self.netIN = None
        self.netOUT = None

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
        message['chain'] = self.chain
        message['blocks'] = self.blocks
        message['header'] = self.headers
        message['netIn'] = self.netIN
        message['netOut'] = self.netOUT
        return json.dumps(message)

class RPC:
    def __init__(self):
        self.base = "bitcoin-cli"
    
    def runCall(self, command):
        if command in Commands.authCall:
            result = self.sendCall(command)
        elif command in Commands.authControl:
            result = self.sendControl(command)
        return result

    def checkDaemon(self):
        PID = subprocess.run(["pidof", "bitcoind"], capture_output = True).stdout.decode()
        print(PID)
        if PID != "": PID = int(PID)
        else: PID = False
        return PID
    
    def caller(self, command):
        call = subprocess.run([self.base, command], capture_output = True)
        return call.stdout.decode()
         
    def sendCall(self, command):
        call = self.caller(command)
        return call
        
    def sendControl(self, command):
        if command == 'uptime':
            call = self.caller(command)
            call = {"uptime": call}
        elif command == 'stop':
            subprocess.run([self.base, "stop"])
            call = {"stop": bool(self.checkDaemon())}
        elif command == 'start':
            subprocess.run(["bitcoind"])
            call = {"start": bool(self.checkDaemon())}
        result = json.dumps(call)
        return result

    

