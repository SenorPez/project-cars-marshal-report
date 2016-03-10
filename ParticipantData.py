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
        self.sector_times = list()

        self.__last_sector = None

    def add_sector_time(self, time, current_sector=None):
        """
        Adds a sector time to the list, if it's unique.
        Note that "current sector" will usually be one sector
        'ahead' due to the way it's presented in the telemetry.
        When the "Sector 1" time is available, current_sector
        will be 2
        """
        try:
            if time != self.sector_times[-1] and \
                    (current_sector != self.__last_sector or \
                    current_sector is None):
                self.sector_times.append(time)
        except IndexError:
            self.sector_times.append(time)

    def merge(self, incoming):
        """
        Merges another participant with this one.
        """
        for sector_time in incoming.sector_times:
            self.add_sector_time(sector_time)

class ParticipantData():
    """
    A class to hold and process field data.
    """
    def __init__(self):
        self.num_participants = None
        self._participants_history = list()
        self._participants = list()

        self.__participant_change = False

        self._temporary_participants = list()

        self.current_lap = 1

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
            self._participants_history.append(
                deepcopy(self.participants))

            if self.num_participants > packet.num_participants:
                #If someone dropped out, we need to set the flag to
                #transfer the data once we get names for everyone in
                #the new configuration.
                self.__participant_change = True
                self.participants = [Participant() \
                    for participant_info in packet.participant_info \
                    if participant_info.is_active][:packet.num_participants]
            self.num_participants = packet.num_participants

        self.current_lap = packet.leader_current_lap
        for index, participant in enumerate(
                packet.participant_info[:self.num_participants]):
            if participant.last_sector_time != -123.0:
                self.participants[index].add_sector_time(
                    participant.last_sector_time,
                    participant.sector)

    @property
    def json_output(self):
        laps = list()
        for i in range(self.current_lap):
            lap_data = dict()
            lap_data['lap_number'] = i
            position_data = list()
            for position, participant in enumerate(self.participants_position):
                position_data.append({'position': position,
                    'name': participant.name})
            lap_data['lap_data'] = position_data
            laps.append(lap_data)

        return laps

    @property
    def participants_position(self):
        return sorted([x for x in self.participants], key=lambda x: x.name)

    @property
    def participants(self):
        if self.__participant_change:
            return self._temporary_participants
        else:
            return self._participants

    @participants.setter
    def participants(self, value):
        if self.__participant_change:
            self._temporary_participants = value
        else:
            self._participants = value

    def combine_data(self, changed):
        combined_participants = list()
        for index, participant in enumerate(
                self.participants[:self.num_participants]):
            if index == changed:
                target_participant = self._participants_history[-1][-1]
            else:
                target_participant = self._participants_history[-1][index]

            target_participant.merge(participant)
            combined_participants.append(target_participant)

        self.__participant_change = False
        self.participants = combined_participants

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
                all([x.name for x in self.participants]):
            #Find where the participants differ.
            previous_names = [x.name for x \
                in self._participants_history[-1]]
            current_names = [x.name for x \
                in self.participants]
            try:
                changed = nonzero([x != y for x, y in zip(
                    previous_names,
                    current_names)])[0]
                #Replace the data of the dropped out person with the
                #participant that was in the last index position.
                self.combine_data(changed)
                    
            except TypeError:
                #The person in the last index is the one who dropped out,
                #so we don't need to do anything.
                raise

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
