

import time
from core import server
from core import data
from threading import Event

def main():
    print("#### testing btcCoreHandler")
    waiter = Event()
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
    for x in range(40):
        print(f"{40 - x}", sep=".", end="\r", flush=True)
        waiter.wait(1)

    
    print("Len Geo: ", len(handler.data_interface.cache['getpeergeo']))

    waiter.wait(2)
    for ip in handler.data_interface.cache['getpeergeo']:
        print(f"IP: {ip} »= COUNTRY: {handler.data_interface.cache['getpeergeo'][ip].get('country_code')}")

    waiter.wait(2)
    print("#### Services deactivation")
    
    handler.SERVICES.worker.set()

    waiter.wait(2)
    handler.graceful_shutdown()

    print("#### all closed")



if __name__ == "__main__":
    main()