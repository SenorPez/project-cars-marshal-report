"""
Provides a class for the storing and management of participant data.
"""

class ParticipantData():
    """
    A class to hold and process participant data.
    """
    def __init__(self):
        self.telemetry_data = None
        self.participant_history = list()
        self.new_participants = list()
        self.lap_data = dict()

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
