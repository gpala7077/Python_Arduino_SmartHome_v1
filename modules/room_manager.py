import json
from datetime import datetime
from threading import Thread

import pandas as pd

from modules.main_manager import Main
from modules.miscellaneous import Queue


class Room(Main):

    def __init__(self, credentials, room_id):
        super().__init__(credentials)
        self.data = self.db.get_room_data(room_id)
        self.things = {thing['thing_name']: Thing(credentials, thing['thing_id'])
                       for thing in self.data['thing_data'].to_dict(orient='records')}
        self.interrupts = Queue('LIFO')

    def initialize(self):
        super(Room, self).initialize()
        self.commands.current_status = self.current_status
        self.commands.third_party = self.third_party
        for thing in self.things:
            print(self.things[thing].initialize())
        return 'Room initialized\n'

    def current_status(self):
        df = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value', 'time_stamp'])
        for thing in self.things:
            df = df.append(self.things[thing].sensors.query('time_stamp=="{}"'.format(
                self.things[thing].sensors['time_stamp'].max()
            )))

        return df

    def process_interrupt(self):
        print(self.commands.execute(self.interrupts.get()))

    def process_message(self):
        topic, msg = self.mosquitto.messages.get()

        if 'interrupt' in topic:
            msg = msg.replace("'", "\"")
            msg = json.loads(msg)
            rows = len(msg['sensor_name'])
            msg.update({'time_stamp': [datetime.now()] * rows})
            msg = pd.DataFrame.from_dict(msg)
            self.interrupts.add(msg)

        elif 'commands' in topic:
            pass

    def run(self):
        super(Room, self).run()
        for thing in self.things:
            Thread(target=self.things[thing].run).start()

        activity = Thread(target=self.monitor_interrupts)
        activity.start()

        while True:
            pass


class Thing(Main):

    def __init__(self, credentials, thing_id):
        super().__init__(credentials)
        self.data = self.db.get_thing_data(thing_id, 'receiver')
        self.sensors = pd.DataFrame(columns=['sensor_name', 'sensor_type', 'sensor_value', 'time_stamp'])

    def initialize(self):
        super(Thing, self).initialize()
        return 'Thing initialized\n'

    def process_message(self):
        topic, msg = self.mosquitto.messages.get()

        if 'info' in topic:
            msg = msg.replace("'", "\"")
            msg = json.loads(msg)
            rows = len(msg['sensor_name'])
            msg.update({'time_stamp': [datetime.now()] * rows})
            msg = pd.DataFrame.from_dict(msg)
            self.sensors = self.sensors.append(msg)

    def run(self):
        super(Thing, self).run()
        self.mosquitto.broadcast(self.data['mqtt_data']['channels'].
                                 query('channel_name == "thing_commands"')['channel_broadcast'], 'status')
        while True:
            pass
