

import time, tomllib
from core import server
from threading import Event
from pprint import pp

def main():
    print("#### testing btcHandler started")

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    

    waiter = Event(config)
    handler = server.Controller()

    waiter.wait(2)
    handler.init_network()
    handler.init_services()

    waiter.wait(2)
    handler.run_all()


    waiter.wait(5)
    handler.SERVICES.deactivate_all()
    print("#### now printing some cached info")
    
    waiter.wait(2)
    print(f"Cache last round: {time.ctime(handler.data_interface.cache_timestamp)}")
    
    waiter.wait(2)
    print("Cache size: ", len(handler.data_interface.cache))
    print("Saved cache: ", handler.data_interface.cache.keys())


    waiter.wait(2)
    print("#### Lets wait a little bit to get geolocation data")
    for x in range(0, 40):
        print("   ", end = "\r", flush = True)
        print(f"{40 - x}", sep=".", end="\r", flush=True)
        waiter.wait(1)

    
    print("Len Geo: ", len(handler.data_interface.cache['getpeergeo']))

    waiter.wait(2)
    for ip in handler.data_interface.cache['getpeergeo']:
        print(f"IP: {ip} »» COUNTRY: {handler.data_interface.cache['getpeergeo'][ip].get('country_code')}")


    print("lets try to get something out of the database")
    ip = input("insert ip: ")
 
    foo = handler.data_interface.database.select_geolocation([ip])
    print(foo)

    waiter.wait(2)
    print("#### Services deactivation")
    
    handler.SERVICES.worker.set()

    waiter.wait(2)
    handler.graceful_shutdown()

    print("#### all closed")



if __name__ == "__main__":
    main()