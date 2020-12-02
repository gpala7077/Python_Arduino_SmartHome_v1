import paho.mqtt.client as mqtt
from threading import Thread
from modules.miscellaneous import Queue


class Mosquitto:
    def __init__(self, host_ip):
        print('Starting up MQTT Client')
        self.client = mqtt.Client()
        self.host_ip = host_ip
        self.messages = Queue('FIFO')
        self.connect()

    def mosquitto_callback(self, client, userdata, message):
        """Mosquitto callback function."""

        task = Thread(target=self.add_message, args=[message])
        task.start()

    def add_message(self, message):
        msg = message.payload.decode("utf-8")
        print('Received message!\n{}\n'.format(msg))
        self.messages.add(msg)

    def connect(self):
        """Connect to MQTT Broker and set callback."""

        print('Connecting to broker... {}'.format(self.host_ip))
        self.client.connect(self.host_ip)
        self.client.on_message = self.mosquitto_callback

    def listen(self, channels):
        """Creates a sub-thread and actively listens to given channels."""

        for channel in channels:
            print('Listening to ...\n{}\n'.format(channel))
            self.client.subscribe(channel)

        listen = Thread(target=self.client.loop_forever)
        listen.start()

        return 'Actively Listening for MQTT Broadcasts'

    def broadcast(self, channels, payload):
        """Broadcast payload to given channels."""

        for channel in channels:
            print('\nBroadcasting on...\n{}\nPayload : {}\n'.format(channel, payload))
            self.client.publish(channel, str(payload))

        return 'Payload sent'
