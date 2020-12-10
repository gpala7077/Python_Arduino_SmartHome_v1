import sys
import time
from functools import partial
from threading import Thread

from mysql.connector import Error

from modules.commands_manager import Commands
from modules.database_manager import Database
from modules.mosquitto_manager import Mosquitto

from PySide2.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QLineEdit,
)


class Window(QWidget):

    def __init__(self, window_title):
        QWidget.__init__(self)
        self.db = None
        self.layout = QVBoxLayout()
        self.window_title = window_title
        self.button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.show_screen = None
        self.resize(400, 600)

    def start(self):
        self.load_window()
        self.connect_widgets()

    def load_window(self):
        self.setWindowTitle(self.window_title)

    def connect_widgets(self):
        self.setLayout(self.layout)


class Login(Window):
    def __init__(self, window_title):
        super(Login, self).__init__(window_title)
        self.layout = QGridLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.username_lbl = QLabel('Enter Username: ')
        self.password_lbl = QLabel('Enter Password: ')

    def load_window(self):
        super(Login, self).load_window()
        self.password.setEchoMode(self.password.Password)
        self.layout.addWidget(self.username_lbl, 0, 0)
        self.layout.addWidget(self.username, 0, 1)
        self.layout.addWidget(self.password_lbl, 1, 0)
        self.layout.addWidget(self.password, 1, 1)
        self.layout.addWidget(self.button, 2, 0, 1, 2)

    def connect_widgets(self):
        super(Login, self).connect_widgets()
        self.button.accepted.connect(lambda: self.show_screen(self.username.text(), self.password.text()))


class Smart_Home(Window):
    def __init__(self, window_title):
        super(Smart_Home, self).__init__(window_title)
        self.rooms = QPushButton('Rooms')
        self.history = QPushButton('History')

    def load_window(self):
        super(Smart_Home, self).load_window()
        self.layout.addWidget(self.rooms)
        self.layout.addWidget(self.history)

    def connect_widgets(self):
        super(Smart_Home, self).connect_widgets()
        close_screen = self.__class__.__name__
        self.rooms.clicked.connect(lambda: self.show_screen('Rooms', close_screen))
        self.history.clicked.connect(lambda: self.show_screen('History', close_screen))


class Rooms(Window):
    def __init__(self, window_title, rooms):
        super(Rooms, self).__init__(window_title)
        self.data = rooms
        self.rooms = {}

    def load_window(self):
        super(Rooms, self).load_window()
        n = len(self.data)  # Count total sensors
        for i in range(n):  # Iterate through each element
            current_row = self.data[i:i + 1].to_dict(orient='records')[0]  # Look at current row
            self.rooms.update({current_row['room_id']: QPushButton(current_row['room_name'])})

        for room in self.rooms:
            self.layout.addWidget(self.rooms[room])

    def connect_widgets(self):
        super(Rooms, self).connect_widgets()
        close_screen = self.__class__.__name__
        n = len(self.data)  # Count total sensors
        for i in range(n):  # Iterate through each element
            current_row = self.data[i:i + 1].to_dict(orient='records')[0]  # Look at current row
            self.rooms[current_row['room_id']].clicked.connect(partial(
                self.show_screen, current_row, close_screen))


class Room(Window):
    def __init__(self, window_title, room_data):
        super(Room, self).__init__(window_title)
        self.data = room_data
        self.mosquitto = Mosquitto()
        self.commands = Commands()
        self.execute_command = QPushButton('Execute')
        self.available_commands = QComboBox()
        self.name = QLabel(self.data['room_data']['room_name'])
        self.sensors = self.mosquitto.get_sensors

    def connect_to_room(self):
        self.mosquitto.host_ip = self.data['mqtt_data']['configuration']['mqtt_value']
        self.commands.data = self.data  # commands data
        self.commands.mosquitto = self.mosquitto  # Give command access to MQTT
        self.mosquitto.commands = self.commands  # Give MQTT access to commands

        print(self.mosquitto.connect())  # Log info
        print(self.mosquitto.listen(self.data['mqtt_data']['channels_dict']['room_info']))  # Log info

    def load_window(self):
        super(Room, self).load_window()
        self.connect_to_room()
        for command in self.data['commands_data'].query('command_type == "app"')['command_name'].tolist():
            self.available_commands.addItem(command)
        self.layout.addWidget(self.execute_command)
        self.layout.addWidget(self.available_commands)

    def connect_widgets(self):
        super(Room, self).connect_widgets()
        command = self.data['commands_data'].query('command_type == "app" and '
                                                   'command_sensor == "room" and '
                                                   'command_name == "{}" and '
                                                   'info_id == "{}" and '
                                                   'info_level == "{}"'.format(self.available_commands.currentText(),
                                                                               self.data['info_id'],
                                                                               self.data['info_level'])).to_dict(
            orient='records')[0]

        self.execute_command.clicked.connect(lambda: self.commands.execute(command))


class Main_Menu(Window):
    def __init__(self, window_title):
        super(Main_Menu, self).__init__(window_title)
        self.smart_home = QPushButton('Smart Home')
        self.db_management = QPushButton('Database Management')

    def load_window(self):
        super(Main_Menu, self).load_window()
        self.layout.addWidget(self.smart_home)
        self.layout.addWidget(self.db_management)

    def connect_widgets(self):
        super(Main_Menu, self).connect_widgets()
        close_screen = self.__class__.__name__
        self.smart_home.clicked.connect((lambda: self.show_screen('Smart_Home', close_screen)))
        self.db_management.clicked.connect((lambda: self.show_screen('Db_Management', close_screen)))


class Navigator:

    def __init__(self):
        self.db = None
        self.screens = None
        self.dynamic_screen = None
        self.login_screen = Login('Login')
        self.credentials = {'username': None,
                            'password': None,
                            'database': 'smart_home',
                            'host': '192.168.50.173'}

    def load_screens(self):

        self.screens = {'Main_Menu': Main_Menu('Main Menu'),
                        'Smart_Home': Smart_Home('Smart Home'),
                        'Rooms': Rooms('Available Rooms', self.db.query('select * from home_rooms'))}
        self.start()

    def start(self):
        for screen in self.screens:
            self.screens[screen].show_screen = self.show_screen
            self.screens[screen].db = self.db
            self.screens[screen].start()

    def show_screen(self, open_screen, close_screen=None):
        print('\nOpening : {}\nClosing : {}\n'.format(open_screen, close_screen))

        if close_screen is not None:
            self.screens[close_screen].close()

        if isinstance(open_screen, str):
            self.screens[open_screen].show()

        elif isinstance(open_screen, dict):
            if any("room" in key for key in list(open_screen.keys())):
                print('Opening {room_name} identified as {room_id}'.format(**open_screen))

                room_data = self.db.get_room_data(open_screen['room_id'])
                self.dynamic_screen = Room(open_screen['room_name'], room_data)
                self.dynamic_screen.start()
                self.dynamic_screen.show()

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
