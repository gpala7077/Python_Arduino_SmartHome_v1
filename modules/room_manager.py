from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from threading import Thread, Timer, Event

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
        self.data = self.db.get_room_data(room_id)  # Get room data from db
        self.things = {thing['thing_name']: Thing(credentials, thing['thing_id'])  # Create dictionary of Things
                       for thing in self.data['thing_data'].to_dict(orient='records')}

    def initialize(self):
        """Initialize Room."""

        super(Room, self).initialize()  # Call super class
        self.commands.current_status = self.current_status  # reference status to commands
        self.commands.third_party = self.third_party  # Reference 3rd party API to commands
        for thing in self.things:  # Initialize all things
            self.things[thing].name = thing
            print(self.things[thing].initialize())
        return '{} initialized\n'.format(self.__class__.__name__)

    def current_status(self):
        """Get currentroom status."""

        print('Getting current status for {}'.format(self.__class__.__name__))
        df = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value'])  # Create empty data frame

        status = []  # Initialize empty condition list
        with ThreadPoolExecutor() as executor:  # Begin sub-threads
            for thing in self.things:
                status.append(executor.submit(self.things[thing].get_status, current=False))  # submit to thread pool

            for result in as_completed(status):  # Wait until all things have been read
                df = df.append(result.result())
        return df

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
        super().__init__(credentials)  # Call super class
        self.data = self.db.get_thing_data(thing_id, 'receiver')  # get thing receiver data
        self.new_status = None

    def initialize(self):
        """Initialize thing receiver"""

        super(Thing, self).initialize()  # Call super class
        self.sensors = self.mosquitto.get_sensors  # reference get_sensors
        self.new_status = self.mosquitto.get_status

        return '{} initialized\n'.__class__.__name__

    def get_status(self, current=True):
        """Returns current or last known status."""
        if current:
            payload = 'status'  # define payload
            channel = self.data['mqtt_data']['channels_dict']['thing_commands']  # Prepare channel
            self.mosquitto.broadcast(channel, payload)  # Request thing status

            retry = 3
            timeout = 10
            started = datetime.now()
            i = 0
            while not self.new_status():
                if (datetime.now() - started).total_seconds() >= timeout and i <= retry:
                    print('\nNo Response...Reattempting. Attempted {} time(s)'.format(i))
                    self.mosquitto.broadcast(channel, payload)  # Request thing status
                    started = datetime.now()
                    i += 1
                elif i > retry:
                    if not self.sensors().empty:
                        print('\nNo Response, sending last known status')
                        return self.sensors()
                    else:
                        return '\nNo Response'

            self.mosquitto.new_status = False
        return self.sensors()

    def status_interval(self, repeat, quit_event):
        """Perpetually request a status update"""
        if quit_event.isSet():
            return
        else:
            Timer(repeat, self.status_interval, args=[repeat, quit_event]).start()
            self.get_status()

    def run(self):
        """Initialize thing. """
        super(Thing, self).run()  # Call super class
        quit_event = Event()
        interval = 60 * 5
        print('Requesting sensor information for {}.\n'
              'Repeating request every {} seconds.\n'.format(self.__class__.__name__, interval))
        self.status_interval(interval, quit_event)
