import hashlib, pathlib, ipaddress

BASE = pathlib.Path.home().joinpath("handler")
DB = BASE.joinpath("geoDB")

index = DB.joinpath("index.r0b")
addrs = DB.joinpath("addresses.r0b")

with open(BASE.joinpath("cert.rob"), "rb") as F:
    CERT = F.read()

ALPHA = {hashlib.blake2b(chr(n).encode(), digest_size = 2, key = CERT).hexdigest() : chr(n) for n in range(32, 127)}

def decode_with_cert(string):
    return "".join([string[c:c+4] for c in range(0, len(string), 4)])

def load_database():
    with open(index, "rb") as F:
        dbTemp = F.read()
    dbTemp = dbTemp.hex()
    db = { dbTemp[x:x+16] : dbTemp[x+16:x+24] for x in range(0, len(dbTemp), 24) }
    return db

def read_value(filePos):
    with open(addrs, "rb") as F:
        F.seek(int(filePos, 16))
        ip_ccode = F.read(8)
        
