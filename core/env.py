


import tomllib
import pathlib

DEFAULT_CONFIG_FILE = pathlib.Path.cwd().joinpath("config.toml")

with open("config.toml", "rb") as f:
    config = tomllib.load(f)


storage = config.get('storage', False)
network = config.get('network', False)
bitcoin = config.get('bitcoin', False)

DEFAULT_ROOT_FOLDER = storage.get('default_folder', pathlib.Path.home())
DEFAULT_DATA_FOLDER = DEFAULT_ROOT_FOLDER.joinpath("btcCoreHandlerData")

DEFAULT_HOST = network.get('host', "0.0.0.0") 
DEFAULT_PORT = network.get('port', 46850)

BTCDAEMON_HOST = bitcoin.get('host', "127.0.0.1")
BTCDAEMON_PORT = bitcoin.get('post', 8332)
BTCDAEMON_USER = bitcoin.get('user', None)
BTCDAEMON_PASS = bitcoin.get('pass', None)

