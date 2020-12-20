from threading import Thread

from modules.hue_manager import Hue
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
        self.third_party['push'].commands = self.commands   # Give access to commands class to PushBullet API
        self.commands.third_party = self.third_party  # Reference 3rd party API to commands
        for room in self.rooms:  # Iterate through each room
            self.rooms[room].third_party = self.third_party  # Provide access to 3rd party apps to rooms
            self.rooms[room].name = room  # Name class as room name for logs
            print(self.rooms[room].initialize())  # Initialize each room

    def initialize_third_party(self):  # Initialize 3rd party apps
        """Initialize third-party applications."""

        self.third_party.update({'hue': Hue(ip_address='192.168.50.34', user='pJPb8WW2wW1P82RKu1sHBLkEQofDMofh2yNDnXzj')})
        self.third_party.update({'push': Push('o.aFYUBKPv0sDSwAcFJXkcHj0rYYRCFWZa')})
        self.third_party.update({'sonos': Sonos('192.168.50.59')})

    def run(self):
        """Run all sub-threads."""
        super(Home, self).run()  # Call parent class
        self.third_party['sonos'].listen('LoFi Hip Hop')
        self.third_party['sonos'].player.volume = 20
        Thread(target=self.third_party['push'].listen()).start() # Listen for commands from PushBullet API - home lvl
        for room in self.rooms:  # Begin room sub-threads
            Thread(target=self.rooms[room].run).start()


if __name__ == '__main__':
    main = Home(credentials)  # Create Main class
    main.initialize()  # Initialize main
    main.run()  # Run main program
