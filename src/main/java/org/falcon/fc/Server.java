package org.falcon.fc;

import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;

public class Server extends Thread {
    private static BlockingQueue networkQueue;
    private BlockingQueue serialQueue;
    ServerSocket serverSocket = null;
    Socket socket = null;

    Server(BlockingQueue networkQueue, BlockingQueue serialQueue) {
        this.networkQueue = networkQueue;
        this.serialQueue = serialQueue;
    }

    @Override
    public void run() {
        try {

            serverSocket = new ServerSocket(4443);

            while (true) {
                socket = serverSocket.accept();

                PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    if (inputLine.equals("keepalive")) {
                        out.println("keepalive");
                        continue;
                    }
                    JSONObject json = new JSONObject(inputLine);
                    try {
                        switch (json.getString("command")) {
                            case "gyro_cal":
                                serialQueue.put("GYROCALINIT true");
                                break;
                            case "mag_cal":
                                serialQueue.put("MAGCALINIT true");
                                //Start daemon
                                break;
                            default:
                                System.out.println("Server Received: " + inputLine);
                                break;
                        }
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
