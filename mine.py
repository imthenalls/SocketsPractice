import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
list_of_clients = []
def accept_wrapper(sock):
    conn,addr = sock.accept()
    list_of_clients.append(conn)
    print(len(list_of_clients))
    print("accepted from",addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:

        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
    if mask & selectors.EVENT_WRITE:
        if data.outb:
           # print('echoing', repr(data.outb), 'to', data.addr)
            if data.outb == b'quit':
                sel.unregister(sock)
                sock.close()
            else:
                data.outb = send_to_all(data.outb, sock)

def send_to_all(message,connection):
    print(len(list_of_clients))
    for clients in list_of_clients:
        sent = clients.send(message)
    message = message[sent:]
    return message

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host,port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock,selectors.EVENT_READ,data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()