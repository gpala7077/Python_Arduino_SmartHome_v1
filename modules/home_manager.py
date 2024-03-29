from datetime import datetime
from threading import Thread, Timer, Event
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from modules.hue_manager import Hue
from modules.main_manager import Main
from modules.project_manager import Projects
from modules.push_manager import Push
from modules.room_manager import Room
from modules.sonos_manager import Sonos
from modules.ifttt_manager import WebHooks_IFTTT
import time


class Home(Main):
    """Main smart home program.

    Attributes
    ----------
    data : dict
        Dictionary defined as {name_of_data: pd.DataFrame}
    rooms : dict
        Dictionary defined as {room name: Room(credentials, room_id)}

    Parameters
    ----------
    credentials : dict
        Dictionary defined as {username: un, password:pwd, host:ip, database:name}

    """

    def __init__(self, role, credentials):
        super().__init__(credentials)  # initialize parent class
        self.data = self.db.get_home_data()  # get home data from db
        self.name = 'Home'
        self.role = role
        self.rooms = {room['room_name']: Room(credentials, room['room_id'])  # create dictionary of rooms
                      for room in self.data['room_data'].to_dict(orient='records')}

    def initialize(self):
        """Initialize Home - extends parent class"""

        super(Home, self).initialize()  # Call parent class
        self.mosquitto.role = self.role
        self.projects.db = self.db
        self.initialize_third_party()  # Initialize third-party APIs
        if self.third_party['push'] is not None:
            self.third_party['push'].commands = self.commands  # Give access to commands class to PushBullet API
        self.commands.third_party = self.third_party  # Reference 3rd party API to commands
        self.commands.current_status = self.current_status  # reference status to commands
        for room in self.rooms:  # Iterate through each room
            self.rooms[room].third_party = self.third_party  # Provide access to 3rd party apps to rooms
            self.rooms[room].name = room  # Name class as room name for logs
            self.rooms[room].role = self.role
            print(self.rooms[room].initialize())  # Initialize each room

        return '{} | {} Initialized.\n'.format(self.__class__.__name__, self.name)

    def initialize_third_party(self):  # Initialize 3rd party apps
        """Initialize third-party applications."""

        self.third_party.update({'hue': Hue(ip_addr='192.168.50.34', user='pJPb8WW2wW1P82RKu1sHBLkEQofDMofh2yNDnXzj')})
        self.third_party.update({'sonos': Sonos('192.168.50.59')})
        self.third_party.update({'ifttt': WebHooks_IFTTT('ckcorpj6ouQG_nn2YGYyQn')})

        try:
            self.third_party.update({'push': Push('o.aFYUBKPv0sDSwAcFJXkcHj0rYYRCFWZa')})

        except:
            print('You have been rate limited')
            self.third_party.update({'push': None})

        return 'Third-party initialized'

    def current_status(self, current=True):
        """Get current home status."""

        print('Getting {} status for {} | {}'.format(['last known', 'current'][(current == True)],
                                                     self.__class__.__name__, self.name))
        df = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value'])  # Create empty data frame

        status = []  # Initialize empty condition list
        with ThreadPoolExecutor() as executor:  # Begin sub-threads
            for room in self.rooms:
                status.append(
                    executor.submit(self.rooms[room].current_status, current=current))  # submit to thread pool

            for result in as_completed(status):  # Wait until all things have been read
                df = df.append(result.result())
        self.status = df
        return self.status

    def status_interval(self, repeat, quit_event):
        """Perpetually request a status update"""

        print('Requesting room information for {}.\n'
              'Repeating request every {} seconds.\n'.format(self.name, repeat))

        if quit_event.isSet():
            return
        else:
            Timer(repeat, self.status_interval, args=[repeat, quit_event]).start()
            data = self.current_status()
            if not data.empty:
                timestamp = [datetime.now()] * data.shape[0]
                data['history_timestamp'] = timestamp
                self.db.replace_insert_data('insert', 'history', data)

    def track_schedule(self, quit_event):
        time_block = self.projects.get_current_time_block()
        time_block = time_block['time_block_id'].tolist()[0]
        task = self.projects.get_current_task(time_block).to_dict(orient='records')[0]

        time_diff = self.projects.get_time_block(task['task_block_end'])['time_block_end'].tolist()[0]
        time_diff = time_diff - datetime.now()

        title, body = self.projects.format_task(task, time_diff)

        print('This task will end in ....')
        print('{} hours, {} minutes, and {} seconds'.format(
            time_diff.seconds // 3600, (time_diff.seconds // 60) % 60, time_diff.seconds % 60))
        if self.third_party['push'] is not None:
            try:
                self.third_party['push'].push.push_note(title=title, body=body)
                Timer(function=self.track_schedule, args=[quit_event], interval=time_diff.seconds+5).start()
            except:
                print('You have been rate limited....')

    def start_rooms(self):
        for room in self.rooms:  # Begin room sub-threads
            Thread(target=self.rooms[room].run).start()
        return 'All Rooms Started\n'

    def run(self):
        """Run all sub-threads."""
        super(Home, self).run()  # Call parent class
        quit_event = Event()
        repeat = 60 * 60
        self.status_interval(repeat, quit_event)
        self.track_schedule(quit_event)
        if self.third_party['push'] is not None:
            Thread(target=self.third_party['push'].listen(self.on_push)).start() # Listen for pushes from PushBullet API

        print(self.start_rooms())