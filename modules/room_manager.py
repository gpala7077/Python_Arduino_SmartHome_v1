from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
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
        super().__init__(credentials)  # Call super class
        self.role = None
        self.data = self.db.get_room_data(room_id)  # Get room data from db
        self.things = {thing['thing_name']: Thing(credentials, thing['thing_id'])  # Create dictionary of Things
                       for thing in self.data['thing_data'].to_dict(orient='records')}

    def initialize(self):
        """Initialize Room."""

        super(Room, self).initialize()  # Call super class
        self.mosquitto.role = self.role
        self.mosquitto.name = self.name
        self.commands.current_status = self.current_status  # reference status to commands
        self.commands.third_party = self.third_party  # Reference 3rd party API to commands
        for thing in self.things:  # Initialize all things
            self.things[thing].name = thing
            print(self.things[thing].initialize())
        return '{} | {} initialized\n'.format(self.__class__.__name__, self.name)

    def current_status(self, current=True):
        """Get current room status."""

        print(
            'Getting {} status for {} | {}'.format(['last known', 'current'][(current == True)],
                                                   self.__class__.__name__, self.name))
        df = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value'])  # Create empty data frame

        status = []  # Initialize empty condition list
        with ThreadPoolExecutor() as executor:  # Begin sub-threads
            for thing in self.things:
                status.append(executor.submit(self.things[thing].current_status, current=current))  # submit to pool

            for result in as_completed(status):  # Wait until all things have been read
                df = df.append(result.result())

        self.status = df
        return self.status

    def run(self):
        """Initialize all the things in room."""

        super(Room, self).run()  # Call super class
        for thing in self.things:  # Initialize all things associated with the room.
            Thread(target=self.things[thing].run).start()  # Run main loops


class Thing(Main):
    """Represents an MCU

    Attributes
    ----------
    data : dict
        Dictionary of pandas data frames

    Parameters
    ----------
    credentials : dict
        Database credentials defined as {'username': 'un', 'password': 'pwd', 'database': 'name', 'host': 'IP'}

    thing_id : int
        Primary key for room

    """

    def __init__(self, credentials, thing_id):
        super().__init__(credentials)  # Call super class
        self.data = self.db.get_thing_data(thing_id, 'receiver')  # get thing receiver data

    def initialize(self):
        """Initialize thing receiver"""

        super(Thing, self).initialize()  # Call super class
        self.mosquitto.name = self.name
        return '{} | {} initialized\n'.format(self.__class__.__name__, self.name)

    def current_status(self, current=True):
        """Returns current or last known status."""

        print(
            'Getting {} status for {} | {}'.format(['last known', 'current'][(current == True)],
                                                   self.__class__.__name__, self.name))
        if current:
            payload = 'status'  # define payload
            channel = self.data['mqtt_data']['channels_dict']['thing_commands']  # Prepare channel
            self.mosquitto.broadcast(channel, payload)  # Request thing status

            retry = 3
            timeout = 10
            started = datetime.now()
            i = 0
            self.new_status_flag = False
            while not self.new_status_flag:
                if (datetime.now() - started).total_seconds() >= timeout and i <= retry:
                    print('\nNo Response...Reattempting. Attempted {} time(s)'.format(i))
                    self.mosquitto.broadcast(channel, payload)  # Request thing status
                    started = datetime.now()
                    i += 1
                elif i > retry:
                    if not self.status.empty:
                        print('\nNo Response, sending last known status')
                        return self.status
                    else:
                        return '\nNo Response'

            self.new_status_flag = False
        return self.status

    def run(self):
        """Initialize thing. """
        super(Thing, self).run()  # Call super class
