

import tomllib
from core import server


def main():
    print("bitcoin Core Handler is starting...")

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    
    handler = server.Controller(config)

    if handler.interface.daemon.is_running:

        handler.init_network()
        handler.init_services()    
        handler.run_all()
        handler.wait_for_shutdown()
        
    else:
        print("ERROR! BITCOIN DAEMON NOT RUNNING!")


if __name__ == "__main__":
    main()
