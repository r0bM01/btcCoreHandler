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

def make_key(data):
    return hashlib.blake2b(data, digest_size = 8, key = CERT).digest()

def load_database():
    with open(index, "rb") as F:
        dbTemp = F.read()
    dbTemp = dbTemp.hex()
    db = { dbTemp[x:x+16] : dbTemp[x+16:x+24] for x in range(0, len(dbTemp), 24) }
    return db

def read_value(filePos):
    with open(addrs, "rb") as F:
        F.seek(int(filePos, 16))
        size = F.read(4)
        data = F.read(int(size.hex(), 16))
    return data

def get_value(addr):
    ipKey = make_key(ipaddress.ip_address(addr).packed)
    index = load_database()
    if ipKey in index:
        value = read_value(index[ipKey])
        value = value.split(b"#")
        result = {'ip': ipaddress.ip_address(value[0]).exploded,
               'country_code2': decode_with_cert(value[1].hex()),
               'country_name': decode_with_cert(value[2].hex()), 
               'isp': decode_with_cert(value[3].hex()) }
    else: 
        result = {"error": "value not found!"}
    return result    
        

def main():
    print("Test tool")
    while True:
        addr = input("IP addr or 'exit'\n>> ")
        if addr.lower() == 'exit': break
        value = get_value(addr)
        if 'error' in value:
            print(value['error'])
        else:
            [print(value[p]) for p in value]