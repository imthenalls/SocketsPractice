#!/usr/bin/env python3

import sys
import socket
import selectors
import types
# 127.0.0.1 65432
sel = selectors.DefaultSelector()
messages = []

def service_connection(key, mask):
    socke = key.fileobj

    if mask & selectors.EVENT_READ:
        recv_data = socke.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data))

    if mask & selectors.EVENT_WRITE:
        sending = input().encode()
        if sending == b'quit':
            print('quiting')
            print("sending", repr(sending))
            sent = socke.send(sending)  # Should be ready to write
            sel.unregister(sock)
            sock.close()
        else:
            print("sending", repr(sending))
            sent = socke.send(sending)  # Should be ready to write

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1:3]
server_addr = (host, int(port))

print("starting connection to", server_addr)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(server_addr)
sock.setblocking(False)

events = selectors.EVENT_READ | selectors.EVENT_WRITE
sel.register(sock, events,)
try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()