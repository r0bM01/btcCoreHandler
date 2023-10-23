import socket, threading, select


from requests import get

class Client:
    def __init__(self):
        self.remoteHost = "192.168.1.238"
        self.remotePort = 4600

        self.remoteSock = False

    def connectToServer(self):
        try:
            self.remoteSock = socket.create_connection((self.remoteHost, self.remotePort))
            self.remoteSock.settimeout(10)

        except OSError:
            self.remoteSock = False


    def disconnectServer(self):
        self.remoteSock.close()
        self.remoteSock = False

    def sendMessage(self, cmd):
        print(cmd)
        commandLenght = hex(len(cmd.encode("utf-8")))[2:]
        commandLenght = commandLenght.zfill(8)
        print(commandLenght)
        self.remoteSock.send(bytes.fromhex(commandLenght))
        self.remoteSock.send(cmd.encode("utf-8"))

    def receiveReply(self):
        replyLenght = int(self.remoteSock.recv(4).hex(), 16)
        reply = self.remoteSock.recv(replyLenght).decode("utf-8")
        return reply

class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else socket.gethostbyname(socket.gethostname()) #"192.168.1.238"
        self.port = int(port) if port else 4600

        self.externalIP = False

        self.socketTimeout = 3
        self.backlog = 5
        self.maxSockets = 1
        self.handCode = "268b6d4f8dc014fe24c389c32d54bb95"

class Peer:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.auth_level = 0

class Manager:
    def __init__(self):
        self.connected = []

    def addNew(self, peer):
        self.connected.append(peer)

class Server:
    def __init__(self, settings):
        self.settings = settings

        self.socket = False

        self.manager = Manager()

    def openSocket(self):
        try:
            self.socket = socket.create_server((self.settings.host, self.settings.port), backlog = self.settings.backlog, reuse_port = True)
            self.socket.settimeout(self.settings.socketTimeout)
        except OSError:
            self.socket = False
            print("server socket problem")

    def getNewPeer(self):
        try:
            peer, addr = self.socket.accept()
            flag = True
        except OSError:
            flag = False
        return peer if flag else flag

    def receiveCommand(self, peer):
        commandLenght = int(peer.recv(4).hex(), 16) #receive 4 bytes indicating lenght for next message
        command = peer.recv(commandLenght).decode('utf-8')
        return command

    def sendReply(self, peer, data):
        #data = data.encode("utf-8")
        dataLenght = hex(len(data))[2:]
        dataLenght = dataLenght.zfill(8)
        peer.send(bytes.fromhex(dataLenght))
        peer.send(data)


    #not implemented yet
    def peerAuthentication(self, peer):
        return True

    """
    def getExternalIP(self):
        externalIP = get('https://api.ipify.org').text
        return externalIP
    """
