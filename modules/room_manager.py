from datetime import datetime
from threading import Thread
import pandas as pd
from modules.main_manager import Main
import json


class Room(Main):

    def __init__(self, credentials, room_id):
        super().__init__(credentials)
        self.data = self.db.get_room_data(room_id)
        self.things = {thing['thing_name']: Thing(credentials, thing['thing_id'])
                       for thing in self.data['thing_data'].to_dict(orient='records')}

    def initialize(self):
        super(Room, self).initialize()
        for thing in self.things:
            print(self.things[thing].initialize())
        return 'Room initialized'

    def run(self):
        super(Room, self).run()
        for thing in self.things:
            Thread(target=self.things[thing].run).start()

        while True:
            pass


class Thing(Main):

    def __init__(self, credentials, thing_id):
        super().__init__(credentials)
        self.data = self.db.get_thing_data(thing_id, 'receiver')
        self.sensors = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value', 'time_stamp'])

    def initialize(self):
        super(Thing, self).initialize()
        return 'Thing initialized'

    def monitor_messages(self):
        while True:
            if self.mosquitto.messages:
                task = Thread(target=self.process_message)
                task.start()

    def process_message(self):
        topic, msg = self.mosquitto.messages.get()

        if 'interrupt' in topic:
            print(msg)

        elif 'info' in topic:
            msg = msg.replace("'", "\"")
            msg = json.loads(msg)
            rows = len(msg['sensor_name'])
            msg.update({'time_stamp': [datetime.now()] * rows})
            msg = pd.DataFrame.from_dict(msg)
            self.sensors = self.sensors.append(msg)

    def run(self):
        super(Thing, self).run()
        status = Thread(target=self.monitor_messages)
        status.start()
        self.mosquitto.broadcast(self.data['mqtt_data']['channels'].
                                 query('channel_name == "thing_commands"')['channel_broadcast'], 'status')
