package org.falcon.fc;

import com.fazecast.jSerialComm.SerialPort;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;

public class SerialRecieveThread extends Thread {
    private static BlockingQueue networkQueue;
    SerialPort serialPort;

    SerialRecieveThread(SerialPort serialPort, BlockingQueue networkQueue) {
        if (!serialPort.isOpen()) {
            serialPort.openPort();
        }
        this.serialPort = serialPort;
        this.networkQueue = networkQueue;
    }

    @Override
    public void run() {
        try {
            BufferedReader in = new BufferedReader(new InputStreamReader(this.serialPort.getInputStream(),"UTF-8"));
            String inputLine;
            while (true) {
                inputLine = in.readLine();
                networkQueue.put(inputLine);
                Thread.sleep(100);
            }
        } catch (IOException|InterruptedException e) {
            e.printStackTrace();
        }
    }
}
