


import tomllib
import pathlib

def check_config():
    return DEFAULT_CONFIG_FILE.exists()

def dump_config():
    lines = []
    lines.append("# btcCoreHandler Config File Automatically Generated #\n\n")
    lines.append("[storage]\n")
    lines.append(f"data_folder = '{str(DEFAULT_DATA_FOLDER)}'\n\n")
    lines.append("[network]\n")
    lines.append(f"host = '{DEFAULT_HANDLER_HOST}'\n")
    lines.append(f"port = '{DEFAULT_HANDLER_PORT}'\n\n")
    lines.append("[bitcoin]\n")
    lines.append(f"host = '{DEFAULT_BTCDAEMON_HOST}'\n")
    lines.append(f"port = '{DEFAULT_BTCDAEMON_PORT}'\n")
    lines.append("user = ''\n")
    lines.append("pass = ''\n")
    DEFAULT_CONFIG_FILE.touch()
    with open(DEFAULT_CONFIG_FILE, "w") as f:
        [f.write(line) for line in lines]

def load_config():
    with open(DEFAULT_CONFIG_FILE, "rb") as f:
        config_data = tomllib.load(f)
    return config_data

### DEFAULT VALUES
DEFAULT_CONFIG_FILE = pathlib.Path.cwd().parents[0].joinpath("config.toml")
DEFAULT_ROOT_FOLDER = pathlib.Path.home()
DEFAULT_DATA_FOLDER = DEFAULT_ROOT_FOLDER.joinpath("btcCoreHandlerData")
DEFAULT_LOGS_FOLDER = DEFAULT_DATA_FOLDER.joinpath("logs")
DEFAULT_STORAGE_FOLDER = DEFAULT_DATA_FOLDER.joinpath("storage")

DEFAULT_HANDLER_HOST = "0.0.0.0"
DEFAULT_HANDLER_PORT = "46850"

DEFAULT_BTCDAEMON_HOST = "127.0.0.1"
DEFAULT_BTCDAEMON_PORT = "8332"
### END OF DEFAULT VALUES


### CONFIG FILE CREATION AND LOAD
if not DEFAULT_CONFIG_FILE.exists():
    dump_config()

config = load_config()

storage = config.get('storage', dict())
network = config.get('network', dict())
bitcoin = config.get('bitcoin', dict())
nextcloud = config.get('nextcloud', dict())
### CONFIG LOADED


### IMPORTS
DATA_FOLDER = storage.get('data_folder', DEFAULT_DATA_FOLDER)

HANDLER_HOST = network.get('host', DEFAULT_HANDLER_HOST)
HANDLER_PORT = network.get('port', DEFAULT_HANDLER_PORT)

BTCDAEMON_HOST = bitcoin.get('host', DEFAULT_BTCDAEMON_HOST)
BTCDAEMON_PORT = bitcoin.get('post', DEFAULT_BTCDAEMON_PORT)
BTCDAEMON_USER = bitcoin.get('user', None)
BTCDAEMON_PASS = bitcoin.get('pass', None)

NEXTCLOUD_USER = nextcloud.get('user', False)
NEXTCLOUD_PASS = nextcloud.get('pass', False)
NEXTCLOUD_CHAT = nextcloud.get('chat', False)