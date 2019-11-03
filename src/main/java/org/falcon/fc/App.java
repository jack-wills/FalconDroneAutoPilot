package org.falcon.fc;

import com.fazecast.jSerialComm.SerialPort;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

/**
 * JavaFX App
 */
public class App  {
    private static BlockingQueue networkSendQueue;
    private static BlockingQueue networkReceiveQueue;
    private static BlockingQueue serialSendQueue;

    public static void main(String[] args) {
        networkSendQueue = new ArrayBlockingQueue(1024);
        networkReceiveQueue = new ArrayBlockingQueue(1024);
        serialSendQueue = new ArrayBlockingQueue(1024);
        SerialPort serialPort = SerialPort.getCommPort("test");

        for (SerialPort s : SerialPort.getCommPorts()) {
            if (s.getDescriptivePortName().equals("STM32 STLink")) {
                serialPort = s;
                break;
            }

        }
        serialPort.openPort();
        serialPort.setBaudRate(115200);
        serialPort.setComPortTimeouts(SerialPort.TIMEOUT_READ_SEMI_BLOCKING, 0, 0);

        Server serverThread = new Server(networkReceiveQueue, serialSendQueue);
        serverThread.setDaemon(true);
        serverThread.start();

        SerialRecieveThread serialRecieveThread = new SerialRecieveThread(serialPort, networkSendQueue);
        serialRecieveThread.setDaemon(true);
        serialRecieveThread.start();

        SerialSendThread serialSendThread = new SerialSendThread(serialPort, serialSendQueue);
        serialSendThread.setDaemon(true);
        serialSendThread.start();

        SerialPassThroughServer serialPassThroughServerThread = new SerialPassThroughServer(serialPort);
        serialPassThroughServerThread.setDaemon(true);
        serialPassThroughServerThread.start();

        NetworkController networkThread = new NetworkController(networkSendQueue);
        networkThread.setDaemon(true);
        networkThread.start();

        while(true);
    }

}