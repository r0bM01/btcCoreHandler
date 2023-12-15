


class ServerRPC:
    def __init__(self, socketObject, eventController):
        self.RPC = socketObject
        self.RPC.openSocket()
        self.rpcClient = None
        self.STOP = False
        self.eventController = eventController
    
    def waitForCall(self):
        while not self.STOP:
            try:
                self.RPC.socket.settimeout(None)
                self.rpcClient, addr = self.RPC.socket.accept()
                self.rpcClient.settimeout(180)
            except OSError:
                self.STOP = True
            
            try:
                command = self.rpcClient.recv(4)
                if bool(command):
                    print("rpc call to stop server")
                    self.eventController.set()
                    self.STOP = True

            except OSError:
                print("SRPC ERROR!")
                self.STOP = True
            
        


