import time, json, hashlib, pathlib, ipaddress

BASE = pathlib.Path.home().joinpath("handler")
DB = BASE.joinpath("geoDB")
if not pathlib.Path.exists(DB): DB.mkdir()

oldGeo = BASE.joinpath("geolocation.rob")


index = DB.joinpath("index.r0b")
addrs = DB.joinpath("addresses.r0b")


with open(index, "wb") as F:
    pass

with open(addrs, "wb") as F:
    pass

with open(BASE.joinpath("cert.rob"), "rb") as F:
    CERT = F.read()

ALPHA = {chr(n): hashlib.blake2b(chr(n).encode(), digest_size = 2, key = CERT).hexdigest() for n in range(32, 127)}
BETA = {hashlib.blake2b(chr(n).encode(), digest_size = 2, key = CERT).hexdigest() : chr(n) for n in range(32, 127)}


def encode_to_cert(string):
    return "".join([ALPHA[c] for c in string])

def mini_hash(char):
    return hashlib.blake2b(char.encode(), digest_size = 2, key = CERT).hexdigest()

def make_key(data):
    return hashlib.blake2b(data, digest_size = 8, key = CERT).digest()

def lenght(data):
    #data already in bytes
    return bytes.fromhex(str(hex(len(data))[2:]).zfill(4))

def make_value(peerObj):
    # 4 bytes (IP) + 4 bytes (CODE) + 2 byte (Country Lenght) + (COUNTRY) + 2 byte (Isp Lenght) + (ISP)
    separator = str("#").encode()

    ip = ipaddress.ip_address(peerObj['ip']).packed + separator# bytes 
    code = bytes.fromhex(encode_to_cert(peerObj['country_code2'])) + separator # bytes
    country = bytes.fromhex(encode_to_cert(peerObj['country_name'].lower())) + separator# bytes
    isp = bytes.fromhex(encode_to_cert(peerObj['isp'].lower())) # bytes
    value = ip + code + country + isp

    return lenght(value) + value

def write_value(value):
    # value already bytes
    with open(addrs, "ab") as F:
        pos = F.tell()
        F.write(value)
    return bytes.fromhex(str(hex(pos)[2:]).zfill(8)) # 4 bytes

def set_value(peerObj):
    ipKey = make_key(ipaddress.ip_address(peerObj['ip']).packed)
    filePos = write_value(make_value(peerObj))
    with open(index, "ab") as F:
        F.write(ipKey)
        F.write(filePos)

def load_database():
    # 8 bytes for IP key
    # 4 bytes for file position
    
    with open(index, "rb") as F:
        data = F.read() #reads 12 bytes
    print("new DB read: ", len(data))
    INDEX = { data[x:x+8] : data[x+8:x+12] for x in range(0, len(data), 12) }
    return INDEX




def main():
    with open(oldGeo, "rb") as G:
        lines = G.readlines()
    
    PEERS = [json.loads(line[:-1]) for line in lines]
    print(f"loaded {len(PEERS)} peers objects")
    print("writing into the database")


    [set_value(p) for p in PEERS]
        
    print("done!", )

    input("press enter to check database")

    db = load_database()
    
    found = 0
    missing = 0
    for p in PEERS:
        if make_key(ipaddress.ip_address(p['ip']).packed) in db:
            found += 1
        else:
            missing += 1
    
    print(f"Found: {found}")
    print(f"Missing: {missing}")
    # a = json.loads('{"ip": "95.49.49.210", "country_name": "Poland", "country_code2": "PL", "isp": "Orange Polska Spolka Akcyjna"}')
    # b = json.loads('{"ip": "79.116.55.242", "country_name": "Spain", "country_code2": "ES", "isp": "Digi Spain Telecom S.L.U."}') 

    
    input("press enter to close conversion")
     

if __name__ == '__main__':
    main()