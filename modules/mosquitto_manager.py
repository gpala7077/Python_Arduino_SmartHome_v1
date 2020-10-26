from threading import Thread
import paho.mqtt.client as mqtt


class Mosquitto(Thread):
    def __init__(self, data, name_data, dummy=False):
        super().__init__()
        print('\n*** Initializing MQTT Client *** ')
        self.client = mqtt.Client()
        self.name_data = name_data
        self.data = data
        self.dummy = dummy

    def run(self):
        self.connect()

        if not self.dummy:
            self.listen()

    def get_sensor(self, pin):
        for sensor in self.name_data['sensor_data']:
            if sensor['pin_id'] == pin:
                return sensor

    def get_thing(self, thing_id):
        for thing in self.name_data['thing_data']:
            if thing['thing_id'] == thing_id:
                return thing

    def get_channel(self, channel, pin=None, thing_id=None):
        for channel_lst in self.data['channels']:
            if channel_lst['channel_name'] == channel:
                channel = channel_lst['channel_broadcast']

                if 'room_name' in channel:
                    channel = channel.replace('room_name', self.name_data['room_data']['room_name'])

                if 'thing_name' in channel:
                    if self.data['type'] == 'thing':
                        channel = channel.replace('thing_name', self.name_data['thing_data']['thing_name'])

                    elif self.data['type'] == 'room':
                        thing_data = self.get_thing(thing_id)
                        channel = channel.replace('thing_name', thing_data['thing_name'])

                if 'pin_sensor' in channel:
                    sensor_data = self.get_sensor(pin)
                    channel = channel.replace('pin_sensor', sensor_data['pin_sensor'])
                    channel = channel.replace('pin_name', sensor_data['pin_name'])

        return channel

    def connect(self):
        print('* Connecting to broker *')
        self.client.connect(self.data['configuration']['mqtt_value'])

        if not self.dummy:
            self.client.on_message = self.data['on_message']

    def listen(self):
        for channel in self.data['listen']:

            channel = self.get_channel(channel)
            print('* Listening to {} *'.format(channel))
            self.client.subscribe(channel)
        self.client.loop_forever()

    def broadcast(self, channel, payload, pin=None, thing_id=None):
        print('channel:{}'.format(channel), 'payload:{}'.format(payload))
        if pin is not None:
            channel = self.get_channel(channel, pin=pin)

        if thing_id is not None:
            channel = self.get_channel(channel, thing_id=thing_id)

        else:
            channel = self.get_channel(channel)

        print('* Publishing on {} *\nPayload...\n{}'.format(channel, payload))
        self.client.publish(channel, payload)
