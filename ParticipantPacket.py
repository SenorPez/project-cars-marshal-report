"""
Provides a class for the Participant Info Strings output by
Project CARS
"""

from Packet import Packet

class ParticipantPacket(Packet):
    """
    Creates an object from a participant info string packet.

    The participant info string packet has a length of 1347, and is
    packet type 1.
    """
    def __init__(self, packet_data):
        unpacked_data = self.unpack_data(packet_data)

        try:
            self.build_version_number = int(unpacked_data.popleft())

            self.test_packet_type(unpacked_data.popleft())

            self.car_name = str(
                unpacked_data.popleft(),
                encoding='utf-8',
                errors='strict').replace(
                    '\x00',
                    '')
            self.car_class_name = str(
                unpacked_data.popleft(),
                encoding='utf-8',
                errors='strict').replace(
                    '\x00',
                    '')
            self.track_location = str(
                unpacked_data.popleft(),
                encoding='utf-8',
                errors='strict').replace(
                    '\x00',
                    '')
            self.track_variation = str(
                unpacked_data.popleft(),
                encoding='utf-8',
                errors='strict').replace(
                    '\x00',
                    '')

            self.name = list()
            for _ in range(16):
                self.name.append(
                    str(
                        unpacked_data.popleft(),
                        encoding='utf-8',
                        errors='strict').replace(
                            '\x00',
                            ''))

        except ValueError:
            raise

    @property
    def packet_type(self):
        return 1

    @property
    def packet_length(self):
        return 1347

    @property
    def packet_string(self):
        packet_string = "HB64s64s64s64s"
        packet_string += "64s"*16
        packet_string += "64x"

        return packet_string

    def __str__(self):
        return "ParticipantPacket"
