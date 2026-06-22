

import tomllib
from core import server


def main():
    print("####################################")

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    
    handler = server.Controller(config)

    if handler.interface.daemon.is_running:

        handler.init_network()
        handler.init_services()

        try:
            handler.run_all()
            handler.wait_for_shutdown()
        except Exception as e:
            print(f"Handler cannot be run due to error: {e}")
            print("####################################")

    else:
        print("ERROR! BITCOIN DAEMON NOT RUNNING!")


if __name__ == "__main__":
    main()
