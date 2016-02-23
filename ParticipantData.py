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
