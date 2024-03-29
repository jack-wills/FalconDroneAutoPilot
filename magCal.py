import serial
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import linalg
from time import sleep
import numpy as np

def fitEllipsoid(magX, magY, magZ):
    a1 = np.square(magX)
    a2 = np.square(magY)
    a3 = np.square(magZ)
    a4 = 2 * np.multiply(magY, magZ)
    a5 = 2 * np.multiply(magX, magZ)
    a6 = 2 * np.multiply(magX, magY)
    a7 = 2 * magX
    a8 = 2 * magY
    a9 = 2 * magZ
    a10 = np.ones(len(magX)).T
    D = np.array([a1, a2, a3, a4, a5, a6, a7, a8, a9, a10])

    # Eqn 7, k = 4
    C1 = np.array([[-1, 1, 1, 0, 0, 0],
                   [1, -1, 1, 0, 0, 0],
                   [1, 1, -1, 0, 0, 0],
                   [0, 0, 0, -4, 0, 0],
                   [0, 0, 0, 0, -4, 0],
                   [0, 0, 0, 0, 0, -4]])

    # Eqn 11
    S = np.matmul(D, D.T)
    S11 = S[:6, :6]
    S12 = S[:6, 6:]
    S21 = S[6:, :6]
    S22 = S[6:, 6:]

    # Eqn 15, find eigenvalue and vector
    # Since S is symmetric, S12.T = S21
    invC1 = np.linalg.inv(C1)
    invS22 = np.linalg.inv(S22)
    tmp = np.matmul(invC1, S11 - np.matmul(S12, np.matmul(invS22, S21)))
    eigenValue, eigenVector = np.linalg.eig(tmp)
    u1 = eigenVector[:, np.argmax(eigenValue)]

    # Eqn 13 solution
    u2 = np.matmul(-np.matmul(np.linalg.inv(S22), S21), u1)

    # Total solution
    u = np.concatenate([u1, u2]).T

    Q = np.array([[u[0], u[5], u[4]],
                  [u[5], u[1], u[3]],
                  [u[4], u[3], u[2]]])

    n = np.array([[u[6]],
                  [u[7]],
                  [u[8]]])

    d = u[9]

    return Q, n, d

def magnetometerCalibration(ser):
    magXList = []
    magYList = []
    magZList = []

    magX = np.array(magXList)
    magY = np.array(magYList)
    magZ = np.array(magZList)

    count = 0

    while(count < 1000):
        if ser.readable():
            data = ser.readline().decode("utf-8").split(' ')
            identifier = data[0]
            if identifier == "MAGCAL" and len(data) == 4:
                magneX = float(data[1])
                magneY = float(data[2])
                magneZ = float(data[3])
                print("X: "+str(magneX)+", Y: "+str(magneY)+", Z: "+str(magneZ))
                magX = np.append(magX, magneX)
                magY = np.append(magY, magneY)
                magZ = np.append(magZ, magneZ)
                count += 1

    print("Data Collected")

    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111, projection='3d')

    ax1.scatter(magX, magY, magZ, s=5, color='r')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')

    # plot unit sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax1.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
    ax1.plot_surface(x, y, z, alpha=0.3, color='b')

    Q, n, d = fitEllipsoid(magX, magY, magZ)

    Qinv = np.linalg.inv(Q)
    b = -np.dot(Qinv, n)
    Ainv = np.real(1 / np.sqrt(np.dot(n.T, np.dot(Qinv, n)) - d) * linalg.sqrtm(Q))

    print("A_inv: ")
    print(Ainv)
    print()
    print("b")
    print(b)
    print()

    string = 'MAGCALVAL ' + str(b[0][0]) + ' ' + str(b[1][0]) + ' ' + str(b[2][0]) + ' ' + str(Ainv[0][0]) + ' ' + str(Ainv[0][1]) + ' ' + str(Ainv[0][2]) + ' ' + str(Ainv[1][0]) + ' ' + str(Ainv[1][1]) + ' ' + str(Ainv[1][2]) + ' ' + str(Ainv[2][0]) + ' ' + str(Ainv[2][1]) + ' ' + str(Ainv[2][2]) + '\n'
    return string