"""
Provides classes to create a Marshal Report
"""
import argparse
import datetime
from glob import glob
import json
import os
import socket

from natsort import natsorted

from AdditionalParticipantPacket import AdditionalParticipantPacket
from ParticipantData import ParticipantData
from ParticipantPacket import ParticipantPacket
from TelemetryData import TelemetryData
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

        self.participant_data = ParticipantData()

        if telemetry is None:
            #Create a new UDP socket.
            pcars_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM)
            pcars_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1)

            #Bind the socket to the port
            server_address = ("", self.udp_port)
            print("Starting listener on port {}".format(
                server_address[1]))
            pcars_socket.bind(server_address)

            try:
                while True:
                    data, _ = pcars_socket.recvfrom(65565)
                    if save:
                        self.__save_packet(data)

                    self.__process_telemetry_packet(data)
            except KeyboardInterrupt:
                print("Closing listenter on port {}".format(
                    server_address[1]))
            finally:
                if self.save_index == 0 and save:
                    os.rmdir(self.save_directory_name)

        else:
            self.__process_telemetry_directory(
                os.path.realpath(telemetry))

    def __save_packet(self, packet):
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

    def __process_telemetry_directory(self, telemetry_directory):
        for packet in natsorted(glob(telemetry_directory+'/pdata*')):
            with open(packet, 'rb') as packet_file:
                packet_data = packet_file.read()

            self.__process_telemetry_packet(packet_data)

    def __process_telemetry_packet(self, packet):
        if len(packet) == 1347:
            self.__dispatch(ParticipantPacket(packet))
        elif len(packet) == 1028:
            self.__dispatch(AdditionalParticipantPacket(
                packet))
        elif len(packet) == 1367:
            self.__dispatch(TelemetryDataPacket(packet))

        fp = open('output.json', 'w')
        json.dump(self.participant_data.json_output,
            fp,
            ensure_ascii=True,
            sort_keys=True)

    def __dispatch(self, packet):
        self.participant_data.add(packet)
        '''
        if packet.packet_type == 0:
            self.__telemetry_packet(packet)
        elif packet.packet_type == 1:
            self.__participant_packet(packet)
        elif packet.packet_type == 2:
            self.__participant_packet(packet)
        '''

    def __telemetry_packet(self, packet):
        """
        Adds a new telemetry packet into the telemetry data for
        the race
        """
        self.telemetry_data.add(packet)

    def __participant_packet(self, packet):
        """
        Adds a new participant packet into the participant data for
        the race
        """
        self.participant_data.add(packet)

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

    MARSHAL_REPORT = MarshalReport(
        telemetry=ARGUMENTS.telemetry,
        save=ARGUMENTS.save_packets)
