package org.falcon.fc;

import com.fazecast.jSerialComm.SerialPort;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.concurrent.BlockingQueue;

public class SerialSendThread extends Thread {
    private static BlockingQueue serialQueue;
    SerialPort serialPort;

    SerialSendThread(SerialPort serialPort, BlockingQueue serialQueue) {
        if (!serialPort.isOpen()) {
            serialPort.openPort();
        }
        this.serialPort = serialPort;
        this.serialQueue = serialQueue;
    }

    @Override
    public void run() {
        PrintWriter serialOut = new PrintWriter(serialPort.getOutputStream(), true);
        String outputLine;
        while (true) {
            if ((outputLine = (String) serialQueue.poll()) != null) {
                serialOut.println(outputLine);
            }
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
