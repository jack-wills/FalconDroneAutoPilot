import serial
import threading
import queue
import time
from time import sleep
import random
import socket
import json
from magCal import magnetometerCalibration

serial_sem = threading.Semaphore()

def read_and_print(ser):
    while(1):
        if ser.readable():
            print(ser.readline())

def serial_pass_through(ser):
    HOST = 'localhost'
    PORT = 8081

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print('Client connection accepted ' + str(addr))
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    raise socket.error
                serial_sem.acquire()
                ser.write(data.encode())
                sleep(0.02)
                serial_sem.release()
            except socket.error as msg:
                print('Client connection closed' + str(addr))
                break
    conn.close()

def read_server(serverQueue):
    HOST = 'localhost'
    PORT = 52000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print('Client connection accepted ' + str(addr))
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    raise socket.error
                print(data)
                json_data = json.loads(data)
                json_data['addr'] = str(addr)
                serverQueue.put(json_data)
            except socket.error as msg:
                print('Client connection closed' + str(addr))
                break
            except json.decoder.JSONDecodeError as err:
                print("Invalid JSON recieved")
                pass
    
    conn.close()

def write_to_ser(ser, serialQueue):
    while 1:
        while(serialQueue.qsize() <= 0):
            pass    
        string = serialQueue.get()
        serial_sem.acquire()
        ser.write(string.encode())
        print(string.encode())
        sleep(0.02)
        serial_sem.release()

def main():
    print("\n-------Start------\n")
    
    #open serial port
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port =  '/dev/tty.SLAB_USBtoUART'
    ser.timeout = 25
    ser.open()
    sleep(0.5)    
    print("Serial port opened.")

    serial_read_thread = threading.Thread(target=read_and_print, args=(ser,), daemon=True)
    serial_read_thread.start()
    serverQueue = queue.Queue()
    serialQueue = queue.Queue()

    read_server_thread = threading.Thread(target=read_server, args=(serverQueue,), daemon=True)
    read_server_thread.start()
    
    write_to_ser_thread = threading.Thread(target=write_to_ser, args=(ser, serialQueue,), daemon=True)
    write_to_ser_thread.start()
    
    serial_pass_through_thread = threading.Thread(target=serial_pass_through, args=(ser,), daemon=True)
    serial_pass_through_thread.start()
    
    while 1:
        while(serverQueue.qsize() <= 0):
            pass   
        json_data = serverQueue.get()
        try:
            if (json_data["command"] == "gyro_cal"):
                serialQueue.put("GYROCALINIT true")
            if (json_data["command"] == "mag_cal"):
                serialQueue.put("MAGCALINIT true")
                serialQueue.put(magnetometerCalibration(ser))
        except KeyError:
            print("Invalid Request")
            pass

            


        


if __name__ == '__main__':
    main()