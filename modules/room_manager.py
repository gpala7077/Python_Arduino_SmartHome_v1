from threading import Thread

import pandas as pd

from modules.main_manager import Main


class Room(Main):
    """Represents a room in the house.

    Attributes
    ----------
    data : dict
        Dictionary of pandas data frames
    things : dict
        Dictionary of things associated with room

    Parameters
    ----------
    credentials : dict
        Database credentials defined as {'username': 'un', 'password': 'pwd', 'database': 'name', 'host': 'IP'}

    room_id : int
        Primary key for room

    """

    def __init__(self, credentials, room_id):
        super().__init__(credentials)                                               # Call super class
        self.data = self.db.get_room_data(room_id)                                  # Get room data from db
        self.things = {thing['thing_name']: Thing(credentials, thing['thing_id'])   # Create dictionary of Things
                       for thing in self.data['thing_data'].to_dict(orient='records')}

    def initialize(self):
        """Initialize Room."""

        super(Room, self).initialize()                                          # Call super class
        self.commands.current_status = self.current_status                      # reference status to commands
        self.commands.third_party = self.third_party                            # Reference 3rd party API to commands
        for thing in self.things:                                               # Initialize all things
            self.things[thing].__class__.__name__ = thing
            print(self.things[thing].initialize())
        return '{} initialized\n'.format(self.__class__.__name__)

    def current_status(self):
        """Get current room status."""

        print('Getting current status for {}'.format(self.__class__.__name__))
        df = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value', 'time_stamp'])# Create empty data frame

        for thing in self.things:
            df = df.append(self.things[thing].sensors().query('time_stamp=="{}"'.format(
                self.things[thing].sensors()['time_stamp'].max()
            )))
        return df

    def run(self):
        """Initialize all the things in room."""

        super(Room, self).run()                             # Call super class
        for thing in self.things:                           # Initialize all things associated with the room.
            Thread(target=self.things[thing].run).start()   # Run main loops


class Thing(Main):
    """Represents an MCU

    Attributes
    ----------
    data : dict
        Dictionary of pandas data frames

    sensors : DataFrame
        Pandas DataFrame of attached sensors

    Parameters
    ----------
    credentials : dict
        Database credentials defined as {'username': 'un', 'password': 'pwd', 'database': 'name', 'host': 'IP'}

    thing_id : int
        Primary key for room

    """

    def __init__(self, credentials, thing_id):
        super().__init__(credentials)                                       # Call super class
        self.data = self.db.get_thing_data(thing_id, 'receiver')            # get thing receiver data
        self.sensors = pd.DataFrame()                                       # Initialize empty data frame

    def initialize(self):
        """Initialize thing receiver"""

        super(Thing, self).initialize()                                     # Call super class
        self.sensors = self.mosquitto.get_sensors                           # reference get_sensors
        return '{} initialized\n'.__class__.__name__

    def run(self):
        """Initialize thing. """

        super(Thing, self).run()                                            # Call super class
        payload = 'status'                                                  # define payload
        channel = self.data['mqtt_data']['channels_dict']['thing_commands'] # define channel
        self.mosquitto.broadcast(channel, payload)                          # Request thing status
