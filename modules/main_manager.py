from modules.commands_manager import Commands
from modules.database_manager import Database
from modules.mosquitto_manager import Mosquitto
from threading import Thread


class Main:
    def __init__(self, credentials):
        self.db = Database(credentials)
        self.data = None
        self.mosquitto = None
        self.commands = None
        self.status = dict()

    def initialize(self):
        self.mosquitto = Mosquitto(self.data['mqtt_data']['configuration']['mqtt_value'])
        self.commands = Commands(self.data)
        print(self.mosquitto.listen(self.data['mqtt_data']['listen']))

    def run(self):
        pass
