import lib.server
import lib.client

print("[1] - start server")
print("[2] - start client")
print("[3] - start GUI")

c = int(input(">> "))

if c == 1: lib.server.main()
if c == 2: lib.client.main()
if c == 3: import ui.main

print("program closed")
