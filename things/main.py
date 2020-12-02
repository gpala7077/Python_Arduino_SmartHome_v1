from modules.commands_manager import Commands
from modules.database_manager import Database
from modules.mosquitto_manager import Mosquitto
from modules.thing_manager import MCU
from threading import Thread

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.90'}


class Main:
    def __init__(self):
        self.db = Database(credentials)
        self.data = self.db.get_thing_data(1)
        self.r_pi = MCU(self.data)
        self.mosquitto = Mosquitto(self.data['mqtt_data']['configuration']['mqtt_value'])
        self.commands = Commands(self.data['commands_data'])

    def initialize(self):
        self.commands.r_pi_read_write = self.r_pi.read_write
        print(self.mosquitto.listen(self.data['mqtt_data']['listen']))
        print(self.r_pi.start())

    def monitor_interrupts(self):
        while True:
            if self.r_pi.interrupts:
                payload = self.r_pi.interrupts.get()
                channels = self.data['mqtt_data']['channels'].query(
                    'channel_name == "thing_interrupt"')['channel_broadcast'].to_list()

                task = Thread(target=self.mosquitto.broadcast, args=[channels, payload])
                task.start()

    def monitor_messages(self):
        while True:
            if self.mosquitto.messages:
                task = Thread(target=self.commands.execute, args=[self.mosquitto.messages.get()])
                task.start()

    def run(self):
        commands = Thread(target=self.monitor_messages)
        activity = Thread(target=self.monitor_interrupts)

        commands.start()
        activity.start()

        while True:
            pass


if __name__ == '__main__':
    main = Main()
    main.initialize()
    main.run()
