import lib.shared.network

C = lib.shared.network.Client()
C.remoteHost = "127.0.0.1"
C.remotePort = 46001

C.connectToServer()
print(C.handshakeCode)

input("\npress enter to stop server")
C.sender("stopdaemon")


