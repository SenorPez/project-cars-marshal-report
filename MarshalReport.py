"""
Provides classes to create a Marshal Report
"""
import argparse
import datetime
from glob import glob
import os
import socket

from natsort import natsorted

from AdditionalParticipantPacket import AdditionalParticipantPacket
from ParticipantPacket import ParticipantPacket
from TelemetryDataPacket import TelemetryDataPacket

class MarshalReport():
    """
    Creates an object to create the Marshal Report from Project
    CARS Telemetry Data.
    """
    def __init__(self, telemetry, save):
        self.save_index = 0
        self.save_directory_name = "packetdata-"+\
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        if telemetry is None:
            #Create a new UDP socket.
            pcars_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM)

            #Bind the socket to the port
            server_address = ("", self.udp_port)
            print("Starting listener on port {}".format(
                server_address[1]))
            pcars_socket.bind(server_address)

            try:
                while True:
                    data, _ = pcars_socket.recvfrom(65565)
                    if save:
                        self._save_packet(data)

                    self._process_telemetry_packet(data)
            except KeyboardInterrupt:
                print("Closing listenter on port {}".format(
                    server_address[1]))
            finally:
                if self.save_index == 0 and save:
                    os.rmdir(self.save_directory_name)

        else:
            self._process_telemetry_directory(telemetry)

    def _save_packet(self, packet):
        if not os.path.exists(self.save_directory_name):
            os.makedirs(self.save_directory_name)
        packet_file = open("./"+self.save_directory_name+"/pdata"+\
            str(self.save_index), 'wb')
        packet_file.write(packet)
        packet_file.close()
        self.save_index += 1

    @property
    def udp_port(self):
        """
        Defines the UDP port Project CARS broadcasts to.
        """
        return 5606

    def _process_telemetry_directory(self, telemetry_directory):
        for packet in natsorted(glob(telemetry_directory+'pdata*')):
            self._process_telemetry_packet(packet)

    @staticmethod
    def _process_telemetry_packet(packet):
        with open(packet, 'rb') as packet_file:
            packet_data = packet_file.read()
            if len(packet_data) == 1347:
                packet_object = ParticipantPacket(packet_data)
            elif len(packet_data) == 1028:
                packet_object = AdditionalParticipantPacket(
                    packet_data)
            elif len(packet_data) == 1367:
                packet_object = TelemetryDataPacket(packet_data)
        print(packet_object)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Project CARS Marshal Report")
    PARSER.add_argument(
        '-v',
        '--version',
        action='version',
        version='Version 0.1')
    PARSER.add_argument(
        '-s',
        '--save-packets',
        dest='save_packets',
        action='store_true',
        help='save telemetry packets for future analysis')
    PARSER.add_argument('telemetry', nargs='?')

    ARGUMENTS = PARSER.parse_args()

    MarshalReport(
        telemetry=ARGUMENTS.telemetry,
        save=ARGUMENTS.save_packets)
