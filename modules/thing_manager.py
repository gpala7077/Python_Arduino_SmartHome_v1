from threading import Thread

import Adafruit_ADS1x15
import Adafruit_DHT
import RPi.GPIO as GPIO

from modules.miscellaneous import Queue


class MCU:
    """Represents a Raspberry Pi and it's attached sensors.

    Attributes
    ----------
    GPIO : object
        GPIO object from RPi.GPIO

    data : dict
        Dictionary defined as {name_of_data: DataFrame}

    bounce_time : int
        Bounce time for pin reset

    interrupts : object
        Object of type Queue, manages list of interrupts

    process_interrupt : function
        Passed function to process current interrupts

    Parameters
    ----------
    data : dict
        Dictionary defined as {name_of_data: DataFrame}
    """

    def __init__(self, data):
        print('Starting up the Raspberry Pi.')
        self.GPIO = GPIO                                             # Set attributes
        self.data = data
        self.bounce_time = 8000
        self.interrupts = Queue('LIFO')
        self.process_interrupt = None

    def start(self):
        """Start the Raspberry Pi."""

        print('Configuring warnings and board pin outs...')
        self.GPIO.setwarnings(False)                                # Turn off warnings
        self.GPIO.setmode(self.GPIO.BCM)                            # Set references as BCM
        self.initialize()                                           # Initialize Raspberry Pi

        return 'Raspberry Pi is up and running\n'

    def interrupt_callback(self, pin):
        """Interrupt callback function."""

        self.add_interrupt(pin)                                     # Add interrupt to queue

    def add_interrupt(self, pin):
        """Adds event to interrupt queue as a sub-thread"""

        result = self.read_write('pin_id == {}'.format(pin))        # Read pin value
        val = [0, 1][self.data['sensor_data'].query('pin_id == {}'.format(pin))['pin_interrupt_on'].to_list()[0] ==
                     'rising']                                      # check if it matches interrupt

        if result['sensor_value'][0] == val:                        # if interrupt values match
            self.interrupts.add(result)                             # Add interrupt to queue
            task = Thread(target=self.process_interrupt)            # run process as a sub-thread
            task.start()                                            # Begin sub-thread

    def configure_pin(self, pin_id, pin_type, pin_up_down):
        """Configures a pin on the raspberry pi."""

        if pin_type == 'input' and pin_up_down == 'up':
            self.GPIO.setup(pin_id, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)

        elif pin_type == 'input' and pin_up_down == 'down':
            self.GPIO.setup(pin_id, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)

        elif pin_type == 'input' and pin_up_down == 'none':
            self.GPIO.setup(pin_id, self.GPIO.IN)

        elif pin_type == 'output' and pin_up_down == 'up':
            self.GPIO.setup(pin_id, self.GPIO.OUT, pull_up_down=self.GPIO.PUD_UP)

        elif pin_type == 'output' and pin_up_down == 'down':
            self.GPIO.setup(pin_id, self.GPIO.OUT, pull_up_down=self.GPIO.PUD_DOWN)

        elif pin_type == 'output' and pin_up_down == 'none':
            self.GPIO.setup(pin_id, self.GPIO.OUT)

    def configure_interrupt(self, pin_id, interrupt_on):
        """Configures a software-based interrupt."""

        if interrupt_on == 'rising':                                    # If pin value rises
            self.GPIO.add_event_detect(pin_id, self.GPIO.RISING,
                                       callback=self.interrupt_callback, bouncetime=self.bounce_time)

        elif interrupt_on == 'falling':                                 # If pin value falls
            self.GPIO.add_event_detect(pin_id, self.GPIO.RISING,
                                       callback=self.interrupt_callback, bouncetime=self.bounce_time)
        elif interrupt_on == 'both':                                    # If pin falls or rises
            self.GPIO.add_event_detect(pin_id, self.GPIO.BOTH,
                                       callback=self.interrupt_callback, bouncetime=self.bounce_time)

    def initialize(self):
        """Initializes all the attached sensors."""

        print('Configuring pins...')
        pin_configuration = self.data['sensor_data']                                    # Get pin configurations
        n = len(pin_configuration)                                                      # Get number of pins

        for i in range(n):                                                              # iterate through each pin
            current_row = pin_configuration[i:i + 1].to_dict(orient='records')[0]       # look at current row
            self.configure_pin(current_row['pin_id'], current_row['pin_type'], current_row['pin_up_down']) # configure
            self.configure_interrupt(current_row['pin_id'], current_row['pin_interrupt_on'])    # set interrupt

    def read_write(self, query=None, read_write='read', write=None):
        """Reads or writes to the initialized sensors.

            Examples:
            to read all: read_write()
            to read specific: read_write('pin_id == 1')
            to read specific: read_write('pin_name == "light1"')
            to write specific: read_write('pin_id == 1', 'write', 1)

        """

        if query is None:                                                          # Read all sensor if not specified
            data = self.data['sensor_data']
        else:
            data = self.data['sensor_data'].query(query)                           # Specify sensors
        value = int()                                                              # Initialize empty value
        n = len(data)                                                              # Count total sensors
        results = {'sensor_type': [], 'sensor_name': [], 'sensor_value': []}       # Create empty dictionary
        for i in range(n):                                                         # Iterate through each element
            current_row = data[i:i + 1].to_dict(orient='records')[0]               # Look at current row

            if read_write == 'write':                                              # If write
                self.GPIO.output(current_row['pin_id'], int(write))                # Write value to pin

            elif current_row['pin_type'] == 'adc':                                 # if sensor type is adc
                value = Adafruit_ADS1x15.ADS1115().read_adc(current_row['pin_id'], gain=1)  # read adc value

            elif current_row['pin_type'] == 'dht':                                 # If sensor type is dht
                humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, current_row['pin_id'])
                value = {'humidity': humidity, 'temperature': temperature}         # read humidity and temperature

            else:
                value = self.GPIO.input(current_row['pin_id'])                     # Read pin value

            if isinstance(value, dict):  # If value read has multiple parts, break apart based on sensor name number
                num = list(filter(lambda x: x.isdigit(), current_row['pin_name']))[0]    # get number in sensor name
                for val in value:                                                        # iterate through read values
                    results['sensor_value'].append(value[val])                           # store sensor value
                    results['sensor_name'].append(val + num)                             # rename sensor
                    results['sensor_type'].append(current_row['pin_sensor'])             # restate sensor type
            else:
                results['sensor_value'].append(value)                                    # Add sensor value
                results['sensor_name'].append(current_row['pin_name'])                   # Add sensor name
                results['sensor_type'].append(current_row['pin_sensor'])                 # Add sensor type

        return results
