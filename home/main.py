from threading import Thread

from modules.hue_manager import HueAPI
from modules.main_manager import Main
from modules.push_manager import Push
from modules.room_manager import Room
from modules.sonos_manager import Sonos

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.173'}


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

    def __init__(self, credentials):
        super().__init__(credentials)  # initialize parent class
        self.data = self.db.get_home_data()  # get home data from db
        self.name = 'Home'
        self.rooms = {room['room_name']: Room(credentials, room['room_id'])  # create dictionary of rooms
                      for room in self.data['room_data'].to_dict(orient='records')}

    def initialize(self):
        """Initialize Home - extends parent class"""

        super(Home, self).initialize()  # Call parent class
        self.initialize_third_party()  # Initialize third-party APIs
        for room in self.rooms:  # Iterate through each room
            self.rooms[room].third_party = self.third_party  # Provide access to 3rd party apps to rooms
            self.rooms[room].name = room  # Name class as room name for logs
            print(self.rooms[room].initialize())  # Initialize each room

    def initialize_third_party(self):  # Initialize 3rd party apps
        """Initialize third-party applications."""

        self.third_party.update({'hue': HueAPI(ip_address='192.168.50.34', user='pJPb8WW2wW1P82RKu1sHBLkEQofDMofh2yNDnXzj')})
        self.third_party.update({'push': Push(key='o.aFYUBKPv0sDSwAcFJXkcHj0rYYRCFWZa')})
        self.third_party.update({'sonos': Sonos('192.168.50.59')})

    def run(self):
        """Run all sub-threads."""

        super(Home, self).run()  # Call parent class
        for room in self.rooms:  # Begin room sub-threads
            Thread(target=self.rooms[room].run).start()

        while True:  # Main tasks for room
            if 0 not in self.tasks:
                # self.tasks.update({0: Thread(target=self.get_status)})
                # self.tasks[0].start()
                pass


if __name__ == '__main__':
    main = Home(credentials)  # Create Main class
    main.initialize()  # Initialize main
    main.run()  # Run main program
