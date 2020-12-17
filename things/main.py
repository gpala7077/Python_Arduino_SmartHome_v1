from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread
import sys
from modules.main_manager import Main
from modules.thing_manager import MCU

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.173'}
thing_id = sys.argv[1]


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

    def process_interrupt(self):
        """Process active interrupt."""
        print('Processing Interrupt for {}'.__class__.__name__)  # Call super class
        channel_1 = self.data['mqtt_data']['channels_dict']['thing_interrupt']
        channel_2 = self.data['mqtt_data']['channels_dict']['thing_info']
        print(self.mosquitto.broadcast(channel_1, self.interrupts.get()))
        print(self.mosquitto.broadcast(channel_2, self.r_pi.read_write()))

    def run(self):
        """Start main loop."""
        super(Thing_Main, self).run()  # Call super class

        while True:  # Main tasks for RaspberryPi
            if 0 not in self.tasks:
                # self.tasks.update({0: Thread(target=self.get_status)})
                # self.tasks[0].start()
                pass


if __name__ == '__main__':
    print('Preparing thing {}.'.format(thing_id))
    main = Thing_Main(credentials, thing_id)
    main.initialize()
    main.run()
