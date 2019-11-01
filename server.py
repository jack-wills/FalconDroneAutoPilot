# Streaming Server
import socket
import time
from random import randint


while True:
    conn, addr = s.accept()
    print('Client connection accepted ' + str(addr))
    while True:
        try:
            data = conn.recv(1024)
            if (data == ''):
                raise socket.error
            print ("Server recieved:" + str(data))
        except socket.error, msg:
            print('Client connection closed' + str(addr))
            break

conn.close()