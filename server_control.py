import lib.shared.network

C = lib.shared.network.ClientRPC()
C.remoteHost = "127.0.0.1"
C.remotePort = 46001

C.connect()

input("\npress enter to stop server")
C.sender("handlerstop")

while True:
    result = C.receiver()
    if not bool(result) or result == 'handlerstopped':
        break
    else:
        print(result)



