import datetime
import json
import time
from threading import Thread

from modules.mosquitto_manager import Mosquitto
import numpy


class HVAC(Thread):
    def __init__(self, query_func):
        Thread.__init__(self)
        self.data = dict()
        self.query = query_func
        self.mosquitto = dict()
        self.status = dict()
        self.monitor_thread = Thread()
        self.stop_thread = False
        self.start()
        time.sleep(1)

    def run(self):
        self.initialize_data()
        self.initialize_mosquitto()

    def initialize_data(self):
        print('initializing data')
        self.data = {
            'thing_id': 1,
            'room_id': 1,
        }

    def initialize_mosquitto(self):
        print('initializing mosquitto')
        self.mosquitto.update({
            'HVAC': MQTT(
                type='HVAC',
                level_id=1,
                thing_id=self.data['thing_id'],
                room_id=self.data['room_id'],
                query_func=self.query,
                on_message=self.message_callback)})

        for channel in self.mosquitto:
            self.mosquitto[channel].start()

    def message_callback(self, client, user_data, message):
        payload = {
            'mosquitto_message': message.payload.decode(),
            'mosquitto_topic': message.topic,
            'mosquitto_qos': message.qos,
            'mosquitto_retain': message.retain,
            'mosquitto_received': datetime.datetime.now()
        }
        # print('Messaged received on \n{}\n{}'.format(payload['mosquitto_topic'], payload['mosquitto_message']))
        if payload['mosquitto_message'].isnumeric():
            payload['mosquitto_message'] = int(payload['mosquitto_message'])

        self.status.update({payload['mosquitto_topic']: payload['mosquitto_message']})
        if 'commands' in payload['mosquitto_topic']:
            self.set_to(payload['mosquitto_message'])

    def current(self, reading, operation):
        temperature = []
        humidity = []
        for channel in self.status:
            if 'temp_humidity' in channel:
                sensors = self.status[channel]
                sensors = sensors.replace("'", '"')
                sensors = json.loads(sensors)

                temperature.append(sensors['temperature'])
                humidity.append(sensors['humidity'])
        if temperature != [] and humidity != []:
            op = {
                'temperature': {
                    'average': numpy.mean(temperature),
                    'sum': numpy.sum(temperature),
                    'min': numpy.min(temperature),
                    'max': numpy.max(temperature),
                    'median': numpy.median(temperature)
                },
                'humidity': {
                    'average': numpy.mean(humidity),
                    'sum': numpy.sum(humidity),
                    'min': numpy.min(humidity),
                    'max': numpy.max(humidity),
                    'median': numpy.median(humidity)
                }
            }
        return op[reading][operation]

    def set_to(self, temp):
        print('Setting HVAC to {} degrees'.format(temp))
        ac = False
        heat = False

        current = self.current('temperature', 'average')
        if temp < current:
            ac = True

        elif temp > current:
            heat = True

        if self.monitor_thread.is_alive():
            self.stop_thread = True
            self.ac('off')
            self.heat('off')
            self.fan('off')
            self.stop_thread = False

        self.monitor_thread = Thread(target=self.monitor, args=[temp, ac, heat])
        self.monitor_thread.start()

    def monitor(self, temp, ac, heat):
        if ac:
            print('on')
            self.ac('on')
            self.fan('on')

        elif heat:
            self.heat('on')
            self.fan('on')

        v_pass = False
        while not v_pass:

            if self.stop_thread:
                print('stopping')
                return
            else:
                current = self.current('temperature', 'average')
                print(temp, current)

                if temp != current:
                    time.sleep(.25)

                elif temp == current:
                    v_pass = True
        if ac:
            self.ac('off')

        elif heat:
            self.heat('off')

        self.fan('off')

    def ac(self, state):
        if state == 'on':
            self.mosquitto['HVAC'].broadcast(
                channel_type='commands',
                info_type='',
                msg='AC_on',
                level=3
            )
        elif state == 'off':
            self.mosquitto['HVAC'].broadcast(
                channel_type='commands',
                info_type='',
                msg='AC_off',
                level=3
            )
        time.sleep(.25)

    def heat(self, state):
        if state == 'on':
            self.mosquitto['HVAC'].broadcast(
                channel_type='commands',
                info_type='',
                msg='heat_on',
                level=3
            )
        elif state == 'off':
            self.mosquitto['HVAC'].broadcast(
                channel_type='commands',
                info_type='',
                msg='heat_off',
                level=3
            )
        time.sleep(.25)

    def fan(self, state):
        if state == 'on':
            self.mosquitto['HVAC'].broadcast(
                channel_type='commands',
                info_type='',
                msg='fan_on',
                level=3
            )
        elif state == 'off':
            self.mosquitto['HVAC'].broadcast(
                channel_type='commands',
                info_type='',
                msg='fan_off',
                level=3
            )
        time.sleep(.25)
