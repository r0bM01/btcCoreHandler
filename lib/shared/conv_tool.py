import time, json, hashlib, pathlib, ipaddress

BASE = pathlib.Path.home().joinpath("handler")


oldGeo = BASE.joinpath("geolocation.rob")
newGeo = BASE.joinpath("geoData.dat")
with open(BASE.joinpath("cert.rob"), "rb") as F:
    certificate = F.read()


def make_alphabet():
    return {chr(n): mini_hash(chr(n)) for n in range(32, 127)}

def string_to_hex(string):
    return [hex(ord(c))[2:] for c in string]

def mini_hash(s, certificate):
    return hashlib.blake2b(s.encode(), digest_size = 2, key = certificate)



def main():
    with open(oldGeo, "rb") as G:
        lines = G.readlines()
    
    PEERS = [json.loads(line[:-1]) for line in lines]

    NEWPEERS = []

    for P in PEERS:
        newPeer = {}
        newPeer['ip'] = ipaddress.ip_address(P['ip']).packed # bytes
        newPeer['countryCode'] = single_byte_hash(string_to_hex(P['country_code2']), certificate) # bytes
        newPeer['countryName'] = single_byte_hash(string_to_hex(P['country_name']), certificate) # bytes
        newPeer['nameLenght'] = bytes.fromhex(hex(len(countryName))[2:]) 
        newPeer['isp'] = single_byte_hash(string_to_hex(P['isp']), certificate) # bytes
        newPeer['ispLenght'] = bytes.fromhex(hex(len(isp))[2:]) 

        NEWPEERS.append(newPeer)
    
    with open(newGeo, "wb") as G:
        for P in NEWPEERS:
            concat = P['ip'] + P['countryCode'] + P['nameLenght'] + P['countryName'] + P['ispLenght'] + P['isp']
            G.write(concat)
           