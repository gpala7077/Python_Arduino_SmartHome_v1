from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import RPi.GPIO as GPIO
import Adafruit_ADS1x15
import Adafruit_DHT
from modules.commands_manager import write_value
from modules.database_manager import Database
from modules.commands_manager import Commands
from modules.mosquitto_manager import Mosquitto


def load_data():
    credentials = {
        'username': 'self',
        'password': 'password',
        'database': 'smart_home',
        'host': '192.168.50.90'
    }
    db = Database(credentials)

    thing_id = 1

    thing_data = db.query('select * from home_things where thing_id = %s', [thing_id])[0]

    room_data = db.query(
        'select * from home_rooms where room_id = '
        '(select rooms_room_id from rooms_things where rooms_thing_id = %s)',
        [thing_id])[0]

    sensor_data = db.query(
        'SELECT * '
        'FROM pins_configurations '
        'WHERE thing_id = %s;',
        [thing_id])

    interrupt_data = db.query(
        'SELECT * '
        'FROM pins_interrupts '
        'WHERE thing_id = %s;',
        [thing_id])

    mqtt_data = {
        'type': 'thing',
        'channels': db.query('SELECT * FROM mosquitto_channels'),
        'configuration': db.query('SELECT * FROM mosquitto_configuration')[0],
        'listen': ['thing_commands', 'group_commands']
    }

    commands_data = db.query('SELECT * FROM commands WHERE info_type = %s AND info_id = %s', ['thing', thing_id])

    data = {
        'room_data': room_data,
        'thing_data': thing_data,
        'sensor_data': sensor_data,
        'interrupt_data': interrupt_data,
        'commands_data': commands_data,
        'mqtt_data': mqtt_data
    }
    return {'data': data, 'query': db.query}


def break_up_sensor_data(data):
    master_data = {}
    for reading in data:
        for key in reading:
            if key in list(master_data.keys()):
                master_data[key].append(reading[key])
            else:
                master_data.update({key: [reading[key]]})

    return master_data


class MCU:
    # Class that represents the microprocessor and its I/O.

    def __init__(self, data, query_func):
        # Initialize requires two inputs. data (dictionary) represents the MCU configuration. query_func represents the
        # authenticated 'Database' class query function that is passed to this class.

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.data = data
        self.query = query_func
        self.sensors = dict()
        self.sensor_org = dict()
        self.mosquitto = object()
        self.commands = object()
        self.run()

    def run(self):
        self.initialize_mosquitto()
        self.initialize_sensors()
        self.initialize_commands()
        print(self.__repr__())

    def reload_data(self):
        new_info = load_data()
        self.data = new_info['data']
        self.run()

    def initialize_mosquitto(self):
        self.data['mqtt_data'].update({'on_message': self.message_callback})
        name_data = {'room_data': self.data['room_data'],
                     'thing_data': self.data['thing_data'],
                     'sensor_data': self.data['sensor_data']}

        self.mosquitto = Mosquitto(self.data['mqtt_data'], name_data=name_data)
        self.mosquitto_dummies = [Mosquitto(self.data['mqtt_data'], name_data=name_data, dummy=True)]
        self.mosquitto.start()
        self.mosquitto.join(timeout=3)

    def initialize_sensors(self):
        for sensor in self.data['sensor_data']:
            sensor_type = sensor['pin_sensor']

            if sensor_type in list(self.sensor_org.keys()):
                self.sensor_org[sensor_type].append(sensor['pin_id'])
            else:
                self.sensor_org.update({sensor_type: [sensor['pin_id']]})

            if sensor['pin_interrupt'] == 1:
                for pin in self.data['interrupt_data']:
                    if pin['pin_id'] == sensor['pin_id']:
                        self.sensors.update({sensor['pin_id']: Sensor(
                            data=sensor, interrupt_data=pin, query_func=self.query,
                            interrupt_func=self.interrupt_callback)})
            else:
                self.sensors.update({sensor['pin_id']: Sensor(
                    data=sensor, query_func=self.query,
                    interrupt_func=self.interrupt_callback)})

    def initialize_commands(self):
        additional_data = {
            'sensors': self.sensors,
            'sensor_org': self.sensor_org,
            'status': self.status,
            'reload': self.reload_data
        }
        self.commands = Commands(self.data['commands_data'], self.mosquitto, additional_data)

    def interrupt_callback(self, channel):
        value = self.sensors[channel].state()
        interrupt = str(self.sensors[channel])
        if self.sensors[channel].interrupt_data['interrupt_value'] == value:
            print('Interrupt activated from pin # {}\n{}'.format(channel, interrupt))
            result = self.status(update_value={channel: value})

            message1 = 'status_update;ignore:{}'.format(self.data['thing_data']['thing_id'])

            mqtt_payloads = {
                'group_commands': message1,
                'thing_info': str(result),
                'thing_interrupts': interrupt
            }
            mqtt = self.mosquitto_dummies * len(mqtt_payloads)
            i = 0
            for t in mqtt:
                t.start()

            threads = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                for payload in mqtt_payloads:
                    threads.append(
                        executor.submit(mqtt[i].broadcast, channel=payload, status=mqtt_payloads[payload]))
                    i += 1

                for result in as_completed(threads):
                    print(result.result())

    def message_callback(self, client, user_data, message):
        payload = {
            'mosquitto_message': message.payload.decode(),
            'mosquitto_topic': message.topic,
            'mosquitto_qos': message.qos,
            'mosquitto_retain': message.retain,
            'mosquitto_received': datetime.datetime.now()
        }

        if 'ignore:' in payload['mosquitto_message']:
            check = payload['mosquitto_message'].split(';')

            if eval(check[1].replace('ignore:')) == self.data['thing_data']['thing_id']:
                return
            else:
                print('Messaged received on \n{}\n{}'.format(payload['mosquitto_topic'], payload['mosquitto_message']))
                self.process_command(payload)
        else:
            print('Messaged received on \n{}\n{}'.format(payload['mosquitto_topic'], payload['mosquitto_message']))
            self.process_command(payload)

    def process_command(self, command):
        command_data = {
            'rule_name': command['mosquitto_topic'],
            'result': command['mosquitto_message'],
            'rule_timer': 0,
            'rule_function': None}

        self.commands.command(command_data)

    def status(self, update_value=None):
        results = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            break_up = False
            for result in self.sensor_org:
                execute = []
                stored = []
                for pin in self.sensor_org[result]:
                    if update_value is not None and pin in list(update_value.keys()):
                        stored.append(update_value[pin])
                    else:
                        execute.append(executor.submit(self.sensors[pin].state))

                for store in as_completed(execute):
                    if isinstance(store.result(), dict):
                        break_up = True
                    else:
                        break_up = False
                    stored.append(store.result())

                if break_up:
                    new_stored = break_up_sensor_data(stored)
                    results.update(new_stored)
                else:
                    results.update({result: stored})

        return results

    def __repr__(self):
        state = '       Current MCU Status\n'
        status = self.status()
        for value in status:
            state += '{:15}------     {}\n'.format(value, status[value])
        return state


class Sensor:
    def __init__(self, data, query_func, interrupt_func, interrupt_data=None):
        self.data = data
        self.query = query_func
        self.interrupt_callback = interrupt_func
        self.interrupt_data = interrupt_data
        self.run()

    def run(self):
        self.initialize()

    def initialize(self):
        print('Initializing Sensor...{} - {}'.format(self.data['pin_id'], self.data['pin_sensor']))
        if self.data['pin_interrupt'] == 1:
            bounce_time = 8000
            if self.interrupt_data['interrupt_pull'] == 'down' and self.interrupt_data['interrupt_on'] == 'rising':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.RISING,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

            elif self.interrupt_data['interrupt_pull'] == 'down' and self.interrupt_data['interrupt_on'] == 'falling':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.FALLING,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

            elif self.interrupt_data['interrupt_pull'] == 'down' and self.interrupt_data['interrupt_on'] == 'both':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.BOTH,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

            elif self.interrupt_data['interrupt_pull'] == 'up' and self.interrupt_data['interrupt_on'] == 'rising':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.RISING,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

            elif self.interrupt_data['interrupt_pull'] == 'up' and self.interrupt_data['interrupt_on'] == 'falling':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.FALLING,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

            elif self.interrupt_data['interrupt_pull'] == 'up' and self.interrupt_data['interrupt_on'] == 'both':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.BOTH,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)
            #
            elif self.interrupt_data['interrupt_pull'] == 'None' and self.interrupt_data['interrupt_on'] == 'rising':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.RISING,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

            elif self.interrupt_data['interrupt_pull'] == 'None' and self.interrupt_data['interrupt_on'] == 'falling':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.FALLING,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

            elif self.interrupt_data['interrupt_pull'] == 'None' and self.interrupt_data['interrupt_on'] == 'both':
                GPIO.setup(self.interrupt_data['pin_id'], GPIO.IN)
                GPIO.add_event_detect(self.interrupt_data['pin_id'], GPIO.BOTH,
                                      callback=self.interrupt_callback, bouncetime=bounce_time)

        elif self.data['pin_type'] == 'input':
            GPIO.setup(self.data['pin_id'], GPIO.IN)

        elif self.data['pin_type'] == 'output':
            GPIO.setup(self.data['pin_id'], GPIO.OUT)

    def state(self):

        if self.data['pin_type'] == 'adc':
            return Adafruit_ADS1x15.ADS1115().read_adc(self.data['pin_id'], gain=1)

        elif self.data['pin_type'] == 'dht':
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.data['pin_id'])
            return {'temperature': temperature, 'humidity': humidity}
        else:
            return GPIO.input(self.data['pin_id'])

    def set(self, value):
        return write_value(self.data['pin_id'], value)

    def __repr__(self):
        current = 'Sensor Name: {pin_name} | Sensor type: {pin_sensor} | Sensor value: {value}'
        value = self.state()
        return current.format(pin_name=self.data['pin_name'], pin_sensor=self.data['pin_sensor'], value=value)
