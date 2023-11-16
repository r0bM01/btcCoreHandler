import socket, threading, select, time, struct


from requests import get

class Proto:
    _remoteSock = False
    _bufferSize = 1024
    _opTimeout = 2
    
    def sockClosure(self):
        self._remoteSock.shutdown(socket.SHUT_RDWR)
        self._remoteSock.close()
        self._remoteSock = False

    #################################################
    def sockSend(self, msg):
        try:
            msgSent = self._remoteSock.send(msg, socket.MSG_WAITALL)
        except (OSError, TimeoutError):
            msgSent = 0
        return True if msgSent == len(msg) else False
    
    def sockRecv(self, size):
        try:
            msg = self._remoteSock.recv(int(size))
        except (OSError, TimeoutError):
            msg = b""
        return msg if len(msg) == int(size) else False
    #################################################
    def highSend(self, data):
        tmpTimeout = self._remoteSock.gettimeout()
        self._remoteSock.settimeout(self._opTimeout)
        chunks = [data[c:c+self._bufferSize] for c in range(0, len(data), self._bufferSize)]
        for c in chunks:
            if self.sockSend(c) and bool(self.sockRecv(1)):
                #time.sleep(0.1)
                flag = True
            else:
                flag = False
                break
        self._remoteSock.settimeout(tmpTimeout)
        return flag
        
    def highRecv(self, size):
        tmpTimeout = self._remoteSock.gettimeout()
        self._remoteSock.settimeout(self._opTimeout)
        bytesRecv = 0
        dataArray = []
        while bytesRecv < size:
            if size - bytesRecv > self._bufferSize:
                chunk = self.sockRecv(self._bufferSize)
            else: 
                chunk = self.sockRecv(size - bytesRecv)
            if bool(chunk):
                self.sockSend(b"1")
                dataArray.append(chunk)
                flag = True
            else:
                #self._remoteSock.send(b"0")
                flag = False
                break
            bytesRecv += len(chunk)
        self._remoteSock.settimeout(tmpTimeout)
        if flag:
            data = bytes()
            for d in dataArray:
                data += d
            return data
        else:
            return False

    def sender(self, data):
        #data must be already encoded in json
        data = data.encode()
        dataLenght = hex(len(data))[2:].zfill(8)
        dataLenght = bytes.fromhex(dataLenght)
        dataSent = False
        if self.sockSend(dataLenght):
            if len(data) > self._bufferSize:
                dataSent = self.highSend(data)
            else:
                dataSent = self.sockSend(data)
        if dataSent:
            self._remoteSock.settimeout(self)
            return True
        else:
            #self._remoteSock.close()
            #self._remoteSock = False
            self.sockClosure()
            return False
    
    def receiver(self):
        #self._remoteSock.settimeout(30)
        dataLenght = self.sockRecv(4)
        if dataLenght:
            dataLenght = int(dataLenght.hex(), 16)
            if dataLenght > self._bufferSize:
                data = self.highRecv(dataLenght)
            else:
                data = self.sockRecv(dataLenght)
        if dataLenght and data:
            return data.decode()
        else:
            #self._remoteSock.close()
            #self._remoteSock = False
            self.sockClosure()
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
            self._remoteSock = socket.create_connection((self.remoteHost, self.remotePort), timeout = self.timeout)
            #self._remoteSock.settimeout(10)
            self.handshakeCode = self.receiver()
            self.isConnected = True if len(self.handshakeCode) == 32 else False
        except (OSError, TimeoutError):
            self.isConnected = False
            self._remoteSock = False

    def disconnectServer(self):
        #self._remoteSock.close()
        #self._remoteSock = False
        self.sockClosure()
        self.isConnected = False
        self.handshakeCode = False


class Settings:
    def __init__(self, host = False, port = False):
        self.host = str(host) if host else "192.168.1.238" #socket.gethostbyname(socket.gethostname()) #"192.168.1.238"
        self.port = int(port) if port else 4600

        self.externalIP = False

        self.socketTimeout = 30
        self.remoteSockTimeout = 15
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
            self._remoteSock, addr = self.socket.accept()
            self._remoteSock.settimeout(self.settings.remoteSockTimeout)
            self.sender(handshakeCode)
        except OSError:
            self._remoteSock = False
        


