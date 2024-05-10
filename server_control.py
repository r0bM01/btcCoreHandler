import lib.network
import time, subprocess

C = lib.network.ClientRPC()


C.connect()

input("\npress enter to stop server")



C.sender("handlerstop")

print("server stopping...wait")
time.sleep(2)
stop = subprocess.run(["pidof", "python3"], capture_output = True).stdout.decode()
print(stop)

