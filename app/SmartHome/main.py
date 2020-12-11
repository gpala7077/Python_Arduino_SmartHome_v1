import site
import sys

import pandas as pd
from PySide2.QtWidgets import QApplication
from mysql.connector import Error
from app.SmartHome.modules.database import Db_Management, Manage_Rooms
from app.SmartHome.modules.smart_home import Login, Main_Menu, Smart_Home, Rooms, Room
from modules.database_manager import Database


class Navigator:

    def __init__(self):
        self.db = None
        self.Qt_db = None
        self.screens = None
        self.login_screen = Login('Login')
        self.credentials = {'username': None,
                            'password': None,
                            'database': 'smart_home',
                            'host': '192.168.50.173'}

    def load_screens(self):

        self.screens = {'Main_Menu': Main_Menu('Main Menu'),
                        'Smart_Home': Smart_Home('Smart Home'),
                        'Rooms': Rooms('Available Rooms', self.db),
                        'Db_Management': Db_Management('SmartHome Database Management'),
                        'Manage_Rooms': Manage_Rooms('Manage Rooms', self.db)
                        }
        self.start()

    def start(self):
        for screen in self.screens:
            self.screens[screen].show_screen = self.show_screen
            self.screens[screen].start()

    def show_screen(self, open_screen, close_screen=None):

        if close_screen is not None:
            close_screen = close_screen.replace(' ', '_')
            self.screens[close_screen].close()

        if isinstance(open_screen, str):
            print('\nOpening : {}\nClosing : {}\n'.format(open_screen, close_screen))
            open_screen = open_screen.replace(' ', '_')
            self.screens[open_screen].show()

        elif isinstance(open_screen, pd.DataFrame):
            data = open_screen
            data_dict = data.to_dict(orient='records')[0]
            print('\nOpening : {}\nClosing : {}\n'.format(data_dict, close_screen))

            if any("room" in key for key in list(data_dict.keys())):
                print('Opening {room_name} identified as {room_id}'.format(**data_dict))
                self.screens.update({'Room': Room(data_dict['room_name'], data_dict['room_id'], self.db)})
                self.screens['Room'].start()
                self.screens['Room'].show()

    def check_credentials(self, username, password):
        self.credentials.update({'username': username})
        self.credentials.update({'password': password})
        try:
            self.db = Database(self.credentials)
            self.login_screen.close()
            self.load_screens()
            self.show_screen('Main_Menu')
        except Error:
            print('Incorrect Credentials!')
            self.login_screen.username.clear()
            self.login_screen.password.clear()

    def login(self):
        self.login_screen.show_screen = self.check_credentials
        self.login_screen.start()
        self.login_screen.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    navigator = Navigator()
    navigator.login()
    sys.exit(app.exec_())
