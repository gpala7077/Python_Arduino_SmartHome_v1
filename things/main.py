from threading import Thread
from modules.main_manager import Main
from modules.thing_manager import MCU

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.90'}


class Thing_Main(Main):

    def __init__(self, credentials, thing_id):
        super().__init__(credentials)
        self.data = self.db.get_thing_data(thing_id=thing_id, role='emitter')
        self.r_pi = MCU(self.data)

    def initialize(self):
        super(Thing_Main, self).initialize()
        self.commands.r_pi_read_write = self.r_pi.read_write
        self.interrupts = self.r_pi.interrupts

        print(self.r_pi.start())

    def process_interrupt(self):
        super(Thing_Main, self).process_interrupt()
        payload = self.interrupts.get()
        channels = self.data['mqtt_data']['channels'].query(
            'channel_name == "thing_interrupt"')['channel_broadcast'].to_list()
        self.mosquitto.broadcast(channels, payload)

    def process_message(self):
        super(Thing_Main, self).process_message()
        topic, msg = self.mosquitto.messages.get()
        self.commands.execute(msg)

    def run(self):
        super(Thing_Main, self).run()

        activity = Thread(target=self.monitor_interrupts)
        activity.start()
        while True:
            pass


if __name__ == '__main__':
    main = Thing_Main(credentials, 1)
    main.initialize()
    main.run()
