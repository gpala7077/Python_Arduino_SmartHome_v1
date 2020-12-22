import time
from functools import partial

import pandas as pd
from PySide2.QtCore import QThread
from PySide2.QtWidgets import QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTableView

from app.QTSmartHome.modules.base import Window
from app.QTSmartHome.modules.database import Pandas
from modules.commands_manager import Commands
from modules.mosquitto_manager import Mosquitto


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


class Main_Menu(Window):
    def __init__(self, window_title):
        super(Main_Menu, self).__init__(window_title)
        self.buttons = {button: QPushButton(button) for button in ('Smart Home', 'Database Management')}

    def load_window(self):
        super(Main_Menu, self).load_window()
        for button in self.buttons:
            self.layout.addWidget(self.buttons[button])

    def connect_widgets(self):
        super(Main_Menu, self).connect_widgets()
        close_screen = self.__class__.__name__
        for button in self.buttons:
            self.buttons[button].clicked.connect(partial(self.show_screen, button, close_screen))


class Smart_Home(Window):
    def __init__(self, window_title):
        super(Smart_Home, self).__init__(window_title)
        self.buttons = {button: QPushButton(button) for button in ('Rooms',)}

    def load_window(self):
        super(Smart_Home, self).load_window()
        for button in self.buttons:
            self.layout.addWidget(self.buttons[button])

    def connect_widgets(self):
        super(Smart_Home, self).connect_widgets()
        close_screen = self.__class__.__name__
        for button in self.buttons:
            self.buttons[button].clicked.connect(partial(self.show_screen, button, close_screen))


class Rooms(Window):
    def __init__(self, window_title, db):
        super(Rooms, self).__init__(window_title)
        self.db = db
        self.data = self.db.query('select * from home_rooms')
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
            data = self.data[i:i + 1]
            current_row = data.to_dict(orient='records')[0]  # Look at current row
            self.rooms[current_row['room_id']].clicked.connect(partial(self.show_screen, data, close_screen))


class DynamicLabel(QThread):

    def __init__(self, label, table, status):
        QThread.__init__(self)
        self.label = label
        self.table = table
        self.status = status

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(5):
            status = self.status()
            if not status.empty:
                self.label = Pandas(status)
                self.table.setModel(self.label)
                return 'Status Captured'
            time.sleep(1)
        return 'Timeout...'


class Room(Window):
    def __init__(self, window_title, room_id, db):
        super(Room, self).__init__(window_title)
        self.db = db
        self.data = self.db.get_room_data(room_id)
        self.mosquitto = Mosquitto()
        self.commands = Commands()
        self.table = QTableView()
        self.command = None
        self.threads = {}
        df = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value'])  # Create empty data frame
        self.current_status = Pandas(df)
        self.execute_command = QPushButton('Execute')
        self.available_commands = QComboBox()
        self.name = QLabel(self.data['room_data']['room_name'])

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
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.execute_command)
        self.layout.addWidget(self.available_commands)

    def connect_widgets(self):
        super(Room, self).connect_widgets()
        self.table.setModel(self.current_status)

        self.execute_command.clicked.connect(lambda: self.check_command(self.command))
        self.execute_command.released.connect(self.update_status)
        self.available_commands.currentTextChanged.connect(self.update_command)

    def update_status(self):
        self.threads.update({0: DynamicLabel(self.current_status, self.table, self.mosquitto.get_sensors)})
        self.threads[0].start()

    def check_command(self, command):
        if command is not None:
            self.commands.execute(self.command)
        else:
            self.update_command()
            self.commands.execute(self.command)

    def update_command(self):
        self.command = self.data['commands_data'].query(
            'command_type == "app" and '
            'command_sensor == "room" and '
            'command_name == "{}" and '
            'info_id == "{}" and '
            'info_level == "{}"'.format(
                self.available_commands.currentText(),
                self.data['info_id'],
                self.data['info_level'])).to_dict(orient='records')[0]
