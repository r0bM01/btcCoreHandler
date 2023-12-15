import socket

S = socket.create_connection(("127.0.0.1", 46001))
input("press enter to stop server")
S.send(b"figaaa")