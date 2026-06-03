

import time
from core import server
from core import data

def main():
    print("testing btcCoreHandler")
    handler = server.Controller()

    handler.init_network()
    handler.init_services()

    time.sleep(2)

    handler.run_all()

    time.sleep(5)


    
    print("now printing some cached info")
    time.sleep(3)
    print(f"Cache last round: {handler.data_interface.cache_timestamp}")

    print("A little bit of this system: ")
    print(handler.data_interface.system)
    
    time.sleep(1)

    print("Some cache: ")
    print("Cache size: ", len(handler.data_interface.cache))
    print("Saved cache: ", handler.data_interface.cache.keys())

    handler.graceful_shutdown()

    print("all closed")



if __name__ == "__main__":
    main()