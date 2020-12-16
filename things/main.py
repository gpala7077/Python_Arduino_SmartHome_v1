from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.main_manager import Main
from modules.thing_manager import MCU

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.173'}


class Thing_Main(Main):
    """Represents an active MCU

    Attributes
    ----------
    data : dict
        Dictionary defined as {name_of_data: pd.DataFrame}

    r_pi : object
        Class object of type MCU

    Parameters
    ----------
    credentials : dict
        Dictionary defined as {username: un, password:pwd, host:ip, database:name}

    thing_id : int
        Primary key for thing_id
    """

    def __init__(self, credentials, thing_id):
        super().__init__(credentials)  # Call super class
        self.data = self.db.get_thing_data(thing_id=thing_id, role='emitter')  # Get thing data
        self.r_pi = MCU(self.data)  # Initialize raspberry pi

    def initialize(self):
        """Initialize Raspberry pi"""
        super(Thing_Main, self).initialize()  # Call super class
        self.commands.r_pi_read_write = self.r_pi.read_write  # Pass read/write to commands
        self.interrupts = self.r_pi.interrupts  # Pass interrupts to main
        self.r_pi.process_interrupt = self.process_interrupt  # Pass function to RPI
        print(self.r_pi.start())  # Start up the RPI

    def interrupt(self, channel, payload):
        return self.mosquitto.broadcast(channel, payload())

    def process_interrupt(self):
        """Process active interrupt."""
        print('Processing Interrupt for {}'.__class__.__name__)  # Call super class
        channel = self.data['mqtt_data']['channels_dict']['thing_interrupt']
        payload = self.interrupts.get()
        print(self.mosquitto.broadcast(channel, payload))

    def run(self):
        """Start main loop."""
        super(Thing_Main, self).run()  # Call super class

        while True:  # Main tasks for RaspberryPi
            if 0 not in self.tasks:
                # self.tasks.update({0: Thread(target=self.get_status)})
                # self.tasks[0].start()
                pass


if __name__ == '__main__':
    main = Thing_Main(credentials, 1)
    main.initialize()
    main.run()
