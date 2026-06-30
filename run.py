
import core.env


def main():
    from core import server
    
    handler = server.Controller()
    handler.logger.base_logger.verbose = False

    if handler.interface.daemon.is_running:

        handler.init_network()
        handler.init_services()    
        handler.run_all()
        handler.wait_for_shutdown()
        print("btcCoreHandler shutdown successfull")
    else:
        print("ERROR! BITCOIN DAEMON NOT RUNNING!")


if __name__ == "__main__":
    if core.env.check_config():
        main()
    else:
        assert "CONFIG FILE NOT READABLE!!"
    
