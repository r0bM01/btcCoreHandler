import json, time, subprocess
import lib.network
import lib.commands


def main():
    ENV = lib.network.Settings()
    server = lib.network.Server(ENV)
    server.openSocket()

    if server.socket:
        print(time.ctime(time.time()))
        print("Server started")
        try:
            while True:
                peer = server.getNewPeer()
                if peer:
                    print("Client connected")
                    setRunning = True
                    while setRunning:
                        request = server.receiveCommand(peer)
                        print("Received command: ", request)
                        if request != "closeconn":
                            result = subprocess.run(["bitcoin-cli", request], capture_output = True)
                            reply = result.stdout
                            server.sendReply(peer, reply)
                        else:
                            setRunning = False
        except KeyboardInterrupt:
            print("Server stopped")







