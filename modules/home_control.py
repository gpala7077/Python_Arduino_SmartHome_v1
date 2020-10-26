import ast
import datetime
from collections import defaultdict
from modules.hue_manager import HueAPI
from modules.mosquitto_manager import Mosquitto
from modules.rules_manager import Rules
from modules.commands_manager import Commands


def combine_data(dictionary):
    combined_dictionary = defaultdict(list)
    for thing_data in [dictionary[status] for status in dictionary]:
        thing_data = ast.literal_eval(thing_data)
        for key, value in thing_data.items():
            for val in value:
                combined_dictionary[key].append(val)
    return dict(combined_dictionary)


class Room:
    def __init__(self, data, query_func):
        self.data = data
        self.query = query_func
        self.things = dict()
        self.rules = object()
        self.commands = object()
        self.mosquitto = object()
        self.interrupt = str()
        self.third_party = dict()
        self.run()

    def run(self):
        self.initialize_third_party()
        self.initialize_mosquitto()
        self.initialize_rules()
        self.initialize_commands()
        self.initialize_things()
        self.mosquitto.broadcast('group_commands', 'status_update')

    def initialize_third_party(self):

        self.third_party.update(
            {'hue': HueAPI(hue_credentials={'192.168.50.34': 'pJPb8WW2wW1P82RKu1sHBLkEQofDMofh2yNDnXzj'})}
        )

    def initialize_mosquitto(self):
        self.data['mqtt_data'].update({'on_message': self.message_callback})
        name_data = {'room_data': self.data['room_data'],
                     'thing_data': self.data['thing_data']}

        self.mosquitto = Mosquitto(data=self.data['mqtt_data'], name_data=name_data)
        self.mosquitto.start()
        self.mosquitto.join(timeout=3)

    def initialize_rules(self):
        self.rules = Rules(self.data['rules_data'])

    def initialize_commands(self):
        additional_data = {
            'hue': self.third_party['hue']
        }

        self.commands = Commands(self.data['commands_data'], self.mosquitto, additional_data=additional_data)

    def initialize_things(self):

        for thing_data in self.data['thing_data']:
            mqtt_data = self.data['mqtt_data']
            mqtt_data.update({'type': 'thing'})
            mqtt_data.update({'listen': ['thing_info', 'thing_sensors']})
            sensor_data = []
            for sensor in self.data['sensor_data']:
                if sensor['thing_id'] == thing_data['thing_id']:
                    sensor_data.append(sensor)
            data = {
                'room_data': self.data['room_data'],
                'sensor_data': sensor_data,
                'thing_data': thing_data,
                'mqtt_data': mqtt_data
            }
            self.things.update({thing_data['thing_id']: Thing(data, self.query)})

    def message_callback(self, client, user_data, message):
        payload = {
            'mosquitto_message': message.payload.decode(),
            'mosquitto_topic': message.topic,
            'mosquitto_qos': message.qos,
            'mosquitto_retain': message.retain,
            'mosquitto_received': datetime.datetime.now()
        }
        print('Messaged received on \n{}\n{}'.format(payload['mosquitto_topic'], payload['mosquitto_message']))

        if '/interrupt' in payload['mosquitto_topic']:
            self.interrupt = payload['mosquitto_message']
            self.process_rules()

        elif '/commands' in payload['mosquitto_topic']:
            self.commands.command(payload['mosquitto_message'])

    def process_rules(self):
        status = combine_data(self.get_status())
        status.update(self.get_third_party_data('hue'))

        actions = self.rules.rules(status)
        for action in actions:
            self.commands.command(action)

    def get_status(self):
        dictionary = {}
        for thing in self.things:
            dictionary.update({self.things[thing].data['thing_data']['thing_id']: self.things[thing].status})
        return dictionary

    def get_third_party_data(self, app):
        if app == 'hue':
            data = self.third_party[app].get_group(self.data['room_data']['room_id'])
            remove = ['name', 'sensors', 'type', 'recycle','class','action']
            for key in remove:
                data.pop(key)
        return data


class Thing:
    def __init__(self, data, query_func):
        self.data = data
        self.query = query_func
        self.status = str()
        self.values = dict()
        self.mosquitto = object()
        self.run()

    def run(self):
        self.initialize_mosquitto()

    def initialize_mosquitto(self):
        self.data['mqtt_data'].update({'on_message': self.message_callback})
        name_data = {'room_data': self.data['room_data'],
                     'thing_data': self.data['thing_data'],
                     'sensor_data': self.data['sensor_data']}

        self.mosquitto = Mosquitto(self.data['mqtt_data'], name_data=name_data)
        self.mosquitto.start()
        self.mosquitto.join(timeout=3)

    def message_callback(self, client, user_data, message):
        payload = {
            'mosquitto_message': message.payload.decode(),
            'mosquitto_topic': message.topic,
            'mosquitto_qos': message.qos,
            'mosquitto_retain': message.retain,
            'mosquitto_received': datetime.datetime.now()
        }
        print('Messaged received on \n{}\n{}'.format(payload['mosquitto_topic'], payload['mosquitto_message']))
        if '/info' in payload['mosquitto_topic']:
            self.status = payload['mosquitto_message']

        elif '/value' in payload['mosquitto_topic']:
            self.values.update({payload['mosquitto_topic']: payload['mosquitto_message']})