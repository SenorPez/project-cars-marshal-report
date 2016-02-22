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
        self.telemetry_data = telemetry_data

    def add(self, participant_data):
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
        self.new_participants = list()
