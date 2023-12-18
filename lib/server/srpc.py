



import lib.network
import lib.crypto

class ServerRPC:
    def __init__(self, eventController):
        self.STOP = False
        self.eventController = eventController
        self.netConfig = lib.network.Settings(host = "127.0.0.1", port = 46001)
        self.netServer = lib.network.Server(self.netConfig)


    def waitForCall(self):
        self.netServer.openSocket()
        while not self.STOP:

            self.netServer.receiveClient(lib.crypto.getRandomBytes(16).hex())
            #self.netServer._remoteSock.settimeout(3)
            # self.netServer.socket.settimeout(3)

            if bool(self.netServer._remoteSock):
                stopCall = self.netServer.receiver()
                if bool(stopCall):
                    # print("rpc call to stop server")
                    self.eventController.set()
                    self.STOP = True
            
        # print("closing call received")


