from threading import Thread
from modules.main_manager import Main
from modules.thing_manager import MCU

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.90'}


class Thing_Main(Main):

    def __init__(self, credentials):
        super().__init__(credentials)
        self.data = self.db.get_thing_data(1)
        self.r_pi = MCU(self.data)

    def initialize(self):
        super(Thing_Main, self).initialize()
        self.commands.r_pi_read_write = self.r_pi.read_write
        print(self.r_pi.start())

    def monitor_interrupts(self):
        while True:
            if self.r_pi.interrupts:
                payload = self.r_pi.interrupts.get()
                channels = self.data['mqtt_data']['channels'].query(
                    'channel_name == "thing_interrupt"')['channel_broadcast'].to_list()

                task = Thread(target=self.mosquitto.broadcast, args=[channels, payload])
                task.start()

    def run(self):
        activity = Thread(target=self.monitor_interrupts)
        activity.start()
        super(Thing_Main, self).run()
        while True:
            pass


if __name__ == '__main__':
    main = Thing_Main(credentials)
    main.initialize()
    main.run()
