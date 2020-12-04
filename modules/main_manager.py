from threading import Thread

from modules.commands_manager import Commands
from modules.database_manager import Database
from modules.hue_manager import HueAPI
from modules.mosquitto_manager import Mosquitto


class Main:
    def __init__(self, credentials):
        print('Loading up {}...'.format(self.__class__.__name__))
        self.db = Database(credentials)
        self.third_party = dict()
        self.data = None
        self.mosquitto = None
        self.commands = None
        self.interrupts = None
        self.status = dict()

    def initialize(self):
        print('Initializing {}'.format(self.__class__.__name__))
        self.mosquitto = Mosquitto(self.data['mqtt_data']['configuration']['mqtt_value'])
        self.commands = Commands(self.data)
        print(self.mosquitto.listen(self.data['mqtt_data']['listen']))

    def monitor_messages(self):
        print('Monitoring All Incoming Messages for {}\n'.format(self.__class__.__name__))

        while True:
            if self.mosquitto.messages:
                task = Thread(target=self.process_message)
                task.start()

    def monitor_interrupts(self):
        print('Monitoring All Interrupt Events for {}\n'.format(self.__class__.__name__))

        while True:
            if self.interrupts:
                task = Thread(target=self.process_interrupt)
                task.start()

    def process_message(self):
        print('Processing Message for {}'.format(self.__class__.__name__))

    def process_interrupt(self):
        print('Processing Interrupt for {}'.format(self.__class__.__name__))

    def run(self):
        print('Starting Main Loop for {}'.format(self.__class__.__name__))
        status = Thread(target=self.monitor_messages)
        status.start()
