import lib.network
import lib.crypto
import json



def main():
    print("btcCoreHandler")
    remoteConn = lib.network.Client()
    remoteConn.connectToServer()
    print(remoteConn)

    try:

        while True:
            command = input("cmd >> ")
            command = lib.crypto.getHashedCommand(command, "fega")
            print(command)

            remoteConn.sender(command)
            result = json.loads(remoteConn.receiver())
            for key, value in result.items():
                print(f"{key}: {value}")

    except KeyboardInterrupt:
        remoteConn.sendCommand("closeconn")
        print("closing")
