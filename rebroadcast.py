from glob import glob
import socket
import sys
from time import sleep

from natsort import natsorted

UDP_IP = "255.255.255.255"
UDP_PORT = 5606

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

for a in natsorted(glob(sys.argv[1]+'pdata*')):
    with open(a, 'rb') as packet_file:
        print(a)
        packet_data = packet_file.read()
        SOCKET.sendto(packet_data, (UDP_IP, UDP_PORT))
        #sleep(1/100)
