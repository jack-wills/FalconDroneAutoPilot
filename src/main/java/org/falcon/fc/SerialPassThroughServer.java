package org.falcon.fc;

import com.fazecast.jSerialComm.SerialPort;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

public class SerialPassThroughServer extends Thread {
    ServerSocket serverSocket = null;
    Socket socket = null;
    SerialPort serialPort;

    SerialPassThroughServer(SerialPort serialPort) {
        if (!serialPort.isOpen()) {
            serialPort.openPort();
        }
        this.serialPort = serialPort;
    }

    @Override
    public void run() {
        try {
            serverSocket = new ServerSocket(4445);

            PrintWriter serialOut = new PrintWriter(serialPort.getOutputStream(), true);

            while (true) {
                socket = serverSocket.accept();

                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    if (inputLine.equals("keepalive")) {
                        out.println("keepalive");
                        continue;
                    }
                    serialOut.println(inputLine);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
