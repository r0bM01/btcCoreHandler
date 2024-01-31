import time, json, hashlib, pathlib, ipaddress

BASE = pathlib.Path.home().joinpath("handler")
DB = BASE.joinpath("geoDB")
DB.mkdir()

oldGeo = BASE.joinpath("geolocation.rob")


index = DB.joinpath("index.r0b")
addrs = DB.joinpath("addresses.r0b")


with open(index, "wb") as F:
    pass

with open(addrs, "wb") as F:
    pass

with open(BASE.joinpath("cert.rob"), "rb") as F:
    CERT = F.read()


def make_dictionary():
    return {chr(n): mini_hash(chr(n)) for n in range(32, 127)}

def encode_to_cert(string):
    hexstring = string.encode().hex()
    return "".join([ALPHA[c] for c in hexstring])

def mini_hash(char):
    return hashlib.blake2b(char.encode(), digest_size = 2, key = CERT).hexdigest()

def make_key(data):
    return hashlib.blake2b(data, digest_size = 8, key = CERT)

def lenght(data):
    #data already in bytes
    return bytes.fromhex(str(hex(len(data))[2:]).zfill(2))

def make_value(peerObj):
    # 4 bytes (IP) + 4 bytes (CODE) + 1 byte (Country Lenght) + (COUNTRY) + 1 byte (Isp Lenght) + (ISP)
    ip = ipaddress.ip_address(peerObj['ip']).packed # bytes 
    code = bytes.fromhex(encode_to_cert(peerObj['country_code2'])) # bytes
    country = bytes.fromhex(encode_to_cert(peerObj['country_name'].lower())) # bytes
    isp = encode_to_cert(peerObj['isp'].lower()) # hex
    value = ip + code + lenght(country) + country + lenght(isp) + isp
    return value

def write_value(value):
    # value already bytes
    with open(addr, "ab") as F:
        pos = F.tell()
        F.write(value)
    return bytes.fromhex(str(hex(pos)[2:]).zfill(8))

def set_value(peerObj):
    ipKey = make_key(ipaddress.ip_address(peerObj['ip']).packed)
    filePos = write_value(make_value(peerObj))
    with open(index, "ab") as F:
        F.write(ipKey)
        F.write(filePos)

def load_database():
    # 8 bytes for IP key
    # 4 bytes for file position
    INDEX = {}
    with open(index, "rb") as F:
        data = True
        while data:
            data = F.read(12) #reads 12 bytes
            if bool(data):
                key = data.hex()[:16]
                INDEX[key] = data.hex()[16:24]
    return INDEX


ALPHA = {chr(n): mini_hash(chr(n)) for n in range(32, 127)}


def main():
    with open(oldGeo, "rb") as G:
        lines = G.readlines()
    
    PEERS = [json.loads(line[:-1]) for line in lines]
    print(f"loaded {len(PEERS)} peers objects")
    print("writing into the database")
    [set_value(p) for p in PEERS]
    print("done!")

    input("press enter to check database")
    db = load_database()
    print(f"There are {len(db)} entries")

    input("press enter to close conversion")
     


           