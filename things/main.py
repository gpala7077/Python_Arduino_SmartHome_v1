from threading import Thread
from modules.main_manager import Main
from modules.thing_manager import MCU

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.90'}


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
        super().__init__(credentials)                                                       # Call super class
        self.data = self.db.get_thing_data(thing_id=thing_id, role='emitter')               # Get thing data
        self.r_pi = MCU(self.data)                                                          # Initialize raspberry pi

    def initialize(self):
        """Initialize Raspberry pi"""
        super(Thing_Main, self).initialize()                                               # Call super class
        self.commands.r_pi_read_write = self.r_pi.read_write                               # Pass read/write to commands
        self.interrupts = self.r_pi.interrupts                                             # Pass interrupts to main
        self.r_pi.process_interrupt = self.process_interrupt                               # Pass function to RPI
        print(self.r_pi.start())                                                           # Start up the RPI

    def process_interrupt(self):
        """Process active interrupt."""
        print('Processing Interrupt for {}'.__class__.__name__)                            # Call super class
        payload = self.interrupts.get()                                                    # Prepare payload
        channels = self.data['mqtt_data']['channels']['thing_interrupt']                   # Prepare channel
        self.mosquitto.broadcast(channels, payload)                                        # Broadcast interrupt

    def run(self):
        """Start main loop."""

        super(Thing_Main, self).run()                                                       # Call super class


if __name__ == '__main__':
    main = Thing_Main(credentials, 1)
    main.initialize()
    main.run()
