"""
Provides a class for the storing and management of telemetry data
"""

import datetime
import json

from Track import Track

class TelemetryData():
    """
    A class to hold and process telemetry data.
    """
    def __init__(self):
        self.participants = None
        self.participant_data = None

        self.race_in_progress = False
        self.track = None
        self.race_mode = None
        self.race_duration = 0

        self.starting_grid = list()

        self.race_number = 0

        self.__open_json_file()

    def link_participants(self, participant_data):
        """
        Link a Participant Data object to the Telemetry Data.
        """
        self.participant_data = participant_data

    def add(self, telemetry_data):
        '''
        participants = None if \
            telemetry_data.num_participants == -1 else \
            telemetry_data.num_participants

        if self.participants != participants:
            self.participant_data.reset_participants()
        self.participants = participants
        '''

        self.race_in_progress = \
            self.game_state(
                telemetry_data.game_session_state) == 2 and \
            self.session_state(
                telemetry_data.game_session_state) == 5

        if self.race_in_progress:
            participants = None if \
                telemetry_data.num_participants == -1 else \
                telemetry_data.num_participants

            if self.participants != participants:
                self.participant_data.reset_participants()
            self.participants = participants

            self.track = Track(
                telemetry_data.track_length,
                verbose=False)

            if telemetry_data.laps_in_event:
                self.race_mode = "Laps"
                self.race_duration = telemetry_data.laps_in_event
            else:
                self.race_mode = "Time"
                time_remaining = divmod(
                    telemetry_data.event_time_remaining, 60)[0]*60
                self.race_duration = time_remaining \
                    if time_remaining > self.race_duration and \
                        time_remaining < 100000000 \
                    else self.race_duration

            if telemetry_data.current_time == -1 and \
                    sum([self.position(x.race_position) for x \
                        in telemetry_data.participant_info]) != 0 and \
                    len(self.participant_data.participants):
                #If the race hasn't started, we have a starting grid.
                self.starting_grid = sorted(
                    (
                        (
                            self.position(x.race_position),
                            self.participant_data.participants[index]) \
                        for index, x in enumerate(
                            telemetry_data.participant_info) \
                        if index < self.participants))

            self.__write_json()
        elif self.track is not None:
            self.race_number += 1
            self.__new_json_file()
            self.track = None

    @staticmethod
    def position(race_position):
        """
        Extract and return the Race Position.
        """
        return race_position & int('01111111', 2)

    def __open_json_file(self):
        file_name = datetime.datetime.now().strftime(
            "%Y%m%d-%H%M%S")+"-{}.json".format(
                self.race_number)

        self.json_file = open(file_name, 'w')

    def __close_json_file(self):
        self.json_file.close()

    def __write_json(self):
        self.json_file.seek(0)
        json.dump(self.__get_values(), self.json_file, indent=4)
        self.json_file.truncate()

    def __new_json_file(self):
        self.__write_json()
        self.__close_json_file()
        self.__open_json_file()

    def __get_values(self):
        values = dict()
        values['track'] = self.track.name
        values['race_mode'] = self.race_mode
        values['race_duration'] = self.race_duration
        values['starting_grid'] = \
            [name for index, name in self.starting_grid]

        return values

    @staticmethod
    def game_state(game_session_state):
        """
        Extract and return the Game State
        """
        return game_session_state & int('00001111', 2)

    @staticmethod
    def session_state(game_session_state):
        """
        Extract and return the Session State
        """
        return (game_session_state & int('11110000', 2)) >> 4

    @staticmethod
    def race_state(race_state):
        """
        Extract and return the Race State
        """
        return race_state & int('00000111', 2)
