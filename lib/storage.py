

import os, pathlib, time
import lib.settings
import lib.crypto

def getTime():
    return int(time.time())

class Data:
    def __init__(self):
        self.fileCert = lib.settings.BASE_DIR.joinpath("cert.rob")
        self.fileLogs = lib.settings.BASE_DIR.joinpath(f"debug_{getTime()}.log")

        self.certificate = False
    
    def init_files(self):
        if not os.path.exists(lib.settings.BASE_DIR): os.mkdir(lib.settings.BASE_DIR)
        F = open(self.fileCert, "wb")
        F.close()
        F = open(self.fileLogs, "w")
        F.close()
    
    def create_certificate(self):
        with open(self.fileCert, "wb") as F:
            dataBytes = lib.crypto.getRandomBytes(lib.settings.CERT_SIZE)
            F.write(dataBytes)
        
    def load_certificate(self):
        with open(self.fileCert, "rb") as F:
            tmpBytes = F.read()
            self.certificate = lib.crypto.getHash(tmpBytes.hex())

    def check_certificate(self):
        if os.path.exists(self.fileCert):
            self.load_certificate()
            result = True if len(self.certificate) == lib.settings.CERT_SIZE else False
        else:
            result = False
        return result
    

class Logger:
    FILE = False
    SESSION = []

    @staticmethod
    def add(message, *args):
        
        log = str(f"{time.ctime(getTime())} - {message}")
        if args:
            arguments = str([a for a in args])
            log += str(f": {arguments}")
        Logger.SESSION.append(log)
        with open(Logger.FILE, "a") as F:
            F.write(log + "\n")
        print(log)
