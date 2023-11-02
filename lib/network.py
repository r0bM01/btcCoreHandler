import socket, threading, select


from requests import get

class Proto:
    def __init__(self):
        self.remoteSock = False

    def sender(self, data):
        #data must be already encoded in json
        data = data.encode()
        dataLenght = hex(len(data))[2:].zfill(8)
        self.remoteSock.send(bytes.fromhex(dataLenght))
        self.remoteSock.send(data)
    
    def receiver(self):
        dataLenght = self.remoteSock.recv(4)
        if dataLenght != b"":
            dataLenght = int(dataLenght.hex(), 16)
            data = self.remoteSock.recv(dataLenght).decode()
            return data
        else:
            self.remoteSock.close()
            self.remoteSock = False


class Client(Proto):
    def __init__(self):
        self.remoteHost = "192.168.1.238"
        self.remotePort = 4600

    def connectToServer(self):
        try:
            self.remoteSock = socket.create_connection((self.remoteHost, self.remotePort))
            self.remoteSock.settimeout(10)

        except OSError:
            self.remoteSock = False

    def disconnectServer(self):
        self.remoteSock.close()
        self.remoteSock = False


class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else "192.168.1.238" #socket.gethostbyname(socket.gethostname()) #"192.168.1.238"
        self.port = int(port) if port else 4600

        self.externalIP = False

        self.socketTimeout = 30
        self.backlog = 5
        self.maxSockets = 1


class Server(Proto):
    def __init__(self, settings):
        self.settings = settings
        self.socket = False

    def openSocket(self):
        try:
            self.socket = socket.create_server((self.settings.host, self.settings.port), backlog = self.settings.backlog, reuse_port = True)
            self.socket.settimeout(self.settings.socketTimeout)
        except OSError:
            self.socket = False
            print("server socket problem")

    def receiveClient(self):
        try:
            self.remoteSock, addr = self.socket.accept()
        except OSError:
            self.remoteSock = False
        


