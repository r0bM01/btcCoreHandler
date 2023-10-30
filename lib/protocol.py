
import subprocess, json


class Commands:
    authCall = {'getblockchaininfo', 'getnetworkinfo', 'getmempoolinfo', 'getmininginfo'}
    authControl = {'uptime', 'start', 'stop'}

    @staticmethod
    def check(command):
        return command in Commands.authCall or command in Commands.authControl
    


class DaemonData:
    def __init__(self):
        self.startDate = None
        self.uptime = None

        self.chain = None
        self.blocks = None
        self.headers = None

        self.netIN = None
        self.netOUT = None

    def update(self, **kwargs):
        pass


class RPC:
    def __init__(self):
        self.base = "bitcoin-cli"
    
    def caller(self, command, output = True):
        call = subprocess.run([self.base, command], capture_output = output)
        if output: return call.stdout.decode()
         
    def sendCall(self, command):
        if command in Commands.authCall: 
            call = self.caller(command)
            result = json.loads(call)
        elif command == 'uptime':
            call = self.caller(command)
            call = {"uptime": call}
            result = json.loads(call)
        elif command == 'stop':
            self.caller(command, output = False)
        elif command == 'start':
            subprocess(["bitcoind"])

    

