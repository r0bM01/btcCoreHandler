import lib.network
import lib.crypto
import json






def main():
    print("btcCoreHandler")
    remoteConn = lib.network.Client()
    remoteConn.connectToServer()
    print(remoteConn)
    print(remoteConn.handshakeCode)

    try:

        while True:
            command = input("cmd >> ")
            hashed = lib.crypto.getHashedCommand(command, "fefa", remoteConn.handshakeCode)
            print(command)

            remoteConn.sender(hashed)
            if command == "closeconn": 
                break
            result = json.loads(remoteConn.receiver())
    
            for key, value in result.items():
                print(f"{key}: {value}")

    except KeyboardInterrupt:
        remoteConn.sender("closeconn")
        print("closing")
