import socket
import sys
import cv2
import cv
import numpy

UDP_IP = "127.0.0.1"  # "171.64.161.62"  # this is this machine's IP address
UDP_PORT = 21234


def main():

    # create the opencv window
    cv.NamedWindow('test', 1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        msg, addr = sock.recvfrom(30720)  # buffer size is 4096 bytes
        print "received message with length " + str(len(msg))

        data = numpy.fromstring (msg, dtype=numpy.uint8)

        image = cv2.imdecode(data, 0)
        cv2.imshow('test', image)
        cv2.waitKey(10)


if __name__ == "__main__":
    main()
