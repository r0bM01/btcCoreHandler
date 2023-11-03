
import os, pathlib

#[HOME DIRECTORY]
HOME = pathlib.Path.home()
BASE_DIR = HOME.joinpath("handler")

#[CERTIFICATE]
CERT_SIZE = 512 #bytes
#CERT_VALIDITY = 60 * 60 * 24 