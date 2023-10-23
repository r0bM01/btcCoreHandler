import lib.network
import json



def main():
    print("btcCoreHandler")
    remoteConn = lib.network.Client()
    remoteConn.connectToServer()
    print(remoteConn)

    try:

        while True:
            command = input("cmd >> ")
            print()

            remoteConn.sendCommand(command)
            result = json.loads(remoteConn.receiveReply())
            for key, value in result.items():
                print(f"{key}: {value}")

    except KeyboardInterrupt:
        remoteConn.sendCommand("closeconn")
        print("closing")
