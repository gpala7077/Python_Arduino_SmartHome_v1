from functools import partial

from PySide2.QtCore import QThread
from PySide2.QtWidgets import QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit

from app.SmartHome.modules.base import Window
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
            self.rooms[current_row['room_id']].clicked.connect(partial(
                self.show_screen, data, close_screen))


class DynamicLabel(QThread):

    def __init__(self, label, status):
        QThread.__init__(self)
        self.label = label
        self.status = status

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            status = self.status()
            msg = ''
            if not status.empty:
                status = status.to_dict(orient='records')
                for record in status:
                    msg += '{sensor_name:20} {sensor_type:20} {sensor_value}\n'.format(**record)
                if self.label.text() != msg:
                    self.label.setText(msg)


class Room(Window):
    def __init__(self, window_title, room_id, db):
        super(Room, self).__init__(window_title)
        self.db = db
        self.data = self.db.get_room_data(room_id)
        self.mosquitto = Mosquitto()
        self.commands = Commands()

        self.command = None
        self.threads = {}

        self.current_status = QLabel('Status')
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

    def load_threads(self):
        self.threads.update({0: DynamicLabel(self.current_status, self.mosquitto.get_sensors)})

    def load_window(self):
        super(Room, self).load_window()
        self.connect_to_room()
        self.load_threads()

        for command in self.data['commands_data'].query('command_type == "app"')['command_name'].tolist():
            self.available_commands.addItem(command)

        self.layout.addWidget(self.current_status)
        self.layout.addWidget(self.execute_command)
        self.layout.addWidget(self.available_commands)

    def connect_widgets(self):
        super(Room, self).connect_widgets()
        for thread in self.threads:
            self.threads[thread].start()

        self.execute_command.clicked.connect(lambda: self.commands.execute(self.command))
        self.available_commands.currentTextChanged.connect(self.update_command)

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
