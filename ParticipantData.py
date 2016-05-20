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
        self.race_positions = list()
        self.sector_times = list()

        self._position = None

        self.__last_sector = None
        self.__add_position = False
        self.__add_starting_position = True

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position

    def add_race_position(self, lap_number, race_position):
        self.race_position = race_position

    def add_sector_time(self, time, current_sector, race_position, invalid):
        """
        Adds a sector time to the list, if it's unique.
        Note that "current sector" will usually be one sector
        'ahead' due to the way it's presented in the telemetry.
        When the "Sector 1" time is available, current_sector
        will be 2
        """
                        
        if race_position != 0:
            if time == -123.0 and len(self.sector_times) == 0:
                self.sector_times.append({
                    'time': 0.00,
                    'position': race_position,
                    'sector': "Start",
                    'invalid': None})
            elif time == -123.0 and len(self.sector_times) >= 1:
                pass
            else:
                if current_sector != self.__last_sector:
                    self.__last_sector = current_sector
                    current_sector = 3 if current_sector == 1 \
                        else current_sector-1
                    self.sector_times.append({
                        'time': time,
                        'position': race_position,
                        'sector': current_sector,
                        'invalid': bool(invalid)})

    def position_by_lap(self, lap):
        try:
            if lap == 0:
                return self.sector_times[0]['position']
            else:
                index = lap*3
                return self.sector_times[index]['position']
        except IndexError:
            return None

    def sector_by_lap(self, lap, sector):
        try:
            if lap == 0:
                return None
            else:
                index = sector+(lap-1)*3
                return self.sector_times[index]['time']
        except IndexError:
            return None

    def invalid_lap(self, lap):
        try:
            if lap == 0:
                return None
            else:
                index = 1+(lap-1)*3
                data = [x['invalid'] for x in self.sector_times[index:index+3]]
                return any(data)
        except IndexError:
            return None

    def merge(self, incoming):
        """
        Merges another participant with this one.
        """

        for sector_time in incoming.sector_times:
            self.sector_times.append(sector_time)

            if sector_time['sector'] == "Start":
                self.__last_sector = None
            else:
                self.__last_sector = sector_time['sector']%3+1

            self.add_sector_time(
                sector_time['time'],
                sector_time['sector'],
                sector_time['position'],
                sector_time['invalid'])

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
        self.laps_in_event = packet.laps_in_event
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
        try:
            for index, participant in enumerate(
                    packet.participant_info[:self.num_participants]):
                self.participants[index].position = participant.race_position
                self.participants[index].add_sector_time(
                    participant.last_sector_time,
                    participant.sector,
                    participant.race_position,
                    participant.invalid_lap)
        except IndexError:
            #TODO: Create temporary storage?
            pass

    @property
    def json_output(self):
        output = dict()
        output['laps'] = list()
        output['drivers'] = list()

        for i in range(min((
                self.laps_in_event,
                self.current_lap))+1):
            lap_data = dict()
            lap_data['lap_number'] = i

            best_sector_1 = None
            best_sector_2 = None
            best_sector_3 = None
            best_lap_time = None
            lap_data['positions'] = list()

            for participant in self.participants_by_position(i):
                try:
                    sector_1 = participant.sector_by_lap(i, 1)
                    if best_sector_1 is None or \
                            sector_1 < best_sector_1:
                        best_sector_1 = sector_1
                except TypeError:
                    sector_1 = None

                try:
                    sector_2 = participant.sector_by_lap(i, 2)
                    if best_sector_2 is None or \
                            sector_2 < best_sector_2:
                        best_sector_2 = sector_2
                except TypeError:
                    sector_2 = None

                try:
                    sector_3 = participant.sector_by_lap(i, 3)
                    if best_sector_3 is None or \
                            sector_3 < best_sector_3:
                        best_sector_3 = sector_3
                except TypeError:
                    sector_3 = None

                try:
                    lap_time = sum((sector_1, sector_2, sector_3))
                    if best_lap_time is None or \
                            sum((sector_1, sector_2, sector_3)) < best_lap_time:
                        best_lap_time = sum((sector_1, sector_2, sector_3))
                except TypeError:
                    lap_time = None

                lap_data['positions'].append({
                    'name': participant.name,
                    'position': participant.position_by_lap(i),
                    'sector_1': sector_1,
                    'sector_2': sector_2,
                    'sector_3': sector_3,
                    'lap_time': lap_time,
                    'invalid_lap': participant.invalid_lap(i)})
                
            lap_data['positions'] = sorted(
                [x for x in lap_data['positions'] \
                    if x['position'] is not None],
                key=lambda x: x['position'])
            lap_data['best_sector_1'] = best_sector_1
            lap_data['best_sector_2'] = best_sector_2
            lap_data['best_sector_3'] = best_sector_3
            lap_data['best_lap_time'] = best_lap_time

            output['laps'].append(lap_data)

        for participant in self.participants_by_name():
            participant_data = dict()
            participant_data['driver'] = participant.name
            participant_data['position'] = participant.position

            try:
                participant_data['best_sector_1'] = min(
                    [x['time'] for x in participant.sector_times \
                        if x['sector'] == 1 and \
                        not x['invalid']])
            except ValueError:
                participant_data['best_sector_1'] = None

            try:
                participant_data['best_sector_2'] = min(
                    [x['time'] for x in participant.sector_times \
                        if x['sector'] == 2 and \
                        not x['invalid']])
            except ValueError:
                participant_data['best_sector_2'] = None

            try:
                participant_data['best_sector_3'] = min(
                    [x['time'] for x in participant.sector_times \
                        if x['sector'] == 3 and \
                        not x['invalid']])
            except ValueError:
                participant_data['best_sector_3'] = None

            try:
                data = [None if x['invalid'] else x['time'] \
                    for x in participant.sector_times \
                    if x['sector'] == 1 or \
                    x['sector'] == 2 or \
                    x['sector'] == 3]
                data = [sum(y) for y in \
                    [list(x) for x in zip(
                        *[iter(data)]*3)] \
                    if y.count(None) == 0]
                participant_data['best_lap_time'] = min(data)
            except ValueError:
                participant_data['best_lap_time'] = None

            participant_data['laps'] = list()
            for i in range(min((
                    self.laps_in_event,
                    self.current_lap))+1):
                lap_data = dict()
                lap_data['lap_number'] = i

                sector_1 = participant.sector_by_lap(i, 1)
                lap_data['sector_1'] = sector_1

                sector_2 = participant.sector_by_lap(i, 2)
                lap_data['sector_2'] = sector_2

                sector_3 = participant.sector_by_lap(i, 3)
                lap_data['sector_3'] = sector_3

                try:
                    lap_data['lap_time'] = sum((
                        sector_1,
                        sector_2,
                        sector_3))
                except TypeError:
                    lap_data['lap_time'] = None

                lap_data['invalid_lap'] = \
                    participant.invalid_lap(i)
                lap_data['position'] = \
                    participant.position_by_lap(i)

                participant_data['laps'].append(lap_data)

            participant_data['laps'] = sorted(
                participant_data['laps'],
                key=lambda x: x['lap_number'])
            output['drivers'].append(participant_data)

        return output

    def participants_by_name(self):
        return sorted(
            [x for x in self.participants \
                if x.name is not None],
            key=lambda x: x.name.lower())

    def participants_by_position(self, lap):
        active = sorted(
            [x for x in self.participants \
                if x.position_by_lap(lap) is not None],
            key=lambda x: x.position_by_lap(lap))
        inactive = [x for x in self.participants \
            if x.position_by_lap(lap) is None]
        return active+inactive

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

            participant.merge(target_participant)
            #target_participant.merge(participant)
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

    def add_sector_time(self, sector, time, position):
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
