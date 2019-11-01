# Streaming Client
import socket
import time
from random import randint

HOST = 'localhost'
PORT = 52000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    data = str(randint(0, 9))
    data = "THROTTLE 2345"
    data = "{\"command\": \"gyro_cal\"}"
    s.send(bytes(data, 'utf-8'))
    print(data)
    time.sleep(1)

s.close()
