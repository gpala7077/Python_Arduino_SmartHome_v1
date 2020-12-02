from modules.main_manager import Main

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.90'}


class Room_Main(Main):

    def __init__(self, credentials):
        super().__init__(credentials)
        self.data = self.db.get_room_data(1)

        print(self.data)


if __name__ == '__main__':
    main = Room_Main(credentials)
    main.initialize()
    main.run()
