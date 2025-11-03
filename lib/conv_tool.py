import time, json, hashlib, pathlib, ipaddress

BASE = pathlib.Path.home().joinpath("handler")
DB = BASE.joinpath("geoDB")
if not pathlib.Path.exists(DB): DB.mkdir()

oldGeo = BASE.joinpath("geolocation.rob")

debug = DB.joinpath("debug.txt")
index = DB.joinpath("index.r0b")
addrs = DB.joinpath("addresses.r0b")

with open(debug, "w") as F:
    pass

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
    return bytes.fromhex(str(hex(len(data))[2:]).zfill(4)) # 2 bytes

def make_value(peerObj):
    
    # separator = str("#").encode()
    
    ip = ipaddress.ip_address(peerObj['ip']).packed # 4 or 16 bytes 
    code = bytes.fromhex(encode_to_cert(peerObj['country_code2'])) # 4 bytes
    country = bytes.fromhex(encode_to_cert(peerObj['country_name'])) # bytes
    isp = bytes.fromhex(encode_to_cert(peerObj['isp'])) # bytes
    value = lenght(ip) + ip + code + lenght(country) + country + lenght(isp) + isp

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
    with open(debug, "a") as D:
        D.write(f"IP: {peerObj['ip']} - Packed: {ipKey} - Hex: {ipKey.hex()}")
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
    
   
    # a = json.loads('{"ip": "95.49.49.210", "country_name": "Poland", "country_code2": "PL", "isp": "Orange Polska Spolka Akcyjna"}')
    # b = json.loads('{"ip": "79.116.55.242", "country_name": "Spain", "country_code2": "ES", "isp": "Digi Spain Telecom S.L.U."}') 

     

if __name__ == '__main__':
    main()