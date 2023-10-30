

import os, pathlib
import lib.settings

class Data:
    def __init__(self):
        self.fileCert = lib.settings.BASE_DIR.joinpath("cert.rob")
        self.fileLogs = lib.settings.BASE_DIR.joinpath("debug.log")

        self.certificate = False
    
    def create_certificate(self, dataBytes):
        with open(self.fileCert, "wb") as F:
            F.write(dataBytes)
        
    def load_certificate(self):
        with open(self.fileCert, "rb") as F:
            self.certificate = F.read()

    def check_certificate(self):
        if os.path.exists(self.fileCert):
            self.load_certificate()
            result = True if len(self.certificate) == lib.settings.CERT_SIZE else False
        else:
            result = False
        return result