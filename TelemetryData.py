"""
Provides a class for the storing and management of telemetry data
"""

class TelemetryData():
    """
    A class to hold and process telemetry data.
    """
    def __init__(self):
        self.participants = None
        self.participant_data = None

    def link_participants(self, participant_data):
        self.participant_data = participant_data

    def add(self, telemetry_data):
        participants = None if \
            telemetry_data.num_participants == -1 else \
            telemetry_data.num_participants

        if self.participants != participants:
            self.participant_data.reset_participants()
        self.participants = participants
