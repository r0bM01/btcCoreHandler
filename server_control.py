import lib.shared.network

C = lib.shared.network.ClientRPC()
C.remoteHost = "127.0.0.1"
C.remotePort = 46001

C.connect()


input("\npress enter to stop server")
C.sender("handlerstop")


