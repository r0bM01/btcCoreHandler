import lib.server
import lib.client

print("[1] - start server")
print("[2] - start client")

c = int(input(">> "))

if c == 1: lib.server.main()
if c == 2: lib.client.main()

print("program closed")
