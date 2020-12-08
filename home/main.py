from threading import Thread

from modules.hue_manager import HueAPI
from modules.main_manager import Main
from modules.room_manager import Room

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
        super().__init__(credentials)                                                    # initialize parent class
        self.data = self.db.get_home_data()                                              # get home data from db
        self.rooms = {room['room_name']: Room(credentials, room['room_id'])              # create dictionary of rooms
                      for room in self.data['room_data'].to_dict(orient='records')}

    def initialize(self):
        """Initialize Home - extends parent class"""

        super(Home, self).initialize()                                     # Call parent class
        self.initialize_third_party()                                      # Initialize third-party APIs
        for room in self.rooms:                                            # Iterate through each room
            self.rooms[room].third_party = self.third_party                # Provide access to 3rd party apps to rooms
            self.rooms[room].__class__.__name__ = room                     # Name class as room name for logs
            print(self.rooms[room].initialize())                           # Initialize each room

    def initialize_third_party(self):                                      # Initialize 3rd party apps
        """Initialize third-party applications."""

        self.third_party.update(
            {'hue': HueAPI(ip_address='192.168.50.34', user='pJPb8WW2wW1P82RKu1sHBLkEQofDMofh2yNDnXzj')}
        )

    def run(self):
        """Run all sub-threads."""

        super(Home, self).run()                                             # Call parent class
        for room in self.rooms:                                             # Begin room sub-threads
            Thread(target=self.rooms[room].run).start()


if __name__ == '__main__':
    main = Home(credentials)                                                # Create Main class
    main.initialize()                                                       # Initialize main
    main.run()                                                              # Run main program
