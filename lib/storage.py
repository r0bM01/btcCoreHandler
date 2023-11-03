

import os, pathlib, time
import lib.settings
import lib.crypto

class Data:
    def __init__(self):
        self.fileCert = lib.settings.BASE_DIR.joinpath("cert.rob")
        self.fileLogs = lib.settings.BASE_DIR.joinpath(f"debug_{time.time()}.log")

        self.certificate = False
    
    def init_logs(self):
        with open(self.fileLogs, "w") as F:
            F.write()
    
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
        arguments = str([a for a in args])
        log = str(f"{time.time()} - {message} : {arguments}")
        Logger.SESSION.append(log)
        with open(FILE, "w") as F:
            F.write(log + "\n")
        print(log)
