from threading import Thread

import RPi.GPIO as GPIO
import Adafruit_ADS1x15
import Adafruit_DHT
from modules.miscellaneous import Queue


class MCU:
    """Represents a Raspberry Pi and it's attached sensors."""

    def __init__(self, data):
        print('Starting up the Raspberry Pi.')
        self.GPIO = GPIO
        self.data = data
        self.bounce_time = 8000
        self.interrupts = Queue('LIFO')

    def start(self):
        """Start the Raspberry Pi."""

        print('Configuring warnings and board pin outs...')
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(self.GPIO.BCM)
        self.initialize()

        return 'Raspberry Pi is up and running'

    def interrupt_callback(self, pin):
        """Interrupt callback function."""

        task = Thread(target=self.add_interrupt, args=[pin])
        task.start()

    def add_interrupt(self, pin):
        """Adds event to interrupt queue as a sub-thread"""
        result = self.read_write('pin_id == {}'.format(pin))
        self.interrupts.add(result)

    def configure_pin(self, pin_id, pin_type, pin_up_down):
        """Configures a pin."""

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

        if interrupt_on == 'rising':
            self.GPIO.add_event_detect(pin_id, self.GPIO.RISING,
                                       callback=self.interrupt_callback, bouncetime=self.bounce_time)

        elif interrupt_on == 'falling':
            self.GPIO.add_event_detect(pin_id, self.GPIO.RISING,
                                       callback=self.interrupt_callback, bouncetime=self.bounce_time)
        # elif interrupt_on == 'both':
        #     self.GPIO.add_event_detect(pin_id, self.GPIO.BOTH,
        #                                callback=self.interrupt_callback, bouncetime=self.bounce_time)

    def initialize(self):
        """Initializes all the attached sensors."""

        print('Configuring pins...')
        pin_configuration = self.data['sensor_data']
        n = len(pin_configuration)

        for i in range(n):
            current_row = pin_configuration[i:i+1].to_dict(orient='records')[0]
            self.configure_pin(current_row['pin_id'], current_row['pin_type'], current_row['pin_up_down'])
            self.configure_interrupt(current_row['pin_id'], current_row['pin_interrupt_on'])

    def read_write(self, query=None, read_write='read', write=None):
        """Reads or writes to the initialized sensors.

            Examples:
            to read all: read_write()
            to read specific: read_write('pin_id == 1')
            to read specific: read_write('pin_name == "light1"')
            to write specific: read_write('pin_id == 1', 'write', 1)

        """

        if query is None:
            data = self.data['sensor_data']
        else:
            data = self.data['sensor_data'].query(query)

        n = len(data)
        results = {}
        for i in range(n):
            current_row = data[i:i + 1].to_dict(orient='records')[0]

            if read_write == 'write':
                value = self.GPIO.output(current_row['pin_id'], int(write))

            elif current_row['pin_type'] == 'adc':
                value = Adafruit_ADS1x15.ADS1115().read_adc(current_row['pin_id'], gain=1)

            elif current_row['pin_type'] == 'dht':
                humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, current_row['pin_id'])
                value = {'humidity': humidity, 'temperature': temperature}

            else:
                value = self.GPIO.input(current_row['pin_id'])

            if isinstance(value, dict): # If value read has multiple parts, break apart based on sensor name number
                num = list(filter(lambda x: x.isdigit(), current_row['pin_name']))[0]
                for val in value:
                    results.update({val + num: value[val]})
            else:
                results.update({current_row['pin_name']: value})

        return results


