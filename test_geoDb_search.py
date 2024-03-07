

import ipaddress, pathlib

import lib.shared.storage
import lib.server.data


def makeGeoObj(geoData):
    geoObj = {"ip": geoData['ip'], "country_code2": geoData['country_code'], "country_name": geoData['country_name'], "isp": geoData['isp']}
    return geoObj

storage = lib.shared.storage.Server()
storage.init_certificate()
geoData = lib.server.data.IPGeolocation()


storage.init_geolocation()

geoNewDir = storage.saveDirs['geoDb'].joinpath('geoNew')
geoNewDir.mkdir(exist_ok = True)

geoOld = lib.shared.storage.Geolocation(storage.certificate, storage.saveDirs['geoDb'])
geoOld.database = geoOld.load_database()

geoNew = lib.shared.storage.Geolocation(storage.certificate, geoNewDir)
geoNew.index.touch(exist_ok = True)
geoNew.addrs.touch(exist_ok = True)

#geoData.FILES = storage.geolocation
#geoData.loadDatabase()

print(f"old database: {len(geoOld.database)} entries")
print("starting copy")


errors = []
counter = 0
for key in geoOld.database:
    try:    
        data = geoOld.get_value(geoOld.database[key])
        geoNew.set_value(makeGeoObj(data))
        counter += 1
    except KeyError:
        errors.append((counter, key.hex()))
        
print(f"Found {len(errors)} errors")


geoNew.database = geoNew.load_database()
print(f"new database: {len(geoNew.database)}")

print("loading data handler")
dataHandler = lib.server.data.IPGeolocation()
dataHandler.FILES = geoNew
dataHandler.loadDatabase()

print("Geolocation DB search Test")
while True:
    text = str(input("search >> ")).lower()
    if text == 'quit': break
    results = dataHandler.search(text)
    print(f"Found: {len(results)} results")
    if input("press 's' to show results >> ") == "s":
        for x in results:
            print(x)
    else:
        print()

print("closing")