from threading import Thread

from modules.hue_manager import HueAPI
from modules.main_manager import Main
from modules.room_manager import Room

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.90'}


class Home(Main):

    def __init__(self, credentials):
        super().__init__(credentials)
        self.data = self.db.get_home_data()
        self.rooms = {room['room_name']: Room(credentials, room['room_id'])
                      for room in self.data['room_data'].to_dict(orient='records')}

    def initialize(self):
        super(Home, self).initialize()
        self.initialize_third_party()
        for room in self.rooms:
            self.rooms[room].third_party = self.third_party
            print(self.rooms[room].initialize())

    def initialize_third_party(self):

        self.third_party.update(
            {'hue': HueAPI(hue_credentials={'192.168.50.34': 'pJPb8WW2wW1P82RKu1sHBLkEQofDMofh2yNDnXzj'})}
        )

    def run(self):
        super(Home, self).run()
        for room in self.rooms:
            Thread(target=self.rooms[room].run).start()

        while True:
            pass


if __name__ == '__main__':
    main = Home(credentials)
    main.initialize()
    main.run()
