import socket, threading, select


from requests import get

class Proto:
    def __init__(self):
        self.remoteSock = False
    #################################################
    def sockSend(self, msg):
        try:
            msgSent = self.remoteSock.send(msg)
        except (OSError, TimeoutError):
            msgSent = 0
        return True if msgSent == len(msg) else False
    
    def sockRecv(self, size):
        try:
            msg = self.remoteSock.recv(int(size))
        except (OSError, TimeoutError):
            msg = b""
        return msg if len(msg) == int(size) else False
    #################################################

    def sender(self, data):
        #data must be already encoded in json
        data = data.encode()
        dataLenght = hex(len(data))[2:].zfill(8)
        dataLenght = bytes.fromhex(dataLenght)
        if self.sockSend(dataLenght) and self.sockSend(data):
            return True
        else:
            self.remoteSock.close()
            self.remoteSock = False
            return False
    
    def receiver(self):
        data = False
        dataLenght = self.sockRecv(4)
        if dataLenght:
            dataLenght = int(dataLenght.hex(), 16)
            data = self.sockRecv(dataLenght)
        if dataLenght and data:
            return data.decode()
        else:
            self.remoteSock.close()
            self.remoteSock = False
            return False

class Client(Proto):
    def __init__(self):
        self.remoteHost = "192.168.1.238"
        self.remotePort = 4600
        self.timeout = 4
        self.isConnected = False
        self.handshakeCode = False

    def connectToServer(self):
        try:
            self.remoteSock = socket.create_connection((self.remoteHost, self.remotePort), timeout = self.timeout)
            #self.remoteSock.settimeout(10)
            self.handshakeCode = self.receiver()
            self.isConnected = True if bool(self.handshakeCode) else False
        except (OSError, TimeoutError):
            self.isConnected = False
            self.remoteSock = False

    def disconnectServer(self):
        self.remoteSock.close()
        self.remoteSock = False
        self.isConnected = False
        self.handshakeCode = False


class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else "192.168.1.238" #socket.gethostbyname(socket.gethostname()) #"192.168.1.238"
        self.port = int(port) if port else 4600

        self.externalIP = False

        self.socketTimeout = 30
        self.remoteSockTimeout = 30
        self.backlog = 1
        self.maxSockets = 1


class Server(Proto):
    def __init__(self, settings):
        self.settings = settings
        self.socket = False

    def openSocket(self):
        try:
            self.socket = socket.create_server((self.settings.host, self.settings.port), family = socket.AF_INET,
                                               backlog = self.settings.backlog, reuse_port = True)
            self.socket.settimeout(self.settings.socketTimeout)
        except OSError:
            self.socket = False


    def receiveClient(self, handshakeCode):
        try:
            self.remoteSock, addr = self.socket.accept()
            self.remoteSock.settimeout(self.settings.remoteSockTimeout)
            self.sender(handshakeCode)
        except OSError:
            self.remoteSock = False
        


