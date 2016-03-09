"""
Provides a class for the storing and management of participant data.
"""

from copy import deepcopy

from numpy import nonzero

class Participant():
    """
    A class to represent a race participant.
    """
    def __init__(self):
        self.name = None

class ParticipantData():
    """
    A class to hold and process field data.
    """
    def __init__(self):
        self.num_participants = None
        self._participants_history = list()
        self.participants = list()

        self.__participant_change = False

        self.__temporary_participants = list()

    def add(self, packet):
        """
        Adds a new data packet.
        """
        if packet.packet_type == 0:
            self.__telemetry_packet(packet)
        elif packet.packet_type == 1:
            self.__participant_packet(packet)
        elif packet.packet_type == 2:
            self.__participant_packet(packet)
        else:
            raise ValueError("Unknown packet type: {}".format(
                packet.packet_type))

    def __telemetry_packet(self, packet):
        if self.num_participants is None and \
                packet.num_participants != -1:
            self.num_participants = packet.num_participants
            self.participants = [Participant() \
                for participant_info in packet.participant_info \
                if participant_info.is_active][:self.num_participants]
        elif self.num_participants != packet.num_participants and \
                packet.num_participants != -1:  
            if self.num_participants > packet.num_participants:
                #If someone dropped out, we need to set the flag to
                #transfer the data once we get names for everyone in
                #the new configuration.
                self.num_participants = packet.num_participants
                self._participants_history.append(
                    deepcopy(self.participants))
                self.__temporary_participants = [Participant() \
                    for participant_info in packet.participant_info \
                    if participant_info.is_active][:self.num_participants]
                self.__participant_change = True
            else:
                self.num_participants = packet.num_participants
                self._participants_history.append(
                    deepcopy(self.participants))
                self.participants = [Participant() \
                    for participant_info in packet.participant_info \
                    if participant_info.is_active][:self.num_participants]


    def __participant_packet(self, packet):
        if self.num_participants is None:
            raise ValueError("Packet order error.")
        elif packet.packet_type == 1:
            participant_names = packet.name
            for participant in self.participants[:16]:
                participant.name = participant_names.pop(0)
        elif packet.packet_type == 2:
            participant_names = packet.name
            for participant \
                    in self.participants[packet.offset:packet.offset+16]:
                participant.name = participant_names.pop(0)

        #Test to see if we have names for everyone, and we have a pending
        #change.
        if self.__participant_change and \
                all([x.name for x in self.__temporary_participants]):
            #Find where the participants differ.
            previous_names = [x.name for x \
                in self.participants_history[-1]]
            current_names = [x.name for x \
                in self.__temporary_participants]
            try:
                changed = nonzero([x != y for x, y in zip(
                    previous_names,
                    current_names)])[0]
                #Replace the data of the dropped out person with the
                #participant that was in the last index position.
                self.participants[changed] = \
                    self.participants_history[-1]
                    
            except TypeError:
                #The person in the last index is the one who dropped out,
                #so we don't need to do anything.
                pass
            self.__participant_change = False

    @property
    def participants_history(self):
        return self._participants_history + [self.participants]

    '''
    def link_telemetry(self, telemetry_data):
        """
        Links a Telemetry Data object with the Participant Data
        """
        self.telemetry_data = telemetry_data

    def add(self, participant_data):
        """
        Adds a participant data packet to the Participant Data
        """
        self.new_participants.extend([x for x in participant_data.name \
            if len(x)])

        if self.telemetry_data.participants is not None and \
                len(self.new_participants) >= \
                    self.telemetry_data.participants:
            try:
                if self.new_participants != \
                        self.participant_history[-1]:
                    raise IndexError
            except IndexError:
                self.participant_history.append(
                    self.new_participants)

                

            finally:
                self.reset_participants()

    def reset_participants(self):
        """
        Resets the building list of new participants.
        """
        self.new_participants = list()

    @property
    def participants(self):
        """
        List of current participants.
        """
        try:
            return self.participant_history[-1]
        except IndexError:
            return list()

class LapData():
    """
    A class to hold each participant's lap data.
    """
    def __init__(self, lap_number):
        self.lap_number = lap_number
        self.valid_lap = True
        
        self.s1_time = None
        self.s2_time = None
        self.s3_time = None
        self.lap_time = None
        self.valid_lap_time = None

    def add_sector_time(self, sector, time):
        if sector == 1:
            self.s1_time = time
        elif sector == 2:
            self.s2_time = time
        elif sector == 3:
            self.s3_time = time
            self.lap_time = sum((
                self.s1_time,
                self.s2_time,
                self.s3_time))
            self.valid_lap_time = self.lap_time \
                if self.valid_lap else None

    def invalidate_lap(self):
        self.valid_lap = False
'''
